"""
AI Social Media Manager - Main Entry Point
Connects the user interface to the LangGraph-based agentic workflow.
"""

import os
import sys
from dotenv import load_dotenv
from graph_setup import SocialMediaManagerGraph, GraphState

class SocialMediaCLI:
    """
    A command-line interface for interacting with the AI Social Media Manager graph.
    """
    def __init__(self):
        load_dotenv()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            print("❌ Error: GROQ_API_KEY not found in .env file")
            sys.exit(1)
        
        print("🚀 Initializing AI Social Media Manager...")
        self.graph = SocialMediaManagerGraph(self.groq_api_key)
        self.session_id_counter = 0

    def print_welcome(self):
        """Prints a welcome message to the user."""
        print("\n" + "="*60)
        print("  🎯 AI Social Media Manager at your service!")
        print("="*60)
        print("\n🌟 Ask me anything related to your social media strategy.")
        print("   Examples: ")
        print("   - 'Create a content strategy for our new product launch'")
        print("   - 'Generate a report of our performance last month'")
        print("   - 'Create and schedule a post about our summer sale'")
        print("   - 'I need a complete market overview, including competitor analysis and performance metrics'")
        print("\nType 'exit' or 'quit' to end the session.")
        print("="*60 + "\n")

    def run(self):
        """Starts the main conversation loop."""
        self.print_welcome()
        
        while True:
            try:
                user_input = input("💬 You: ").strip()
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break

                # Each new input from the user in the CLI can be treated as a new "session" for the graph
                self.session_id_counter += 1
                session_id = f"cli-session-{self.session_id_counter}"

                print("🤖 AI Manager: Processing your request...")
                print("─" * 60)
                
                # Invoke the graph with the user's request
                result = self.graph.run(user_input, session_id=session_id)
                
                # The `run` method in the graph should be updated to return the final state
                # and the final response should be extracted from there.
                final_response = result.get('final_response', "Workflow finished, but no final response was prepared.")

                print("─" * 60)
                print(f"✅ Final Response: {final_response}")
                print("\n" + "="*60 + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An unexpected error occurred: {e}")
                import traceback
                traceback.print_exc()
                print("🔄 Please try again.")

if __name__ == "__main__":
    try:
        cli = SocialMediaCLI()
        cli.run()
    except Exception as e:
        print(f"💥 A critical error occurred on startup: {e}")
        sys.exit(1)
