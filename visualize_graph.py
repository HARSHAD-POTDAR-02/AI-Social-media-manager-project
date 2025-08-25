"""
Visualization Tool for AI Social Media Manager Graph Architecture
Generates a visual representation of the LangGraph workflow
"""

import os
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches
from typing import Dict, List, Tuple

class GraphVisualizer:
    """
    Visualizer for the social media manager graph architecture
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_colors = {
            'entry': '#e1f5fe',
            'orchestrator': '#fff3e0',
            'core_agent': '#e8f5e8',
            'specialized_agent': '#f3e5f5',
            'utility': '#fce4ec',
            'human': '#ffebee',
            'final': '#e0f2f1'
        }
        self.edge_colors = {
            'normal': '#2196F3',
            'conditional': '#FF9800',
            'parallel': '#9C27B0',
            'error': '#F44336',
            'human': '#E91E63'
        }
        
    def build_graph(self):
        """
        Build the graph structure based on the architecture
        """
        # Entry and orchestration nodes
        self.graph.add_node("user_input", type="entry", label="User Input")
        self.graph.add_node("orchestrator", type="orchestrator", label="Orchestrator\nAgent")
        self.graph.add_node("route_request", type="orchestrator", label="Central Router\n(LLM-based)")
        
        # Core agent nodes
        core_agents = [
            ("strategy", "Strategy\nAgent"),
            ("content", "Content\nAgent"),
            ("publishing", "Publishing\nAgent"),
            ("community", "Community\nAgent"),
            ("listening", "Listening\nAgent"),
            ("analytics", "Analytics\nAgent")
        ]
        
        for agent_id, label in core_agents:
            self.graph.add_node(agent_id, type="core_agent", label=label)
        
        # Specialized agent nodes
        specialized_agents = [
            ("crisis", "Crisis\nAgent"),
            ("influencer", "Influencer\nAgent"),
            ("paid_social", "Paid Social\nAgent"),
            ("compliance", "Compliance\nAgent")
        ]
        
        for agent_id, label in specialized_agents:
            self.graph.add_node(agent_id, type="specialized_agent", label=label)
        
        # Utility nodes
        self.graph.add_node("parallel_coordinator", type="utility", label="Parallel\nCoordinator")
        self.graph.add_node("parallel_execution", type="utility", label="Parallel\nExecution")
        self.graph.add_node("aggregate_results", type="utility", label="Aggregate\nResults")
        
        # Human-in-the-loop nodes
        self.graph.add_node("human_review", type="human", label="Human\nReview")
        self.graph.add_node("apply_feedback", type="human", label="Apply\nFeedback")
        
        # Error handling
        self.graph.add_node("error_handler", type="human", label="Error\nHandler")
        
        # Final nodes
        self.graph.add_node("prepare_response", type="final", label="Prepare\nResponse")
        self.graph.add_node("complete", type="final", label="Complete\nWorkflow")
        
        # Add edges - Main flow
        self.graph.add_edge("user_input", "orchestrator", edge_type="normal")
        self.graph.add_edge("orchestrator", "route_request", edge_type="normal")
        
        # Routing edges (conditional)
        for agent in ["strategy", "content", "publishing", "community", 
                     "listening", "analytics", "crisis", "influencer", 
                     "paid_social", "compliance", "parallel_coordinator"]:
            self.graph.add_edge("route_request", agent, edge_type="conditional")
        
        # Sequential workflow
        self.graph.add_edge("strategy", "content", edge_type="normal")
        self.graph.add_edge("content", "compliance", edge_type="normal")
        self.graph.add_edge("compliance", "publishing", edge_type="conditional")
        self.graph.add_edge("publishing", "listening", edge_type="normal")
        self.graph.add_edge("listening", "prepare_response", edge_type="normal")
        
        # Parallel workflow
        self.graph.add_edge("parallel_coordinator", "parallel_execution", edge_type="parallel")
        self.graph.add_edge("parallel_execution", "aggregate_results", edge_type="parallel")
        self.graph.add_edge("aggregate_results", "prepare_response", edge_type="parallel")
        
        # Human review paths
        self.graph.add_edge("strategy", "human_review", edge_type="human")
        self.graph.add_edge("content", "human_review", edge_type="human")
        self.graph.add_edge("crisis", "human_review", edge_type="human")
        self.graph.add_edge("human_review", "apply_feedback", edge_type="human")
        self.graph.add_edge("apply_feedback", "route_request", edge_type="human")
        
        # Error handling paths
        for agent in ["strategy", "content", "publishing", "compliance"]:
            self.graph.add_edge(agent, "error_handler", edge_type="error")
        self.graph.add_edge("error_handler", "human_review", edge_type="error")
        
        # Final edges
        self.graph.add_edge("prepare_response", "complete", edge_type="normal")
        
    def visualize(self, save_path: str = "graph_architecture.png", show: bool = True):
        """
        Generate and save the graph visualization
        """
        # Build the graph
        self.build_graph()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(20, 14))
        ax.set_title("AI Social Media Manager - LangGraph Architecture", 
                     fontsize=20, fontweight='bold', pad=20)
        
        # Calculate layout
        pos = self._hierarchical_layout()
        
        # Draw edges with different styles
        for edge in self.graph.edges(data=True):
            source, target, data = edge
            edge_type = data.get('edge_type', 'normal')
            
            if edge_type == 'conditional':
                nx.draw_networkx_edges(self.graph, pos, [(source, target)],
                                      edge_color=self.edge_colors['conditional'],
                                      style='dashed', width=1.5, alpha=0.7,
                                      arrows=True, arrowsize=15, ax=ax)
            elif edge_type == 'parallel':
                nx.draw_networkx_edges(self.graph, pos, [(source, target)],
                                      edge_color=self.edge_colors['parallel'],
                                      style='dotted', width=2, alpha=0.8,
                                      arrows=True, arrowsize=15, ax=ax)
            elif edge_type == 'error':
                nx.draw_networkx_edges(self.graph, pos, [(source, target)],
                                      edge_color=self.edge_colors['error'],
                                      style='dashdot', width=1.5, alpha=0.6,
                                      arrows=True, arrowsize=15, ax=ax)
            elif edge_type == 'human':
                nx.draw_networkx_edges(self.graph, pos, [(source, target)],
                                      edge_color=self.edge_colors['human'],
                                      style='solid', width=1.5, alpha=0.7,
                                      arrows=True, arrowsize=15, ax=ax)
            else:
                nx.draw_networkx_edges(self.graph, pos, [(source, target)],
                                      edge_color=self.edge_colors['normal'],
                                      style='solid', width=2, alpha=0.8,
                                      arrows=True, arrowsize=20, ax=ax)
        
        # Draw nodes with custom styling
        for node, (x, y) in pos.items():
            node_data = self.graph.nodes[node]
            node_type = node_data.get('type', 'core_agent')
            label = node_data.get('label', node)
            
            # Create fancy box for node
            if node_type == 'entry':
                bbox = FancyBboxPatch((x-0.08, y-0.03), 0.16, 0.06,
                                     boxstyle="round,pad=0.01",
                                     facecolor=self.node_colors[node_type],
                                     edgecolor='#0277bd', linewidth=2)
            elif node_type == 'orchestrator':
                bbox = FancyBboxPatch((x-0.08, y-0.03), 0.16, 0.06,
                                     boxstyle="round,pad=0.01",
                                     facecolor=self.node_colors[node_type],
                                     edgecolor='#f57c00', linewidth=2)
            elif node_type == 'human':
                bbox = FancyBboxPatch((x-0.08, y-0.03), 0.16, 0.06,
                                     boxstyle="round,pad=0.01",
                                     facecolor=self.node_colors[node_type],
                                     edgecolor='#d32f2f', linewidth=2)
            else:
                bbox = FancyBboxPatch((x-0.08, y-0.03), 0.16, 0.06,
                                     boxstyle="round,pad=0.01",
                                     facecolor=self.node_colors.get(node_type, '#ffffff'),
                                     edgecolor='#666666', linewidth=1.5)
            
            ax.add_patch(bbox)
            ax.text(x, y, label, horizontalalignment='center',
                   verticalalignment='center', fontsize=10, fontweight='bold')
        
        # Add legend
        legend_elements = [
            mpatches.Patch(color=self.node_colors['entry'], label='Entry Point'),
            mpatches.Patch(color=self.node_colors['orchestrator'], label='Orchestrator/Router'),
            mpatches.Patch(color=self.node_colors['core_agent'], label='Core Agent'),
            mpatches.Patch(color=self.node_colors['specialized_agent'], label='Specialized Agent'),
            mpatches.Patch(color=self.node_colors['utility'], label='Utility/Parallel'),
            mpatches.Patch(color=self.node_colors['human'], label='Human/Error'),
            mpatches.Patch(color=self.node_colors['final'], label='Final'),
        ]
        
        edge_legend = [
            plt.Line2D([0], [0], color=self.edge_colors['normal'], linewidth=2, label='Normal Flow'),
            plt.Line2D([0], [0], color=self.edge_colors['conditional'], linewidth=2, 
                      linestyle='--', label='Conditional'),
            plt.Line2D([0], [0], color=self.edge_colors['parallel'], linewidth=2, 
                      linestyle=':', label='Parallel'),
            plt.Line2D([0], [0], color=self.edge_colors['human'], linewidth=2, label='Human Review'),
            plt.Line2D([0], [0], color=self.edge_colors['error'], linewidth=2, 
                      linestyle='-.', label='Error Path'),
        ]
        
        ax.legend(handles=legend_elements + edge_legend, loc='upper left', 
                 bbox_to_anchor=(0.02, 0.98), ncol=2, fontsize=10)
        
        # Add annotations
        ax.text(0.5, -0.1, "LLM-based Routing (Groq API)", 
               transform=ax.transAxes, ha='center', fontsize=12, 
               style='italic', color='#666')
        
        ax.text(0.5, -0.15, "All agents connected via LangGraph StateGraph", 
               transform=ax.transAxes, ha='center', fontsize=10, 
               color='#999')
        
        # Clean up the plot
        ax.set_xlim(-0.2, 1.2)
        ax.set_ylim(-0.2, 1.2)
        ax.axis('off')
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"Graph visualization saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def _hierarchical_layout(self) -> Dict:
        """
        Create a hierarchical layout for the graph
        """
        # Define layers
        layers = {
            0: ["user_input"],
            1: ["orchestrator"],
            2: ["route_request"],
            3: ["strategy", "analytics", "community", "crisis", "parallel_coordinator"],
            4: ["content", "listening", "influencer", "paid_social", "parallel_execution"],
            5: ["compliance", "aggregate_results"],
            6: ["publishing", "human_review", "error_handler"],
            7: ["apply_feedback"],
            8: ["prepare_response"],
            9: ["complete"]
        }
        
        pos = {}
        for layer, nodes in layers.items():
            y = 1 - (layer / 9)  # Normalize y position
            for i, node in enumerate(nodes):
                if node in self.graph.nodes():
                    x = (i + 1) / (len(nodes) + 1)  # Distribute horizontally
                    pos[node] = (x, y)
        
        return pos
    
    def generate_mermaid_diagram(self) -> str:
        """
        Generate a Mermaid diagram code for the architecture
        """
        mermaid_code = """graph TD
    %% Entry Points
    START([User Input]) --> ORCHESTRATOR{Orchestrator Agent}
    ORCHESTRATOR --> ROUTER{Central Router<br/>LLM-based Routing}
    
    %% Core Agents
    ROUTER -->|Direct/Sequential| STRATEGY[Strategy Agent]
    ROUTER -->|Direct| CONTENT[Content Agent]
    ROUTER -->|Direct| PUBLISHING[Publishing Agent]
    ROUTER -->|Direct| COMMUNITY[Community Agent]
    ROUTER -->|Direct| LISTENING[Listening Agent]
    ROUTER -->|Direct| ANALYTICS[Analytics Agent]
    
    %% Specialized Agents
    ROUTER -->|Direct| CRISIS[Crisis Agent]
    ROUTER -->|Direct| INFLUENCER[Influencer Agent]
    ROUTER -->|Direct| PAID_SOCIAL[Paid Social Agent]
    ROUTER -->|Direct| COMPLIANCE[Compliance Agent]
    
    %% Parallel Execution
    ROUTER -->|Parallel| PARALLEL_COORD[Parallel Coordinator]
    PARALLEL_COORD --> PARALLEL_EXEC[Parallel Execution]
    PARALLEL_EXEC --> AGGREGATE[Aggregate Results]
    
    %% Sequential Workflow
    STRATEGY --> CONTENT
    CONTENT --> COMPLIANCE
    COMPLIANCE -->|Passed| PUBLISHING
    COMPLIANCE -->|Failed| CONTENT
    PUBLISHING --> LISTENING
    
    %% Human Review
    STRATEGY -.->|Review Needed| HUMAN[Human Review]
    CONTENT -.->|Review Needed| HUMAN
    CRISIS -.->|High Priority| HUMAN
    HUMAN --> APPLY_FEEDBACK[Apply Feedback]
    APPLY_FEEDBACK --> ROUTER
    
    %% Error Handling
    STRATEGY -.->|Error| ERROR[Error Handler]
    CONTENT -.->|Error| ERROR
    PUBLISHING -.->|Error| ERROR
    ERROR --> HUMAN
    
    %% Final Steps
    LISTENING --> PREPARE[Prepare Response]
    AGGREGATE --> PREPARE
    PREPARE --> COMPLETE([Complete Workflow])
    
    %% Styling
    classDef agentNode fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef routerNode fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef humanNode fill:#ffebee,stroke:#f44336,stroke-width:2px
    classDef finalNode fill:#e0f2f1,stroke:#009688,stroke-width:2px
    
    class STRATEGY,CONTENT,PUBLISHING,COMMUNITY,LISTENING,ANALYTICS agentNode
    class CRISIS,INFLUENCER,PAID_SOCIAL,COMPLIANCE agentNode
    class ORCHESTRATOR,ROUTER routerNode
    class HUMAN,ERROR,APPLY_FEEDBACK humanNode
    class PREPARE,COMPLETE finalNode"""
        
        return mermaid_code

if __name__ == "__main__":
    # Create visualizer
    visualizer = GraphVisualizer()
    
    # Generate and save visualization
    visualizer.visualize(save_path="graph_architecture.png", show=False)
    
    # Also save as PDF
    visualizer.visualize(save_path="graph_architecture.pdf", show=False)
    
    # Generate Mermaid diagram
    mermaid_code = visualizer.generate_mermaid_diagram()
    
    # Save Mermaid diagram to file
    with open("graph_architecture_mermaid.md", "w") as f:
        f.write("# AI Social Media Manager - Graph Architecture\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```")
    
    print("\nVisualization files created:")
    print("- graph_architecture.png")
    print("- graph_architecture.pdf")
    print("- graph_architecture_mermaid.md")
    print("\nYou can now view the graph architecture!")
