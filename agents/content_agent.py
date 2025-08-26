"""
Content Agent for AI Social Media Manager
Handles content creation, text generation, and visual ideation
"""

from typing import Dict, Any

class ContentAgent:
    """
    Content agent for creating social media content
    """
    
    def __init__(self):
        print("Initializing Content Agent")
        self.name = "content"
        
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content creation tasks
        """
        # Mark current node for the router
        state['current_agent'] = self.name
        print(f"Content Agent processing: {state.get('user_request', '')}")
        print("CONTENT AGENT IS PROCESSING")
    
        # Add content to state
        state['generated_content'] = {
            'posts': 'Social media posts created',
            'hashtags': '#trending #socialmedia #content',
            'visuals': 'Visual suggestions prepared'
        }
    
        # Optionally enrich context when in sequential mode
        current_task = {}
        if state.get('workflow_type') == 'sequential':
            # Get the current task from the sequence if available
            current_idx = state.get('sequence_index', 0)
            if state.get('task_decomposition'):
                tasks = state['task_decomposition']
                if 0 <= current_idx < len(tasks):
                    current_task = tasks[current_idx]
            # Update the state with the task results
            state['context_data'].update({
                'content_results': state['generated_content'],
                'current_task': current_task.get('task', 'content_creation'),
                'status': 'completed'
            })
    
        state['agent_responses'].append({
            'agent': self.name,
            'action': 'content_creation',
            'result': 'Content generated successfully'
        })
    
        return state