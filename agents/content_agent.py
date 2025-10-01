"""
Content Agent for AI Social Media Manager
Simplified architecture with clear separation of concerns
"""

from typing import Dict, Any, List, Optional
import os
import requests
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agent communication system
from agents.agent_communication import AgentCommunication, AgentCoordinator


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
        self.model = "llama-3.1-8b-instant"
        self.max_reflections = 3  # Reduced from 5 for better performance
        
        # OpenRouter setup for image generation
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.openrouter_api_key:
            print("Warning: OPENROUTER_API_KEY is not set. Image generation will be disabled.")
        else:
            print(f"OpenRouter API key loaded: {self.openrouter_api_key[:20]}...")
        self.image_model = "google/gemini-2.5-flash-image-preview:free"

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.5) -> str:
        """Simplified LLM call method"""
        if not self.client:
            print("Warning: No LLM client available, using placeholder")
            return "[LLM unavailable] Placeholder content for: " + user_prompt[:50] + "..."
        
        try:
            print(f"Making LLM call with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=800,
            )
            content = response.choices[0].message.content
            if content:
                content = content.strip()
                print(f"LLM response received: {len(content)} characters")
                return content
            else:
                print("Warning: Empty response from LLM")
                return "[Empty response] Please try again with a different request."
        except Exception as e:
            print(f"Groq API error: {e}")
            return f"[Error] Unable to generate content: {str(e)}"

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
    
    def _generate_image(self, prompt: str) -> Optional[str]:
        """Generate image URL from Pollinations AI"""
        try:
            print(f"Generating image with prompt: {prompt}")
            
            # Always use Pollinations AI for image generation
            encoded_prompt = requests.utils.quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024"
            print(f"Generated image URL: {image_url}")
            
            # Return the URL directly instead of downloading
            return image_url
            
            # # Commented out download code - keep for future use if needed
            # # Create images directory if it doesn't exist
            # import os
            # os.makedirs("generated_images", exist_ok=True)
            # 
            # # Generate filename
            # import time
            # filename = f"generated_images/image_{int(time.time())}.jpg"
            # 
            # # Download the image
            # response = requests.get(image_url, timeout=30)
            # if response.status_code == 200:
            #     with open(filename, 'wb') as f:
            #         f.write(response.content)
            #     print(f"Image saved to: {filename}")
            #     return filename
            # else:
            #     print(f"Failed to download image: {response.status_code}")
            #     return None
                
        except Exception as e:
            print(f"Error generating image: {e}")
            return None

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
    
    def _create_enhanced_content_brief(self, state: Dict[str, Any], strategy_data: Dict, analytics_data: Dict) -> str:
        """Create enhanced content brief using previous agent insights"""
        # Start with basic brief
        brief = self._create_content_brief(state)
        
        # Add strategy insights
        if strategy_data:
            brief += "\n\nStrategy Recommendations:"
            if strategy_data.get('focus_area'):
                brief += f"\n- Focus on: {strategy_data['focus_area']}"
            if strategy_data.get('strategy_summary'):
                brief += f"\n- Key insight: {strategy_data['strategy_summary'][:100]}..."
        
        # Add analytics insights
        if analytics_data:
            brief += "\n\nAnalytics Insights:"
            if analytics_data.get('top_theme'):
                brief += f"\n- Best performing theme: {analytics_data['top_theme']}"
            if analytics_data.get('engagement_rate'):
                brief += f"\n- Current engagement rate: {analytics_data['engagement_rate']}%"
            if analytics_data.get('best_content_type'):
                brief += f"\n- Best content format: {analytics_data['best_content_type']}"
        
        return brief
    
    def _needs_image(self, request: str) -> bool:
        """Check if request needs image generation"""
        image_keywords = ['image', 'picture', 'photo', 'visual', 'generate image', 'create image', 'make image']
        return any(keyword in request.lower() for keyword in image_keywords)
    
    def _extract_image_prompt(self, request: str) -> str:
        """Extract image description from user request"""
        # Simple extraction - look for patterns like "image of X" or "make image X"
        request_lower = request.lower()
        
        # Try different patterns
        patterns = [
            'image of ',
            'picture of ',
            'photo of ',
            'generate image ',
            'create image ',
            'make image '
        ]
        
        for pattern in patterns:
            if pattern in request_lower:
                start_idx = request_lower.find(pattern) + len(pattern)
                # Extract until next sentence or end
                remaining = request[start_idx:].split('.')[0].split('and')[0].strip()
                if remaining:
                    return remaining
        
        # Fallback: use the whole request
        return request

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced content creation with strategy and analytics integration
        """
        print(f"Content Agent processing: {state.get('user_request', '')}")
        state["current_agent"] = self.name
        
        user_request = state.get('user_request', '')
        
        # Get previous agent insights using communication system
        agent_context = AgentCoordinator.prepare_agent_context(state, self.name)
        strategy_data = agent_context.get('strategy_recommendations', {})
        analytics_data = agent_context.get('analytics_insights', {})
        
        if strategy_data:
            print(f"[CONTENT] Using strategy recommendations from previous agent")
        if analytics_data:
            print(f"[CONTENT] Using analytics data: best_theme={analytics_data.get('top_theme', 'N/A')}")
        
        # Check if image generation is needed
        image_url = None
        if self._needs_image(user_request):
            image_prompt = self._extract_image_prompt(user_request)
            print(f"Image generation requested: {image_prompt}")
            image_url = self._generate_image(image_prompt)
        
        # Create enhanced brief with previous agent data
        brief = self._create_enhanced_content_brief(state, strategy_data, analytics_data)
        content = self._generate_content(brief)
        
        # Do 2 reflection cycles
        for i in range(2):
            critique = self._critique_content(content, brief)
            improved = self._generate_content(brief, content, critique)
            if improved and len(improved) > 10:
                content = improved
        
        # Add communication metadata
        AgentCommunication.add_communication_metadata(state, self.name, bool(strategy_data or analytics_data))
        
        # Set results with image if generated
        result = {
            'content': content,
            'reflection_count': 3,
            'status': 'completed',
            'used_strategy_data': bool(strategy_data),
            'used_analytics_data': bool(analytics_data)
        }
        
        if image_url:
            result['image_path'] = image_url
            result['has_image'] = True
        
        state['generated_content'] = result
        
        # Add agent response only once
        existing_responses = [r for r in state.get('agent_responses', []) if r.get('agent') == self.name]
        if not existing_responses:
            response_text = 'Multi-platform content created successfully'
            if strategy_data:
                response_text += ' (based on strategy recommendations)'
            if image_url:
                response_text += ' (with generated image)'
            
            state['agent_responses'].append({
                'agent': self.name,
                'action': 'content_creation',
                'result': response_text,
                'reflection_count': 3,
                'has_image': bool(image_url),
                'image_url': image_url,
                'used_previous_agents': list(agent_context.get('previous_agents', {}).keys())
            })
        
        print(f"Content generated: {len(content)} chars, Image: {bool(image_url)}")
        return state