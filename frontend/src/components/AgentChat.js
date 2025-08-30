import React, { useState, useRef, useEffect } from 'react';
import { 
  PaperAirplaneIcon,
  UserIcon,
  CpuChipIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const API_BASE_URL = 'http://localhost:8000';

const AgentChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [currentWorkflow, setCurrentWorkflow] = useState(null);
  const [agentQueue, setAgentQueue] = useState([]);
  const [completedAgents, setCompletedAgents] = useState([]);
  const messagesEndRef = useRef(null);

  const agents = [
    { id: 'all', name: 'All Agents', description: 'Let AI decide the best agent', color: 'bg-gray-500', icon: '🤖' },
    { id: 'strategy', name: 'Strategy Agent', description: 'Content planning & trends', color: 'bg-blue-500', icon: '🎯' },
    { id: 'content', name: 'Content Agent', description: 'Content creation & writing', color: 'bg-green-500', icon: '✍️' },
    { id: 'analytics', name: 'Analytics Agent', description: 'Performance & insights', color: 'bg-purple-500', icon: '📊' },
    { id: 'community', name: 'Community Agent', description: 'Engagement & responses', color: 'bg-pink-500', icon: '💬' },
    { id: 'publishing', name: 'Publishing Agent', description: 'Scheduling & posting', color: 'bg-orange-500', icon: '📱' },
    { id: 'crisis', name: 'Crisis Agent', description: 'Crisis management', color: 'bg-red-500', icon: '🚨' }
  ];

  const quickPrompts = [
    "Create a post about our new product launch",
    "Analyze our Instagram performance last month", 
    "Generate 5 reel ideas for summer campaign",
    "Schedule posts for next week across platforms",
    "Create a content strategy for Q2",
    "Monitor sentiment around our brand"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
      agent: selectedAgent
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setCurrentWorkflow(null);
    setAgentQueue([]);
    setCompletedAgents([]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: `web-${Date.now()}`,
          context_data: selectedAgent !== 'all' ? { preferred_agent: selectedAgent } : {}
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      setCurrentWorkflow(data.workflow_type);
      setAgentQueue(data.agent_queue || []);
      setCompletedAgents(data.agent_responses?.map(r => r.agent) || []);

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.final_response,
        timestamp: new Date(),
        workflow_type: data.workflow_type,
        agent_responses: data.agent_responses || [],
        generated_content: data.generated_content
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const WorkflowProgress = ({ workflow, queue, completed }) => {
    if (!workflow || workflow === 'direct') return null;

    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <h4 className="text-sm font-semibold text-blue-800 mb-3">Sequential Workflow Progress</h4>
        <div className="flex items-center space-x-2 overflow-x-auto">
          {queue.map((agent, index) => {
            const isCompleted = completed.includes(agent);
            const isCurrent = !isCompleted && index === completed.length;
            
            return (
              <div key={`${agent}-${index}`} className="flex items-center flex-shrink-0">
                <div className={`flex items-center px-3 py-2 rounded-full text-xs font-medium transition-all ${
                  isCompleted 
                    ? 'bg-green-100 text-green-800 border border-green-200' 
                    : isCurrent 
                    ? 'bg-yellow-100 text-yellow-800 border border-yellow-200 animate-pulse' 
                    : 'bg-gray-100 text-gray-600 border border-gray-200'
                }`}>
                  {isCompleted ? (
                    <CheckCircleIcon className="w-4 h-4 mr-1" />
                  ) : isCurrent ? (
                    <ClockIcon className="w-4 h-4 mr-1" />
                  ) : (
                    <ClockIcon className="w-4 h-4 mr-1 opacity-50" />
                  )}
                  <span className="capitalize">{agent}</span>
                </div>
                {index < queue.length - 1 && (
                  <div className="w-6 h-px bg-gray-300 mx-2"></div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const MessageBubble = ({ message }) => {
    const isUser = message.type === 'user';
    const selectedAgentInfo = agents.find(a => a.id === message.agent);
    
    return (
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
        <div className={`flex items-start space-x-3 max-w-4xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
          <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            isUser 
              ? selectedAgentInfo?.color || 'bg-blue-500'
              : 'bg-gradient-to-br from-gray-600 to-gray-800'
          }`}>
            {isUser ? (
              <UserIcon className="w-5 h-5 text-white" />
            ) : (
              <CpuChipIcon className="w-5 h-5 text-white" />
            )}
          </div>
          
          <div className={`rounded-xl px-4 py-3 ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : message.isError 
              ? 'bg-red-50 text-red-800 border border-red-200'
              : 'bg-white text-gray-800 border border-gray-200 shadow-sm'
          }`}>
            {isUser && selectedAgent !== 'all' && (
              <div className="text-xs opacity-80 mb-1">
                → {selectedAgentInfo?.name}
              </div>
            )}
            
            <div className="whitespace-pre-wrap">{message.content}</div>
            
            {/* Generated Content Display */}
            {message.generated_content && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
                <div className="flex items-center space-x-2 mb-2">
                  <SparklesIcon className="w-4 h-4 text-purple-600" />
                  <h5 className="font-semibold text-gray-700">Generated Content</h5>
                </div>
                <div className="text-gray-700 whitespace-pre-wrap bg-white p-3 rounded border">
                  {message.generated_content.content}
                </div>
                {message.generated_content.reflection_count > 0 && (
                  <div className="text-xs text-gray-500 mt-2">
                    ✨ Refined through {message.generated_content.reflection_count} iterations
                  </div>
                )}
              </div>
            )}
            
            {/* Agent Activities */}
            {message.agent_responses && message.agent_responses.length > 0 && (
              <div className="mt-4 space-y-2">
                <h5 className="font-semibold text-gray-700 text-sm">Agent Activities:</h5>
                {message.agent_responses.map((response, index) => (
                  <div key={index} className="text-xs bg-gray-50 rounded-lg p-3 border">
                    <div className="flex items-center space-x-2 mb-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="font-medium capitalize text-gray-700">{response.agent}</span>
                    </div>
                    <div className="text-gray-600">{response.result}</div>
                  </div>
                ))}
              </div>
            )}
            
            <div className="text-xs opacity-70 mt-2">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-full">
      {/* Agent Selection Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-3">Select Agent</h3>
          <div className="space-y-2">
            {agents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => setSelectedAgent(agent.id)}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg text-left transition-all ${
                  selectedAgent === agent.id
                    ? 'bg-blue-50 border border-blue-200 text-blue-700'
                    : 'hover:bg-gray-50 text-gray-700'
                }`}
              >
                <div className={`w-8 h-8 rounded-lg ${agent.color} flex items-center justify-center text-white text-sm`}>
                  {agent.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">{agent.name}</div>
                  <div className="text-xs text-gray-500 truncate">{agent.description}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Quick Prompts */}
        <div className="p-4 flex-1 overflow-y-auto">
          <h4 className="font-medium text-gray-900 mb-3">Quick Prompts</h4>
          <div className="space-y-2">
            {quickPrompts.map((prompt, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(prompt)}
                className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-gray-700"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-lg ${agents.find(a => a.id === selectedAgent)?.color || 'bg-gray-500'} flex items-center justify-center text-white`}>
              {agents.find(a => a.id === selectedAgent)?.icon || '🤖'}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">
                {agents.find(a => a.id === selectedAgent)?.name || 'AI Agent'}
              </h3>
              <p className="text-sm text-gray-500">
                {agents.find(a => a.id === selectedAgent)?.description || 'AI Assistant'}
              </p>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {/* Welcome Message */}
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <CpuChipIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-medium text-gray-700 mb-2">
                Ready to help with your social media!
              </h3>
              <p className="text-gray-500 mb-6 max-w-md mx-auto">
                Choose an agent above or let me decide the best one for your task. 
                I can help with strategy, content creation, analytics, and more.
              </p>
            </div>
          )}

          {/* Workflow Progress */}
          <WorkflowProgress 
            workflow={currentWorkflow} 
            queue={agentQueue} 
            completed={completedAgents} 
          />

          {/* Messages */}
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-600 to-gray-800 flex items-center justify-center">
                  <CpuChipIcon className="w-5 h-5 text-white" />
                </div>
                <div className="bg-white rounded-xl px-4 py-3 border border-gray-200 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-gray-600 text-sm">Processing your request...</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 px-6 py-4">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Ask ${agents.find(a => a.id === selectedAgent)?.name || 'AI Agent'} anything...`}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
                rows="1"
                style={{ minHeight: '48px', maxHeight: '120px' }}
                disabled={isLoading}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white p-3 rounded-xl transition-colors flex-shrink-0"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentChat;