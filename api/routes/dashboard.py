from fastapi import APIRouter, HTTPException
import asyncio
from services.instagram_service import InstagramService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/data")
async def get_dashboard_data():
    """Get all dashboard data in parallel for faster loading"""
    try:
        instagram_service = InstagramService()
        
        # Run all API calls in parallel
        tasks = [
            asyncio.create_task(get_account_data(instagram_service)),
            asyncio.create_task(get_media_data(instagram_service)),
            asyncio.create_task(get_top_posts_data(instagram_service)),
            asyncio.create_task(get_sentiment_data(instagram_service))
        ]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        account_data, media_data, top_posts_data, sentiment_data = results
        
        # Handle exceptions
        if isinstance(account_data, Exception):
            account_data = {"success": False, "error": str(account_data)}
        if isinstance(media_data, Exception):
            media_data = {"success": False, "data": []}
        if isinstance(top_posts_data, Exception):
            top_posts_data = {"success": False, "data": []}
        if isinstance(sentiment_data, Exception):
            sentiment_data = {"success": False, "data": {"positive_percentage": 70, "neutral_percentage": 25, "negative_percentage": 5}}
        
        return {
            "success": True,
            "data": {
                "account": account_data,
                "media": media_data,
                "top_posts": top_posts_data,
                "sentiment": sentiment_data
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_account_data(instagram_service):
    """Get account info asynchronously"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, instagram_service.get_account_info)

async def get_media_data(instagram_service):
    """Get media list asynchronously"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, instagram_service.get_media_list, 10)

async def get_top_posts_data(instagram_service):
    """Get top posts asynchronously"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, instagram_service.get_top_posts, 5)

async def get_sentiment_data(instagram_service):
    """Get sentiment analysis asynchronously"""
    import requests
    from services.sentiment_service import sentiment_analyzer
    
    try:
        # Get recent posts
        media_result = instagram_service.get_media_list(5)  # Reduced from 10 to 5
        if not media_result.get('success'):
            return {"success": False, "error": "Failed to fetch posts"}
        
        posts = media_result.get('data', {}).get('data', [])
        all_comments = []
        
        # Collect comments from recent posts (limit to 3 posts for speed)
        for post in posts[:3]:
            try:
                comments_url = f"https://graph.facebook.com/v19.0/{post['id']}/comments"
                params = {
                    'access_token': instagram_service.access_token,
                    'fields': 'text',
                    'limit': 10  # Limit comments per post
                }
                
                comments_response = requests.get(comments_url, params=params, timeout=5)
                if comments_response.status_code == 200:
                    comments_data = comments_response.json()
                    for comment in comments_data.get('data', []):
                        if comment.get('text'):
                            all_comments.append(comment['text'])
            except:
                continue
        
        # Analyze sentiment
        if not all_comments:
            sentiment_result = {
                'overall_sentiment': 'neutral',
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 100,
                'total_comments': 0,
                'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        else:
            sentiment_result = sentiment_analyzer.analyze_comments_sentiment(all_comments)
        
        return {
            "success": True, 
            "data": {
                **sentiment_result,
                "sample_comments": all_comments[:5],  # Reduced sample size
                "has_comments": len(all_comments) > 0
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}