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

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_setup import SocialMediaManagerGraph
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Social Media Manager API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # Process the request through the graph
        result = graph.run(
            user_request=request.message,
            session_id=session_id,
            context_data=request.context_data or {}
        )
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)