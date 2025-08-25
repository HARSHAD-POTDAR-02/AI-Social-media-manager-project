"""
AI Social Media Manager - Dynamic CLI Interface
Natural conversation interface for social media management
"""

import os
import sys
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from central_router import CentralRouter
from agents.orchestrator_agent import OrchestratorAgent

class DynamicSocialMediaCLI:
    def __init__(self):
        load_dotenv()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            print("❌ Error: GROQ_API_KEY not found in .env file")
            sys.exit(1)
            
        self.router = CentralRouter(self.groq_api_key)
        self.orchestrator = OrchestratorAgent()
        self.agents = {}
        self.session_context = {
            'requests_processed': 0,
            'last_workflow': None,
            'active_campaign': None,
            'user_preferences': {}
        }
        self.initialize_agents()
        
    def initialize_agents(self):
        """Initialize all agent instances dynamically"""
        try:
            from agents.content_agent import ContentAgent
            self.agents['content'] = ContentAgent()
        except ImportError:
            pass
            
        try:
            from agents.analytics_agent import AnalyticsAgent
            self.agents['analytics'] = AnalyticsAgent()
        except ImportError:
            pass
            
        try:
            from agents.strategy_agent import StrategyAgent
            self.agents['strategy'] = StrategyAgent()
        except ImportError:
            pass
            
        try:
            from agents.community_agent import CommunityAgent
            self.agents['community'] = CommunityAgent()
        except ImportError:
            pass
    
    def print_welcome(self):
        """Print dynamic welcome message"""
        welcome_messages = [
            "🎯 AI Social Media Manager at your service!",
            "🚀 Ready to boost your social media presence!",
            "✨ Your AI-powered social media assistant is here!",
            "🎨 Let's create some amazing content together!"
        ]
        
        import random
        message = random.choice(welcome_messages)
        
        print("\n" + "="*60)
        print(f"  {message}")
        print("="*60)
        
        capabilities = [
            "💡 Create engaging posts and content strategies",
            "📊 Analyze your social media performance", 
            "🤝 Manage community interactions and responses",
            "📱 Plan multi-platform publishing campaigns",
            "🔍 Monitor brand mentions and trends",
            "⚡ Handle crisis management situations"
        ]
        
        print("\n🌟 What I can help you with:")
        for capability in capabilities:
            print(f"   {capability}")
            
        print(f"\n📈 Available agents: {', '.join(self.agents.keys()) if self.agents else 'Loading...'}")
        print("\n💬 Just tell me what you need! Examples:")
        print("   • 'Create a post about our new product launch'")
        print("   • 'Show me analytics for last month'") 
        print("   • 'Help me respond to this customer complaint'")
        print("   • 'Plan a content strategy for Instagram'")
        print("   • 'Test the orchestrator with a complex request'")
        print("\n" + "="*60 + "\n")
    
    def detect_intent(self, user_input):
        """Detect what the user wants to do"""
        user_input_lower = user_input.lower()
        
        # Direct agent testing patterns
        agent_patterns = {
            'content': ['content', 'post', 'write', 'create', 'copy', 'caption'],
            'analytics': ['analytics', 'report', 'performance', 'metrics', 'stats', 'data'],
            'strategy': ['strategy', 'plan', 'campaign', 'schedule', 'calendar'],
            'community': ['community', 'respond', 'reply', 'comment', 'message', 'customer'],
            'orchestrator': ['orchestrator', 'test orchestrator', 'complex', 'workflow']
        }
        
        # Workflow patterns
        workflow_patterns = {
            'content_creation': ['make a post', 'create content', 'publish', 'new post'],
            'crisis_management': ['crisis', 'urgent', 'problem', 'issue', 'complaint'],
            'campaign_planning': ['campaign', 'strategy', 'multi-platform', 'schedule posts'],
            'performance_analysis': ['analyze', 'performance', 'how did', 'results', 'roi']
        }
        
        # Check for direct agent requests
        for agent, keywords in agent_patterns.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return {
                    'type': 'direct_agent',
                    'target': agent,
                    'confidence': 0.8
                }
        
        # Check for workflow requests
        for workflow, keywords in workflow_patterns.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return {
                    'type': 'workflow',
                    'target': workflow,
                    'confidence': 0.9
                }
        
        # Check for help/info requests
        if any(word in user_input_lower for word in ['help', 'what can you do', 'capabilities', 'options']):
            return {'type': 'help', 'confidence': 1.0}
            
        # Check for exit requests
        if any(word in user_input_lower for word in ['exit', 'quit', 'bye', 'goodbye']):
            return {'type': 'exit', 'confidence': 1.0}
            
        # Default to full workflow
        return {
            'type': 'full_workflow',
            'target': 'orchestrator',
            'confidence': 0.6
        }
    
    def handle_direct_agent(self, agent_name, user_input):
        """Handle direct agent interaction"""
        if agent_name not in self.agents:
            print(f"⚠️  Agent '{agent_name}' is not available. Available agents: {', '.join(self.agents.keys())}")
            return
            
        print(f"🤖 Connecting you to the {agent_name.title()} Agent...")
        print("─" * 50)
        
        try:
            state = {
                'user_request': user_input,
                'agent_responses': [],
                'current_agent': agent_name,
                'timestamp': datetime.now().isoformat(),
                'session_context': self.session_context
            }
            
            agent = self.agents[agent_name]
            result = agent.process(state)
            
            print(f"✅ {agent_name.title()} Agent Response:")
            if isinstance(result, dict):
                # Pretty print the result based on agent type
                if agent_name == 'content':
                    self.display_content_result(result)
                elif agent_name == 'analytics':
                    self.display_analytics_result(result)
                else:
                    self.display_generic_result(result)
            else:
                print(f"   {result}")
                
        except Exception as e:
            print(f"❌ Error with {agent_name} agent: {str(e)}")
            
        print("─" * 50)
    
    def handle_workflow(self, workflow_type, user_input):
        """Handle specific workflow types"""
        print(f"🔄 Starting {workflow_type.replace('_', ' ').title()} Workflow...")
        print("─" * 50)
        
        workflows = {
            'content_creation': self.content_creation_workflow,
            'crisis_management': self.crisis_management_workflow,
            'campaign_planning': self.campaign_planning_workflow,
            'performance_analysis': self.performance_analysis_workflow
        }
        
        if workflow_type in workflows:
            workflows[workflow_type](user_input)
        else:
            print(f"⚠️  Workflow '{workflow_type}' not implemented yet.")
    
    def content_creation_workflow(self, user_input):
        """Handle content creation workflow"""
        print("📝 Content Creation Workflow Active")
        
        steps = [
            ("🎯 Strategy Planning", "strategy"),
            ("✍️  Content Creation", "content"),
            ("🛡️  Compliance Check", "compliance"),
            ("📱 Publishing Plan", "publishing")
        ]
        
        state = {
            'user_request': user_input,
            'workflow_type': 'content_creation',
            'agent_responses': [],
            'requires_approval': True
        }
        
        for step_name, agent_name in steps:
            print(f"\n{step_name}...")
            
            if agent_name in self.agents:
                try:
                    state['current_agent'] = agent_name
                    result = self.agents[agent_name].process(state)
                    state['agent_responses'].append({
                        'agent': agent_name,
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"   ✅ {step_name} completed")
                    
                    # Show preview of result
                    if isinstance(result, dict) and 'content' in result:
                        preview = str(result['content'])[:100] + "..." if len(str(result['content'])) > 100 else str(result['content'])
                        print(f"   📋 Preview: {preview}")
                        
                except Exception as e:
                    print(f"   ❌ Error in {step_name}: {str(e)}")
                    state['errors'] = state.get('errors', []) + [str(e)]
            else:
                print(f"   ⚠️  {agent_name} agent not available - simulating step")
                state['agent_responses'].append({
                    'agent': agent_name,
                    'result': f"Simulated {step_name} completion",
                    'timestamp': datetime.now().isoformat()
                })
        
        print(f"\n🎉 Content Creation Workflow Complete!")
        print(f"   📊 Steps completed: {len([r for r in state['agent_responses'] if 'error' not in str(r)])}")
        
        if state.get('requires_approval'):
            approval = input("\n👤 Human Review - Approve this content? (y/n): ").strip().lower()
            state['human_approval'] = approval == 'y'
            print(f"   {'✅ Approved' if state['human_approval'] else '❌ Rejected'}")
    
    def crisis_management_workflow(self, user_input):
        """Handle crisis management workflow"""
        print("🚨 Crisis Management Protocol Activated")
        print("   🔍 Analyzing situation severity...")
        
        # Simulate crisis analysis
        crisis_keywords = ['urgent', 'crisis', 'complaint', 'angry', 'problem', 'issue']
        severity = 'HIGH' if any(word in user_input.lower() for word in crisis_keywords) else 'MEDIUM'
        
        print(f"   📊 Crisis Level: {severity}")
        
        if severity == 'HIGH':
            print("   🚨 HIGH SEVERITY - Immediate escalation required")
            print("   📞 Notifying crisis management team...")
            print("   ⏱️  Response required within 15 minutes")
        else:
            print("   ⚠️  MEDIUM SEVERITY - Standard crisis protocol")
            print("   📝 Generating response strategy...")
        
        # Generate crisis response
        if 'community' in self.agents:
            try:
                state = {
                    'user_request': user_input,
                    'crisis_level': severity,
                    'requires_immediate_response': severity == 'HIGH'
                }
                response = self.agents['community'].process(state)
                print(f"\n💬 Suggested Response Generated:")
                print(f"   {response}")
            except Exception as e:
                print(f"   ❌ Error generating response: {str(e)}")
    
    def campaign_planning_workflow(self, user_input):
        """Handle campaign planning workflow"""
        print("📅 Campaign Planning Workflow")
        print("   🎯 Analyzing campaign requirements...")
        
        # This would integrate with strategy and content agents
        print("   📊 Market research and competitor analysis...")
        print("   📝 Content calendar creation...")
        print("   🎨 Creative asset planning...")
        print("   📱 Multi-platform optimization...")
        print("   📈 Success metrics definition...")
        
        print("\n✅ Campaign Framework Ready!")
    
    def performance_analysis_workflow(self, user_input):
        """Handle performance analysis"""
        print("📊 Performance Analysis Starting...")
        
        if 'analytics' in self.agents:
            try:
                state = {'user_request': user_input, 'analysis_type': 'comprehensive'}
                result = self.agents['analytics'].process(state)
                self.display_analytics_result(result)
            except Exception as e:
                print(f"❌ Analytics error: {str(e)}")
        else:
            print("⚠️  Analytics agent not available - showing simulated data")
    
    def handle_full_workflow(self, user_input):
        """Handle complete workflow through orchestrator and routing"""
        print("🎯 Processing through full AI workflow...")
        print("─" * 50)
        
        try:
            # Step 1: Route the request
            print("1️⃣  Analyzing request and determining optimal workflow...")
            routing_decision = self.router.route(user_input)
            
            print(f"   🎯 Primary Agent: {routing_decision['primary_agent']}")
            print(f"   🔄 Workflow Type: {routing_decision['workflow_type']}")
            print(f"   🔍 Priority: {routing_decision['priority']}")
            
            if routing_decision.get('secondary_agents'):
                print(f"   👥 Additional Agents: {', '.join(routing_decision['secondary_agents'])}")
            
            # Step 2: Orchestrator processing
            print("\n2️⃣  Orchestrator coordinating workflow...")
            state = {
                'user_request': user_input,
                'routing_decision': routing_decision,
                'agent_responses': [],
                'current_agent': 'orchestrator'
            }
            
            orchestrator_result = self.orchestrator.process(state)
            print("   ✅ Orchestration complete")
            
            # Step 3: Execute primary agent
            primary_agent = routing_decision['primary_agent']
            print(f"\n3️⃣  Executing {primary_agent} agent...")
            
            if primary_agent in self.agents:
                agent_result = self.agents[primary_agent].process(state)
                print("   ✅ Primary agent execution complete")
                
                # Display result based on agent type
                if primary_agent == 'content':
                    self.display_content_result(agent_result)
                elif primary_agent == 'analytics':
                    self.display_analytics_result(agent_result)
                else:
                    self.display_generic_result(agent_result)
            else:
                print(f"   ⚠️  {primary_agent} agent not available - workflow simulated")
            
            # Step 4: Human review if required
            if routing_decision.get('requires_human_review'):
                print("\n4️⃣  Human review required...")
                review = input("   👤 Please review and provide feedback: ").strip()
                if review:
                    print(f"   📝 Review recorded: {review[:50]}...")
            
            print("\n🎉 Full workflow completed successfully!")
            
        except Exception as e:
            print(f"❌ Workflow error: {str(e)}")
    
    def display_content_result(self, result):
        """Display content creation results nicely"""
        print("📝 Content Created:")
        if isinstance(result, dict):
            if 'post_text' in result:
                print(f"   📄 Post: {result['post_text']}")
            if 'hashtags' in result:
                print(f"   #️⃣  Hashtags: {result['hashtags']}")
            if 'platform' in result:
                print(f"   📱 Platform: {result['platform']}")
        else:
            print(f"   {result}")
    
    def display_analytics_result(self, result):
        """Display analytics results nicely"""
        print("📊 Analytics Report:")
        if isinstance(result, dict):
            for key, value in result.items():
                if key in ['engagement_rate', 'reach', 'impressions']:
                    print(f"   📈 {key.title()}: {value}")
        else:
            print(f"   {result}")
    
    def display_generic_result(self, result):
        """Display generic agent results"""
        if isinstance(result, dict):
            print("   📋 Results:")
            for key, value in result.items():
                print(f"      • {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
        else:
            print(f"   {result}")
    
    def show_help(self):
        """Show dynamic help information"""
        print("\n💡 How to use the AI Social Media Manager:")
        print("─" * 50)
        print("🗣️  Just type what you want to do naturally! Examples:")
        print()
        
        examples = [
            ("Direct Agent Testing:", [
                "'test the content agent with a product launch post'",
                "'show me analytics for Instagram'",
                "'help me plan a content strategy'",
                "'test orchestrator with a complex request'"
            ]),
            ("Content Workflows:", [
                "'create a post about our summer sale'",
                "'make content for LinkedIn about our company update'",
                "'I need a Instagram story about our event'"
            ]),
            ("Analysis & Strategy:", [
                "'analyze our social media performance'",
                "'plan a campaign for our new product'",
                "'show me trending hashtags in our industry'"
            ]),
            ("Crisis Management:", [
                "'help me respond to this angry customer'",
                "'we have a PR crisis, what should we do?'",
                "'urgent: negative reviews need immediate response'"
            ])
        ]
        
        for category, example_list in examples:
            print(f"   {category}")
            for example in example_list:
                print(f"      • {example}")
            print()
        
        print("💡 Tips:")
        print("   • Be specific about what platform or content type you need")
        print("   • Mention if it's urgent or requires immediate attention")
        print("   • Ask for help anytime with 'help' or 'what can you do'")
        print("   • Type 'exit' or 'quit' to end the session")
        print("─" * 50)
    
    def run(self):
        """Main dynamic conversation loop"""
        self.print_welcome()
        
        print("💬 What would you like to do? (Type 'help' for examples)")
        
        while True:
            try:
                # Get user input
                user_input = input("\n🎯 You: ").strip()
                
                if not user_input:
                    print("💭 I'm here when you need me! Try asking for help or tell me what you'd like to do.")
                    continue
                
                # Update session context
                self.session_context['requests_processed'] += 1
                
                # Detect intent and route appropriately
                intent = self.detect_intent(user_input)
                
                print(f"\n🤖 AI Manager: ", end="")
                
                if intent['type'] == 'exit':
                    print("👋 Thanks for using AI Social Media Manager! Have a great day!")
                    break
                    
                elif intent['type'] == 'help':
                    print("I'd be happy to help! Here's what I can do:")
                    self.show_help()
                    
                elif intent['type'] == 'direct_agent':
                    print(f"I'll connect you directly to the {intent['target']} agent.")
                    self.handle_direct_agent(intent['target'], user_input)
                    
                elif intent['type'] == 'workflow':
                    print(f"Starting the {intent['target'].replace('_', ' ')} workflow for you.")
                    self.handle_workflow(intent['target'], user_input)
                    
                elif intent['type'] == 'full_workflow':
                    print("Let me process this through our complete AI system.")
                    self.handle_full_workflow(user_input)
                
                # Update last workflow
                self.session_context['last_workflow'] = intent['type']
                
                # Ask for next action
                if self.session_context['requests_processed'] % 3 == 0:
                    print(f"\n✨ You've made {self.session_context['requests_processed']} requests so far. Need anything else?")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Oops! Something went wrong: {str(e)}")
                print("🔄 Don't worry, I'm still here to help. Try again!")

if __name__ == "__main__":
    try:
        print("🚀 Initializing AI Social Media Manager...")
        cli = DynamicSocialMediaCLI()
        cli.run()
    except Exception as e:
        print(f"💥 Startup error: {str(e)}")
        sys.exit(1)