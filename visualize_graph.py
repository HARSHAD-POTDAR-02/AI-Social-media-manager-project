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
from graph_setup import SocialMediaManagerGraph

class GraphVisualizer:
    """
    Visualizer for the social media manager graph architecture
    """
    
    def __init__(self, graph_app):
        self.graph_app = graph_app
        raw_graph = self.graph_app.get_graph()
        self.graph = self._to_networkx_graph(raw_graph)
        self.node_colors = {
            'entry': '#e1f5fe',
            'agent': '#e8f5e8',
            'router': '#fff3e0',
            'utility': '#fce4ec',
            'final': '#e0f2f1'
        }
        self.edge_colors = {
            'normal': '#2196F3',
            'conditional': '#FF9800',
            'error': '#F44336'
        }
        
    def visualize(self, save_path: str = "graph_architecture.png", show: bool = True):
        """
        Generate and save the graph visualization
        """
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.set_title("AI Social Media Manager - LangGraph Architecture", fontsize=20, fontweight='bold', pad=20)
        
        pos = nx.spring_layout(self.graph, seed=42)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, ax=ax, edge_color='#cccccc', width=1.5, alpha=0.8)

        # Draw nodes
        node_colors_list = [self.node_colors.get(self._get_node_type(node), '#ffffff') for node in self.graph.nodes()]
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors_list, node_size=5000, ax=ax, node_shape='s')

        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, ax=ax, font_size=10, font_weight='bold')

        ax.axis('off')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"Graph visualization saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig

    def _get_node_type(self, node_name: str) -> str:
        if "user_input" in node_name:
            return "entry"
        if "route_request" in node_name:
            return "router"
        if "execute_agent" in node_name:
            return "agent"
        if "prepare_response" in node_name:
            return "final"
        if node_name == "END":
            return "final"
        return "utility"

    def generate_mermaid_diagram(self) -> str:
        """
        Generate a Mermaid diagram code for the architecture
        """
        mermaid_code = "graph TD\n"
        for u, v in self.graph.edges():
            mermaid_code += f"    {u} --> {v}\n"
        return mermaid_code

    def _to_networkx_graph(self, raw_graph) -> nx.DiGraph:
        """
        Convert the object returned by app.get_graph() into a NetworkX DiGraph by
        introspecting common node/edge accessors. This keeps visualization
        synchronized with graph_setup.py without hardcoding structure.
        """
        # If it's already a networkx graph, adapt/return
        if isinstance(raw_graph, (nx.DiGraph, nx.Graph)):
            return raw_graph if isinstance(raw_graph, nx.DiGraph) else nx.DiGraph(raw_graph)

        g = nx.DiGraph()

        # Helper to stringify node identifiers reliably
        def node_id(n):
            if isinstance(n, str):
                return n
            for attr in ("id", "name", "key", "label"):
                if hasattr(n, attr):
                    try:
                        return str(getattr(n, attr))
                    except Exception:
                        pass
            return str(n)

        # Extract nodes
        nodes_iter = None
        if hasattr(raw_graph, "nodes"):
            nodes_attr = getattr(raw_graph, "nodes")
            nodes_iter = nodes_attr() if callable(nodes_attr) else nodes_attr
        elif hasattr(raw_graph, "get_nodes"):
            nodes_iter = raw_graph.get_nodes()

        if nodes_iter is not None:
            try:
                for n in nodes_iter:
                    g.add_node(node_id(n))
            except Exception:
                try:
                    for n in nodes_iter.keys():
                        g.add_node(node_id(n))
                except Exception:
                    pass

        # Extract edges
        edges_iter = None
        if hasattr(raw_graph, "edges"):
            edges_attr = getattr(raw_graph, "edges")
            edges_iter = edges_attr() if callable(edges_attr) else edges_attr
        elif hasattr(raw_graph, "get_edges"):
            edges_iter = raw_graph.get_edges()

        def add_edge(u, v):
            g.add_node(node_id(u))
            g.add_node(node_id(v))
            g.add_edge(node_id(u), node_id(v))

        if edges_iter is not None:
            try:
                for e in edges_iter:
                    if isinstance(e, tuple) and len(e) >= 2:
                        add_edge(e[0], e[1])
                    else:
                        u = None
                        v = None
                        for s_attr in ("source", "start", "u", "from_node", "from_id"):
                            if u is None and hasattr(e, s_attr):
                                u = getattr(e, s_attr)
                        for t_attr in ("target", "end", "v", "to_node", "to_id"):
                            if v is None and hasattr(e, t_attr):
                                v = getattr(e, t_attr)
                        if u is not None and v is not None:
                            add_edge(u, v)
            except Exception:
                pass

        return g

if __name__ == "__main__":
    # Initialize the graph from graph_setup
    groq_api_key = os.getenv("GROQ_API_KEY", "your-api-key-here")
    manager_graph = SocialMediaManagerGraph(groq_api_key)
    
    # Create visualizer
    visualizer = GraphVisualizer(manager_graph.app)
    
    # Generate and save visualization
    visualizer.visualize(save_path="graph_architecture.png", show=False)
    
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
    print("- graph_architecture_mermaid.md")
    print("\nYou can now view the graph architecture!")