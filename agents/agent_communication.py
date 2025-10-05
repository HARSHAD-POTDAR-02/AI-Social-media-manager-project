"""
Agent Communication System
Enables seamless data sharing and coordination between agents in sequential workflows
"""

from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime

class AgentCommunication:
    """
    Universal communication system for agent-to-agent data sharing
    """
    
    @staticmethod
    def extract_agent_data(state: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """Extract data from a specific previous agent"""
        agent_responses = state.get('agent_responses', [])
        
        for response in agent_responses:
            if response.get('agent') == agent_name:
                return {
                    'agent': agent_name,
                    'result': response.get('result', ''),
                    'timestamp': response.get('timestamp', ''),
                    'action': response.get('action', ''),
                    'raw_response': response
                }
        return {}
    
    @staticmethod
    def extract_all_previous_data(state: Dict[str, Any], current_agent: str) -> Dict[str, Any]:
        """Extract data from all previous agents"""
        agent_responses = state.get('agent_responses', [])
        previous_data = {}
        
        for response in agent_responses:
            agent = response.get('agent')
            if agent and agent != current_agent:
                previous_data[agent] = {
                    'result': response.get('result', ''),
                    'timestamp': response.get('timestamp', ''),
                    'action': response.get('action', ''),
                    'raw_response': response
                }
        
        return previous_data
    
    @staticmethod
    def extract_analytics_insights(agent_responses: List[Dict]) -> Dict[str, Any]:
        """Extract structured insights from analytics agent"""
        insights = {}
        
        for response in agent_responses:
            if response.get('agent') == 'analytics':
                result = response.get('result', '')
                
                # Extract numerical metrics
                insights.update(AgentCommunication._parse_metrics(result))
                
                # Extract content themes
                insights.update(AgentCommunication._parse_content_themes(result))
                # Store full summary
                insights['analytics_summary'] = result[:500] + '...' if len(result) > 500 else result
                
        return insights
    
    @staticmethod
    def extract_strategy_recommendations_from_state(state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract strategy recommendations from strategy agent's generated content"""
        generated_content = state.get('generated_content', {})
        if generated_content.get('type') == 'strategy_consultation':
            response = generated_content.get('content', '')

            return {
                'strategy_summary': generated_content.get('strategy_summary', response[:300] + '...' if len(response) > 300 else response),
                'focus_area': generated_content.get('focus_area', 'General Strategy'),
                'has_strategy': True,
                'raw_response': response
            }
        return {}

    @staticmethod
    def extract_strategy_recommendations(agent_responses: List[Dict]) -> Dict[str, Any]:
        """Extract strategy recommendations from strategy agent responses (fallback method)"""
        recommendations = {}

        for response in agent_responses:
            if response.get('agent') == 'strategy':
                result = response.get('result', '')

                # Extract recommendations
                recommendations['strategy_summary'] = result[:300] + '...' if len(result) > 300 else result
                recommendations['has_strategy'] = True

                # Parse specific recommendations
                if 'focus on' in result.lower():
                    focus_match = re.search(r'focus on ([^.]+)', result.lower())
                    if focus_match:
                        recommendations['focus_area'] = focus_match.group(1).strip()

        return recommendations
        """Parse numerical metrics from text"""
        metrics = {}
        
        # Engagement rate - multiple patterns
        eng_patterns = [
            r'engagement rate.*?(\d+\.?\d*)%?',
            r'engagement rate.*?is.*?(\d+\.?\d*)',
            r'(\d+\.?\d*).*?engagement rate'
        ]
        for pattern in eng_patterns:
            eng_match = re.search(pattern, text.lower())
            if eng_match:
                metrics['engagement_rate'] = float(eng_match.group(1))
                break
        
        # Average likes - multiple patterns
        likes_patterns = [
            r'average.*?(\d+\.?\d*).*?likes',
            r'(\d+\.?\d*).*?likes.*?per post',
            r'average likes.*?(\d+\.?\d*)'
        ]
        for pattern in likes_patterns:
            likes_match = re.search(pattern, text.lower())
            if likes_match:
                metrics['avg_likes'] = float(likes_match.group(1))
                break
        
        # Average comments - multiple patterns
        comments_patterns = [
            r'average.*?(\d+\.?\d*).*?comments',
            r'(\d+\.?\d*).*?comments.*?per post',
            r'average comments.*?(\d+\.?\d*)'
        ]
        for pattern in comments_patterns:
            comments_match = re.search(pattern, text.lower())
            if comments_match:
                metrics['avg_comments'] = float(comments_match.group(1))
                break
        
        # Followers
        followers_match = re.search(r'(\d+)\s+followers', text.lower())
        if followers_match:
            metrics['followers'] = int(followers_match.group(1))
        
        return metrics
    
    @staticmethod
    def _parse_content_themes(text: str) -> Dict[str, Any]:
        """Parse content themes and insights"""
        themes = {}
        
        # Enhanced theme detection
        theme_keywords = {
            'sports': ['sports', 'cricket', 'soccer', 'football', 'virat kohli', 'match', 'game'],
            'fitness': ['fitness', 'workout', 'gym', 'health', 'exercise'],
            'lifestyle': ['lifestyle', 'daily', 'life', 'routine'],
            'business': ['business', 'entrepreneur', 'startup', 'work'],
            'tech': ['tech', 'technology', 'digital', 'app', 'software'],
            'food': ['food', 'recipe', 'cooking', 'restaurant'],
            'travel': ['travel', 'trip', 'vacation', 'destination'],
            'motivational': ['motivational', 'inspiring', 'inspiration', 'ganpati', 'visarjan']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                themes['top_theme'] = theme
                break
        
        # Best performing content type
        if 'images' in text.lower() and ('performing' in text.lower() or 'posts are' in text.lower()):
            themes['best_content_type'] = 'images'
        elif 'video' in text.lower() and 'performing' in text.lower():
            themes['best_content_type'] = 'video'
        elif 'carousel' in text.lower() and 'performing' in text.lower():
            themes['best_content_type'] = 'carousel'
        elif 'all.*posts are images' in text.lower():
            themes['best_content_type'] = 'images'
        
        # Best posting times
        time_match = re.search(r'best.*?time.*?(\d{1,2}:\d{2}).*?(\d{1,2}:\d{2})', text.lower())
        if time_match:
            themes['best_posting_times'] = [time_match.group(1), time_match.group(2)]
        elif '14:00' in text and '18:00' in text:
            themes['best_posting_times'] = ['14:00', '18:00']
        
        return themes
    
    @staticmethod
    def create_context_for_agent(state: Dict[str, Any], current_agent: str) -> str:
        """Create contextual information for current agent based on previous agents"""
        previous_data = AgentCommunication.extract_all_previous_data(state, current_agent)
        
        if not previous_data:
            return "No previous agent data available."
        
        context_parts = [f"Previous Agent Insights for {current_agent.title()} Agent:"]
        
        # Add analytics insights if available
        if 'analytics' in previous_data:
            analytics_insights = AgentCommunication.extract_analytics_insights([previous_data['analytics']['raw_response']])
            if analytics_insights:
                context_parts.append(f"Analytics Data: {json.dumps(analytics_insights, indent=1)}")
        
        # Add strategy insights if available
        if 'strategy' in previous_data:
            strategy_data = AgentCommunication.extract_strategy_recommendations([previous_data['strategy']['raw_response']])
            if strategy_data:
                context_parts.append(f"Strategy Recommendations: {json.dumps(strategy_data, indent=1)}")
        
        # Add content data if available
        if 'content' in previous_data:
            content_data = AgentCommunication.extract_content_data([previous_data['content']['raw_response']])
            if content_data:
                context_parts.append(f"Generated Content: {json.dumps(content_data, indent=1)}")
        
        return "\n\n".join(context_parts)
    
    @staticmethod
    def should_use_previous_data(current_agent: str, user_request: str) -> bool:
        """Determine if current agent should use data from previous agents"""
        
        # Agents that benefit from previous data
        data_dependent_agents = {
            'strategy': ['analytics'],  # Strategy uses analytics
            'content': ['strategy', 'analytics'],  # Content uses strategy and analytics
            'publishing': ['content'],  # Publishing uses content
            'community': ['analytics', 'content'],  # Community uses analytics and content
            'crisis': ['analytics', 'listening'],  # Crisis uses analytics and listening
        }
        
        return current_agent in data_dependent_agents
    
    @staticmethod
    def add_communication_metadata(state: Dict[str, Any], current_agent: str, used_previous_data: bool = False):
        """Add metadata about agent communication to state"""
        if 'agent_communication' not in state:
            state['agent_communication'] = {}
        
        state['agent_communication'][current_agent] = {
            'timestamp': datetime.now().isoformat(),
            'used_previous_data': used_previous_data,
            'previous_agents': list(AgentCommunication.extract_all_previous_data(state, current_agent).keys())
        }

class AgentCoordinator:
    """
    Coordinates agent execution and data flow in sequential workflows
    """
    
    @staticmethod
    def prepare_agent_context(state: Dict[str, Any], current_agent: str) -> Dict[str, Any]:
        """Prepare enhanced context for agent including previous agent data"""
        
        # Check if agent should use previous data
        user_request = state.get('user_request', '')
        should_use_data = AgentCommunication.should_use_previous_data(current_agent, user_request)
        
        enhanced_context = {
            'user_request': user_request,
            'current_agent': current_agent,
            'use_previous_data': should_use_data
        }
        
        if should_use_data:
            # Add previous agent insights
            previous_data = AgentCommunication.extract_all_previous_data(state, current_agent)
            enhanced_context['previous_agents'] = previous_data
            
            # Add specific insights based on agent type
            if current_agent == 'strategy':
                enhanced_context['analytics_insights'] = AgentCommunication.extract_analytics_insights(
                    state.get('agent_responses', [])
                )
            elif current_agent == 'content':
                enhanced_context['strategy_recommendations'] = AgentCommunication.extract_strategy_recommendations(
                    state.get('agent_responses', [])
                )
                enhanced_context['analytics_insights'] = AgentCommunication.extract_analytics_insights(
                    state.get('agent_responses', [])
                )
            elif current_agent == 'publishing':
                enhanced_context['content_data'] = AgentCommunication.extract_content_data(
                    state.get('agent_responses', [])
                )
        
        return enhanced_context