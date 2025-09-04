"""
Background Scheduler Service
Handles automatic posting of scheduled content
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from agents.publishing_agent import PublishingAgent
except ImportError:
    # Fallback import path
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from agents.publishing_agent import PublishingAgent

class SchedulerService:
    def __init__(self):
        self.posts_file = "scheduled_posts.json"
        self.publishing_agent = PublishingAgent()
        self.running = False
        
    def load_posts(self) -> List[Dict]:
        """Load scheduled posts from JSON file"""
        try:
            with open(self.posts_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_posts(self, posts: List[Dict]):
        """Save scheduled posts to JSON file"""
        with open(self.posts_file, 'w') as f:
            json.dump(posts, f, indent=2, default=str)
    
    def check_and_publish_due_posts(self):
        """Check for posts that are due and publish them"""
        try:
            posts = self.load_posts()
            current_time = datetime.now()
            updated_posts = []
            published_count = 0
            
            for post in posts:
                if post.get('status') != 'scheduled':
                    updated_posts.append(post)
                    continue
                
                scheduled_time = datetime.fromisoformat(post['scheduled_time'])
                
                # Check if post is due (within 30 seconds tolerance)
                if scheduled_time <= current_time + timedelta(seconds=30):
                    print(f"Publishing due post: {post['id']} scheduled for {scheduled_time}")
                    
                    # Update status to publishing
                    post['status'] = 'publishing'
                    
                    # Attempt to publish
                    try:
                        publish_result = self.publishing_agent._publish_to_instagram(post)
                        
                        if publish_result['success']:
                            post['status'] = 'published'
                            post['published_at'] = current_time.isoformat()
                            post['published_id'] = publish_result.get('post_id')
                            published_count += 1
                            print(f"Successfully published post {post['id']}")
                            
                            # Don't add published posts back to the list (remove from calendar)
                            continue
                        else:
                            post['status'] = 'failed'
                            post['error_message'] = publish_result.get('error')
                            print(f"Failed to publish post {post['id']}: {publish_result.get('error')}")
                            
                    except Exception as e:
                        post['status'] = 'failed'
                        post['error_message'] = str(e)
                        print(f"Exception publishing post {post['id']}: {e}")
                
                # Keep non-published posts in the list
                updated_posts.append(post)
            
            # Save updated posts (published posts are removed)
            if len(updated_posts) != len(posts):
                self.save_posts(updated_posts)
                print(f"Published {published_count} posts, removed from calendar")
                
        except Exception as e:
            print(f"Error in scheduler service: {e}")
    
    async def start_scheduler(self):
        """Start the background scheduler"""
        self.running = True
        print("Scheduler service started - checking every 30 seconds")
        
        while self.running:
            try:
                self.check_and_publish_due_posts()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(30)
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        print("Scheduler service stopped")

# Global scheduler instance
scheduler_service = SchedulerService()