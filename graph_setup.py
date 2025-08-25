"""
AI Social Media Manager - LangGraph Architecture
Main graph setup file containing the complete workflow and agent connections
"""

from typing import TypedDict, Literal, List, Dict, Any, Optional, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from langgraph.prebuilt import ToolExecutor, ToolInvocation
import operator
from datetime import datetime

# Import all agent modules
from agents.orchestrator_agent import OrchestratorAgent
from agents.strategy_agent import StrategyAgent
from agents.content_agent import ContentAgent
from agents.publishing_agent import PublishingAgent
from agents.community_agent import CommunityAgent
from agents.listening_agent import ListeningAgent
from agents.analytics_agent import AnalyticsAgent
from agents.crisis_agent import CrisisAgent
from agents.influencer_agent import InfluencerAgent
from agents.paid_social_agent import PaidSocialAgent
from agents.compliance_agent import ComplianceAgent
from agents.parallel_coordinator_agent import ParallelCoordinatorAgent
from central_router import CentralRouter

# Define the state structure for the graph
class GraphState(TypedDict):
    """
    State structure for the social media manager graph
    """
    # Core state fields
    user_request: str
    current_agent: str
    workflow_type: Literal["sequential", "parallel", "direct"]
    
    # Task and context management
    task_decomposition: List[Dict[str, Any]]
    parallel_tasks: List[Dict[str, Any]]
    context_data: Dict[str, Any]
    
    # Content and strategy fields
    content_strategy: Optional[Dict[str, Any]]
    generated_content: Optional[Dict[str, Any]]
    compliance_status: Optional[Dict[str, Any]]
    
    # Workflow control
    workflow_step: int
    approval_needed: bool
    human_feedback: Optional[str]
    
    # Results and responses
    agent_responses: Annotated[List[Dict[str, Any]], operator.add]
    final_response: Optional[str]
    
    # Error handling
    error_state: Optional[Dict[str, Any]]
    retry_count: int
    
    # Monitoring and analytics
    performance_metrics: Dict[str, Any]
    timestamp: datetime
    session_id: str
    
    # Crisis management
    crisis_level: Optional[Literal["low", "medium", "high", "critical"]]
    crisis_response_plan: Optional[Dict[str, Any]]

