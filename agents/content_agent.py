"""
Content Agent for AI Social Media Manager
Simplified architecture with clear separation of concerns
"""

from typing import Dict, Any, List, Optional
import os
from groq import Groq


class ContentAgent:
    """
    Content agent with simplified reflection architecture
    """

    def __init__(self):
        print("Initializing Content Agent")
        self.name = "content"
        
        # LLM client setup
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY is not set. Content generation will fail without it.")
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = "openai/gpt-oss-20b"
        self.max_reflections = 3  # Reduced from 5 for better performance

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.5) -> str:
        """Simplified LLM call method"""
        if not self.client:
            return "[LLM unavailable] Placeholder content."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=800,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API error: {e}")
            return "[Error] Unable to generate content."

    def _generate_content(self, brief: str, previous_content: Optional[str] = None, 
                         feedback: Optional[str] = None) -> str:
        """Generator agent - creates content"""
        system_prompt = """You are a senior social media copywriter. Generate concise, high-impact social content.
        Follow brand voice and platform norms. Return only the content without meta commentary.
        Include relevant hashtags when appropriate."""
        
        user_prompt = f"Create content for: {brief}"
        
        if feedback:
            user_prompt += f"\n\nApply this feedback: {feedback}"
        if previous_content:
            user_prompt += f"\n\nImprove this previous version: {previous_content}"
        
        return self._call_llm(system_prompt, user_prompt, temperature=0.7)

    def _critique_content(self, content: str, brief: str) -> str:
        """Critique agent - provides improvement suggestions"""
        system_prompt = """You are a professional content critic. Provide actionable, concise critique.
        Focus on clarity, tone, hook, structure, call-to-action, platform fit, and hashtags.
        Provide 3-5 bullet points of improvements and suggest specific wording where needed.
        Do NOT rewrite the full draft."""
        
        user_prompt = f"""Brief: {brief}
        
        Content to critique:
        {content}
        
        Please provide constructive criticism and specific improvement suggestions."""
        
        return self._call_llm(system_prompt, user_prompt, temperature=0.3)

    def _create_content_brief(self, state: Dict[str, Any]) -> str:
        """Create a clear content brief from state"""
        ctx = state.get("context_data", {})
        
        # Use specific task for this agent if available
        agent_tasks = ctx.get('agent_tasks', {})
        specific_task = agent_tasks.get('content')
        
        if specific_task:
            brief_parts = [f"Specific task: {specific_task}"]
        else:
            # Fallback to full request
            request = state.get('user_request', '')
            brief_parts = [f"Main request: {request}"]
        
        # Add context information
        for key in ['platform', 'tone', 'audience', 'constraints']:
            if ctx.get(key):
                brief_parts.append(f"{key.capitalize()}: {ctx[key]}")
        
        # Add feedback if available
        if ctx.get('content_feedback'):
            brief_parts.append(f"Feedback to incorporate: {ctx['content_feedback']}")
        
        return "\n".join(brief_parts)

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simplified content creation process with reflection
        """
        user_request = state.get('user_request', '')

        state["current_agent"] = self.name
        print(f"Content Agent processing: {user_request}")
        
        # Create content brief
        brief = self._create_content_brief(state)
        ctx = state.get("context_data", {})
        
        # Get any previous content or feedback
        previous_content = ctx.get('previous_draft')
        user_feedback = ctx.get('content_feedback')
        
        # Generate initial content
        content = self._generate_content(brief, previous_content, user_feedback)
        reflections = 0
        
        # Reflection loop (generate -> critique -> improve)
        for reflection in range(self.max_reflections):
            critique = self._critique_content(content, brief)
            
            # Generate improved content based on critique
            improved_content = self._generate_content(
                brief, 
                previous_content=content, 
                feedback=critique
            )
            
            # If content didn't improve significantly, break early
            if improved_content == content or not improved_content.strip():
                break
                
            content = improved_content
            reflections += 1
        
        # Apply user feedback if provided (final polish)
        if user_feedback and not previous_content:
            final_content = self._generate_content(
                brief, 
                previous_content=content, 
                feedback=user_feedback
            )
            if final_content and final_content != content:
                content = final_content
                reflections += 1
        
        # Update state with results
        state['generated_content'] = {
            'content': content,
            'reflection_count': reflections,
            'status': 'completed'
        }
        
        # Update context for sequential workflows
        if state.get('workflow_type') == 'sequential':
            state['context_data'].update({
                'content_results': state['generated_content'],
                'current_task': 'content_creation',
                'status': 'completed'
            })
        
        # Track agent response
        state['agent_responses'].append({
            'agent': self.name,
            'action': 'content_creation',
            'result': f'Content generated with {reflections} reflection cycles',
            'reflection_count': reflections
        })
        
        return state