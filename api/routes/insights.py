from fastapi import APIRouter, HTTPException
from services.instagram_service import InstagramService
from datetime import datetime, timedelta

router = APIRouter(prefix="/instagram/insights", tags=["insights"])

@router.get("/weekly")
async def get_weekly_insights():
    """Get weekly performance insights using real Instagram data"""
    try:
        instagram_service = InstagramService()
        
        # Get account insights for the last 7 days with correct v23 metrics
        insights = instagram_service.get_account_insights(period="day", days=7, metrics="reach,profile_views,accounts_engaged")
        
        if not insights.get('success'):
            return {"success": False, "data": []}
        
        # Get media posts for engagement calculation
        media_result = instagram_service.get_media_list(50)
        posts = media_result.get('data', {}).get('data', []) if media_result.get('success') else []
        
        # Process real insights data
        insights_data = insights.get('data', [])
        
        # Create daily data structure
        daily_data = {}
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            day_name = date.strftime('%a')
            daily_data[day_name] = {
                "name": day_name,
                "engagement": 0,
                "reach": 0, 
                "impressions": 0,
                "views": 0
            }
        
        # Fill with real insights data
        for insight in insights_data:
            metric_name = insight.get('name')
            values = insight.get('values', [])
            
            for i, value_obj in enumerate(values[:7]):
                if i < 7:
                    date = datetime.now() - timedelta(days=6-i)
                    day_name = date.strftime('%a')
                    value = value_obj.get('value', 0)
                    
                    if metric_name == 'impressions':
                        daily_data[day_name]["impressions"] = value
                    elif metric_name == 'reach':
                        daily_data[day_name]["reach"] = value
                    elif metric_name == 'profile_views':
                        daily_data[day_name]["views"] = value
        
        # Calculate engagement from posts data
        for post in posts:
            if post.get('timestamp'):
                post_date = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
                day_name = post_date.strftime('%a')
                if day_name in daily_data:
                    engagement = (post.get('like_count', 0) + post.get('comments_count', 0))
                    daily_data[day_name]["engagement"] += engagement
        
        data = list(daily_data.values())
        return {"success": True, "data": data}
        
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

@router.get("/performance")
async def get_performance_insights():
    """Get real performance insights using Instagram insights API"""
    try:
        instagram_service = InstagramService()
        
        # Get account insights with correct v23 metrics
        insights = instagram_service.get_account_insights(period="day", days=7, metrics="reach,profile_views,accounts_engaged,total_interactions")
        if not insights.get('success'):
            return {"success": False, "data": []}
        
        # Get media for engagement and saves data
        media_result = instagram_service.get_media_list(50)
        posts = media_result.get('data', {}).get('data', []) if media_result.get('success') else []
        
        # Get individual post insights for saves/shares
        post_insights = {}
        for post in posts[:10]:  # Limit to recent posts
            try:
                insights_result = instagram_service.get_media_insights(post['id'])
                if insights_result.get('success'):
                    post_insights[post['id']] = insights_result.get('data', [])
            except:
                continue
        
        insights_data = insights.get('data', [])
        
        # Process real data by day
        data = []
        for i in range(7):
            day_data = {
                "date": f"Day {i + 1}",
                "engagement": 0,
                "reach": 0,
                "views": 0,
                "impressions": 0,
                "saves": 0,
                "shares": 0
            }
            
            # Fill with real insights
            for insight in insights_data:
                values = insight.get('values', [])
                if len(values) > i:
                    value = values[i].get('value', 0)
                    metric_name = insight.get('name')
                    
                    if metric_name == 'impressions':
                        day_data["impressions"] = value
                    elif metric_name == 'reach':
                        day_data["reach"] = value
                    elif metric_name == 'profile_views':
                        day_data["views"] = value
            
            # Calculate engagement from posts
            day_posts = [p for p in posts if p.get('timestamp')]
            for post in day_posts:
                post_date = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
                days_ago = (datetime.now() - post_date.replace(tzinfo=None)).days
                if days_ago == (6 - i):  # Match the day
                    day_data["engagement"] += (post.get('like_count', 0) + post.get('comments_count', 0))
                    
                    # Get saves from post insights
                    if post['id'] in post_insights:
                        for insight in post_insights[post['id']]:
                            if insight.get('name') == 'saved':
                                day_data["saves"] += insight.get('value', 0)
            
            # Estimate shares (Instagram doesn't provide this directly)
            day_data["shares"] = int(day_data["engagement"] * 0.05)
            
            data.append(day_data)
        
        return {"success": True, "data": data}
        
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

