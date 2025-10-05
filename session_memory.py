"""
Session-Based Memory Manager for AI Social Media Manager
Provides centralized, dictionary-based memory storage for all agents to share conversation context
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict

class SessionMemoryManager:
    """
    Centralized session-based memory manager for all agents.
    Maintains conversation context and history in a simple dictionary format.
    """

    def __init__(self, persistence_file: str = "session_memory.json"):
        """
        Initialize the session memory manager

        Args:
            persistence_file: Optional file path for persisting memory across sessions
        """
        self.persistence_file = persistence_file
        self.memory_store = self._load_memory_from_file() if os.path.exists(persistence_file) else {}
        self.max_memory_items = 100  # Limit memory to prevent excessive growth
        self.max_context_length = 2000  # Max characters per context entry

    def _load_memory_from_file(self) -> Dict[str, Any]:
        """Load memory from persistence file"""
        try:
            with open(self.persistence_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load memory file: {e}")
            return {}

    def _save_memory_to_file(self):
        """Save memory to persistence file"""
        try:
            with open(self.persistence_file, 'w') as f:
                json.dump(self.memory_store, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Could not save memory file: {e}")

    def get_session_memory(self, session_id: str) -> Dict[str, Any]:
        """
        Get memory for a specific session

        Args:
            session_id: Unique identifier for the session

        Returns:
            Dictionary containing session memory data
        """
        if session_id not in self.memory_store:
            self.memory_store[session_id] = {
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'conversation_history': [],
                'context_summary': {},
                'agent_interactions': {},
                'user_preferences': {},
                'key_topics': [],
                'important_facts': [],
                'session_metadata': {}
            }

        return self.memory_store[session_id]

    def update_session_memory(self, session_id: str, updates: Dict[str, Any]):
        """
        Update memory for a specific session

        Args:
            session_id: Unique identifier for the session
            updates: Dictionary of updates to apply to session memory
        """
        session_memory = self.get_session_memory(session_id)

        # Apply updates
        for key, value in updates.items():
            if key == 'conversation_history' and isinstance(value, dict):
                # Handle new conversation entry
                session_memory['conversation_history'].append(value)
            elif key == 'context_summary' and isinstance(value, dict):
                # Merge context summary
                session_memory['context_summary'].update(value)
            elif key in ['agent_interactions', 'user_preferences'] and isinstance(value, dict):
                # Merge these nested dictionaries
                session_memory[key].update(value)
            elif key == 'key_topics' and isinstance(value, list):
                # Add new topics, avoid duplicates
                for topic in value:
                    if topic not in session_memory['key_topics']:
                        session_memory['key_topics'].append(topic)
            elif key == 'important_facts' and isinstance(value, list):
                # Add new facts, avoid duplicates
                for fact in value:
                    if fact not in session_memory['important_facts']:
                        session_memory['important_facts'].append(fact)
            else:
                session_memory[key] = value

        # Update timestamp
        session_memory['last_updated'] = datetime.now().isoformat()

        # Truncate conversation history if too long
        if len(session_memory['conversation_history']) > self.max_memory_items:
            session_memory['conversation_history'] = session_memory['conversation_history'][-self.max_memory_items:]

        # Truncate context entries if too long
        for key in ['context_summary', 'agent_interactions', 'user_preferences']:
            if isinstance(session_memory.get(key), dict):
                for sub_key, sub_value in session_memory[key].items():
                    if isinstance(sub_value, str) and len(sub_value) > self.max_context_length:
                        session_memory[key][sub_key] = sub_value[:self.max_context_length] + "..."

        # Save to file periodically
        self._save_memory_to_file()

    def add_conversation_entry(self, session_id: str, user_input: str, agent_response: str,
                             agent_name: str, metadata: Dict[str, Any] = None):
        """
        Add a conversation entry to session memory

        Args:
            session_id: Unique identifier for the session
            user_input: The user's input message
            agent_response: The agent's response
            agent_name: Name of the agent that responded
            metadata: Additional metadata about the interaction
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'agent_response': agent_response,
            'agent_name': agent_name,
            'metadata': metadata or {}
        }

        self.update_session_memory(session_id, {
            'conversation_history': entry
        })

        # Also update agent interactions
        agent_key = f"{agent_name}_interactions"
        current_count = self.memory_store[session_id]['agent_interactions'].get(agent_key, 0)
        self.update_session_memory(session_id, {
            'agent_interactions': {agent_key: current_count + 1}
        })

    def get_conversation_context(self, session_id: str, max_entries: int = 10) -> str:
        """
        Get recent conversation context as formatted text

        Args:
            session_id: Unique identifier for the session
            max_entries: Maximum number of recent entries to include

        Returns:
            Formatted conversation context string
        """
        session_memory = self.get_session_memory(session_id)

        if not session_memory['conversation_history']:
            return "No previous conversation context available."

        # Get recent entries
        recent_entries = session_memory['conversation_history'][-max_entries:]

        context_parts = ["Recent Conversation Context:"]
        for i, entry in enumerate(recent_entries, 1):
            context_parts.append(f"\n{i}. User: {entry['user_input']}")
            context_parts.append(f"   {entry['agent_name']}: {entry['agent_response'][:200]}...")
            if entry['metadata']:
                context_parts.append(f"   Metadata: {entry['metadata']}")

        return "\n".join(context_parts)

    def get_agent_context(self, session_id: str, agent_name: str) -> Dict[str, Any]:
        """
        Get context specific to an agent for the current session

        Args:
            session_id: Unique identifier for the session
            agent_name: Name of the agent requesting context

        Returns:
            Dictionary containing agent-specific context
        """
        session_memory = self.get_session_memory(session_id)

        # Get agent-specific data
        agent_context = {
            'session_id': session_id,
            'conversation_history': session_memory['conversation_history'],
            'key_topics': session_memory['key_topics'],
            'important_facts': session_memory['important_facts'],
            'user_preferences': session_memory['user_preferences'],
            'previous_agent_responses': []
        }

        # Add recent agent interactions
        for entry in session_memory['conversation_history']:
            if entry['agent_name'] != agent_name:
                agent_context['previous_agent_responses'].append({
                    'agent': entry['agent_name'],
                    'response': entry['agent_response'],
                    'timestamp': entry['timestamp']
                })

        return agent_context

    def extract_key_insights(self, session_id: str) -> Dict[str, Any]:
        """
        Extract key insights and patterns from the session memory

        Args:
            session_id: Unique identifier for the session

        Returns:
            Dictionary containing extracted insights
        """
        session_memory = self.get_session_memory(session_id)

        insights = {
            'session_duration': self._calculate_session_duration(session_memory),
            'most_active_agent': self._get_most_active_agent(session_memory),
            'conversation_topics': session_memory['key_topics'][:5],  # Top 5 topics
            'user_engagement_level': self._assess_engagement_level(session_memory),
            'key_preferences': list(session_memory['user_preferences'].keys())[:3]
        }

        return insights

    def _calculate_session_duration(self, session_memory: Dict[str, Any]) -> str:
        """Calculate how long the session has been active"""
        created_at = datetime.fromisoformat(session_memory['created_at'])
        duration = datetime.now() - created_at

        if duration.days > 0:
            return f"{duration.days} days"
        elif duration.seconds > 3600:
            return f"{duration.seconds // 3600} hours"
        else:
            return f"{duration.seconds // 60} minutes"

    def _get_most_active_agent(self, session_memory: Dict[str, Any]) -> str:
        """Find the most frequently used agent in this session"""
        agent_counts = {}

        for entry in session_memory['conversation_history']:
            agent = entry['agent_name']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        return max(agent_counts.items(), key=lambda x: x[1])[0] if agent_counts else "None"

    def _assess_engagement_level(self, session_memory: Dict[str, Any]) -> str:
        """Assess user engagement level based on conversation patterns"""
        history = session_memory['conversation_history']

        if len(history) < 3:
            return "Low - Just starting"
        elif len(history) < 10:
            return "Medium - Building conversation"
        else:
            return "High - Active conversation"

    def clear_session_memory(self, session_id: str):
        """
        Clear memory for a specific session

        Args:
            session_id: Unique identifier for the session to clear
        """
        if session_id in self.memory_store:
            del self.memory_store[session_id]
            self._save_memory_to_file()

    def clear_old_sessions(self, max_age_days: int = 7):
        """
        Clear sessions older than specified days

        Args:
            max_age_days: Maximum age in days for sessions to keep
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        sessions_to_remove = []

        for session_id, session_data in self.memory_store.items():
            try:
                created_at = datetime.fromisoformat(session_data['created_at'])
                if created_at < cutoff_date:
                    sessions_to_remove.append(session_id)
            except (ValueError, KeyError):
                # Remove sessions with invalid timestamps
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.memory_store[session_id]

        if sessions_to_remove:
            self._save_memory_to_file()
            print(f"Cleared {len(sessions_to_remove)} old sessions")

    def get_session_summary(self, session_id: str) -> str:
        """
        Get a human-readable summary of the session

        Args:
            session_id: Unique identifier for the session

        Returns:
            Formatted summary string
        """
        session_memory = self.get_session_memory(session_id)
        insights = self.extract_key_insights(session_id)

        summary = f"""
Session Summary ({session_id}):
- Duration: {insights['session_duration']}
- Most Active Agent: {insights['most_active_agent']}
- Engagement Level: {insights['user_engagement_level']}
- Conversation Topics: {', '.join(insights['conversation_topics'])}
- Key Preferences: {', '.join(insights['user_preferences'])}
- Total Interactions: {len(session_memory['conversation_history'])}
- Last Updated: {session_memory['last_updated']}
        """.strip()

        return summary

# Global session memory manager instance
_session_memory_manager = None

def get_session_memory_manager() -> SessionMemoryManager:
    """Get or create the global session memory manager instance"""
    global _session_memory_manager
    if _session_memory_manager is None:
        _session_memory_manager = SessionMemoryManager()
    return _session_memory_manager

def reset_session_memory_manager():
    """Reset the global session memory manager (for testing)"""
    global _session_memory_manager
    _session_memory_manager = None
