from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional
import sys
import os
import json
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.scheduled_post import CreateScheduledPost, ContentRequest
from agents.content_agent import ContentAgent
from agents.publishing_agent import PublishingAgent

router = APIRouter(prefix="/scheduling", tags=["scheduling"])

@router.post("/create-and-schedule")
async def create_and_schedule_content(request: ContentRequest):
    """Generate content with AI and schedule/publish it"""
    try:
        # Initialize agents
        content_agent = ContentAgent()
        publishing_agent = PublishingAgent()
        
        # Create state for content generation
        state = {
            "user_request": request.content_request,
            "context_data": {"platform": request.platform},
            "agent_responses": []
        }
        
        # Generate content (with image if needed)
        print(f"Generating content for: {request.content_request}")
        content_state = content_agent.process(state)
        
        # Add scheduling context to state
        content_state["user_request"] += f" and {request.schedule_time or 'schedule for later'}"
        
        # Process with publishing agent
        print(f"Processing with publishing agent")
        final_state = publishing_agent.process(content_state)
        
        generated_content = final_state.get("generated_content", {})
        agent_responses = final_state.get("agent_responses", [])
        
        return {
            "success": True,
            "message": "Content generated and processed",
            "content": generated_content,
            "agent_responses": agent_responses,
            "schedule_time": request.schedule_time
        }
        
    except Exception as e:
        print(f"Error in create_and_schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts")
async def get_scheduled_posts(status: Optional[str] = None):
    """Get all scheduled posts"""
    try:
        posts_file = "scheduled_posts.json"
        try:
            with open(posts_file, 'r') as f:
                posts = json.load(f)
        except FileNotFoundError:
            posts = []
        
        if status:
            posts = [p for p in posts if p.get("status") == status]
        
        return {"success": True, "data": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publish/{post_id}")
async def publish_post_now(post_id: str):
    """Publish a scheduled post immediately"""
    try:
        publishing_agent = PublishingAgent()
        result = publishing_agent._publish_now(post_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to publish"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/{year}/{month}")
async def get_calendar_data(year: int, month: int):
    """Get calendar data for a specific month"""
    try:
        posts_file = "scheduled_posts.json"
        try:
            with open(posts_file, 'r') as f:
                posts = json.load(f)
        except FileNotFoundError:
            posts = []
        
        # Filter posts for the specified month
        calendar_posts = []
        for post in posts:
            try:
                scheduled_time = datetime.fromisoformat(post["scheduled_time"].replace('Z', '+00:00'))
                if scheduled_time.year == year and scheduled_time.month == month:
                    calendar_posts.append({
                        "id": post["id"],
                        "content": post["content"][:50] + "..." if len(post["content"]) > 50 else post["content"],
                        "platform": post["platform"],
                        "scheduled_time": post["scheduled_time"],
                        "status": post["status"],
                        "media_type": post["media_type"],
                        "has_media": len(post.get("media_urls", [])) > 0
                    })
            except Exception as e:
                print(f"Error processing post {post.get('id', 'unknown')}: {e}")
                continue
        
        return {
            "success": True,
            "data": {
                "year": year,
                "month": month,
                "posts": calendar_posts
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))