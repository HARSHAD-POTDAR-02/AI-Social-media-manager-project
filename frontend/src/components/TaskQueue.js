import React, { useState } from 'react';
import { 
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  PlayIcon,
  PauseIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';

const TaskQueue = ({ isPreview = false }) => {
  const [tasks] = useState([
    {
      id: 1,
      title: 'Generate Instagram Reels',
      agent: 'content',
      status: 'running',
      progress: 75,
      startTime: '2:30 PM',
      estimatedCompletion: '3:15 PM'
    },
    {
      id: 2,
      title: 'Analyze Weekly Performance',
      agent: 'analytics',
      status: 'queued',
      progress: 0,
      startTime: '3:15 PM',
      estimatedCompletion: '3:45 PM'
    },
    {
      id: 3,
      title: 'Schedule LinkedIn Posts',
      agent: 'publishing',
      status: 'completed',
      progress: 100,
      startTime: '1:45 PM',
      estimatedCompletion: '2:30 PM'
    }
  ]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <PlayIcon className="w-4 h-4 text-blue-600" />;
      case 'queued':
        return <ClockIcon className="w-4 h-4 text-yellow-600" />;
      case 'completed':
        return <CheckCircleIcon className="w-4 h-4 text-green-600" />;
      case 'paused':
        return <PauseIcon className="w-4 h-4 text-gray-600" />;
      case 'error':
        return <ExclamationCircleIcon className="w-4 h-4 text-red-600" />;
      default:
        return <ClockIcon className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'text-blue-700 bg-blue-100';
      case 'queued':
        return 'text-yellow-700 bg-yellow-100';
      case 'completed':
        return 'text-green-700 bg-green-100';
      case 'paused':
        return 'text-gray-700 bg-gray-100';
      case 'error':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-700 bg-gray-100';
    }
  };

  const getAgentColor = (agent) => {
    const colors = {
      'content': 'bg-green-500',
      'analytics': 'bg-purple-500',
      'publishing': 'bg-orange-500',
      'strategy': 'bg-blue-500',
      'community': 'bg-pink-500'
    };
    return colors[agent] || 'bg-gray-500';
  };

  if (isPreview) {
    return (
      <div>
        <h4 className="font-medium text-gray-900 mb-3 text-sm">Active Tasks</h4>
        <div className="space-y-2">
          {tasks.slice(0, 2).map((task) => (
            <div key={task.id} className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
              <div className={`w-6 h-6 rounded ${getAgentColor(task.agent)} flex items-center justify-center`}>
                <CpuChipIcon className="w-3 h-3 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-gray-900 truncate">{task.title}</p>
                <div className="flex items-center space-x-1">
                  {getStatusIcon(task.status)}
                  <span className="text-xs text-gray-500 capitalize">{task.status}</span>
                </div>
              </div>
            </div>
          ))}
          {tasks.length > 2 && (
            <p className="text-xs text-gray-500 text-center">+{tasks.length - 2} more tasks</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Task Queue</h2>
          <p className="text-gray-600">Monitor and manage your AI agent tasks</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            {tasks.filter(t => t.status === 'running').length} running, 
            {tasks.filter(t => t.status === 'queued').length} queued
          </span>
        </div>
      </div>

      {/* Task List */}
      <div className="space-y-4">
        {tasks.map((task) => (
          <div key={task.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-lg ${getAgentColor(task.agent)} flex items-center justify-center`}>
                  <CpuChipIcon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{task.title}</h3>
                  <p className="text-sm text-gray-500 capitalize">{task.agent} Agent</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                  {getStatusIcon(task.status)}
                  <span className="ml-1 capitalize">{task.status}</span>
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            {task.status === 'running' && (
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>{task.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${task.progress}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Task Details */}
            <div className="flex items-center justify-between text-sm text-gray-500">
              <div className="flex items-center space-x-4">
                <span>Started: {task.startTime}</span>
                <span>ETA: {task.estimatedCompletion}</span>
              </div>
              <div className="flex items-center space-x-2">
                <button className="text-blue-600 hover:text-blue-700 font-medium">
                  View Details
                </button>
                {task.status === 'running' && (
                  <button className="text-red-600 hover:text-red-700 font-medium">
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TaskQueue;