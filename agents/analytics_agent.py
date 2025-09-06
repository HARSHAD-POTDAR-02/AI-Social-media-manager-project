"""
Enhanced Analytics Agent with LLM Integration
Conversational AI that continuously feeds real-time data for natural responses
"""

from typing import Dict, Any, List, Optional
import sys
import os
import json
import asyncio
from datetime import datetime, timedelta
import threading
import time
from groq import Groq

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.services.instagram_service import InstagramService

class AnalyticsAgent:
    """
    Enhanced Analytics Agent with continuous data feeding and LLM integration
    """
    
    def __init__(self, groq_api_key: str = None):
        print("🔍 Initializing Enhanced Analytics Agent with LLM")
        self.name = "analytics"
        self.description = "AI Analytics Specialist with Cached Data"
        
        # Initialize services
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY required for analytics agent")
        
        self.groq_client = Groq(api_key=self.groq_api_key)
        
        try:
            self.instagram_service = InstagramService()
            print("✅ Instagram Analytics Service Connected")
        except Exception as e:
            print(f"⚠️ Instagram Service Error: {e}")
            self.instagram_service = None
        
        # Use cached data instead of continuous updates
        self.cached_data = {}
        self.data_loaded = False
        
        # System prompt for the LLM
        self.system_prompt = """You are an expert Instagram analytics specialist with access to real-time data. 

Your personality:
- Conversational and friendly, like talking to a knowledgeable friend
- Use natural language, not robotic responses
- Ask follow-up questions to understand what they really want to know
- Give actionable insights, not just numbers
- Be curious about their goals and challenges

You have access to comprehensive Instagram data including:
- Account metrics (followers, engagement rates, growth trends)
- Post performance (likes, comments, reach, impressions)
- Audience insights (demographics, activity times, behavior)
- Content analysis (best performing types, hashtag performance)
- Competitive benchmarks and industry standards

When responding:
1. Answer their specific question naturally
2. Provide context and insights, not just raw numbers
3. Ask clarifying questions if needed
4. Suggest next steps or related analyses
5. Be conversational - use "you", "your", contractions, etc.

Current data context will be provided with each conversation."""

    def get_cached_data(self):
        """Get data from cache - only fetch once per session"""
        if self.data_loaded and self.cached_data:
            print("📋 Using cached analytics data")
            return self.cached_data
            
        try:
            print("🔄 Loading analytics data for first time...")
            # Fetch data once when needed, not continuously
            account_data = self.instagram_service.get_account_info()
            media_data = self.instagram_service.get_media_list(limit=30)
            top_posts = self.instagram_service.get_top_posts(10)
            
            self.cached_data = {
                'timestamp': datetime.now().isoformat(),
                'account': account_data.get('data', {}) if account_data.get('success') else {},
                'recent_posts': media_data.get('data', {}).get('data', []) if media_data.get('success') else [],
                'top_posts': top_posts.get('data', []) if top_posts.get('success') else [],
                'analytics': self._calculate_analytics_summary(
                    account_data.get('data', {}) if account_data.get('success') else {},
                    media_data.get('data', {}).get('data', []) if media_data.get('success') else []
                )
            }
            self.data_loaded = True
            print("✅ Analytics data cached successfully")
            return self.cached_data
        except Exception as e:
            print(f"❌ Failed to get cached data: {e}")
            return {}



    def _calculate_analytics_summary(self, account_info: Dict, posts: List[Dict]) -> Dict:
        """Calculate comprehensive analytics summary"""
        if not posts:
            return {}
            
        followers = account_info.get('followers_count', 1)
        total_likes = sum(post.get('like_count', 0) for post in posts)
        total_comments = sum(post.get('comments_count', 0) for post in posts)
        
        engagement_rate = ((total_likes + total_comments) / (len(posts) * followers)) * 100 if followers > 0 else 0
        
        # Content type analysis
        content_types = {}
        for post in posts:
            media_type = post.get('media_type', 'UNKNOWN')
            engagement = post.get('like_count', 0) + post.get('comments_count', 0)
            
            if media_type not in content_types:
                content_types[media_type] = {'total': 0, 'count': 0}
            content_types[media_type]['total'] += engagement
            content_types[media_type]['count'] += 1
        
        # Calculate averages
        for media_type in content_types:
            count = content_types[media_type]['count']
            content_types[media_type]['avg'] = content_types[media_type]['total'] / count if count > 0 else 0
        
        # Time analysis
        hourly_engagement = {}
        for post in posts:
            try:
                post_time = datetime.fromisoformat(post.get('timestamp', '').replace('Z', '+00:00'))
                hour = post_time.hour
                engagement = post.get('like_count', 0) + post.get('comments_count', 0)
                
                if hour not in hourly_engagement:
                    hourly_engagement[hour] = []
                hourly_engagement[hour].append(engagement)
            except:
                continue
        
        # Calculate best posting times
        best_hours = {}
        for hour, engagements in hourly_engagement.items():
            best_hours[hour] = sum(engagements) / len(engagements)
        
        return {
            'engagement_rate': round(engagement_rate, 2),
            'avg_likes_per_post': round(total_likes / len(posts), 1),
            'avg_comments_per_post': round(total_comments / len(posts), 1),
            'total_engagement': total_likes + total_comments,
            'posts_analyzed': len(posts),
            'content_type_performance': content_types,
            'best_posting_hours': dict(sorted(best_hours.items(), key=lambda x: x[1], reverse=True)[:5]),
            'followers_count': followers,
            'media_count': account_info.get('media_count', 0)
        }

    def can_handle(self, user_request: str) -> bool:
        """Check if request is analytics-related"""
        analytics_keywords = [
            'analytics', 'performance', 'metrics', 'insights', 'engagement', 'reach',
            'impressions', 'followers', 'growth', 'data', 'statistics', 'trends',
            'analysis', 'report', 'dashboard', 'numbers', 'stats'
        ]
        
        request_lower = user_request.lower()
        return any(keyword in request_lower for keyword in analytics_keywords)

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process analytics requests using LLM with cached data"""
        state['current_agent'] = self.name
        user_request = state.get('user_request', '')
        
        print(f"🔍 Analytics Agent Processing: {user_request}")
        
        # Get cached data (same as analytics.js)
        data_context = json.dumps(self.get_cached_data(), indent=2, default=str)
        
        # Create conversation with LLM
        try:
            response = self._get_llm_response(user_request, data_context)
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            response = f"I'm having trouble accessing the AI right now, but I can see your Instagram data. Let me give you a quick overview: You have {self.cached_data.get('analytics', {}).get('followers_count', 0):,} followers with a {self.cached_data.get('analytics', {}).get('engagement_rate', 0):.1f}% engagement rate. What specific metrics would you like to know about?"
        
        # Update state
        state['generated_content'] = {
            'content': response,
            'type': 'analytics_conversation',
            'status': 'completed'
        }
        
        self._add_agent_response(state, 'analytics_conversation', response)
        state['final_response'] = response
        
        return state

    def _get_llm_response(self, user_request: str, data_context: str) -> str:
        """Get natural response from LLM with current data context"""
        
        messages = [
            {
                "role": "system",
                "content": f"{self.system_prompt}\n\nCurrent Instagram Data:\n{data_context}"
            },
            {
                "role": "user", 
                "content": user_request
            }
        ]
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Groq API Error: {e}")
            raise e

    def _add_agent_response(self, state: Dict[str, Any], action: str, result: str):
        """Add agent response to state"""
        if 'agent_responses' not in state:
            state['agent_responses'] = []
        
        # Check if response already exists to prevent duplicates
        existing = [r for r in state['agent_responses'] if r.get('agent') == self.name and r.get('action') == action]
        if not existing:
            state['agent_responses'].append({
                'agent': self.name,
                'action': action,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })

    def get_current_data_summary(self) -> Dict[str, Any]:
        """Get current data summary for external use"""
        return {
            'data_loaded': self.data_loaded,
            'data_available': bool(self.cached_data),
            'analytics_summary': self.cached_data.get('analytics', {})
        }
    
    def refresh_cache(self):
        """Force refresh of cached data"""
        self.data_loaded = False
        self.cached_data = {}
        return self.get_cached_data()