"""
Content Strategy API Routes
Provides trending-based content strategy for dashboard
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.trends_service import TrendsService

router = APIRouter()
trends_service = TrendsService()

@router.get("/content-strategy")
async def get_content_strategy() -> Dict[str, Any]:
    """Get comprehensive content strategy based on current trends"""
    try:
        strategy_data = trends_service.get_comprehensive_strategy()
        
        return {
            "success": True,
            "data": strategy_data
        }
        
    except Exception as e:
        print(f"Error getting content strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get content strategy: {str(e)}")

@router.get("/trending-topics")
async def get_trending_topics() -> Dict[str, Any]:
    """Get current trending topics"""
    try:
        trends = trends_service.get_trending_topics()
        
        return {
            "success": True,
            "data": {
                "trends": trends,
                "count": len(trends),
                "last_updated": trends[0]['timestamp'] if trends else None
            }
        }
        
    except Exception as e:
        print(f"Error getting trending topics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")

@router.post("/generate-strategy")
async def generate_custom_strategy(request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate custom content strategy based on user preferences"""
    try:
        niche = request.get('niche', 'general')
        keywords = request.get('keywords', [])
        
        # Get trends
        trends = trends_service.get_trending_topics()
        
        # Generate strategy
        strategy = trends_service.generate_content_strategy(trends, niche)
        
        # Get interest data for custom keywords if provided
        interest_data = {}
        if keywords:
            interest_data = trends_service.get_topic_interest_over_time(keywords)
        
        return {
            "success": True,
            "data": {
                "strategy": strategy,
                "interest_data": interest_data,
                "trends_analyzed": len(trends)
            }
        }
        
    except Exception as e:
        print(f"Error generating custom strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate strategy: {str(e)}")

@router.get("/topic-analysis/{keyword}")
async def analyze_topic(keyword: str) -> Dict[str, Any]:
    """Analyze a specific topic/keyword"""
    try:
        # Get interest over time
        interest_data = trends_service.get_topic_interest_over_time([keyword])
        
        # Get related queries
        related_data = trends_service.get_related_queries(keyword)
        
        return {
            "success": True,
            "data": {
                "keyword": keyword,
                "interest_analysis": interest_data.get(keyword, {}),
                "related_queries": related_data,
                "analyzed_at": trends_service.pytrends is not None
            }
        }
        
    except Exception as e:
        print(f"Error analyzing topic {keyword}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze topic: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for content strategy service"""
    return {
        "success": True,
        "data": {
            "service": "content_strategy",
            "pytrends_available": trends_service.pytrends is not None,
            "groq_available": trends_service.groq_client is not None,
            "status": "healthy"
        }
    }