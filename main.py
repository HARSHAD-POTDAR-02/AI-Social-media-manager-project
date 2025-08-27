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
        self.last_draft = None  # store last generated content for iterative feedback

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
        print("\nTip: After I generate a post, send feedback using 'feedback: <your notes>' to refine the draft.")
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
                
                # Handle feedback mode
                if user_input.lower().startswith("feedback:"):
                    feedback_text = user_input[len("feedback:"):].strip()
                    if not self.last_draft:
                        print("⚠️ No previous draft found. Please first ask me to create content, then provide feedback.")
                        print("─" * 60)
                        continue
                    context_data = {
                        "content_feedback": feedback_text,
                        "previous_draft": self.last_draft,
                    }
                    # word the request so router clearly sends to content agent
                    routed_request = "Create a revised content draft applying the provided feedback."
                    result = self.graph.run(routed_request, session_id=session_id, context_data=context_data)
                else:
                    # Regular request flow
                    result = self.graph.run(user_input, session_id=session_id)
                
                # Final response and capture last draft if available
                final_response = result.get('final_response')
                generated = result.get('generated_content', {}) or {}
                
                # Store the generated content for potential feedback
                if isinstance(generated, dict) and generated.get('content'):
                    self.last_draft = generated.get('content')
                    
                    # Display the generated content in a clean format
                    print("─" * 60)
                    print("🎯 GENERATED CONTENT:")
                    print("-" * 30)
                    print(self.last_draft)
                    print("-" * 30)
                    
                    # Show iteration count if available
                    iterations = generated.get('iterations', 0)
                    if iterations > 0:
                        print(f"\n(Refined through {iterations} iterations of generation and critique)")
                
                # Only show final response if it's different from the generated content
                if final_response and final_response != self.last_draft:
                    print("\n📝 Additional Details:")
                    print(f"{final_response}")
                
                print("\n💡 Tip: Type 'feedback: your notes' to refine this content")
                print("="*60 + "\n")

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