@router.get("/audience")
async def get_audience_insights():
    """Get real audience demographics using instagram_manage_insights permission"""
    try:
        instagram_service = InstagramService()
        
        # Get audience demographics with v23 metrics
        url = f"{instagram_service.base_url}/{instagram_service.instagram_account_id}/insights"
        params = {
            'metric': 'follower_demographics',
            'period': 'lifetime',
            'metric_type': 'total_value',
            'access_token': instagram_service.access_token
        }
        
        import requests
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {"success": False, "data": []}
        
        result = response.json()
        if 'error' in result:
            return {"success": False, "data": []}
        
        data = []
        insights_data = result.get('data', [])
        
        for insight in insights_data:
            if insight.get('name') == 'audience_gender_age':
                values = insight.get('values', [])
                if values and values[0].get('value'):
                    age_gender_data = values[0]['value']
                    
                    # Process age demographics
                    age_totals = {}
                    total_audience = 0
                    
                    for key, count in age_gender_data.items():
                        if '.' in key:  # Format: "F.25-34" or "M.18-24"
                            age_range = key.split('.')[1]
                            age_totals[age_range] = age_totals.get(age_range, 0) + count
                            total_audience += count
                    
                    # Convert to percentages
                    for age_range, count in age_totals.items():
                        percentage = (count / total_audience * 100) if total_audience > 0 else 0
                        data.append({
                            "demographic": f"Age {age_range}",
                            "value": round(percentage),
                            "color": get_color_for_age(age_range)
                        })
        
        # Fallback if no real data
        if not data:
            data = [{"demographic": "No Audience Data", "value": 100, "color": "#6B7280"}]
        
        return {"success": True, "data": data}
        
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

@router.get("/engagement-time")
async def get_engagement_by_time():
    """Get engagement by time of day"""
    try:
        instagram_service = InstagramService()
        media_result = instagram_service.get_media_list(50)
        
        if not media_result.get('success'):
            return {"success": False, "data": []}
        
        posts = media_result.get('data', {}).get('data', [])
        hourly_engagement = [0] * 24
        
        for post in posts:
            if post.get('timestamp'):
                hour = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00')).hour
                engagement = (post.get('like_count', 0) + post.get('comments_count', 0))
                hourly_engagement[hour] += engagement
        
        data = [
            {"time": "6AM", "engagement": hourly_engagement[6] + hourly_engagement[7]},
            {"time": "9AM", "engagement": hourly_engagement[9] + hourly_engagement[10]},
            {"time": "12PM", "engagement": hourly_engagement[12] + hourly_engagement[13]},
            {"time": "3PM", "engagement": hourly_engagement[15] + hourly_engagement[16]},
            {"time": "6PM", "engagement": hourly_engagement[18] + hourly_engagement[19]},
            {"time": "9PM", "engagement": hourly_engagement[21] + hourly_engagement[22]},
            {"time": "12AM", "engagement": hourly_engagement[0] + hourly_engagement[1]}
        ]
        
        return {"success": True, "data": data}
        
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

@router.get("/engagement-trends")
async def get_engagement_trends():
    """Get weekly engagement trends"""
    try:
        instagram_service = InstagramService()
        media_result = instagram_service.get_media_list(50)
        
        if not media_result.get('success'):
            return {"success": False, "data": []}
        
        posts = media_result.get('data', {}).get('data', [])
        
        # Group posts by weeks
        weeks_data = [[], [], [], []]
        for i, post in enumerate(posts[:40]):  # Limit to 40 posts
            week_index = i // 10
            if week_index < 4:
                weeks_data[week_index].append(post)
        
        data = []
        for i, week_posts in enumerate(weeks_data):
            likes = sum(post.get('like_count', 0) for post in week_posts)
            comments = sum(post.get('comments_count', 0) for post in week_posts)
            shares = int(likes * 0.1)  # Approximate shares
            
            data.append({
                "week": f"Week {i + 1}",
                "likes": likes,
                "comments": comments,
                "shares": shares
            })
        
        return {"success": True, "data": data}
        
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

@router.get("/reach")
async def get_reach_insights():
    """Get real reach and impressions data using Instagram insights"""
    try:
        instagram_service = InstagramService()
        
        # Get comprehensive insights with v23 metrics
        insights = instagram_service.get_account_insights(period="day", days=7, metrics="reach,profile_views,accounts_engaged")
        
        if not insights.get('success'):
            return {"success": False, "data": []}
        
        total_reach = 0
        total_impressions = 0
        total_profile_views = 0
        total_website_clicks = 0
        
        insights_data = insights.get('data', [])
        
        for insight in insights_data:
            values = insight.get('values', [])
            total_value = sum(v.get('value', 0) for v in values)
            metric_name = insight.get('name')
            
            if metric_name == 'reach':
                total_reach = total_value
            elif metric_name == 'impressions':
                total_impressions = total_value
            elif metric_name == 'profile_views':
                total_profile_views = total_value
            elif metric_name == 'website_clicks':
                total_website_clicks = total_value
        
        data = [
            {"metric": "Reach", "value": total_reach, "color": "#3B82F6"},
            {"metric": "Impressions", "value": total_impressions, "color": "#10B981"},
            {"metric": "Profile Views", "value": total_profile_views, "color": "#F59E0B"}
        ]
        
        # Add website clicks if available
        if total_website_clicks > 0:
            data.append({"metric": "Website Clicks", "value": total_website_clicks, "color": "#8B5CF6"})
        
        return {"success": True, "data": data}
        
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

def get_color_for_age(age_range):
    """Get color for age demographic"""
    colors = {
        "13-17": "#3B82F6",
        "18-24": "#10B981", 
        "25-34": "#F59E0B",
        "35-44": "#EF4444",
        "45-54": "#8B5CF6",
        "55-64": "#06B6D4",
        "65+": "#6B7280"
    }
    return colors.get(age_range, "#6B7280")