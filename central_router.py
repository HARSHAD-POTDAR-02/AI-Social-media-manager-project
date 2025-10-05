"""
Central Router for AI Social Media Manager
Uses Groq API for intelligent LLM-based routing of tasks to appropriate agents
"""

import json
from typing import Dict, List, Any, Optional
from groq import Groq
import re

class CentralRouter:
    """
    Central router that uses LLM to intelligently route tasks to appropriate agents
    """
    
    def __init__(self, groq_api_key: str):
        """
        Initialize the router with Groq API
        """
        self.client = Groq(api_key=groq_api_key)
        self.model = "openai/gpt-oss-120b" 
              
        # Define agent capabilities for context
        self.agent_capabilities = {
            "strategy": "Content strategy planning, trend research, content calendar creation, competitor analysis",
            "content": "Content creation, text generation, visual ideation, hashtag optimization, copywriting",
            "publishing": "Content scheduling, cross-platform publishing, optimal timing, queue management",
            "community": "Community management, real-time responses, sentiment analysis, customer queries",
            "listening": "Social listening, brand mentions monitoring, industry intelligence, influencer tracking",
            "analytics": "Performance analysis, ROI measurement, predictive analytics, reporting",
            "crisis": "Crisis management, issue detection, response coordination, reputation recovery",
            "compliance": "Brand safety, content moderation, legal compliance, risk assessment",
            "general": "General conversation, casual chat, questions, explanations, help with any topic"
        }
        
    def route(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route the user request to appropriate agent(s) using LLM
        """
        # Create the routing prompt
        routing_prompt = self._create_routing_prompt(user_request, context)
        
        try:
            # Call Groq API for routing decision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": routing_prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent routing
                max_tokens=800  # Increased for complex routing decisions
            )
            
            # Parse the response
            routing_decision = self._parse_routing_response(response.choices[0].message.content)
            
            # Validate that we have proper sequential agents for complex requests
            if routing_decision['workflow_type'] == 'sequential' and not routing_decision.get('secondary_agents'):
                print("Warning: Sequential workflow detected but no secondary agents found. Using enhanced fallback.")
                return self._enhanced_fallback_routing(user_request)
            
            # Add task decomposition for sequential workflows
            if routing_decision['workflow_type'] == 'sequential':
                routing_decision['agent_tasks'] = self._decompose_tasks(user_request, routing_decision)
            
            print(f"Router Decision: {json.dumps(routing_decision, indent=2)}")
            
            return routing_decision
            
        except Exception as e:
            print(f"Routing error: {str(e)}")
            # Use enhanced fallback for complex requests
            return self._enhanced_fallback_routing(user_request)
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the routing LLM
        """
        return """You are an intelligent task router for an AI Social Media Manager system.
        Your job is to analyze user requests and determine which agent(s) should handle them.
        
        Available agents and their capabilities:
        - strategy: Content strategy planning, trend research, content calendar, competitor analysis
        - content: Content creation, text generation, visual ideation, hashtag optimization
        - publishing: Content scheduling, cross-platform publishing, optimal timing
        - community: Community management, responses, sentiment analysis, customer queries
        - listening: Social listening, brand mentions, industry intelligence, influencer tracking
        - analytics: Performance analysis, ROI measurement, predictive analytics, reporting
        - crisis: Crisis management, issue detection, response coordination, reputation recovery
        - compliance: Brand safety, content moderation, legal compliance, risk assessment
        - general: General conversation, casual chat, questions, explanations, help with any topic
        
        CRITICAL: For complex multi-step requests, you MUST identify ALL required agents in the correct sequence.
        
        Workflow types:
        - direct: Single agent can handle the entire task
        - sequential: Multiple agents work in order (most common for complex requests)
        - parallel: Independent tasks that can run simultaneously
        
        RESPOND ONLY IN VALID JSON FORMAT:
        {
            "primary_agent": "first_agent_name",
            "workflow_type": "sequential",
            "reasoning": "Brief explanation",
            "secondary_agents": ["agent2", "agent3", "agent4"],
            "requires_human_review": false,
            "priority": "medium"
        }
        
        Example for complex request:
        "Analyze performance, create content, and schedule posts"
        {
            "primary_agent": "analytics",
            "workflow_type": "sequential",
            "reasoning": "Multi-step workflow: analyze first, then create content based on insights, then schedule",
            "secondary_agents": ["content", "publishing"],
            "requires_human_review": false,
            "priority": "medium"
        }"""
    
    def _create_routing_prompt(self, user_request: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Create the routing prompt with user request and context
        """
        prompt = f"User Request: {user_request}\n\n"
        
        if context:
            prompt += f"Additional Context:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        prompt += """Based on this request, determine the appropriate routing.
        Consider:
        1. The main task or goal
        2. Any subtasks that need to be completed
        3. Whether tasks can be parallelized
        4. If human review is needed for sensitive content
        5. The priority level based on urgency or impact
        
        Respond with the JSON routing decision."""
        
        return prompt
    
    def _decompose_tasks(self, user_request: str, routing_decision: Dict[str, Any]) -> Dict[str, str]:
        """
        Decompose complex request into specific tasks for each agent
        """
        try:
            agents = [routing_decision['primary_agent']] + routing_decision.get('secondary_agents', [])
            
            decompose_prompt = f"""Break down this complex request into specific tasks for each agent:

User Request: {user_request}

Agents in sequence: {agents}

For each agent, provide ONLY the specific task they should focus on, not the entire request.

Respond in JSON format:
{{
    "analytics": "Analyze Instagram performance from past 2 weeks and identify top-performing content types",
    "content": "Generate 5 reel ideas with scripts based on analytics insights",
    "publishing": "Schedule the 5 reels at optimal times over next week",
    "community": "Monitor comments and generate sentiment analysis report"
}}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a task decomposer. Break complex requests into specific, focused tasks for each agent."},
                    {"role": "user", "content": decompose_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response.choices[0].message.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            print(f"Task decomposition error: {e}")
        
        # Fallback: return empty dict
        return {}
    
    def _parse_routing_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a routing decision
        """
        try:
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                routing_json = json.loads(json_match.group())
                
                # Validate and normalize the response
                routing_decision = {
                    "primary_agent": routing_json.get("primary_agent", "strategy"),
                    "workflow_type": routing_json.get("workflow_type", "direct"),
                    "reasoning": routing_json.get("reasoning", ""),
                    "secondary_agents": routing_json.get("secondary_agents", []),
                    "parallel_tasks": routing_json.get("parallel_tasks", []),
                    "requires_human_review": routing_json.get("requires_human_review", False),
                    "priority": routing_json.get("priority", "medium")
                }
                
                return routing_decision
            else:
                # If no JSON found, try to parse the text response
                return self._parse_text_response(response)
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._parse_text_response(response)
        except Exception as e:
            print(f"Parsing error: {e}")
            return self._fallback_routing("")
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """
        Parse a text response when JSON parsing fails
        """
        response_lower = response.lower()
        
        # Determine primary agent based on keywords
        primary_agent = "strategy"  # Default
        
        agent_keywords = {
            "content": ["create", "write", "generate", "post", "caption", "copy"],
            "strategy": ["strategy", "plan", "calendar", "trend", "competitor"],
            "publishing": ["publish", "schedule", "post", "share", "upload"],
            "analytics": ["analyze", "report", "metrics", "performance", "roi"],
            "community": ["respond", "engage", "comment", "reply", "community"],
            "listening": ["monitor", "listen", "track", "mention", "sentiment"],
            "crisis": ["crisis", "urgent", "emergency", "issue", "problem"],
            "compliance": ["compliance", "legal", "safety", "moderate", "risk"]
        }
        
        for agent, keywords in agent_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                primary_agent = agent
                break
        
        # Determine workflow type
        workflow_type = "direct"
        if "parallel" in response_lower or "simultaneous" in response_lower:
            workflow_type = "parallel"
        elif "sequential" in response_lower or "then" in response_lower or "after" in response_lower:
            workflow_type = "sequential"
        
        return {
            "primary_agent": primary_agent,
            "workflow_type": workflow_type,
            "reasoning": "Parsed from text response",
            "secondary_agents": [],
            "parallel_tasks": [],
            "requires_human_review": "review" in response_lower or "approve" in response_lower,
            "priority": "high" if "urgent" in response_lower or "critical" in response_lower else "medium"
        }
    
    def _fallback_routing(self, user_request: str) -> Dict[str, Any]:
        """
        Fallback routing when LLM fails
        Uses more conservative routing that defaults to direct workflow
        """
        request_lower = user_request.lower()
        
        # Default to direct workflow for most cases
        workflow_type = "direct"
        secondary_agents = []
        requires_review = False
        priority = "medium"
        
        # Content-related requests
        content_keywords = ["create", "write", "generate", "post", "caption", "content"]
        if any(word in request_lower for word in content_keywords):
            # Check if scheduling is explicitly mentioned
            if "schedule" in request_lower or "publish" in request_lower:
                workflow_type = "sequential"
                secondary_agents = ["publishing"]
                reasoning = "Content creation with scheduling requires sequential workflow"
            else:
                reasoning = "Direct content creation task"
            
            return {
                "primary_agent": "content",
                "workflow_type": workflow_type,
                "reasoning": reasoning,
                "secondary_agents": secondary_agents,
                "parallel_tasks": [],
                "requires_human_review": requires_review,
                "priority": priority
            }
        
        # Analytics requests
        elif any(word in request_lower for word in ["analyze", "report", "metrics", "performance"]):
            return {
                "primary_agent": "analytics",
                "workflow_type": "direct",
                "reasoning": "Analytics task that can be handled by a single agent",
                "secondary_agents": [],
                "parallel_tasks": [],
                "requires_human_review": False,
                "priority": "medium"
            }
        
        # Crisis management
        elif any(word in request_lower for word in ["crisis", "urgent", "emergency"]):
            return {
                "primary_agent": "crisis",
                "workflow_type": "direct",
                "reasoning": "Crisis management task that requires immediate attention",
                "secondary_agents": [],
                "parallel_tasks": [],
                "requires_human_review": True,
                "priority": "critical"
            }
        
        # Community engagement
        elif any(word in request_lower for word in ["respond", "reply", "engage", "comment"]):
            return {
                "primary_agent": "community",
                "workflow_type": "direct",
                "reasoning": "Direct community engagement task",
                "secondary_agents": [],
                "parallel_tasks": [],
                "requires_human_review": False,
                "priority": "high"
            }
            
        # Strategy and planning
        elif any(word in request_lower for word in ["strategy", "plan", "calendar", "competitor"]):
            return {
                "primary_agent": "strategy",
                "workflow_type": "direct",
                "reasoning": "Strategic planning task",
                "secondary_agents": [],
                "parallel_tasks": [],
                "requires_human_review": False,
                "priority": "medium"
            }
        
        # Default to strategy agent for complex or unclear requests
        return {
            "primary_agent": "strategy",
            "workflow_type": "direct",
            "reasoning": "Default routing to strategy agent",
            "secondary_agents": [],
            "parallel_tasks": [],
            "requires_human_review": False,
            "priority": "medium"
        }
    
    def _enhanced_fallback_routing(self, user_request: str) -> Dict[str, Any]:
        """
        Enhanced fallback routing for complex multi-step requests
        """
        request_lower = user_request.lower()
        
        # Detect complex multi-step workflows
        steps = []
        
        # Check for analytics/performance analysis
        if any(word in request_lower for word in ["analyze", "performance", "metrics", "insights", "data"]):
            steps.append("analytics")
        
        # Check for content creation
        if any(word in request_lower for word in ["create", "generate", "write", "content", "post", "reel", "script"]):
            steps.append("content")
        
        # Check for publishing/scheduling
        if any(word in request_lower for word in ["schedule", "publish", "post", "optimal time"]):
            steps.append("publishing")
        
        # Check for community/sentiment monitoring
        if any(word in request_lower for word in ["monitor", "comments", "sentiment", "engagement", "discussion"]):
            steps.append("community")
        
        # Check for listening/social monitoring
        if any(word in request_lower for word in ["listen", "mentions", "track", "monitor"]):
            steps.append("listening")
        
        # Remove duplicates while preserving order
        unique_steps = []
        for step in steps:
            if step not in unique_steps:
                unique_steps.append(step)
        
        if len(unique_steps) > 1:
            return {
                "primary_agent": unique_steps[0],
                "workflow_type": "sequential",
                "reasoning": f"Complex multi-step workflow detected with {len(unique_steps)} agents: {', '.join(unique_steps)}",
                "secondary_agents": unique_steps[1:],
                "parallel_tasks": [],
                "requires_human_review": "approval" in request_lower or "review" in request_lower,
                "priority": "high" if "urgent" in request_lower else "medium"
            }
        elif len(unique_steps) == 1:
            return {
                "primary_agent": unique_steps[0],
                "workflow_type": "direct",
                "reasoning": f"Single-step workflow for {unique_steps[0]} agent",
                "secondary_agents": [],
                "parallel_tasks": [],
                "requires_human_review": False,
                "priority": "medium"
            }
        else:
            # Fallback to strategy for unclear requests
            return {
                "primary_agent": "strategy",
                "workflow_type": "direct",
                "reasoning": "Unclear request, defaulting to strategy agent",
                "secondary_agents": [],
                "parallel_tasks": [],
                "requires_human_review": False,
                "priority": "medium"
            }
    
    def analyze_complexity(self, user_request: str) -> Dict[str, Any]:
        """
        Analyze the complexity of a request to determine if parallel execution is beneficial
        """
        prompt = f"""Analyze this request and determine if it contains multiple independent tasks that could be executed in parallel:

Request: {user_request}

Identify:
1. Independent tasks that don't depend on each other
2. Tasks that must be done sequentially
3. Estimated complexity (simple/moderate/complex)

Respond in JSON format:
{{
    "independent_tasks": ["task1", "task2"],
    "sequential_tasks": ["task1", "task2"],
    "complexity": "simple|moderate|complex",
    "parallel_benefit": true/false
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a task complexity analyzer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
        except Exception as e:
            print(f"Complexity analysis error: {e}")
        
        return {
            "independent_tasks": [],
            "sequential_tasks": [user_request],
            "complexity": "moderate",
            "parallel_benefit": False
        }

if __name__ == "__main__":
    # Example usage
    import os
    
    # Get API key from environment
    groq_api_key = os.getenv("GROQ_API_KEY", "your-api-key-here")
    
    # Initialize router
    router = CentralRouter(groq_api_key)
    
    # Test routing decisions
    test_requests = [
        "Create a social media strategy for launching a new product",
        "Analyze last month's Instagram performance",
        "Respond to negative comments on our latest post",
        "Schedule posts for next week across all platforms",
        "There's a crisis! Customers are complaining about our service",
        "Create content calendar and write posts for the upcoming campaign"
    ]
    
    for request in test_requests:
        print(f"\n{'='*50}")
        print(f"Request: {request}")
        print(f"{'='*50}")
        decision = router.route(request)
        print(f"Routing: {decision['primary_agent']} ({decision['workflow_type']})")
        print(f"Reasoning: {decision['reasoning']}")
