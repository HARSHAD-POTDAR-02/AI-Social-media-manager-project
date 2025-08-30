import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader, CheckCircle, Clock } from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentWorkflow, setCurrentWorkflow] = useState(null);
  const [agentQueue, setAgentQueue] = useState([]);
  const [completedAgents, setCompletedAgents] = useState([]);
  const messagesEndRef = useRef(null);

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
      timestamp: new Date()
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
          session_id: `web-${Date.now()}`
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      // Update workflow info
      setCurrentWorkflow(data.workflow_type);
      setAgentQueue(data.agent_queue || []);
      setCompletedAgents(data.agent_responses?.map(r => r.agent) || []);

      // Add bot response
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
        <h3 className="text-sm font-semibold text-blue-800 mb-2">
          Sequential Workflow Progress
        </h3>
        <div className="flex items-center space-x-2">
          {queue.map((agent, index) => {
            const isCompleted = completed.includes(agent);
            const isCurrent = !isCompleted && index === completed.length;
            
            return (
              <div key={`${agent}-${index}`} className="flex items-center">
                <div className={`flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                  isCompleted 
                    ? 'bg-green-100 text-green-800' 
                    : isCurrent 
                    ? 'bg-yellow-100 text-yellow-800' 
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="w-3 h-3 mr-1" />
                  ) : isCurrent ? (
                    <Loader className="w-3 h-3 mr-1 animate-spin" />
                  ) : (
                    <Clock className="w-3 h-3 mr-1" />
                  )}
                  {agent}
                </div>
                {index < queue.length - 1 && (
                  <div className="w-4 h-px bg-gray-300 mx-1"></div>
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
    
    return (
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex items-start space-x-2 max-w-3xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-500' : 'bg-gray-500'
          }`}>
            {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
          </div>
          
          <div className={`rounded-lg px-4 py-2 ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : message.isError 
              ? 'bg-red-100 text-red-800 border border-red-200'
              : 'bg-gray-100 text-gray-800'
          }`}>
            <div className="whitespace-pre-wrap">{message.content}</div>
            
            {/* Show generated content if available */}
            {message.generated_content && (
              <div className="mt-3 p-3 bg-white rounded border">
                <h4 className="font-semibold text-gray-700 mb-2">Generated Content:</h4>
                <div className="text-gray-600 whitespace-pre-wrap">
                  {message.generated_content.content}
                </div>
              </div>
            )}
            
            {/* Show agent responses */}
            {message.agent_responses && message.agent_responses.length > 0 && (
              <div className="mt-3 space-y-2">
                <h4 className="font-semibold text-gray-700">Agent Activities:</h4>
                {message.agent_responses.map((response, index) => (
                  <div key={index} className="text-xs bg-white rounded p-2 border">
                    <span className="font-medium capitalize">{response.agent}:</span> {response.result}
                  </div>
                ))}
              </div>
            )}
            
            <div className="text-xs opacity-70 mt-1">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <h1 className="text-xl font-semibold text-gray-800">
            🎯 AI Social Media Manager
          </h1>
          <p className="text-sm text-gray-600">
            Your intelligent assistant for social media management
          </p>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {/* Welcome Message */}
          {messages.length === 0 && (
            <div className="text-center py-12">
              <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h2 className="text-lg font-medium text-gray-700 mb-2">
                Welcome to AI Social Media Manager!
              </h2>
              <p className="text-gray-500 mb-6">
                Ask me anything about your social media strategy. I can help with content creation, 
                analytics, scheduling, and more.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {[
                  "Create a post about our new product launch",
                  "Analyze our Instagram performance last month",
                  "Generate 5 reel ideas for summer campaign",
                  "Schedule posts for next week across platforms"
                ].map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setInputMessage(example)}
                    className="text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors"
                  >
                    <div className="text-sm text-gray-700">{example}</div>
                  </button>
                ))}
              </div>
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
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-gray-500 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gray-100 rounded-lg px-4 py-2">
                  <div className="flex items-center space-x-2">
                    <Loader className="w-4 h-4 animate-spin" />
                    <span className="text-gray-600">Processing your request...</span>
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
                placeholder="Ask me anything about your social media strategy..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows="1"
                style={{ minHeight: '44px', maxHeight: '120px' }}
                disabled={isLoading}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white p-3 rounded-lg transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;