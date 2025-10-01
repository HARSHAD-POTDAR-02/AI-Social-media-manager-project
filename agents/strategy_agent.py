"""
Enhanced Strategy Agent with AI-Powered Strategic Planning
Handles content strategy, trend analysis, competitor research, and strategic insights
"""

from typing import Dict, Any, List, Optional
import sys
import os
import json
import requests
from datetime import datetime, timedelta
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.services.instagram_service import InstagramService
from agents.agent_communication import AgentCommunication, AgentCoordinator

class StrategyAgent:
    """
    AI-Powered Strategy Agent for comprehensive social media planning
    """
    
    def __init__(self, groq_api_key: str = None):
        print("[INIT] Initializing Enhanced Strategy Agent with AI")
        self.name = "strategy"
        self.description = "AI Strategy Specialist & Content Planner"
        
        # Initialize LLM client
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            print("[WARN] GROQ_API_KEY not found - strategy insights will be limited")
            self.groq_client = None
        else:
            self.groq_client = Groq(api_key=self.groq_api_key)
        
        # Initialize Instagram service for data-driven strategies
        try:
            self.instagram_service = InstagramService()
            print("[OK] Instagram Analytics Connected for Strategy")
        except Exception as e:
            print(f"[WARN] Instagram Service Error: {e}")
            self.instagram_service = None
        
        # Cache for strategy data
        self.cached_data = {}
        self.data_loaded = False
        
        # Strategy-focused system prompt
        self.system_prompt = """You are an expert social media strategist and content planning specialist with deep knowledge of Instagram marketing.

Your expertise includes:
- Content strategy development and planning
- Trend analysis and viral content identification
- Audience behavior and engagement optimization
- Competitor analysis and market positioning
- Brand voice development and consistency
- Campaign planning and content series design
- Hashtag strategy and discoverability
- Posting schedule optimization
- Performance forecasting and ROI analysis
- Crisis prevention and brand protection

Your personality:
- Strategic thinker who sees the big picture
- Data-driven but creative in approach
- Conversational and collaborative
- Proactive in identifying opportunities
- Focused on actionable recommendations
- Ask clarifying questions to understand goals

When providing strategy advice:
1. Base recommendations on actual performance data when available
2. Consider current trends and market dynamics
3. Provide specific, actionable steps
4. Explain the reasoning behind recommendations
5. Ask follow-up questions to refine strategy
6. Think long-term while addressing immediate needs

Current Instagram data and performance metrics will be provided for context."""

    def get_strategy_data(self):
        """Get comprehensive data for strategy planning"""
        if self.data_loaded and self.cached_data:
            print("[CACHE] Using cached strategy data")
            return self.cached_data
            
        try:
            print("[LOAD] Loading strategy data...")
            
            # Get Instagram data for strategy insights
            account_data = self.instagram_service.get_account_info() if self.instagram_service else None
            media_data = self.instagram_service.get_media_list(limit=50) if self.instagram_service else None
            top_posts = self.instagram_service.get_top_posts(20) if self.instagram_service else None
            
            # Process data for strategy insights
            account_info = account_data.get('data', {}) if account_data and account_data.get('success') else {}
            posts = media_data.get('data', {}).get('data', []) if media_data and media_data.get('success') else []
            top_performing = top_posts.get('data', []) if top_posts and top_posts.get('success') else []
            
            self.cached_data = {
                'timestamp': datetime.now().isoformat(),
                'account': account_info,
                'recent_posts': posts,
                'top_posts': top_performing,
                'strategy_insights': self._analyze_strategy_data(account_info, posts, top_performing),
                'trends': self._identify_trends(posts),
                'content_gaps': self._identify_content_gaps(posts),
                'optimization_opportunities': self._find_optimization_opportunities(account_info, posts)
            }
            
            self.data_loaded = True
            print("[OK] Strategy data loaded successfully")
            return self.cached_data
            
        except Exception as e:
            print(f"[ERROR] Failed to load strategy data: {e}")
            return {}

    def _analyze_strategy_data(self, account_info: Dict, posts: List[Dict], top_posts: List[Dict]) -> Dict:
        """Analyze data for strategic insights"""
        if not posts:
            return {}
            
        # Performance analysis
        total_engagement = sum(post.get('like_count', 0) + post.get('comments_count', 0) for post in posts)
        avg_engagement = total_engagement / len(posts) if posts else 0
        followers = account_info.get('followers_count', 1)
        engagement_rate = (avg_engagement / followers) * 100 if followers > 0 else 0
        
        # Content type performance
        content_performance = {}
        posting_times = {}
        hashtag_performance = {}
        
        for post in posts:
            # Content type analysis
            media_type = post.get('media_type', 'UNKNOWN')
            engagement = post.get('like_count', 0) + post.get('comments_count', 0)
            
            if media_type not in content_performance:
                content_performance[media_type] = {'total_engagement': 0, 'count': 0, 'posts': []}
            
            content_performance[media_type]['total_engagement'] += engagement
            content_performance[media_type]['count'] += 1
            content_performance[media_type]['posts'].append({
                'id': post.get('id'),
                'engagement': engagement,
                'timestamp': post.get('timestamp')
            })
            
            # Posting time analysis
            try:
                post_time = datetime.fromisoformat(post.get('timestamp', '').replace('Z', '+00:00'))
                hour = post_time.hour
                day = post_time.strftime('%A')
                
                if hour not in posting_times:
                    posting_times[hour] = {'total_engagement': 0, 'count': 0}
                posting_times[hour]['total_engagement'] += engagement
                posting_times[hour]['count'] += 1
            except:
                continue
        
        # Calculate averages and insights
        for content_type in content_performance:
            count = content_performance[content_type]['count']
            content_performance[content_type]['avg_engagement'] = content_performance[content_type]['total_engagement'] / count if count > 0 else 0
        
        for hour in posting_times:
            count = posting_times[hour]['count']
            posting_times[hour]['avg_engagement'] = posting_times[hour]['total_engagement'] / count if count > 0 else 0
        
        # Best performing content insights
        best_content_type = max(content_performance.items(), key=lambda x: x[1]['avg_engagement']) if content_performance else None
        best_posting_hours = sorted(posting_times.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)[:3]
        
        return {
            'overall_engagement_rate': round(engagement_rate, 2),
            'avg_engagement_per_post': round(avg_engagement, 1),
            'total_posts_analyzed': len(posts),
            'content_type_performance': content_performance,
            'best_content_type': best_content_type[0] if best_content_type else None,
            'best_posting_hours': [hour for hour, data in best_posting_hours],
            'posting_frequency': len(posts) / 30 if posts else 0,  # Posts per day over last 30 days
            'top_performing_posts': sorted(posts, key=lambda x: x.get('like_count', 0) + x.get('comments_count', 0), reverse=True)[:5]
        }

    def _identify_trends(self, posts: List[Dict]) -> Dict:
        """Identify content trends and patterns"""
        if not posts:
            return {}
        
        # Analyze recent vs older posts performance
        recent_posts = [p for p in posts if self._is_recent_post(p.get('timestamp', ''))]
        older_posts = [p for p in posts if not self._is_recent_post(p.get('timestamp', ''))]
        
        recent_avg = sum(p.get('like_count', 0) + p.get('comments_count', 0) for p in recent_posts) / len(recent_posts) if recent_posts else 0
        older_avg = sum(p.get('like_count', 0) + p.get('comments_count', 0) for p in older_posts) / len(older_posts) if older_posts else 0
        
        trend_direction = 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable'
        
        return {
            'performance_trend': trend_direction,
            'recent_avg_engagement': round(recent_avg, 1),
            'older_avg_engagement': round(older_avg, 1),
            'trend_percentage': round(((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0, 1)
        }

    def _identify_content_gaps(self, posts: List[Dict]) -> List[str]:
        """Identify content gaps and opportunities"""
        gaps = []
        
        if not posts:
            return ['No recent content to analyze']
        
        # Check content type diversity
        content_types = set(post.get('media_type') for post in posts)
        if 'VIDEO' not in content_types:
            gaps.append('Missing video content - consider adding Reels or video posts')
        if 'CAROUSEL_ALBUM' not in content_types:
            gaps.append('Missing carousel posts - great for engagement and storytelling')
        
        # Check posting frequency
        posting_frequency = len(posts) / 30
        if posting_frequency < 0.5:
            gaps.append('Low posting frequency - consider posting more regularly')
        elif posting_frequency > 2:
            gaps.append('High posting frequency - ensure quality over quantity')
        
        return gaps

    def _find_optimization_opportunities(self, account_info: Dict, posts: List[Dict]) -> List[str]:
        """Find optimization opportunities"""
        opportunities = []
        
        if not posts:
            return ['Start creating content to identify optimization opportunities']
        
        # Engagement rate analysis
        followers = account_info.get('followers_count', 1)
        avg_engagement = sum(post.get('like_count', 0) + post.get('comments_count', 0) for post in posts) / len(posts)
        engagement_rate = (avg_engagement / followers) * 100 if followers > 0 else 0
        
        if engagement_rate < 1:
            opportunities.append('Low engagement rate - focus on audience-relevant content')
        if engagement_rate < 3:
            opportunities.append('Improve call-to-actions and audience interaction')
        
        # Content consistency
        recent_posts = [p for p in posts if self._is_recent_post(p.get('timestamp', ''), days=7)]
        if len(recent_posts) < 3:
            opportunities.append('Increase posting consistency for better algorithm performance')
        
        return opportunities

    def _is_recent_post(self, timestamp: str, days: int = 14) -> bool:
        """Check if post is recent"""
        try:
            post_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return (datetime.now().replace(tzinfo=post_time.tzinfo) - post_time).days <= days
        except:
            return False

    def can_handle(self, user_request: str) -> bool:
        """Check if request is strategy-related"""
        strategy_keywords = [
            'strategy', 'plan', 'planning', 'calendar', 'schedule', 'content strategy',
            'trends', 'trending', 'viral', 'competitor', 'competition', 'analysis',
            'audience', 'target', 'brand', 'voice', 'campaign', 'hashtag', 'hashtags',
            'optimization', 'optimize', 'improve', 'growth', 'grow', 'increase',
            'engagement', 'reach', 'visibility', 'algorithm', 'best time', 'when to post',
            'content ideas', 'content types', 'what to post', 'posting frequency'
        ]
        
        request_lower = user_request.lower()
        return any(keyword in request_lower for keyword in strategy_keywords)

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process strategy requests with AI-powered insights"""
        state['current_agent'] = self.name
        user_request = state.get('user_request', '')
        
        print(f"[STRATEGY] Processing: {user_request}")
        
        # Use new communication system to get previous agent data
        agent_context = AgentCoordinator.prepare_agent_context(state, self.name)
        analytics_data = agent_context.get('analytics_insights', {})
        
        if analytics_data:
            print(f"[STRATEGY] Using analytics insights: engagement_rate={analytics_data.get('engagement_rate', 'N/A')}")
        
        # Get strategy data and combine with previous agent insights
        full_data = self.get_strategy_data()
        strategy_context = self._create_enhanced_context(full_data, analytics_data, user_request)
        
        # Generate AI-powered strategy response - NO FALLBACKS, LLM ONLY
        try:
            response = self._get_strategy_response(user_request, strategy_context)
        except Exception as e:
            print(f"[ERROR] LLM Error: {e}")
            response = f"Unable to generate strategy due to LLM error: {str(e)}. Please try again."
        
        # Add communication metadata
        AgentCommunication.add_communication_metadata(state, self.name, bool(analytics_data))
        
        # Update state with strategy results
        state['generated_content'] = {
            'content': response,
            'type': 'strategy_consultation',
            'status': 'completed',
            'based_on_analytics': bool(analytics_data),
            'used_previous_agents': list(agent_context.get('previous_agents', {}).keys())
        }
        
        self._add_agent_response(state, 'strategy_planning', response)
        state['final_response'] = response
        
        return state

    def _get_strategy_response(self, user_request: str, strategy_context: str) -> str:
        """Generate AI-powered strategy response - LLM ONLY"""
        if not self.groq_client:
            raise Exception("GROQ client not available - cannot generate strategy without LLM")
        
        # Enhanced system prompt that considers previous analytics
        focused_prompt = """You are an expert social media strategist. Analyze the provided data and create actionable strategic recommendations.
        
If analytics data from previous agents is available, reference specific findings and build strategic recommendations on top of them.

Provide:
- Data-driven strategic insights
- Specific actionable recommendations
- Content strategy based on performance data
- Growth tactics and next steps
- Follow-up questions to refine strategy
        
Be conversational, specific, and reference the actual data provided."""
        
        messages = [
            {
                "role": "system",
                "content": f"{focused_prompt}\n\nAvailable Data:\n{strategy_context}"
            },
            {
                "role": "user",
                "content": user_request
            }
        ]
        
        completion = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return completion.choices[0].message.content.strip()
    
    def _extract_analytics_insights(self, agent_responses: List[Dict]) -> Dict[str, Any]:
        """Extract insights from previous analytics agent responses"""
        analytics_insights = {}
        
        for response in agent_responses:
            if response.get('agent') == 'analytics':
                result = response.get('result', '')
                
                # Extract key metrics from analytics response
                if 'engagement rate' in result.lower():
                    # Parse engagement rate, followers, etc. from analytics text
                    import re
                    
                    # Extract engagement rate
                    eng_match = re.search(r'engagement rate.*?(\d+\.?\d*)%?', result.lower())
                    if eng_match:
                        analytics_insights['analytics_engagement_rate'] = float(eng_match.group(1))
                    
                    # Extract average likes
                    likes_match = re.search(r'average likes.*?(\d+\.?\d*)', result.lower())
                    if likes_match:
                        analytics_insights['analytics_avg_likes'] = float(likes_match.group(1))
                    
                    # Extract average comments
                    comments_match = re.search(r'average comments.*?(\d+\.?\d*)', result.lower())
                    if comments_match:
                        analytics_insights['analytics_avg_comments'] = float(comments_match.group(1))
                    
                    # Extract content insights
                    if 'sports' in result.lower():
                        analytics_insights['top_content_theme'] = 'sports'
                    
                    analytics_insights['analytics_summary'] = result[:300] + '...' if len(result) > 300 else result
                    
        return analytics_insights
    
    def _create_enhanced_context(self, strategy_data: Dict, analytics_data: Dict, user_request: str) -> str:
        """Create enhanced context combining strategy data with analytics insights"""
        try:
            insights = strategy_data.get('strategy_insights', {})
            
            # Combine strategy data with analytics insights
            enhanced_context = {
                'user_request': user_request,
                'strategy_metrics': {
                    'engagement_rate': insights.get('overall_engagement_rate', 0),
                    'avg_engagement': insights.get('avg_engagement_per_post', 0),
                    'best_content_type': insights.get('best_content_type', 'Unknown'),
                    'posting_frequency': insights.get('posting_frequency', 0),
                    'followers': strategy_data.get('account', {}).get('followers_count', 0)
                },
                'analytics_insights': analytics_data,
                'content_gaps': strategy_data.get('content_gaps', [])[:2],
                'optimization_opportunities': strategy_data.get('optimization_opportunities', [])[:2]
            }
            
            return json.dumps(enhanced_context, indent=1)
            
        except Exception as e:
            print(f"[WARN] Enhanced context creation failed: {e}")
            return json.dumps({'error': 'Context creation failed'}, indent=1)



    def _add_agent_response(self, state: Dict[str, Any], action: str, result: str):
        """Add agent response to state with analytics reference"""
        if 'agent_responses' not in state:
            state['agent_responses'] = []
        
        # Check if this builds on analytics insights
        previous_analytics = any(r.get('agent') == 'analytics' for r in state.get('agent_responses', []))
        
        # Check for duplicates
        existing = [r for r in state['agent_responses'] if r.get('agent') == self.name and r.get('action') == action]
        if not existing:
            state['agent_responses'].append({
                'agent': self.name,
                'action': action,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'builds_on_analytics': previous_analytics
            })

    def refresh_cache(self):
        """Force refresh of cached strategy data"""
        self.data_loaded = False
        self.cached_data = {}
        return self.get_strategy_data()

    def generate_content_calendar(self, days: int = 30) -> Dict[str, Any]:
        """Generate a strategic content calendar"""
        data = self.get_strategy_data()
        insights = data.get('strategy_insights', {})
        
        # Basic calendar structure
        calendar = {
            'duration_days': days,
            'recommended_posting_frequency': max(1, insights.get('posting_frequency', 1)),
            'best_posting_hours': insights.get('best_posting_hours', [9, 12, 18]),
            'content_mix': {
                'photos': 40,
                'carousels': 30,
                'reels': 30
            },
            'weekly_themes': [
                'Monday Motivation',
                'Tutorial Tuesday', 
                'Wednesday Wisdom',
                'Throwback Thursday',
                'Feature Friday',
                'Weekend Vibes'
            ]
        }
        
        return calendar
