import React, { useState } from 'react';
import { 
  ChatBubbleLeftRightIcon,
  HeartIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  SparklesIcon,
  PaperAirplaneIcon
} from '@heroicons/react/24/outline';

const Community = () => {
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [filter, setFilter] = useState('all');

  const conversations = [
    {
      id: 1,
      platform: 'Instagram',
      user: '@sarah_johnson',
      avatar: 'https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=100',
      lastMessage: "Love this new collection! When will it be available in size M?",
      timestamp: '2 min ago',
      status: 'pending',
      sentiment: 'positive',
      priority: 'high',
      postContext: 'Summer Collection Launch'
    },
    {
      id: 2,
      platform: 'LinkedIn',
      user: 'Michael Chen',
      avatar: 'https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?auto=compress&cs=tinysrgb&w=100',
      lastMessage: "Great insights on content strategy! Could you share more about the analytics tools you mentioned?",
      timestamp: '15 min ago',
      status: 'pending',
      sentiment: 'positive',
      priority: 'medium',
      postContext: 'Content Strategy Tips'
    },
    {
      id: 3,
      platform: 'Twitter',
      user: '@designlover',
      avatar: 'https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg?auto=compress&cs=tinysrgb&w=100',
      lastMessage: "The quality seems to have dropped recently. Not happy with my last order.",
      timestamp: '1 hour ago',
      status: 'urgent',
      sentiment: 'negative',
      priority: 'high',
      postContext: 'Product Quality Discussion'
    },
    {
      id: 4,
      platform: 'Facebook',
      user: 'Emma Wilson',
      avatar: 'https://images.pexels.com/photos/1130626/pexels-photo-1130626.jpeg?auto=compress&cs=tinysrgb&w=100',
      lastMessage: "Thank you for the quick response! The issue has been resolved.",
      timestamp: '3 hours ago',
      status: 'resolved',
      sentiment: 'positive',
      priority: 'low',
      postContext: 'Customer Support'
    }
  ];

  const aiSuggestions = [
    "Thank you for your interest! Size M will be available next week. I'll notify you when it's in stock! 🛍️",
    "I appreciate your feedback! I'd be happy to share more details about our analytics approach. Let me send you some resources.",
    "I'm sorry to hear about your experience. Let me connect you with our quality team to resolve this immediately."
  ];

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'negative':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'neutral':
        return 'text-gray-600 bg-gray-50 border-gray-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-700 bg-yellow-100';
      case 'urgent':
        return 'text-red-700 bg-red-100';
      case 'resolved':
        return 'text-green-700 bg-green-100';
      default:
        return 'text-gray-700 bg-gray-100';
    }
  };

  const getPlatformColor = (platform) => {
    const colors = {
      'Instagram': 'bg-pink-500',
      'LinkedIn': 'bg-blue-600',
      'Twitter': 'bg-sky-500',
      'Facebook': 'bg-indigo-600'
    };
    return colors[platform] || 'bg-gray-500';
  };

  const filteredConversations = conversations.filter(conv => {
    if (filter === 'all') return true;
    if (filter === 'pending') return conv.status === 'pending' || conv.status === 'urgent';
    if (filter === 'resolved') return conv.status === 'resolved';
    return conv.sentiment === filter;
  });

  return (
    <div className="p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Community Management</h2>
          <p className="text-gray-600">Manage conversations and engage with your audience</p>
        </div>
        
        {/* Filters */}
        <div className="flex space-x-2">
          {[
            { id: 'all', label: 'All', count: conversations.length },
            { id: 'pending', label: 'Pending', count: conversations.filter(c => c.status === 'pending' || c.status === 'urgent').length },
            { id: 'positive', label: 'Positive', count: conversations.filter(c => c.sentiment === 'positive').length },
            { id: 'negative', label: 'Negative', count: conversations.filter(c => c.sentiment === 'negative').length }
          ].map((filterOption) => (
            <button
              key={filterOption.id}
              onClick={() => setFilter(filterOption.id)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === filterOption.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {filterOption.label} ({filterOption.count})
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Conversations List */}
        <div className="lg:col-span-1 bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900">Conversations</h3>
          </div>
          <div className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
            {filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => setSelectedConversation(conversation)}
                className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                  selectedConversation?.id === conversation.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="relative">
                    <img
                      src={conversation.avatar}
                      alt={conversation.user}
                      className="w-10 h-10 rounded-full object-cover"
                    />
                    <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full ${getPlatformColor(conversation.platform)}`}></div>
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium text-gray-900 text-sm truncate">{conversation.user}</h4>
                      <span className="text-xs text-gray-500">{conversation.timestamp}</span>
                    </div>
                    
                    <p className="text-sm text-gray-600 line-clamp-2 mb-2">{conversation.lastMessage}</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(conversation.status)}`}>
                          {conversation.status}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs border ${getSentimentColor(conversation.sentiment)}`}>
                          {conversation.sentiment}
                        </span>
                      </div>
                      {conversation.priority === 'high' && (
                        <ExclamationTriangleIcon className="w-4 h-4 text-orange-500" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Conversation Detail */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col">
          {selectedConversation ? (
            <>
              {/* Conversation Header */}
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <img
                    src={selectedConversation.avatar}
                    alt={selectedConversation.user}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{selectedConversation.user}</h3>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <span>{selectedConversation.platform}</span>
                      <span>•</span>
                      <span>{selectedConversation.postContext}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedConversation.status)}`}>
                      {selectedConversation.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 p-4 space-y-4 overflow-y-auto">
                {/* User Message */}
                <div className="flex items-start space-x-3">
                  <img
                    src={selectedConversation.avatar}
                    alt={selectedConversation.user}
                    className="w-8 h-8 rounded-full object-cover"
                  />
                  <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-md">
                    <p className="text-sm text-gray-800">{selectedConversation.lastMessage}</p>
                    <span className="text-xs text-gray-500 mt-1 block">{selectedConversation.timestamp}</span>
                  </div>
                </div>
              </div>

              {/* AI Suggestions */}
              <div className="p-4 border-t border-gray-200 bg-gray-50">
                <div className="flex items-center space-x-2 mb-3">
                  <SparklesIcon className="w-4 h-4 text-purple-600" />
                  <h4 className="font-medium text-gray-900 text-sm">AI Suggested Replies</h4>
                </div>
                <div className="space-y-2 mb-4">
                  {aiSuggestions.slice(0, 2).map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setReplyText(suggestion)}
                      className="w-full text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all text-sm"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>

              {/* Reply Input */}
              <div className="p-4 border-t border-gray-200">
                <div className="flex items-end space-x-3">
                  <div className="flex-1">
                    <textarea
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      placeholder="Type your reply..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      rows="2"
                    />
                  </div>
                  <button
                    onClick={() => {
                      // Handle reply logic here
                      setReplyText('');
                    }}
                    disabled={!replyText.trim()}
                    className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white p-3 rounded-lg transition-colors"
                  >
                    <PaperAirplaneIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <ChatBubbleLeftRightIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select a conversation to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-2">
            <ChatBubbleLeftRightIcon className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-900">Total Messages</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">247</p>
          <p className="text-sm text-green-600">+12% this week</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-2">
            <ClockIcon className="w-5 h-5 text-yellow-600" />
            <span className="font-medium text-gray-900">Avg Response Time</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">12m</p>
          <p className="text-sm text-green-600">-3m improvement</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-2">
            <HeartIcon className="w-5 h-5 text-pink-600" />
            <span className="font-medium text-gray-900">Satisfaction Rate</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">94%</p>
          <p className="text-sm text-green-600">+2% this month</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-2">
            <CheckCircleIcon className="w-5 h-5 text-green-600" />
            <span className="font-medium text-gray-900">Resolution Rate</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">89%</p>
          <p className="text-sm text-green-600">+5% this month</p>
        </div>
      </div>
    </div>
  );
};

export default Community;