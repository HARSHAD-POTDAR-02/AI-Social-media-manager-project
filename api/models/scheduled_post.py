from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"

class Platform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"

class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"

class ScheduledPost(BaseModel):
    id: Optional[str] = None
    content: str = Field(..., description="Post content/caption")
    platform: Platform = Field(..., description="Target social media platform")
    media_type: MediaType = Field(default=MediaType.IMAGE, description="Type of media content")
    media_urls: List[str] = Field(default=[], description="URLs of media files")
    scheduled_time: datetime = Field(..., description="When to publish the post")
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Current status of the post")
    created_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    published_id: Optional[str] = Field(None, description="Platform-specific post ID after publishing")
    error_message: Optional[str] = Field(None, description="Error message if publishing failed")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")

class CreateScheduledPost(BaseModel):
    content: str
    platform: Platform
    media_type: MediaType = MediaType.IMAGE
    media_urls: List[str] = []
    scheduled_time: datetime
    metadata: Dict[str, Any] = {}

class ContentRequest(BaseModel):
    content_request: str
    platform: str = "instagram"
    schedule_time: Optional[str] = None