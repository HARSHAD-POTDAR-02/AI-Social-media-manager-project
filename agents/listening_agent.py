"""
Listening Agent for AI Social Media Manager
Handles social listening, monitoring, and tracking
"""

from typing import Dict, Any

class ListeningAgent:
    """
    Listening agent for monitoring social media activity
    """
    
    def __init__(self):
        print("Initializing Listening Agent")
        self.name = "listening"
        
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process social listening tasks
        """
        state['current_agent'] = self.name
        print(f"Listening Agent processing: {state.get('user_request', '')}")
        print("LISTENING AGENT IS PROCESSING")
        
        # Only add response if not already added for this agent
        existing_responses = [r for r in state.get('agent_responses', []) if r.get('agent') == self.name]
        if not existing_responses:
            state['agent_responses'].append({
                'agent': self.name,
                'action': 'social_listening',
                'result': 'Social monitoring complete',
                'mentions': 25,
                'sentiment_score': 0.8
            })
        
        return state
