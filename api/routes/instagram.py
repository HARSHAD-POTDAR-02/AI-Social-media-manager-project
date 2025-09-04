from fastapi import APIRouter, HTTPException
from services.instagram_service import InstagramService

router = APIRouter(prefix="/instagram", tags=["instagram"])

# Lazy initialization of Instagram service
_instagram_service = None

def get_instagram_service():
    """Get Instagram service instance with lazy initialization"""
    global _instagram_service
    if _instagram_service is None:
        try:
            _instagram_service = InstagramService()
        except Exception as e:
            print(f"Failed to initialize Instagram service: {e}")
            _instagram_service = None
    return _instagram_service

@router.get("/validate")
async def validate_instagram_connection():
    """Validate Instagram API connection"""
    instagram_service = get_instagram_service()
    if not instagram_service:
        raise HTTPException(status_code=500, detail="Instagram service not initialized")
    
    try:
        result = instagram_service.validate_connection()
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('message', 'Connection validation failed'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/account")
async def get_account_info():
    """Get Instagram account information"""
    instagram_service = get_instagram_service()
    if not instagram_service:
        raise HTTPException(status_code=500, detail="Instagram service not initialized")
    
    try:
        result = instagram_service.get_account_info()
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch account info'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/media")
async def get_media_list(limit: int = 25):
    """Get recent Instagram media posts"""
    instagram_service = get_instagram_service()
    if not instagram_service:
        raise HTTPException(status_code=500, detail="Instagram service not initialized")
    
    try:
        result = instagram_service.get_media_list(limit)
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch media list'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demographics")
async def get_audience_demographics():
    """Get real audience demographics"""
    instagram_service = get_instagram_service()
    if not instagram_service:
        raise HTTPException(status_code=500, detail="Instagram service not initialized")
    
    try:
        result = instagram_service.get_audience_demographics()
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch demographics'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/account")
async def get_account_insights(days: int = 7):
    """Get account-level insights"""
    instagram_service = get_instagram_service()
    if not instagram_service:
        raise HTTPException(status_code=500, detail="Instagram service not initialized")
    
    try:
        result = instagram_service.get_account_insights(days=days)
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch account insights'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/media/{media_id}")
async def get_media_insights(media_id: str):
    """Get insights for specific media"""
    instagram_service = get_instagram_service()
    if not instagram_service:
        raise HTTPException(status_code=500, detail="Instagram service not initialized")
    
    try:
        data = instagram_service.get_media_insights(media_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-posts")
async def get_top_posts(limit: int = 10):
    """Get top performing posts"""
    instagram_service = get_instagram_service()
    if not instagram_service:
        raise HTTPException(status_code=500, detail="Instagram service not initialized")
    
    try:
        result = instagram_service.get_top_posts(limit)
        if result.get('success', False):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch top posts'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stories")
async def get_stories():
    """Get Instagram Stories"""
    try:
        data = instagram_service.get_stories()
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comments/{media_id}")
async def get_comments(media_id: str):
    """Get comments for specific media"""
    try:
        data = instagram_service.get_comments(media_id)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hashtag/{hashtag_id}")
async def get_hashtag_insights(hashtag_id: str):
    """Get hashtag insights"""
    try:
        data = instagram_service.get_hashtag_insights(hashtag_id)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment-analysis")
async def get_sentiment_analysis():
    """Get sentiment analysis of recent posts and comments"""
    import requests
    from services.sentiment_service import sentiment_analyzer
    
    instagram_service = get_instagram_service()
    if not instagram_service:
        raise HTTPException(status_code=500, detail="Instagram service not initialized")
    
    try:
        # Get recent posts
        media_result = instagram_service.get_media_list(10)
        if not media_result.get('success'):
            return {"success": False, "error": "Failed to fetch posts"}
        
        posts = media_result.get('data', {}).get('data', [])
        all_comments = []
        
        # Collect comments from recent posts
        for post in posts[:5]:  # Analyze comments from last 5 posts
            try:
                comments_url = f"https://graph.facebook.com/v19.0/{post['id']}/comments"
                params = {
                    'access_token': instagram_service.access_token,
                    'fields': 'text'
                }
                
                comments_response = requests.get(comments_url, params=params, timeout=10)
                if comments_response.status_code == 200:
                    comments_data = comments_response.json()
                    for comment in comments_data.get('data', []):
                        if comment.get('text'):
                            all_comments.append(comment['text'])
            except:
                continue  # Skip if can't fetch comments for this post
        
        # Analyze sentiment - if no comments, default to neutral
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
                "sample_comments": all_comments[:10],  # Include sample comments
                "has_comments": len(all_comments) > 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))