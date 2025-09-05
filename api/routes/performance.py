from fastapi import APIRouter
import time
import psutil
import os

router = APIRouter(prefix="/performance", tags=["performance"])

@router.get("/health")
async def performance_health():
    """Quick health check endpoint"""
    start_time = time.time()
    
    # Basic system info
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    return {
        "status": "healthy",
        "response_time_ms": round(response_time, 2),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2)
        },
        "api_status": "running"
    }

@router.get("/instagram-test")
async def test_instagram_connection():
    """Test Instagram API connection speed"""
    from services.instagram_service import InstagramService
    
    start_time = time.time()
    
    try:
        instagram_service = InstagramService()
        result = instagram_service.validate_connection()
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "success": result.get('success', False),
            "response_time_ms": round(response_time, 2),
            "message": result.get('message', 'Unknown'),
            "status": "connected" if result.get('success') else "failed"
        }
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            "success": False,
            "response_time_ms": round(response_time, 2),
            "error": str(e),
            "status": "error"
        }