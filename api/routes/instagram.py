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

@router.get("/insights/account")
async def get_account_insights(days: int = 7):
    """Get account-level insights"""
    try:
        data = instagram_service.get_account_insights(days=days)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/media/{media_id}")
async def get_media_insights(media_id: str):
    """Get insights for specific media"""
    try:
        data = instagram_service.get_media_insights(media_id)
        return {"success": True, "data": data}
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