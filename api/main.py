"""
FastAPI Backend for AI Social Media Manager
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
import os
import sys
from datetime import datetime
from contextlib import asynccontextmanager

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_setup import SocialMediaManagerGraph
from dotenv import load_dotenv
from routes.instagram import router as instagram_router
from routes.scheduling import router as scheduling_router
from routes.scheduler import router as scheduler_router
from routes.dashboard import router as dashboard_router
from routes.performance import router as performance_router
from routes.insights import router as insights_router
from routes.content_strategy import router as content_strategy_router
from services.scheduler_service import scheduler_service

# Load environment variables from the api/.env file
load_dotenv('.env')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the scheduler service
    print("Starting scheduler service...")
    scheduler_task = asyncio.create_task(scheduler_service.start_scheduler())
    yield
    # Shutdown: Stop the scheduler service
    print("Stopping scheduler service...")
    scheduler_service.stop_scheduler()
    scheduler_task.cancel()

app = FastAPI(title="AI Social Media Manager API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(instagram_router)
app.include_router(scheduling_router)
app.include_router(scheduler_router, prefix="/api")
app.include_router(dashboard_router)
app.include_router(performance_router)
app.include_router(insights_router)
app.include_router(content_strategy_router, prefix="/api")

# Initialize the graph
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

graph = SocialMediaManagerGraph(groq_api_key)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    session_id: str
    workflow_type: str
    agent_queue: List[str]
    current_agent: Optional[str]
    agent_responses: List[Dict[str, Any]]
    generated_content: Optional[Dict[str, Any]]
    final_response: str
    status: str

@app.get("/")
async def root():
    return {"message": "AI Social Media Manager API is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for processing user requests"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"web-session-{datetime.now().timestamp()}"
        
        print(f"Processing chat request: {request.message}")
        print(f"Session ID: {session_id}")
        
        # Process the request through the graph
        try:
            result = graph.run(
                user_request=request.message,
                session_id=session_id,
                context_data=request.context_data or {}
            )
            print(f"Graph result: {result}")
            
            # Analytics agent now uses cached data, no continuous updates needed
                
        except Exception as graph_error:
            print(f"Graph execution error: {graph_error}")
            # Return a simple response instead of failing
            result = {
                'workflow_type': 'direct',
                'agent_queue': [],
                'current_agent': 'orchestrator',
                'agent_responses': [{'agent': 'orchestrator', 'action': 'error_handling', 'result': str(graph_error)}],
                'generated_content': None,
                'final_response': f'Request processed with error handling: {str(graph_error)}'
            }
        
        # Format response
        response = ChatResponse(
            session_id=session_id,
            workflow_type=result.get('workflow_type', 'direct'),
            agent_queue=result.get('agent_queue', []),
            current_agent=result.get('current_agent'),
            agent_responses=result.get('agent_responses', []),
            generated_content=result.get('generated_content'),
            final_response=result.get('final_response', 'Request processed successfully'),
            status="completed"
        )
        
        return response
        
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler service status"""
    posts = scheduler_service.load_posts()
    scheduled_posts = [p for p in posts if p.get('status') == 'scheduled']
    return {
        "running": scheduler_service.running,
        "timestamp": datetime.now().isoformat(),
        "scheduled_posts_count": len(scheduled_posts),
        "scheduled_posts": scheduled_posts[:3]  # Show first 3 for debugging
    }

@app.post("/scheduler/check-now")
async def check_scheduler_now():
    """Manually trigger scheduler check for testing"""
    try:
        scheduler_service.check_and_publish_due_posts()
        return {"success": True, "message": "Scheduler check completed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/analytics/status")
async def analytics_status():
    """Get analytics agent data status"""
    try:
        status = graph.analytics_agent.get_current_data_summary()
        return {"success": True, "data": status}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/analytics/refresh")
async def refresh_analytics_cache():
    """Refresh analytics cache with fresh data"""
    try:
        graph.analytics_agent.refresh_cache()
        return {"success": True, "message": "Analytics cache refreshed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)