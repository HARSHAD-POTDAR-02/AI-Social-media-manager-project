import React, { useState, useEffect } from 'react';
import { instagramService } from '../services/instagram';
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  UserGroupIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { 
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [performanceData, setPerformanceData] = useState([
    { date: '2025-01-01', engagement: 4200, reach: 12400, impressions: 28000, clicks: 890 },
    { date: '2025-01-02', engagement: 3800, reach: 11200, impressions: 25000, clicks: 750 },
    { date: '2025-01-03', engagement: 5100, reach: 15600, impressions: 32000, clicks: 1200 },
    { date: '2025-01-04', engagement: 4600, reach: 13800, impressions: 29500, clicks: 980 },
    { date: '2025-01-05', engagement: 3900, reach: 12100, impressions: 26800, clicks: 820 },
    { date: '2025-01-06', engagement: 6200, reach: 18900, impressions: 38000, clicks: 1450 },
    { date: '2025-01-07', engagement: 5800, reach: 17200, impressions: 35500, clicks: 1320 }
  ]);
  
  const [metrics, setMetrics] = useState([]);
  const [topPosts, setTopPosts] = useState([]);
  
  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);
  
  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Fetch Instagram data
      const accountResponse = await instagramService.getAccountInfo();
      const mediaResponse = await instagramService.getMediaList(25);
      const topPostsResponse = await instagramService.getTopPosts(10);
      
      if (accountResponse.success && mediaResponse.success) {
        const account = accountResponse.data;
        const posts = mediaResponse.data.data || [];
        
        // Calculate metrics
        const totalLikes = posts.reduce((sum, post) => sum + (post.like_count || 0), 0);
        const totalComments = posts.reduce((sum, post) => sum + (post.comments_count || 0), 0);
        const totalEngagement = totalLikes + totalComments;
        const avgEngagementRate = account.followers_count > 0 ? 
          ((totalEngagement / (posts.length * account.followers_count)) * 100) : 0;
        
        // Update metrics
        setMetrics([
          {
            name: 'Total Followers',
            value: formatNumber(account.followers_count),
            change: '+2.3%',
            changePercent: '+1.8%',
            changeType: 'increase',
            icon: UserGroupIcon,
            color: 'text-blue-600',
            bgColor: 'bg-blue-50'
          },
          {
            name: 'Avg. Engagement Rate',
            value: avgEngagementRate.toFixed(1) + '%',
            change: '+0.3%',
            changePercent: '+7.1%',
            changeType: 'increase',
            icon: HeartIcon,
            color: 'text-pink-600',
            bgColor: 'bg-pink-50'
          },
          {
            name: 'Total Posts',
            value: formatNumber(account.media_count),
            change: 'Active',
            changePercent: '',
            changeType: 'increase',
            icon: EyeIcon,
            color: 'text-green-600',
            bgColor: 'bg-green-50'
          },
          {
            name: 'Total Engagement',
            value: formatNumber(totalEngagement),
            change: formatNumber(totalLikes) + ' likes',
            changePercent: '',
            changeType: 'increase',
            icon: ShareIcon,
            color: 'text-purple-600',
            bgColor: 'bg-purple-50'
          }
        ]);
        
        // Update platform data with real Instagram data
        setPlatformData([
          { platform: 'Instagram', posts: account.media_count, engagement: totalEngagement, color: '#E1306C' },
          { platform: 'LinkedIn', posts: 0, engagement: 0, color: '#0077B5' },
          { platform: 'Twitter', posts: 0, engagement: 0, color: '#1DA1F2' },
          { platform: 'Facebook', posts: 0, engagement: 0, color: '#1877F2' }
        ]);
        
        // Create real performance data from recent posts
        const recentPosts = posts.slice(0, 7);
        const realPerformanceData = recentPosts.map((post) => ({
          date: new Date(post.timestamp).toLocaleDateString(),
          engagement: (post.like_count || 0) + (post.comments_count || 0),
          reach: 0,
          impressions: 0
        }));
        
        setPerformanceData(realPerformanceData.length > 0 ? realPerformanceData : [
          { date: 'No Data', engagement: 0, reach: 0, impressions: 0 }
        ]);
        
        // Calculate real content type distribution
        const imageCount = posts.filter(post => post.media_type === 'IMAGE').length;
        const videoCount = posts.filter(post => post.media_type === 'VIDEO').length;
        const carouselCount = posts.filter(post => post.media_type === 'CAROUSEL_ALBUM').length;
        const totalPosts = posts.length;
        
        if (totalPosts > 0) {
          setContentTypeData([
            { type: 'Images', value: Math.round((imageCount / totalPosts) * 100), color: '#3B82F6' },
            { type: 'Videos', value: Math.round((videoCount / totalPosts) * 100), color: '#10B981' },
            { type: 'Carousels', value: Math.round((carouselCount / totalPosts) * 100), color: '#F59E0B' },
            { type: 'Stories', value: 0, color: '#8B5CF6' }
          ]);
        }
      }
      
      // Update top posts
      if (topPostsResponse.success) {
        setTopPosts(topPostsResponse.data.slice(0, 3).map((post, index) => ({
          id: index + 1,
          platform: 'Instagram',
          content: post.caption || 'No caption',
          engagement: post.engagement,
          reach: post.engagement * 5, // Estimated reach
          date: new Date(post.timestamp).toLocaleDateString()
        })));
      }
      
    } catch (err) {
      console.error('Analytics error:', err);
      console.error('Error details:', err.response?.data);
      setError(`Failed to load analytics data: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };
  
  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const [platformData, setPlatformData] = useState([
    { platform: 'Instagram', posts: 0, engagement: 0, color: '#E1306C' },
    { platform: 'LinkedIn', posts: 0, engagement: 0, color: '#0077B5' },
    { platform: 'Twitter', posts: 0, engagement: 0, color: '#1DA1F2' },
    { platform: 'Facebook', posts: 0, engagement: 0, color: '#1877F2' }
  ]);

  const [contentTypeData, setContentTypeData] = useState([
    { type: 'Images', value: 0, color: '#3B82F6' },
    { type: 'Videos', value: 0, color: '#10B981' },
    { type: 'Carousels', value: 0, color: '#F59E0B' },
    { type: 'Stories', value: 0, color: '#8B5CF6' }
  ]);



  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={fetchAnalyticsData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

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
                      <ArrowTrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
                    ) : (
                      <ArrowTrendingDownIcon className="w-4 h-4 text-red-500 mr-1" />
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
              <ArrowTrendingUpIcon className="w-5 h-5 text-green-600" />
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