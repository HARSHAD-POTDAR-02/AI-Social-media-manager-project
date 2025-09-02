"""
Analytics Agent for AI Social Media Manager
Handles performance analysis, reporting, and insights
"""

from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.services.instagram_service import InstagramService

class AnalyticsAgent:
    """
    Analytics agent for performance measurement and reporting
    """
    
    def __init__(self):
        print("Initializing Analytics Agent")
        self.name = "analytics"
        self.instagram_service = InstagramService()
        
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process analytics and reporting tasks
        """
        state['current_agent'] = self.name
        print(f"Analytics Agent processing: {state.get('user_request', '')}")
        print("ANALYTICS AGENT IS PROCESSING")
        
        state['performance_metrics'] = {
            'engagement_rate': 5.2,
            'reach': 10000,
            'impressions': 50000,
            'roi': 3.5
        }
        
        # Get real Instagram data for analytics
        try:
            from api.services.instagram_service import InstagramService
            instagram_service = InstagramService()
            
            account_data = instagram_service.get_account_info()
            media_data = instagram_service.get_media_list(limit=10)
            
            if account_data.get('success') and media_data.get('success'):
                posts = media_data.get('data', {}).get('data', [])
                total_likes = sum(post.get('like_count', 0) for post in posts)
                total_comments = sum(post.get('comments_count', 0) for post in posts)
                followers = account_data.get('data', {}).get('followers_count', 1)
                
                engagement_rate = ((total_likes + total_comments) / (len(posts) * followers)) * 100 if followers > 0 else 0
                
                state['performance_metrics'] = {
                    'engagement_rate': round(engagement_rate, 2),
                    'followers_count': followers,
                    'media_count': account_data.get('data', {}).get('media_count', 0),
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'avg_likes_per_post': round(total_likes / len(posts), 1) if posts else 0
                }
            else:
                state['performance_metrics'] = {
                    'engagement_rate': 0,
                    'followers_count': 0,
                    'media_count': 0,
                    'total_likes': 0,
                    'total_comments': 0
                }
        except Exception as e:
            print(f"Analytics agent Instagram error: {e}")
            state['performance_metrics'] = {'error': str(e)}
        
        # Only add response if not already added for this agent
        existing_responses = [r for r in state.get('agent_responses', []) if r.get('agent') == self.name]
        if not existing_responses:
            state['agent_responses'].append({
                'agent': self.name,
                'action': 'performance_analysis',
                'result': 'Real Instagram analytics generated',
                'metrics': state['performance_metrics']
            })
        
        return state
