"""
Publishing Agent for AI Social Media Manager
Handles content scheduling and cross-platform publishing
"""

from typing import Dict, Any

class PublishingAgent:
    """
    Publishing agent for scheduling and posting content
    """
    
    def __init__(self):
        print("Initializing Publishing Agent")
        self.name = "publishing"
        
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process publishing and scheduling tasks
        """
        state['current_agent'] = self.name
        print(f"Publishing Agent processing: {state.get('user_request', '')}")
        print("🚀 PUBLISHING AGENT IS PROCESSING")
        
        # Only add response if not already added for this agent
        existing_responses = [r for r in state.get('agent_responses', []) if r.get('agent') == self.name]
        if not existing_responses:
            state['agent_responses'].append({
                'agent': self.name,
                'action': 'content_publishing',
                'result': 'Content scheduled and published',
                'platforms': ['Instagram', 'LinkedIn', 'X', 'Facebook']
            })
        
        return state
