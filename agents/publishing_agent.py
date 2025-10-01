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
from agents.agent_communication import AgentCommunication, AgentCoordinator

class PublishingAgent:
    """
    Publishing agent for scheduling and posting content
    """
    
    def __init__(self):
        print("Initializing Publishing Agent")
        self.name = "publishing"
        self.posts_file = os.path.abspath("scheduled_posts.json")
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
    
    def _parse_schedule_time(self, time_str: str) -> datetime:
        """Parse various time formats into datetime"""
        if not time_str:
            # Default to current time + 1 minute for immediate scheduling
            return datetime.now() + timedelta(minutes=1)
        
        if time_str.lower() == "now":
            # Schedule for current time + 1 minute
            return datetime.now() + timedelta(minutes=1)
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(time_str)
        except:
            pass
        
        # Parse natural language times
        time_str = time_str.lower().strip()
        now = datetime.now()
        
        # Handle specific times like "8pm", "3:30pm", "14:00"
        import re
        
        # Match patterns like "8pm", "8:30pm", "12.47pm", "20:00", "8:30 pm"
        time_patterns = [
            r'(\d{1,2})\.(\d{2})\s*pm',  # 12.47pm
            r'(\d{1,2})\.(\d{2})\s*am',  # 8.30am
            r'(\d{1,2}):(\d{2})\s*pm',  # 8:30pm
            r'(\d{1,2}):(\d{2})\s*am',  # 8:30am
            r'(\d{1,2})\s*pm',  # 8pm
            r'(\d{1,2})\s*am',  # 8am
            r'(\d{1,2}):(\d{2})',  # 14:30 (24h format)
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, time_str)
            if match:
                if 'pm' in time_str:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if len(match.groups()) > 1 else 0
                    if hour != 12:
                        hour += 12
                elif 'am' in time_str:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if len(match.groups()) > 1 else 0
                    if hour == 12:
                        hour = 0
                else:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if len(match.groups()) > 1 else 0
                
                target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If time has passed today, schedule for tomorrow
                if target_time <= now:
                    target_time += timedelta(days=1)
                
                return target_time
        
        # Handle day-specific scheduling
        if 'tomorrow' in time_str:
            base_date = now + timedelta(days=1)
        elif 'monday' in time_str:
            days_ahead = 0 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            base_date = now + timedelta(days=days_ahead)
        else:
            base_date = now
        
        # Default to 9 AM if no specific time
        return base_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    def _create_scheduled_post(self, content: str, image_url: Optional[str] = None, 
                              schedule_time: Optional[str] = None) -> Dict:
        """Create a scheduled post"""
        posts = self._load_posts()
        
        # Parse schedule time with enhanced parsing
        scheduled_datetime = self._parse_schedule_time(schedule_time or "now")
        
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
        Enhanced publishing with content agent integration
        """
        state['current_agent'] = self.name
        print(f"Publishing Agent processing: {state.get('user_request', '')}")
        
        user_request = state.get('user_request', '').lower()
        
        # Get content from previous agent using communication system
        agent_context = AgentCoordinator.prepare_agent_context(state, self.name)
        content_data = agent_context.get('content_data', {})
        
        # Also check state for generated content (fallback)
        generated_content = state.get('generated_content', {})
        
        if content_data:
            print(f"[PUBLISHING] Using content from Content Agent")
            content = content_data.get('generated_content', '')
            # Look for image in content agent response
            image_path = None
            for response in state.get('agent_responses', []):
                if response.get('agent') == 'content' and response.get('image_url'):
                    image_path = response['image_url']
                    break
        elif generated_content:
            content = generated_content.get('content', '')
            image_path = generated_content.get('image_path')
        else:
            content = ''
            image_path = None
        
        # If no content from communication system, try to get from state directly
        if not content and generated_content:
            content = generated_content.get('content', '')
        
        result_message = "Content processed"
        
        if content:
            
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
                    # Extract schedule time from user request
                    schedule_time = None
                    
                    # Look for time patterns in user request
                    import re
                    time_patterns = [
                        r'at (\d{1,2}\.\d{2}\s*(?:am|pm))',  # at 12.47pm
                        r'at (\d{1,2}:\d{2}\s*(?:am|pm))',  # at 8:30pm
                        r'at (\d{1,2}\s*(?:am|pm))',        # at 8pm
                        r'(\d{1,2}\.\d{2}\s*(?:am|pm))',   # 12.47pm
                        r'(\d{1,2}:\d{2}\s*(?:am|pm))',   # 8:30pm
                        r'(\d{1,2}\s*(?:am|pm))',          # 8pm
                        r'(\d{1,2}:\d{2})',               # 14:30
                        r'(tomorrow)',
                        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
                    ]
                    
                    for pattern in time_patterns:
                        match = re.search(pattern, user_request, re.IGNORECASE)
                        if match:
                            schedule_time = match.group(1)
                            break
                    
                    # Create scheduled post
                    print(f"Creating scheduled post with time: {schedule_time}")
                    print(f"Content being scheduled (first 100 chars): {content[:100]}...")
                    print(f"Full content length: {len(content)} characters")
                    post = self._create_scheduled_post(content, image_url, schedule_time)
                    
                    # Get scheduled time for display
                    scheduled_datetime = self._parse_schedule_time(schedule_time or "now")
                    print(f"Parsed scheduled time: {scheduled_datetime}")
                    print(f"Current time: {datetime.now()}")
                    
                    # NEVER publish immediately - always schedule
                    result_message = f"Content scheduled for {scheduled_datetime.strftime('%I:%M %p on %B %d, %Y')}. Will be posted automatically by scheduler."
        
        # Add communication metadata
        AgentCommunication.add_communication_metadata(state, self.name, bool(content_data))
        
        # Add response
        state['agent_responses'].append({
            'agent': self.name,
            'action': 'content_publishing',
            'result': result_message,
            'platforms': ['Instagram'],
            'used_content_agent': bool(content_data)
        })
        
        return state
