"""
Scheduler API routes for managing scheduled posts
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import os
import uuid

router = APIRouter()

class ScheduledPost(BaseModel):
    content: str
    platform: str
    scheduled_time: str
    image_url: Optional[str] = None
    
class UpdateScheduledPost(BaseModel):
    id: str
    content: str
    platform: str
    scheduled_time: str
    image_url: Optional[str] = None

POSTS_FILE = os.path.abspath("scheduled_posts.json")

def load_posts() -> List[Dict]:
    """Load scheduled posts from JSON file"""
    try:
        with open(POSTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_posts(posts: List[Dict]):
    """Save scheduled posts to JSON file"""
    with open(POSTS_FILE, 'w') as f:
        json.dump(posts, f, indent=2, default=str)

@router.get("/scheduled-posts")
async def get_scheduled_posts():
    """Get all scheduled posts"""
    try:
        posts = load_posts()
        return {"success": True, "data": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule-post")
async def schedule_post(post: ScheduledPost):
    """Schedule a new post"""
    try:
        posts = load_posts()
        
        new_post = {
            "id": str(uuid.uuid4()),
            "content": post.content,
            "platform": post.platform,
            "media_type": "image" if post.image_url else "text",
            "media_urls": [post.image_url] if post.image_url else [],
            "scheduled_time": post.scheduled_time,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "metadata": {"created_manually": True}
        }
        
        posts.append(new_post)
        save_posts(posts)
        
        return {"success": True, "data": new_post}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/scheduled-posts/{post_id}")
async def update_scheduled_post(post_id: str, post: UpdateScheduledPost):
    """Update a scheduled post"""
    try:
        posts = load_posts()
        
        for i, existing_post in enumerate(posts):
            if existing_post["id"] == post_id:
                posts[i].update({
                    "content": post.content,
                    "platform": post.platform,
                    "scheduled_time": post.scheduled_time,
                    "media_urls": [post.image_url] if post.image_url else [],
                    "media_type": "image" if post.image_url else "text",
                    "updated_at": datetime.now().isoformat()
                })
                save_posts(posts)
                return {"success": True, "data": posts[i]}
        
        raise HTTPException(status_code=404, detail="Post not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/scheduled-posts/{post_id}")
async def delete_scheduled_post(post_id: str):
    """Delete a scheduled post"""
    try:
        posts = load_posts()
        
        posts = [post for post in posts if post["id"] != post_id]
        save_posts(posts)
        
        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reschedule-post")
async def reschedule_post(post_id: str, new_time: str):
    """Reschedule a post to a new time"""
    try:
        posts = load_posts()
        
        for post in posts:
            if post["id"] == post_id:
                post["scheduled_time"] = new_time
                post["updated_at"] = datetime.now().isoformat()
                save_posts(posts)
                return {"success": True, "data": post}
        
        raise HTTPException(status_code=404, detail="Post not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))