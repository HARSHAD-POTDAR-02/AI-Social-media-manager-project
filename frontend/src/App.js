import React, { useState } from 'react';
import { 
  HomeIcon, 
  ChatBubbleLeftRightIcon, 
  CalendarIcon, 
  ChartBarIcon, 
  UserGroupIcon,
  CogIcon,
  BellIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { 
  HomeIcon as HomeSolid,
  ChatBubbleLeftRightIcon as ChatSolid,
  CalendarIcon as CalendarSolid,
  ChartBarIcon as ChartSolid,
  UserGroupIcon as UserGroupSolid
} from '@heroicons/react/24/solid';
import './App.css';

// Import components
import Dashboard from './components/Dashboard';
import AgentChat from './components/AgentChat';
import Calendar from './components/Calendar';
import ContentCalendar from './components/ContentCalendar';
import Analytics from './components/Analytics';
import Community from './components/Community';
import TaskQueue from './components/TaskQueue';



function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [notifications] = useState([
    { id: 1, message: "Content strategy updated", time: "2 min ago", type: "info" },
    { id: 2, message: "New comment on Instagram post", time: "5 min ago", type: "engagement" },
    { id: 3, message: "Analytics report ready", time: "10 min ago", type: "analytics" }
  ]);
  const [showNotifications, setShowNotifications] = useState(false);

  const navigation = [
    { 
      name: 'Dashboard', 
      id: 'dashboard', 
      icon: HomeIcon, 
      iconSolid: HomeSolid,
      description: 'Overview & insights'
    },
    { 
      name: 'AI Agents', 
      id: 'agents', 
      icon: ChatBubbleLeftRightIcon, 
      iconSolid: ChatSolid,
      description: 'Chat with AI agents'
    },
    { 
      name: 'Content Calendar', 
      id: 'calendar', 
      icon: CalendarIcon, 
      iconSolid: CalendarSolid,
      description: 'Schedule & manage posts'
    },
    { 
      name: 'Analytics', 
      id: 'analytics', 
      icon: ChartBarIcon, 
      iconSolid: ChartSolid,
      description: 'Performance metrics'
    }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard onNavigate={setActiveTab} />;
      case 'agents':
        return <AgentChat />;
      case 'calendar':
        return <ContentCalendar />;
      case 'analytics':
        return <Analytics />;
      case 'community':
        return <Community />;
      default:
        return <Dashboard onNavigate={setActiveTab} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg border-r border-gray-200">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">AI</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Social Manager</h1>
              <p className="text-xs text-gray-500">AI-Powered Platform</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = activeTab === item.id ? item.iconSolid : item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                  activeTab === item.id
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                <div>
                  <div className="font-medium">{item.name}</div>
                  <div className="text-xs text-gray-500">{item.description}</div>
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 capitalize">
                {navigation.find(nav => nav.id === activeTab)?.name || 'Dashboard'}
              </h2>
              <p className="text-sm text-gray-500">
                {navigation.find(nav => nav.id === activeTab)?.description}
              </p>
            </div>
            

          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-hidden">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;