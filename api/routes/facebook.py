from fastapi import APIRouter, HTTPException
from services.facebook_service import FacebookService

router = APIRouter(prefix="/facebook", tags=["facebook"])

_facebook_service = None

def get_facebook_service():
    """Get Facebook service instance with lazy initialization"""
    global _facebook_service
    if _facebook_service is None:
        try:
            _facebook_service = FacebookService()
        except Exception as e:
            print(f"Failed to initialize Facebook service: {e}")
            _facebook_service = None
    return _facebook_service

@router.get("/account")
async def get_account_info():
    """Get Facebook Page information"""
    facebook_service = get_facebook_service()
    if not facebook_service:
        raise HTTPException(status_code=500, detail="Facebook service not initialized")
    
    try:
        result = facebook_service.get_account_info()
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch account info'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/media")
async def get_media_list(limit: int = 25):
    """Get recent Facebook posts"""
    facebook_service = get_facebook_service()
    if not facebook_service:
        raise HTTPException(status_code=500, detail="Facebook service not initialized")
    
    try:
        result = facebook_service.get_media_list(limit)
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch posts'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/media/{post_id}")
async def get_media_insights(post_id: str):
    """Get insights for specific Facebook post"""
    facebook_service = get_facebook_service()
    if not facebook_service:
        raise HTTPException(status_code=500, detail="Facebook service not initialized")
    
    try:
        data = facebook_service.get_media_insights(post_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/page")
async def get_page_insights(days: int = 7):
    """Get Facebook Page insights"""
    facebook_service = get_facebook_service()
    if not facebook_service:
        raise HTTPException(status_code=500, detail="Facebook service not initialized")
    
    try:
        result = facebook_service.get_page_insights(days=days)
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch page insights'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-posts")
async def get_top_posts(limit: int = 10):
    """Get top performing Facebook posts"""
    facebook_service = get_facebook_service()
    if not facebook_service:
        raise HTTPException(status_code=500, detail="Facebook service not initialized")
    
    try:
        result = facebook_service.get_top_posts(limit)
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch top posts'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment-analysis")
async def get_sentiment_analysis():
    """Get sentiment analysis of Facebook posts and comments"""
    import requests
    from services.sentiment_service import sentiment_analyzer
    
    facebook_service = get_facebook_service()
    if not facebook_service:
        raise HTTPException(status_code=500, detail="Facebook service not initialized")
    
    try:
        media_result = facebook_service.get_media_list(10)
        if not media_result.get('success'):
            return {"success": False, "error": "Failed to fetch posts"}
        
        posts = media_result.get('data', {}).get('data', [])
        all_comments = []
        
        for post in posts[:5]:
            try:
                comments_url = f"https://graph.facebook.com/v21.0/{post['id']}/comments"
                params = {
                    'access_token': facebook_service.access_token,
                    'fields': 'message'
                }
                
                comments_response = requests.get(comments_url, params=params, timeout=10)
                if comments_response.status_code == 200:
                    comments_data = comments_response.json()
                    for comment in comments_data.get('data', []):
                        if comment.get('message'):
                            all_comments.append(comment['message'])
            except:
                continue
        
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
                "sample_comments": all_comments[:10],
                "has_comments": len(all_comments) > 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/performance")
async def get_performance_insights():
    """Get Facebook performance insights (placeholder for now)"""
    # Return empty data for now since Facebook Page Insights API requires additional setup
    return {
        "success": True,
        "data": []
    }

@router.get("/insights/audience")
async def get_audience_insights():
    """Get Facebook audience insights (placeholder for now)"""
    return {
        "success": True,
        "data": []
    }

@router.get("/insights/engagement-time")
async def get_engagement_time_insights():
    """Get Facebook engagement time insights (placeholder for now)"""
    return {
        "success": True,
        "data": []
    }

@router.get("/insights/engagement-trends")
async def get_engagement_trends():
    """Get Facebook engagement trends (placeholder for now)"""
    return {
        "success": True,
        "data": []
    }

@router.get("/insights/reach")
async def get_reach_insights():
    """Get Facebook reach insights (placeholder for now)"""
    return {
        "success": True,
        "data": []
    }
