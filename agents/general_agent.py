"""
General Conversational Agent for AI Social Media Manager
A ChatGPT-style conversational AI with session memory integration
"""

from typing import Dict, Any, List, Optional
import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Import session memory manager for centralized memory storage
from session_memory import get_session_memory_manager

# Import agent communication system
from agents.agent_communication import AgentCommunication, AgentCoordinator


class GeneralAgent:
    """
    General conversational AI agent with ChatGPT-like capabilities and session memory
    """

    def __init__(self, groq_api_key: str = None):
        print("[INIT] Initializing General Conversational Agent")
        self.name = "general"
        self.description = "General Conversational AI Assistant"

        # LLM client setup
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            print("[WARN] GROQ_API_KEY not found - general chat will be limited")
            self.groq_client = None
        else:
            self.groq_client = Groq(api_key=self.groq_api_key)

        # Session memory manager for conversation context
        self.session_memory = get_session_memory_manager()

        # Conversational AI system prompt
        self.system_prompt = """You are a helpful, intelligent, and conversational AI assistant. You engage in natural, flowing conversations while maintaining context and memory of previous interactions.

Your personality:
- Friendly and approachable, like a knowledgeable friend
- Helpful and informative, providing clear explanations
- Engaging and conversational, not robotic or formal
- Patient and understanding, especially with follow-up questions
- Honest about limitations and uncertainties
- Witty and light-hearted when appropriate

Your capabilities:
- Answer questions on any topic with accurate, up-to-date information
- Provide explanations, examples, and step-by-step guidance
- Help with creative tasks, brainstorming, and problem-solving
- Engage in casual conversation and maintain context
- Remember previous parts of our conversation
- Ask clarifying questions when needed
- Admit when you don't know something

Guidelines for responses:
- Be conversational and natural, like talking to a friend
- Use appropriate emojis to add warmth and expression 😊
- Keep responses helpful and actionable
- Reference previous conversation context when relevant
- Ask follow-up questions to continue the conversation
- Stay on topic but be flexible for tangents
- Be comprehensive but not overwhelming

Remember: You're here to help and have a conversation, not just answer questions!"""

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Make LLM call with error handling"""
        if not self.groq_client:
            return "I'm sorry, but I'm not able to connect to my language model right now. Please check your API configuration."

        try:
            print(f"Making conversational LLM call...")
            response = self.groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )

            content = response.choices[0].message.content
            if content:
                return content.strip()
            return "I understand your question, but I'm having trouble generating a response right now."

        except Exception as e:
            print(f"LLM Error: {e}")
            return f"I'm experiencing some technical difficulties right now. Please try again in a moment! Error: {str(e)}"

    def _build_conversation_context(self, session_context: Dict[str, Any]) -> str:
        """Build conversation context from session memory"""
        conversation_history = session_context.get('conversation_history', [])

        if not conversation_history:
            print("[GENERAL] No conversation history found")
            return ""

        # Get last 5 exchanges for context (not too much to overwhelm)
        recent_exchanges = conversation_history[-5:]
        print(f"[GENERAL] Building context from {len(recent_exchanges)} recent exchanges")

        context_parts = ["Previous conversation:"]
        for i, entry in enumerate(recent_exchanges, 1):
            user_msg = entry.get('user_input', '')
            agent_msg = entry.get('agent_response', '')
            
            # Show full recent messages for better memory
            context_parts.append(f"\nUser said: {user_msg}")
            if agent_msg:
                # Truncate agent messages but keep user messages full
                agent_preview = agent_msg[:150] + "..." if len(agent_msg) > 150 else agent_msg
                context_parts.append(f"You responded: {agent_preview}")

        result = "\n".join(context_parts)
        print(f"[GENERAL] Context built: {len(result)} characters")
        return result

    def can_handle(self, user_request: str) -> bool:
        """General agent can handle any conversational request"""
        # General agent handles everything that's not specifically strategy/content focused
        general_keywords = [
            'hello', 'hi', 'hey', 'help', 'question', 'what', 'how', 'why', 'when', 'where',
            'can you', 'could you', 'would you', 'do you', 'are you', 'tell me', 'explain',
            'chat', 'talk', 'discuss', 'conversation', 'about', 'regarding', 'concerning'
        ]

        request_lower = user_request.lower()
        return any(keyword in request_lower for keyword in general_keywords) or len(user_request.split()) < 10

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process conversational requests with session memory integration
        """
        state['current_agent'] = self.name
        user_request = state.get('user_request', '')
        session_id = state.get('session_id', '')

        print(f"[GENERAL] Conversational request: {user_request}")
        print(f"[GENERAL] Session ID: {session_id}")

        # Get session context for conversation history
        session_context = state.get('session_context', {})
        conversation_history = session_context.get('conversation_history', [])
        user_preferences = session_context.get('user_preferences', {})

        print(f"[GENERAL] Session context: {len(conversation_history)} previous exchanges")
        if conversation_history:
            print(f"[GENERAL] Last exchange: {conversation_history[-1].get('user_input', 'N/A')[:50]}...")
        else:
            print("[GENERAL] WARNING: No conversation history found in session context!")

        # Build conversation context for the AI
        conversation_context = self._build_conversation_context(session_context)

        # Create conversational prompt
        if conversation_context:
            full_prompt = f"""Current user request: {user_request}

{conversation_context}

Please respond naturally to the current request, taking into account our previous conversation. Be helpful, engaging, and maintain the conversational flow."""
        else:
            full_prompt = f"""User request: {user_request}

This appears to be the start of our conversation. Please respond helpfully and engage in natural conversation."""

        # Generate conversational response
        try:
            response = self._call_llm(self.system_prompt, full_prompt, temperature=0.8)
        except Exception as e:
            print(f"[ERROR] General agent error: {e}")
            response = "I'm having some trouble processing your request right now. Could you try rephrasing it or asking me something else?"

        # Update state with results
        state['generated_content'] = {
            'content': response,
            'type': 'general_conversation',
            'status': 'completed',
            'used_session_context': bool(conversation_history)
        }

        # Add agent response
        if 'agent_responses' not in state:
            state['agent_responses'] = []

        existing = [r for r in state['agent_responses'] if r.get('agent') == self.name]
        if not existing:
            state['agent_responses'].append({
                'agent': self.name,
                'action': 'general_conversation',
                'result': response,
                'timestamp': datetime.now().isoformat(),
                'conversation_context_used': bool(conversation_history)
            })

        print(f"[GENERAL] Response generated: {len(response)} characters")
        return state

    def chat(self, user_message: str, session_id: str = None) -> str:
        """
        Simple chat interface for direct conversation
        """
        # Create a minimal state for the conversation
        state = {
            'user_request': user_message,
            'session_id': session_id or f"chat_{datetime.now().timestamp()}",
            'session_context': {},
            'agent_responses': []
        }

        # Get or create session context
        if session_id:
            session_memory = self.session_memory.get_session_memory(session_id)
            state['session_context'] = {
                'conversation_history': session_memory.get('conversation_history', []),
                'user_preferences': session_memory.get('user_preferences', {})
            }

        # Process through the agent
        result_state = self.process(state)

        # Update session memory with this exchange
        if session_id:
            self.session_memory.add_conversation_entry(
                session_id=session_id,
                user_input=user_message,
                agent_response=result_state['generated_content']['content'],
                agent_name=self.name
            )

        return result_state['generated_content']['content']

    def start_chat_session(self):
        """
        Interactive chat session for testing the general agent
        """
        print("🤖 General AI Assistant - Chat Session Started!")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("Type 'clear' to clear conversation history.")
        print("=" * 50)

        session_id = f"interactive_chat_{datetime.now().timestamp()}"

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['exit', 'quit']:
                    print("👋 Goodbye! Thanks for chatting!")
                    break

                if user_input.lower() == 'clear':
                    # Clear session memory for this session
                    self.session_memory.clear_session_memory(session_id)
                    print("🧹 Conversation history cleared!")
                    continue

                if not user_input:
                    continue

                # Get response from general agent
                response = self.chat(user_input, session_id)

                print(f"\nAssistant: {response}\n")
                print("-" * 50)

            except KeyboardInterrupt:
                print("\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.")
