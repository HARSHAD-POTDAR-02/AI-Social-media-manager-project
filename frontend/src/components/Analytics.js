import React, { useState } from 'react';
import { 
  ChartBarIcon, 
  TrendingUpIcon, 
  TrendingDownIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart, 
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7d');
  
  const performanceData = [
    { date: '2025-01-01', engagement: 4200, reach: 12400, impressions: 28000, clicks: 890 },
    { date: '2025-01-02', engagement: 3800, reach: 11200, impressions: 25000, clicks: 750 },
    { date: '2025-01-03', engagement: 5100, reach: 15600, impressions: 32000, clicks: 1200 },
    { date: '2025-01-04', engagement: 4600, reach: 13800, impressions: 29500, clicks: 980 },
    { date: '2025-01-05', engagement: 3900, reach: 12100, impressions: 26800, clicks: 820 },
    { date: '2025-01-06', engagement: 6200, reach: 18900, impressions: 38000, clicks: 1450 },
    { date: '2025-01-07', engagement: 5800, reach: 17200, impressions: 35500, clicks: 1320 }
  ];

  const platformData = [
    { platform: 'Instagram', posts: 45, engagement: 8900, color: '#E1306C' },
    { platform: 'LinkedIn', posts: 28, engagement: 5600, color: '#0077B5' },
    { platform: 'Twitter', posts: 67, engagement: 4200, color: '#1DA1F2' },
    { platform: 'Facebook', posts: 32, engagement: 3800, color: '#1877F2' }
  ];

  const contentTypeData = [
    { type: 'Images', value: 45, color: '#3B82F6' },
    { type: 'Videos', value: 30, color: '#10B981' },
    { type: 'Carousels', value: 15, color: '#F59E0B' },
    { type: 'Stories', value: 10, color: '#8B5CF6' }
  ];

  const topPosts = [
    {
      id: 1,
      platform: 'Instagram',
      content: "Behind the scenes of our latest photoshoot ✨",
      engagement: 2847,
      reach: 15600,
      date: '2025-01-06'
    },
    {
      id: 2,
      platform: 'LinkedIn',
      content: "5 tips for authentic brand storytelling in 2025",
      engagement: 1923,
      reach: 12400,
      date: '2025-01-05'
    },
    {
      id: 3,
      platform: 'Twitter',
      content: "Quick thread on social media trends to watch 🧵",
      engagement: 1654,
      reach: 8900,
      date: '2025-01-04'
    }
  ];

  const metrics = [
    {
      name: 'Total Followers',
      value: '127.5K',
      change: '+2.3K',
      changePercent: '+1.8%',
      changeType: 'increase',
      icon: UserGroupIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      name: 'Avg. Engagement Rate',
      value: '4.2%',
      change: '+0.3%',
      changePercent: '+7.1%',
      changeType: 'increase',
      icon: HeartIcon,
      color: 'text-pink-600',
      bgColor: 'bg-pink-50'
    },
    {
      name: 'Weekly Reach',
      value: '89.2K',
      change: '+12.1K',
      changePercent: '+15.7%',
      changeType: 'increase',
      icon: EyeIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      name: 'Click-through Rate',
      value: '2.8%',
      change: '-0.2%',
      changePercent: '-6.7%',
      changeType: 'decrease',
      icon: ShareIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    }
  ];

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {/* Header with Time Range Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <p className="text-gray-600">Track your social media performance across all platforms</p>
        </div>
        <div className="flex space-x-2">
          {['7d', '30d', '90d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <div key={metric.name} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600">{metric.name}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{metric.value}</p>
                  <div className="flex items-center mt-2">
                    {metric.changeType === 'increase' ? (
                      <TrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
                    ) : (
                      <TrendingDownIcon className="w-4 h-4 text-red-500 mr-1" />
                    )}
                    <span className={`text-sm font-medium ${
                      metric.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {metric.change}
                    </span>
                    <span className="text-sm text-gray-500 ml-1">({metric.changePercent})</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${metric.bgColor}`}>
                  <Icon className={`w-6 h-6 ${metric.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Trends */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Performance Trends</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Area type="monotone" dataKey="engagement" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Area type="monotone" dataKey="reach" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Platform Performance */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Platform Performance</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={platformData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="platform" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar dataKey="engagement" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Content Type Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Content Types</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={contentTypeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={30}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {contentTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 mt-4">
            {contentTypeData.map((item) => (
              <div key={item.type} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: item.color }}></div>
                  <span className="text-sm text-gray-600">{item.type}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Performing Posts */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Top Performing Posts</h3>
          <div className="space-y-4">
            {topPosts.map((post, index) => (
              <div key={post.id} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                  #{index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">{post.platform}</span>
                    <span className="text-xs text-gray-500">{post.date}</span>
                  </div>
                  <p className="text-sm text-gray-700 truncate">{post.content}</p>
                </div>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <HeartIcon className="w-4 h-4" />
                    <span>{post.engagement.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <EyeIcon className="w-4 h-4" />
                    <span>{post.reach.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Insights and Recommendations */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">AI Insights & Recommendations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUpIcon className="w-5 h-5 text-green-600" />
              <span className="font-medium text-green-800">Growth Opportunity</span>
            </div>
            <p className="text-sm text-green-700">
              Video content performs 40% better than images. Consider increasing video posts.
            </p>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <ClockIcon className="w-5 h-5 text-blue-600" />
              <span className="font-medium text-blue-800">Optimal Timing</span>
            </div>
            <p className="text-sm text-blue-700">
              Your audience is most active on weekends between 2-4 PM.
            </p>
          </div>
          
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <ChartBarIcon className="w-5 h-5 text-purple-600" />
              <span className="font-medium text-purple-800">Engagement Boost</span>
            </div>
            <p className="text-sm text-purple-700">
              Posts with questions get 60% more comments. Try adding CTAs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;