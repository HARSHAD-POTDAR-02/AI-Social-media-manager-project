"""
Publishing Agent for AI Social Media Manager
Handles content scheduling and cross-platform publishing
"""

from typing import Dict, Any, Optional
import sys
import os
import json
import uuid
import requests
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.services.instagram_service import InstagramService

class PublishingAgent:
    """
    Publishing agent for scheduling and posting content
    """
    
    def __init__(self):
        print("Initializing Publishing Agent")
        self.name = "publishing"
        self.posts_file = "scheduled_posts.json"
        try:
            self.instagram_service = InstagramService()
        except Exception as e:
            print(f"Warning: Instagram service not available: {e}")
            self.instagram_service = None
        
    def _load_posts(self) -> list:
        """Load posts from JSON file"""
        try:
            with open(self.posts_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _save_posts(self, posts: list):
        """Save posts to JSON file"""
        with open(self.posts_file, 'w') as f:
            json.dump(posts, f, indent=2, default=str)
    
    def _create_scheduled_post(self, content: str, image_url: Optional[str] = None, 
                              schedule_time: Optional[str] = None) -> Dict:
        """Create a scheduled post"""
        posts = self._load_posts()
        
        # Parse schedule time
        if schedule_time and schedule_time.lower() == "now":
            scheduled_datetime = datetime.now()
        elif schedule_time:
            try:
                scheduled_datetime = datetime.fromisoformat(schedule_time)
            except:
                scheduled_datetime = datetime.now() + timedelta(hours=1)
        else:
            scheduled_datetime = datetime.now() + timedelta(hours=1)
        
        # Create post
        post = {
            "id": str(uuid.uuid4()),
            "content": content,
            "platform": "instagram",
            "media_type": "image" if image_url else "text",
            "media_urls": [image_url] if image_url else [],
            "scheduled_time": scheduled_datetime.isoformat(),
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "metadata": {"generated_by_ai": True}
        }
        
        posts.append(post)
        self._save_posts(posts)
        return post
    
    def _ensure_public_image_url(self, image_url: str) -> Optional[str]:
        """Ensure we have a publicly accessible image URL.
        - If the URL is already http(s), return as-is.
        - If it's a data URI (base64), try uploading to IMGBB if API key is set.
        Returns a usable http(s) URL or None.
        """
        try:
            if not image_url:
                return None
            if image_url.startswith("http://") or image_url.startswith("https://"):
                return image_url

            # Handle data URI base64 case
            if image_url.startswith("data:image/"):
                imgbb_key = os.getenv("IMGBB_API_KEY")
                if not imgbb_key:
                    print("No IMGBB_API_KEY set; cannot convert base64 image to public URL")
                    return None

                # Extract base64 payload
                try:
                    base64_data = image_url.split(",", 1)[1]
                except Exception:
                    print("Malformed data URI; unable to extract base64 payload")
                    return None

                upload_url = "https://api.imgbb.com/1/upload"
                params = {"key": imgbb_key}
                data = {"image": base64_data}
                resp = requests.post(upload_url, params=params, data=data, timeout=60)
                if resp.status_code == 200:
                    payload = resp.json()
                    if payload.get("success") and payload.get("data", {}).get("url"):
                        return payload["data"]["url"]
                    # Some responses place display_url
                    if payload.get("data", {}).get("display_url"):
                        return payload["data"]["display_url"]
                    print(f"IMGBB upload response missing URL: {payload}")
                    return None
                else:
                    print(f"IMGBB upload failed: {resp.status_code} - {resp.text}")
                    return None

            # Unknown scheme
            return None
        except Exception as e:
            print(f"Error ensuring public image URL: {e}")
            return None

    def _publish_to_instagram(self, post: Dict) -> Dict:
        """Publish post to Instagram"""
        if not self.instagram_service:
            return {"success": False, "error": "Instagram service not available"}
        
        try:
            media_urls = post.get("media_urls", [])
            
            if not media_urls:
                return {"success": False, "error": "No media provided"}
            # Ensure we have a publicly accessible URL
            public_url = self._ensure_public_image_url(media_urls[0])
            if not public_url:
                return {"success": False, "error": "No public image URL available for Instagram ingestion"}

            # Create media container
            url = f"https://graph.facebook.com/v19.0/{self.instagram_service.instagram_account_id}/media"
            params = {
                "access_token": self.instagram_service.access_token,
                "image_url": public_url,
                "caption": post["content"]
            }
            
            response = requests.post(url, params=params, timeout=30)
            
            if response.status_code == 200:
                container_data = response.json()
                container_id = container_data["id"]
                
                # Publish the container
                publish_url = f"https://graph.facebook.com/v19.0/{self.instagram_service.instagram_account_id}/media_publish"
                publish_params = {
                    "access_token": self.instagram_service.access_token,
                    "creation_id": container_id
                }
                
                publish_response = requests.post(publish_url, params=publish_params, timeout=30)
                
                if publish_response.status_code == 200:
                    publish_data = publish_response.json()
                    return {"success": True, "post_id": publish_data["id"]}
                else:
                    return {"success": False, "error": f"Publish failed: {publish_response.text}"}
            else:
                return {"success": False, "error": f"Container creation failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Publishing error: {str(e)}"}
    
    def _publish_now(self, post_id: str) -> Dict:
        """Publish a post immediately"""
        posts = self._load_posts()
        
        # Find post
        post = None
        for p in posts:
            if p["id"] == post_id:
                post = p
                break
        
        if not post:
            return {"success": False, "error": "Post not found"}
        
        # Update status
        post["status"] = "publishing"
        self._save_posts(posts)
        
        # Publish
        result = self._publish_to_instagram(post)
        
        # Update post with result
        if result["success"]:
            post["status"] = "published"
            post["published_at"] = datetime.now().isoformat()
            post["published_id"] = result.get("post_id")
        else:
            post["status"] = "failed"
            post["error_message"] = result.get("error")
        
        self._save_posts(posts)
        return result
    
    def _upload_local_image(self, image_path: str) -> Optional[str]:
        """Upload local image file to hosting service and return public URL"""
        try:
            print(f"Uploading image: {image_path}")
            
            # Use imgbb.com free hosting
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                # Free API key for testing (get your own at imgbb.com)
                response = requests.post(
                    'https://api.imgbb.com/1/upload?key=2d1f7b0c5c8b9a1e3f4d6c8a9b2e5f7d',
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        image_url = data['data']['url']
                        print(f"Image uploaded successfully: {image_url}")
                        return image_url
            
            # Fallback: use file.io
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                response = requests.post('https://file.io', files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        image_url = data['link']
                        print(f"Image uploaded to file.io: {image_url}")
                        return image_url
            
            print("All image upload services failed")
            return None
            
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced publishing with scheduling and Instagram posting
        """
        state['current_agent'] = self.name
        print(f"Publishing Agent processing: {state.get('user_request', '')}")
        
        user_request = state.get('user_request', '').lower()
        generated_content = state.get('generated_content', {})
        
        # Check if we need to schedule or publish
        schedule_now = any(phrase in user_request for phrase in [
            'post now', 'publish now', 'right now', 'post it now', 'post immediately', 'publish it now', 'post it on instagram', 'post on instagram'
        ])
        schedule_later = any(phrase in user_request for phrase in ['schedule', 'monday', 'tuesday', 'tomorrow'])
        
        result_message = "Content processed"
        
        # Always try to post if we have content and image
        if generated_content:
            schedule_now = True  # Force immediate posting for any content with image
        
        if generated_content and (schedule_now or schedule_later):
            content = generated_content.get('content', '')
            image_path = generated_content.get('image_path')
            
            # Check if we have an image (URL or file path)
            if not image_path:
                result_message = f"No image generated. Content only: {content[:50]}..."
            else:
                # Handle both URLs and local file paths
                if image_path.startswith('http'):
                    # Direct URL - use as is
                    image_url = image_path
                    print(f"Using direct image URL: {image_url}")
                elif os.path.exists(image_path):
                    # Local file - upload to hosting service
                    image_url = self._upload_local_image(image_path)
                    if not image_url:
                        result_message = f"Failed to upload image. Content: {content[:50]}..."
                        image_url = None
                else:
                    result_message = f"Image not found: {image_path}. Content: {content[:50]}..."
                    image_url = None
                
                if image_url:
                    # Determine schedule time
                    schedule_time = "now" if schedule_now else None
                    if 'monday' in user_request:
                        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
                        schedule_time = next_monday.replace(hour=9, minute=0).isoformat()
                    
                    # Create scheduled post
                    post = self._create_scheduled_post(content, image_url, schedule_time)
                    
                    # If scheduling for now, publish immediately
                    if schedule_now:
                        publish_result = self._publish_now(post['id'])
                        if publish_result['success']:
                            result_message = f"Content published to Instagram successfully! Post ID: {publish_result.get('post_id', 'N/A')}"
                        else:
                            result_message = f"Publishing failed: {publish_result.get('error', 'Unknown error')}"
                    else:
                        result_message = f"Content scheduled for {post['scheduled_time']}"
        
        # Add response
        state['agent_responses'].append({
            'agent': self.name,
            'action': 'content_publishing',
            'result': result_message,
            'platforms': ['Instagram']
        })
        
        return state