class SocialMediaManagerGraph:
    """
    Main graph class for the AI Social Media Manager
    """
    
    def __init__(self, groq_api_key: str):
        """
        Initialize the graph with all agents and connections
        """
        # Initialize the central router
        self.router = CentralRouter(groq_api_key)
        
        # Initialize all agents
        self.orchestrator = OrchestratorAgent()
        self.strategy_agent = StrategyAgent()
        self.content_agent = ContentAgent()
        self.publishing_agent = PublishingAgent()
        self.community_agent = CommunityAgent()
        self.listening_agent = ListeningAgent()
        self.analytics_agent = AnalyticsAgent()
        self.crisis_agent = CrisisAgent()
        self.influencer_agent = InfluencerAgent()
        self.paid_social_agent = PaidSocialAgent()
        self.compliance_agent = ComplianceAgent()
        self.parallel_coordinator = ParallelCoordinatorAgent()
        
        # Create the state graph
        self.workflow = StateGraph(GraphState)
        
        # Add all nodes to the graph
        self._add_nodes()
        
        # Add all edges and conditional routing
        self._add_edges()
        
        # Compile the graph with checkpointing
        self.checkpointer = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.checkpointer)
    
    def _add_nodes(self):
        """
        Add all agent nodes to the graph
        """
        # Entry point and orchestration
        self.workflow.add_node("user_input", self.process_user_input)
        self.workflow.add_node("orchestrator", self.orchestrator.process)
        self.workflow.add_node("route_request", self.route_request)
        
        # Core agents
        self.workflow.add_node("strategy", self.strategy_agent.process)
        self.workflow.add_node("content", self.content_agent.process)
        self.workflow.add_node("publishing", self.publishing_agent.process)
        self.workflow.add_node("community", self.community_agent.process)
        self.workflow.add_node("listening", self.listening_agent.process)
        self.workflow.add_node("analytics", self.analytics_agent.process)
        
        # Specialized agents
        self.workflow.add_node("crisis", self.crisis_agent.process)
        self.workflow.add_node("influencer", self.influencer_agent.process)
        self.workflow.add_node("paid_social", self.paid_social_agent.process)
        self.workflow.add_node("compliance", self.compliance_agent.process)
        
        # Parallel execution
        self.workflow.add_node("parallel_coordinator", self.parallel_coordinator.process)
        self.workflow.add_node("parallel_execution", self.execute_parallel_tasks)
        self.workflow.add_node("aggregate_results", self.aggregate_parallel_results)
        
        # Human-in-the-loop nodes
        self.workflow.add_node("human_review", self.human_review_checkpoint)
        self.workflow.add_node("apply_human_feedback", self.apply_human_feedback)
        
        # Error handling
        self.workflow.add_node("error_handler", self.handle_error)
        
        # Final nodes
        self.workflow.add_node("prepare_response", self.prepare_final_response)
        self.workflow.add_node("complete", self.complete_workflow)
    
    def _add_edges(self):
        """
        Add all edges and conditional routing to the graph
        """
        # Set entry point
        self.workflow.set_entry_point("user_input")
        
        # From user input to orchestrator
        self.workflow.add_edge("user_input", "orchestrator")
        
        # From orchestrator to routing
        self.workflow.add_edge("orchestrator", "route_request")
        
        # Conditional routing based on intent classification
        self.workflow.add_conditional_edges(
            "route_request",
            self.determine_workflow_path,
            {
                "strategy": "strategy",
                "content": "content",
                "publishing": "publishing",
                "community": "community",
                "listening": "listening",
                "analytics": "analytics",
                "crisis": "crisis",
                "influencer": "influencer",
                "paid_social": "paid_social",
                "compliance": "compliance",
                "parallel": "parallel_coordinator",
                "sequential": "strategy",  # Start sequential workflow with strategy
            }
        )
        
        # Sequential workflow edges
        self.workflow.add_conditional_edges(
            "strategy",
            self.check_human_review,
            {
                "human_review": "human_review",
                "continue": "content",
                "error": "error_handler"
            }
        )
        
        self.workflow.add_conditional_edges(
            "content",
            self.check_human_review,
            {
                "human_review": "human_review",
                "continue": "compliance",
                "error": "error_handler"
            }
        )
        
        self.workflow.add_conditional_edges(
            "compliance",
            self.check_compliance,
            {
                "passed": "publishing",
                "failed": "content",  # Return to content for revision
                "error": "error_handler"
            }
        )
        
        self.workflow.add_edge("publishing", "listening")
        self.workflow.add_edge("listening", "prepare_response")
        
        # Analytics workflows
        self.workflow.add_conditional_edges(
            "analytics",
            self.determine_analytics_output,
            {
                "report": "prepare_response",
                "strategy_input": "strategy",
                "content_optimization": "content",
                "error": "error_handler"
            }
        )
        
        # Community management workflows
        self.workflow.add_conditional_edges(
            "community",
            self.determine_community_action,
            {
                "response": "prepare_response",
                "crisis": "crisis",
                "monitoring": "listening",
                "error": "error_handler"
            }
        )
        
        # Crisis management workflows
        self.workflow.add_conditional_edges(
            "crisis",
            self.assess_crisis_level,
            {
                "low": "prepare_response",
                "high": "human_review",
                "critical": "human_review",
                "error": "error_handler"
            }
        )
        
        # Parallel execution edges
        self.workflow.add_edge("parallel_coordinator", "parallel_execution")
        self.workflow.add_edge("parallel_execution", "aggregate_results")
        self.workflow.add_edge("aggregate_results", "prepare_response")
        
        # Human review edges
        self.workflow.add_edge("human_review", "apply_human_feedback")
        self.workflow.add_conditional_edges(
            "apply_human_feedback",
            self.route_after_human_feedback,
            {
                "retry": "route_request",
                "continue": "prepare_response",
                "error": "error_handler"
            }
        )
        
        # Error handling edges
        self.workflow.add_conditional_edges(
            "error_handler",
            self.determine_error_recovery,
            {
                "retry": "route_request",
                "human": "human_review",
                "end": "complete"
            }
        )
        
        # Final edges
        self.workflow.add_edge("prepare_response", "complete")
        self.workflow.add_edge("complete", END)
    
    def process_user_input(self, state: GraphState) -> GraphState:
        """
        Process initial user input and prepare state
        """
        print(f"Processing user input: {state['user_request']}")
        state['timestamp'] = datetime.now()
        state['workflow_step'] = 0
        state['retry_count'] = 0
        state['agent_responses'] = []
        return state
    
    def route_request(self, state: GraphState) -> GraphState:
        """
        Use the central router to determine which agent(s) to invoke
        """
        routing_decision = self.router.route(state['user_request'], state.get('context_data', {}))
        state['current_agent'] = routing_decision['primary_agent']
        state['workflow_type'] = routing_decision['workflow_type']
        
        if routing_decision['workflow_type'] == 'parallel':
            state['parallel_tasks'] = routing_decision['parallel_tasks']
        
        print(f"Routing to: {routing_decision['primary_agent']} via {routing_decision['workflow_type']} workflow")
        return state
    
    def determine_workflow_path(self, state: GraphState) -> str:
        """
        Determine the next node based on routing decision
        """
        if state['workflow_type'] == 'parallel':
            return 'parallel'
        elif state['workflow_type'] == 'sequential':
            return 'sequential'
        else:
            # Direct routing to specific agent
            return state['current_agent']
    
    def check_human_review(self, state: GraphState) -> str:
        """
        Check if human review is needed
        """
        if state.get('approval_needed', False):
            return 'human_review'
        elif state.get('error_state'):
            return 'error'
        else:
            return 'continue'
    
    def check_compliance(self, state: GraphState) -> str:
        """
        Check compliance status
        """
        if state.get('error_state'):
            return 'error'
        elif state.get('compliance_status', {}).get('passed', False):
            return 'passed'
        else:
            return 'failed'
    
    def determine_analytics_output(self, state: GraphState) -> str:
        """
        Determine analytics workflow output
        """
        if state.get('error_state'):
            return 'error'
        
        analytics_type = state.get('context_data', {}).get('analytics_type', 'report')
        return analytics_type
    
    def determine_community_action(self, state: GraphState) -> str:
        """
        Determine community management action
        """
        if state.get('error_state'):
            return 'error'
        
        action = state.get('context_data', {}).get('community_action', 'response')
        return action
    
    def assess_crisis_level(self, state: GraphState) -> str:
        """
        Assess crisis level for appropriate response
        """
        if state.get('error_state'):
            return 'error'
        
        crisis_level = state.get('crisis_level', 'low')
        if crisis_level in ['high', 'critical']:
            return 'high'
        else:
            return 'low'
    
    def execute_parallel_tasks(self, state: GraphState) -> GraphState:
        """
        Execute tasks in parallel
        """
        print(f"Executing {len(state.get('parallel_tasks', []))} tasks in parallel")
        # In actual implementation, this would execute agents concurrently
        return state
    
    def aggregate_parallel_results(self, state: GraphState) -> GraphState:
        """
        Aggregate results from parallel execution
        """
        print("Aggregating parallel execution results")
        return state
    
    def human_review_checkpoint(self, state: GraphState) -> GraphState:
        """
        Checkpoint for human review
        """
        print("Human review required")
        state['approval_needed'] = True
        return state
    
    def apply_human_feedback(self, state: GraphState) -> GraphState:
        """
        Apply human feedback to the state
        """
        print("Applying human feedback")
        state['approval_needed'] = False
        return state
    
    def route_after_human_feedback(self, state: GraphState) -> str:
        """
        Determine routing after human feedback
        """
        if state.get('human_feedback') == 'retry':
            return 'retry'
        elif state.get('error_state'):
            return 'error'
        else:
            return 'continue'
    
    def handle_error(self, state: GraphState) -> GraphState:
        """
        Handle errors in the workflow
        """
        print(f"Handling error: {state.get('error_state')}")
        state['retry_count'] = state.get('retry_count', 0) + 1
        return state
    
    def determine_error_recovery(self, state: GraphState) -> str:
        """
        Determine error recovery strategy
        """
        if state.get('retry_count', 0) >= 3:
            return 'human'
        elif state.get('retry_count', 0) < 3:
            return 'retry'
        else:
            return 'end'
    
    def prepare_final_response(self, state: GraphState) -> GraphState:
        """
        Prepare the final response for the user
        """
        print("Preparing final response")
        responses = state.get('agent_responses', [])
        state['final_response'] = f"Completed workflow with {len(responses)} agent responses"
        return state
    
    def complete_workflow(self, state: GraphState) -> GraphState:
        """
        Complete the workflow and return final state
        """
        print(f"Workflow completed: {state.get('final_response')}")
        return state
    
    def run(self, user_request: str, session_id: str = None) -> Dict[str, Any]:
        """
        Run the graph with a user request
        """
        initial_state = {
            "user_request": user_request,
            "session_id": session_id or f"session_{datetime.now().timestamp()}",
            "workflow_step": 0,
            "agent_responses": [],
            "context_data": {},
            "retry_count": 0
        }
        
        # Run the graph
        config = {"configurable": {"thread_id": session_id}} if session_id else {}
        result = self.app.invoke(initial_state, config)
        
        return result

if __name__ == "__main__":
    # Example usage
    import os
    groq_api_key = os.getenv("GROQ_API_KEY", "your-api-key-here")
    
    # Initialize the graph
    graph = SocialMediaManagerGraph(groq_api_key)
    
    # Example request
    result = graph.run("Create a social media strategy for launching a new product")
    print(f"Final result: {result.get('final_response')}")
