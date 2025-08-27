"""
Content Agent for AI Social Media Manager
Handles content creation, text generation, and visual ideation
"""

from typing import Dict, Any, List
import os
from groq import Groq
from langgraph.graph import MessageGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


class ContentAgent:
    """
    Content agent for creating social media content with internal reflection (generate <-> critique) loop
    """

    def __init__(self):
        print("Initializing Content Agent")
        self.name = "content"
        # LLM client for internal generation/critique
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY is not set. Content generation will fail without it.")
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = "openai/gpt-oss-120b"
        self.max_reflections = 5

    # ------------------------
    # Internal LLM helpers
    # ------------------------
    def _groq_chat(self, messages: List[Dict[str, str]], temperature: float = 0.5, max_tokens: int = 800) -> str:
        if not self.client:
            # Fallback to deterministic stub for dev without API
            return "[LLM unavailable] Placeholder content."
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"Groq generation error: {e}")
            return "[Error] Unable to generate content right now."

    # ------------------------
    # Reflection graph builder
    # ------------------------
    def _build_reflection_graph(self, max_iters: int) -> MessageGraph:
        builder = MessageGraph()

        def _count_critiques(state: List[BaseMessage]) -> int:
            return sum(1 for m in state if isinstance(m, AIMessage) and str(m.content).strip().startswith("CRITIQUE #"))

        def _count_drafts(state: List[BaseMessage]) -> int:
            return sum(1 for m in state if isinstance(m, AIMessage) and str(m.content).strip().startswith("DRAFT #"))

        def _last_draft(state: List[BaseMessage]) -> str:
            for m in reversed(state):
                if isinstance(m, AIMessage) and str(m.content).strip().startswith("DRAFT #"):
                    # Remove the heading line to get pure content
                    content = str(m.content)
                    parts = content.split("\n", 1)
                    return parts[1] if len(parts) > 1 else content
            return ""

        def generation_node(state: List[BaseMessage]) -> List[BaseMessage]:
            draft_no = _count_drafts(state) + 1

            system_prompt = (
                "You are a senior social media copywriter. Generate concise, high-impact social content. "
                "Follow brand voice and platform norms. If a critique is provided, revise accordingly. "
                "Return only the content draft without meta commentary. Include relevant hashtags when appropriate."
            )

            # Build conversation for the generator
            groq_messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

            # Convert state into compact prompt context
            original_brief = ""
            for m in state:
                if isinstance(m, HumanMessage):
                    original_brief = m.content
                    break

            latest_critique = None
            for m in reversed(state):
                if isinstance(m, AIMessage) and str(m.content).strip().startswith("CRITIQUE #"):
                    latest_critique = str(m.content)
                    break

            prev_draft = _last_draft(state)

            if latest_critique:
                user_content = (
                    f"Original brief:\n{original_brief}\n\n"
                    f"Latest critique to apply:\n{latest_critique}\n\n"
                )
                if prev_draft:
                    user_content += f"Previous draft (revise this):\n{prev_draft}\n\n"
                user_content += "Revise the draft accordingly."
            elif prev_draft:
                user_content = (
                    f"Original brief:\n{original_brief}\n\n"
                    f"Previous draft (revise this):\n{prev_draft}\n\n"
                    f"Revise the draft accordingly."
                )
            else:
                user_content = original_brief

            groq_messages.append({"role": "user", "content": user_content})

            draft = self._groq_chat(groq_messages, temperature=0.6, max_tokens=900)
            draft = draft.strip()

            return [AIMessage(content=f"DRAFT #{draft_no}\n{draft}")]

        def reflection_node(state: List[BaseMessage]) -> List[BaseMessage]:
            critique_no = _count_critiques(state) + 1
            latest_draft = _last_draft(state)

            system_prompt = (
                "You are a professional content critic and editor. Provide actionable, concise critique to improve the draft. "
                "Focus on clarity, tone, hook, structure, call-to-action, platform fit, and hashtags. "
                "Do NOT rewrite the full draft. Instead, provide 5-8 bullet points of improvements and, where necessary, suggest specific wording fragments."
            )

            groq_messages: List[Dict[str, str]] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Critique the following draft:\n\n{latest_draft}"},
            ]

            critique = self._groq_chat(groq_messages, temperature=0.3, max_tokens=700)
            critique = critique.strip()

            return [AIMessage(content=f"CRITIQUE #{critique_no}\n{critique}")]

        def should_continue(state: List[BaseMessage]):
            # Stop after max_iters critiques
            if _count_critiques(state) >= max_iters:
                return END
            return "reflect"

        builder.add_node("generate", generation_node)
        builder.add_node("reflect", reflection_node)
        builder.set_entry_point("generate")
        builder.add_conditional_edges("generate", should_continue)
        builder.add_edge("reflect", "generate")
        return builder.compile()

    # ------------------------
    # Public API
    # ------------------------
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content creation tasks via an internal reflection loop (MessageGraph).
        - Generates initial content.
        - Iteratively critiques and refines up to self.max_reflections times.
        - Optionally applies user feedback (if provided in state['context_data']['content_feedback']).
        """
        # Mark current node for the router
        state["current_agent"] = self.name
        print(f"Content Agent processing: {state.get('user_request', '')}")
        print("CONTENT AGENT IS PROCESSING")

        # Build the reflection graph
        graph = self._build_reflection_graph(self.max_reflections)

        # Build the initial brief from state
        ctx = state.get("context_data", {}) or {}
        platform = ctx.get("platform", "")
        tone = ctx.get("tone", "")
        audience = ctx.get("audience", "")
        extras = ctx.get("constraints", "")
        feedback = ctx.get("content_feedback", "")

        brief_lines = [
            f"Task: {state.get('user_request', '').strip()}",
        ]
        if platform:
            brief_lines.append(f"Platform: {platform}")
        if tone:
            brief_lines.append(f"Tone: {tone}")
        if audience:
            brief_lines.append(f"Audience: {audience}")
        if extras:
            brief_lines.append(f"Constraints: {extras}")
        if feedback:
            brief_lines.append(f"Feedback to apply: {feedback}")
        brief_lines.append("Output: a polished social post/caption with optional hashtags; no meta commentary.")
        initial_brief = "\n".join(brief_lines)

        # Seed messages with overall content guidelines + user brief
        messages: List[BaseMessage] = [
            SystemMessage(content=(
                "You are assisting with social media content creation. "
                "Follow instructions precisely. Keep output concise and platform-appropriate."
            )),
            HumanMessage(content=initial_brief),
        ]

        # If a previous draft is provided via context, seed it so the loop can revise it
        prev_draft_ctx = ctx.get("previous_draft")
        if prev_draft_ctx:
            messages.append(AIMessage(content=f"DRAFT #BASE\n{prev_draft_ctx}"))

        # Run reflection loop
        messages = graph.invoke(messages)

        # Extract final draft (the last DRAFT message)
        final_draft = ""
        iterations = 0
        for m in reversed(messages):
            if isinstance(m, AIMessage) and str(m.content).strip().startswith("DRAFT #"):
                content = str(m.content)
                parts = content.split("\n", 1)
                final_draft = parts[1] if len(parts) > 1 else content
                break
        iterations = sum(1 for m in messages if isinstance(m, AIMessage) and str(m.content).strip().startswith("CRITIQUE #"))

        # Optional: apply user feedback within the same ContentAgent call (extra quick polish)
        if feedback and not prev_draft_ctx:
            print("Applying user feedback within ContentAgent...")
            feedback_graph = self._build_reflection_graph(max_iters=2)
            feedback_messages: List[BaseMessage] = [
                SystemMessage(content=(
                    "You will revise a social content draft based on explicit user feedback."
                )),
                HumanMessage(content=f"User feedback to apply:\n{feedback}"),
                AIMessage(content=f"DRAFT #BASE\n{final_draft}"),
            ]
            feedback_messages = feedback_graph.invoke(feedback_messages)
            for m in reversed(feedback_messages):
                if isinstance(m, AIMessage) and str(m.content).strip().startswith("DRAFT #"):
                    content = str(m.content)
                    parts = content.split("\n", 1)
                    final_draft = parts[1] if len(parts) > 1 else content
                    break
            iterations += 2  # approximate extra refinement rounds

        # Populate state
        state['generated_content'] = {
            'content': final_draft or '[No content generated]',
            'iterations': iterations,
        }

        # Optionally enrich context when in sequential mode
        current_task = {}
        if state.get('workflow_type') == 'sequential':
            current_idx = state.get('sequence_index', 0)
            if state.get('task_decomposition'):
                tasks = state['task_decomposition']
                if 0 <= current_idx < len(tasks):
                    current_task = tasks[current_idx]
            state['context_data'].update({
                'content_results': state['generated_content'],
                'current_task': current_task.get('task', 'content_creation'),
                'status': 'completed'
            })

        state['agent_responses'].append({
            'agent': self.name,
            'action': 'content_creation_reflection',
            'result': 'Content generated and refined',
            'iterations': iterations,
        })

        return state