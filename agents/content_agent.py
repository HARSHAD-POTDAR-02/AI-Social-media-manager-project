"""
Content Agent for AI Social Media Manager
Simplified architecture with clear separation of concerns and session memory integration
"""

from typing import Dict, Any, List, Optional
import os
import requests
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import session memory manager for centralized memory storage
from session_memory import get_session_memory_manager

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
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.max_reflections = 2  # Reduced from 3 for better performance

        # OpenRouter setup for image generation
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.openrouter_api_key:
            print("Warning: OPENROUTER_API_KEY is not set. Image generation will be disabled.")
        else:
            print(f"OpenRouter API key loaded: {self.openrouter_api_key[:20]}...")
        self.image_model = "google/gemini-2.5-flash-image-preview:free"

        # Session memory manager
        self.session_memory = get_session_memory_manager()

        # Content creation system prompt
        self.system_prompt = """You are an expert social media content creator specializing in Instagram and TikTok content.
You create engaging, platform-optimized content that drives engagement and growth.

Your expertise includes:
- Creating viral reel concepts and hooks
- Writing compelling captions with CTAs
- Optimizing content for Instagram/TikTok algorithms
- Understanding audience psychology and engagement patterns
- Crafting content series and thematic campaigns
- Using trending formats and audio effectively
- Use emojis to make the content more lively and engaging


Focus on:
- High-engagement hooks in the first 3 seconds
- Clear value proposition and storytelling
- Strong call-to-actions that drive comments/shares
- Platform-specific formatting and best practices
- Hashtag strategies for discoverability
- Content that encourages saves and shares"""

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
                return "[Empty response] Please try again with a different request."
        except Exception as e:
            print(f"Groq API error: {e}")
            return f"[Error] Unable to generate content: {str(e)}"

    def _clean_content_formatting(self, content: str) -> str:
        """Clean up messy AI formatting and make content presentable"""
        if not content:
            return ""

        # Remove HTML-like tags
        content = content.replace('<br>', '\n').replace('<br/>', '\n')
        content = content.replace('&nbsp;', ' ').replace('&amp;', '&')
        content = content.replace('<strong>', '**').replace('</strong>', '**')
        content = content.replace('<em>', '*').replace('</em>', '*')

        # Fix markdown-style formatting
        content = content.replace('**', '').replace('*', '')

        # Clean up excessive newlines
        import re
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Max 2 consecutive newlines

        # Remove leading/trailing whitespace from each line
        lines = content.split('\n')
        clean_lines = [line.strip() for line in lines]
        content = '\n'.join(clean_lines)

        # Fix common formatting issues
        content = content.replace('1️⃣', '1.').replace('2️⃣', '2.').replace('3️⃣', '3.')
        content = content.replace('4️⃣', '4.').replace('5️⃣', '5.')

        # Remove excessive emojis (keep only key ones)
        emoji_pattern = r'[^\w\s.,!?-]'  # Keep basic punctuation
        # Actually, let's keep emojis as they make content engaging

        return content.strip()

    def _generate_content(self, brief: str, previous_content: str = None, feedback: str = None, context_prompt: str = "") -> str:
        """Generate content using AI with proper formatting"""
        system_prompt = f"""You are an expert social media content creator. Create engaging, well-formatted content.

IMPORTANT FORMATTING RULES:
- Use clean, readable text without HTML tags (<br>, <strong>, etc.)
- Use plain text with emojis for visual appeal
- Structure content with clear headings, bullet points, and numbered lists
- Keep formatting simple and professional
- Use emojis sparingly and appropriately
- Ensure content is mobile-friendly and easy to read

{self.system_prompt}

RESPONSE FORMAT:
- Provide exactly what was requested (e.g., 5 reel ideas = exactly 5 reel ideas)
- Make content engaging with emojis and clear formatting
- Include specific details and examples for each idea
- End with relevant hashtags

Remember: Your response should be a direct answer to the user's request, nothing more, nothing less."""

        user_prompt = f"Create content based on this brief:\n{brief}"

        if context_prompt:
            user_prompt += f"\n{context_prompt}"

        if feedback:
            user_prompt += f"\n\nApply this feedback: {feedback}"
        if previous_content:
            user_prompt += f"\n\nPrevious version (improve this): {previous_content}"

        content = self._call_llm(system_prompt, user_prompt, temperature=0.7)

        # Clean up the formatting
        content = self._clean_content_formatting(content)

        return content

    def _critique_content(self, content: str, brief: str, context_prompt: str = "") -> str:
        """Critique agent - provides improvement suggestions"""
        system_prompt = """You are a professional content critic. Provide actionable, concise critique.
        Focus on clarity, tone, hook, structure, call-to-action, platform fit, and hashtags.
        Provide 3-5 bullet points of improvements and suggest specific wording where needed.
        Do NOT rewrite the full draft."""

        user_prompt = f"""Brief: {brief}
        {context_prompt}

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

        except Exception as e:
            print(f"Error generating image: {e}")
            return None

    def _create_content_brief(self, state: Dict[str, Any]) -> str:
        """Create a clear content brief from state"""
        ctx = state.get("context_data", {})

        # Use specific task for this agent if available
        agent_tasks = ctx.get('agent_tasks', {})
        specific_task = agent_tasks.get('content')

        # Get conversation context for better understanding
        session_context = state.get('session_context', {})
        conversation_history = session_context.get('conversation_history', [])

        if specific_task:
            brief_parts = [f"Specific task: {specific_task}"]
        else:
            # Fallback to full request with context
            request = state.get('user_request', '')
            brief_parts = [f"Main request: {request}"]

        # Add recent conversation context to understand the flow
        if conversation_history:
            recent_requests = [entry.get('user_input', '') for entry in conversation_history[-3:]]
            if recent_requests:
                brief_parts.append(f"Recent conversation context: {', '.join(recent_requests)}")

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

    def _validate_content_relevance(self, content: str, user_request: str) -> bool:
        """Check if generated content is relevant to the user's request"""
        if not content or not user_request:
            return False

        # Convert to lowercase for comparison
        content_lower = content.lower()
        request_lower = user_request.lower()

        # Check for obvious mismatches
        fitness_keywords = ['fitness', 'workout', 'exercise', 'gym', 'training']
        summer_keywords = ['summer', 'beach', 'sun', 'vacation', 'holiday']
        winter_keywords = ['winter', 'snow', 'cold', 'holiday', 'christmas']
        reel_keywords = ['reel', 'video', 'tiktok', 'instagram']
        brand_keywords = ['brand', 'business', 'company', 'marketing', 'website']

        # If user asked for summer content but got fitness content
        if any(word in request_lower for word in summer_keywords) and any(word in content_lower for word in fitness_keywords):
            return False

        # If user asked for reel ideas but got brand marketing
        if any(word in request_lower for word in reel_keywords) and any(word in content_lower for word in brand_keywords):
            return False

        # If user asked for winter but got summer content
        if any(word in request_lower for word in winter_keywords) and any(word in content_lower for word in summer_keywords):
            return False

        # Basic relevance check - does content contain key terms from request?
        request_words = set(request_lower.split())
        content_words = set(content_lower.split())

        # At least 20% of request words should appear in content (simple heuristic)
        if request_words:
            overlap = len(request_words.intersection(content_words))
            relevance_score = overlap / len(request_words)
            return relevance_score > 0.2

        return True
 
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced content creation with strategy, analytics, and session memory integration
        """
        print(f"Content Agent processing: {state.get('user_request', '')}")
        state["current_agent"] = self.name

        user_request = state.get('user_request', '')
        session_id = state.get('session_id', '')

        # Get previous agent insights using communication system
        agent_context = AgentCoordinator.prepare_agent_context(state, self.name)
        strategy_data = agent_context.get('strategy_recommendations', {})
        analytics_data = agent_context.get('analytics_insights', {})

        if strategy_data:
            print(f"[CONTENT] Using strategy recommendations from previous agent")
        if analytics_data:
            print(f"[CONTENT] Using analytics data: best_theme={analytics_data.get('top_theme', 'N/A')}")

        # Get session context for personalization
        session_context = state.get('session_context', {})
        conversation_history = session_context.get('conversation_history', [])
        user_preferences = session_context.get('user_preferences', {})

        print(f"[CONTENT] Session context: {len(conversation_history)} previous interactions")

        # Build conversation context for the AI prompt
        context_prompt = ""
        if conversation_history:
            context_prompt = "\n\nConversation Context:\n"
            for i, entry in enumerate(conversation_history[-3:], 1):  # Last 3 exchanges
                context_prompt += f"Previous request {i}: {entry.get('user_input', '')}\n"
                if entry.get('agent_response'):
                    # Clean up the previous response for context
                    prev_response = entry.get('agent_response', '')[:200]
                    prev_response = prev_response.replace('*', '').replace('<br>', ' ')
                    context_prompt += f"Previous response {i}: {prev_response}...\n"
                context_prompt += "\n"

        # Debug: Show what the AI will see in the brief
        ctx = state.get("context_data", {})
        agent_tasks = ctx.get('agent_tasks', {})
        specific_task = agent_tasks.get('content')
        print(f"[CONTENT] Specific task: {specific_task}")
        print(f"[CONTENT] User request: {user_request}")

        # Check if image generation is needed
        image_url = None
        if self._needs_image(user_request):
            image_prompt = self._extract_image_prompt(user_request)
            print(f"Image generation requested: {image_prompt}")
            image_url = self._generate_image(image_prompt)

        # Create enhanced brief with all available data
        brief = self._create_enhanced_content_brief(state, strategy_data, analytics_data)
        print(f"[CONTENT] Brief created: {brief[:200]}...")

        content = self._generate_content(brief, context_prompt=context_prompt)

        # Validate content relevance
        is_relevant = self._validate_content_relevance(content, user_request)
        if not is_relevant:
            print("[CONTENT] Warning: Generated content may not be fully relevant to request")
            # Try one more time with more explicit instructions
            enhanced_brief = f"IMPORTANT: Respond ONLY to this specific request: {user_request}\n\nOriginal brief:\n{brief}"
            content = self._generate_content(enhanced_brief, context_prompt=context_prompt)

        # Do 2 reflection cycles
        for i in range(2):
            critique = self._critique_content(content, brief, context_prompt)
            improved = self._generate_content(brief, content, critique, context_prompt)
            if improved and len(improved) > 10:
                content = improved

        # Add communication metadata
        AgentCommunication.add_communication_metadata(state, self.name, bool(strategy_data or analytics_data))

        # Set results with image if generated
        result = {
            'content': content,
            'reflection_count': 2,
            'status': 'completed',
            'used_strategy_data': bool(strategy_data),
            'used_analytics_data': bool(analytics_data),
            'used_session_context': bool(session_context)
        }

        if image_url:
            result['image_path'] = image_url
            result['has_image'] = True

        state['generated_content'] = result

        # Update session memory with this agent response
        if session_id:
            metadata = {
                'reflection_count': 2,
                'has_image': bool(image_url),
                'used_previous_agents': bool(strategy_data or analytics_data),
                'session_context_used': bool(session_context)
            }

            # Note: The graph_setup.py will handle updating session memory with the final response

        # Add agent response only once
        existing_responses = [r for r in state.get('agent_responses', []) if r.get('agent') == self.name]
        if not existing_responses:
            response_text = 'Multi-platform content created successfully'
            if strategy_data:
                response_text += ' (based on strategy recommendations)'
            if analytics_data:
                response_text += ' (informed by analytics)'
            if session_context:
                response_text += ' (personalized with conversation history)'
            if image_url:
                response_text += ' (with generated image)'

            state['agent_responses'].append({
                'agent': self.name,
                'action': 'content_creation',
                'result': response_text,
                'reflection_count': 2,
                'has_image': bool(image_url),
                'image_url': image_url,
                'used_previous_agents': list(agent_context.get('previous_agents', {}).keys()),
                'used_session_context': bool(session_context)
            })

        print(f"Content generated: {len(content)} chars, Image: {bool(image_url)}")
        return state
