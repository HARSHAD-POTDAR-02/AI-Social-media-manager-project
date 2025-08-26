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
            "influencer": "Influencer discovery, partnership management, campaign tracking",
            "paid_social": "Paid advertising, campaign optimization, audience targeting, budget management",
            "compliance": "Brand safety, content moderation, legal compliance, risk assessment"
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
                max_tokens=500
            )
            
            # Parse the response
            routing_decision = self._parse_routing_response(response.choices[0].message.content)
            
            print(f"Router Decision: {json.dumps(routing_decision, indent=2)}")
            
            return routing_decision
            
        except Exception as e:
            print(f"Routing error: {str(e)}")
            # Fallback to basic routing
            return self._fallback_routing(user_request)
    
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
        - influencer: Influencer discovery, partnership management, campaign tracking
        - paid_social: Paid advertising, campaign optimization, audience targeting, budget management
        - compliance: Brand safety, content moderation, legal compliance, risk assessment
        
        Decision Making Process:
        1. First, analyze if the request is a direct query that can be handled by a single agent
        2. If multiple tasks are present, determine if they are related and can be handled by the same agent
        3. Only use sequential workflow if tasks must happen in order (e.g., create content then publish it)
        4. Only use parallel workflow for completely independent tasks that can be done simultaneously
        
        Workflow types:
        - direct: Single agent can handle the entire task (use this when the request is focused on one specific action)
        - sequential: Multiple agents need to work in sequence (e.g., strategy -> content -> publishing)
        - parallel: Multiple independent tasks that can be done simultaneously
        
        You must respond in JSON format with the following structure:
        {
            "primary_agent": "agent_name",
            "workflow_type": "direct|sequential|parallel",
            "reasoning": "Detailed explanation of routing decision, including why you chose direct/sequential/parallel",
            "secondary_agents": ["agent1", "agent2"],  // Only include if workflow_type is sequential/parallel
            "parallel_tasks": [  // Only for parallel workflows
                {"agent": "agent_name", "task": "specific task description"}
            ],
            "requires_human_review": true/false,  // Set to true for sensitive content or high-impact decisions
            "priority": "low|medium|high|critical"  // Based on urgency and business impact
        }
        
        Examples:
        
        User: "Create a post about our new product"
        {
            "primary_agent": "content",
            "workflow_type": "direct",
            "reasoning": "Simple content creation task that only requires the content agent",
            "secondary_agents": [],
            "parallel_tasks": [],
            "requires_human_review": false,
            "priority": "medium"
        }
        
        User: "Create and schedule a post about our new product"
        {
            "primary_agent": "content",
            "workflow_type": "sequential",
            "reasoning": "Content needs to be created first, then scheduled",
            "secondary_agents": ["publishing"],
            "parallel_tasks": [],
            "requires_human_review": false,
            "priority": "medium"
        }
        
        User: "Analyze our performance and create a report"
        {
            "primary_agent": "analytics",
            "workflow_type": "direct",
            "reasoning": "Analytics agent can both analyze and generate reports",
            "secondary_agents": [],
            "parallel_tasks": [],
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
            "influencer": ["influencer", "partnership", "collaboration", "ambassador"],
            "paid_social": ["ad", "advertis", "campaign", "paid", "promotion"],
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
