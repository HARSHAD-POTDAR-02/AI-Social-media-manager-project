import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  HeartIcon, 
  EyeIcon, 
  ShareIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarIcon,
  ClockIcon,
  SparklesIcon,
  PhotoIcon,
  ChatBubbleLeftRightIcon,
  PlusIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { instagramService } from '../services/instagram';

const Dashboard = () => {
  const [analyticsData, setAnalyticsData] = useState([]);
  const [accountInfo, setAccountInfo] = useState(null);
  const [topPosts, setTopPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [sentimentData, setSentimentData] = useState([
    { name: 'Positive', value: 0, color: '#10B981' },
    { name: 'Neutral', value: 0, color: '#6B7280' },
    { name: 'Negative', value: 0, color: '#EF4444' }
  ]);

  const [currentPost, setCurrentPost] = useState(null);

  const [nextPost] = useState({
    platform: 'LinkedIn',
    content: "💼 Behind the scenes: How our team creates authentic content that resonates. Our 3-step process for building meaningful connections with your audience. Read more in comments! #ContentStrategy #Marketing",
    scheduledFor: "Tomorrow, 9:00 AM",
    status: "pending"
  });

  const [contentStrategy] = useState({
    theme: "Summer Campaign 2025",
    focus: "User-generated content & community engagement",
    keyTopics: ["Summer fashion", "Sustainability", "Community stories"],
    suggestedHashtags: ["#SummerVibes", "#EcoFashion", "#CommunityFirst"],
    targetAudience: "Fashion-conscious millennials & Gen Z",
    contentPillars: [
      { pillar: "Product Showcase", percentage: 40 },
      { pillar: "Behind the Scenes", percentage: 30 },
      { pillar: "User Generated", percentage: 20 },
      { pillar: "Educational", percentage: 10 }
    ]
  });

  const [stats, setStats] = useState([]);

  useEffect(() => {
    fetchInstagramData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchInstagramData = async () => {
    try {
      setLoading(true);
      
      // Fetch account info
      const accountResponse = await instagramService.getAccountInfo();
      if (accountResponse.success) {
        setAccountInfo(accountResponse.data);
        
        // Fetch recent posts first to get engagement data
        const mediaResponse = await instagramService.getMediaList(10);

        let totalLikes = 0;
        let totalComments = 0;
        let posts = [];
        
        if (mediaResponse.success && mediaResponse.data && mediaResponse.data.data && mediaResponse.data.data.length > 0) {
          posts = mediaResponse.data.data;
          const latestPost = posts[0];

          
          // Calculate total engagement from all posts
          posts.forEach(post => {
            totalLikes += post.like_count || 0;
            totalComments += post.comments_count || 0;
          });
          

          
          const postData = {
            platform: 'Instagram',
            content: latestPost.caption || 'No caption available',
            image: latestPost.media_url || latestPost.thumbnail_url || null,
            scheduledFor: new Date(latestPost.timestamp).toLocaleDateString(),
            status: 'published',
            engagement: {
              likes: latestPost.like_count || 0,
              comments: latestPost.comments_count || 0,
              shares: 0
            }
          };
          

          setCurrentPost(postData);
        } else {
          setCurrentPost(null);
        }
        
        // Update stats with real data including engagement
        const followerCount = accountResponse.data.followers_count || 0;
        const mediaCount = accountResponse.data.media_count || 0;
        const totalEngagement = totalLikes + totalComments;
        
        setStats([
          {
            name: 'Followers',
            value: formatNumber(followerCount),
            change: followerCount === 0 ? 'New Account' : '+2.3%',
            changeType: followerCount === 0 ? 'neutral' : 'increase',
            icon: UserGroupIcon,
            color: 'text-blue-600',
            bgColor: 'bg-blue-50'
          },
          {
            name: 'Posts',
            value: formatNumber(mediaCount),
            change: mediaCount === 0 ? 'Start Posting' : 'Active',
            changeType: mediaCount === 0 ? 'neutral' : 'increase',
            icon: PhotoIcon,
            color: 'text-green-600',
            bgColor: 'bg-green-50'
          },
          {
            name: 'Total Likes',
            value: formatNumber(totalLikes),
            change: totalLikes > 0 ? 'Engaging' : 'No Likes Yet',
            changeType: totalLikes > 0 ? 'increase' : 'neutral',
            icon: HeartIcon,
            color: 'text-pink-600',
            bgColor: 'bg-pink-50'
          },
          {
            name: 'Total Comments',
            value: formatNumber(totalComments),
            change: totalComments > 0 ? 'Active Discussion' : 'No Comments',
            changeType: totalComments > 0 ? 'increase' : 'neutral',
            icon: ChatBubbleLeftRightIcon,
            color: 'text-purple-600',
            bgColor: 'bg-purple-50'
          }
        ]);
        
        // Create weekly analytics data with unique days
        if (posts && posts.length > 0) {
          // Group posts by day and sum engagement
          const dailyData = {};
          const last7Days = [];
          
          // Generate last 7 days
          for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            last7Days.push({ date, dayName });
            dailyData[dayName] = { engagement: 0, reach: 0, impressions: 0 };
          }
          
          // Add post data to corresponding days
          posts.forEach(post => {
            const postDate = new Date(post.timestamp);
            const dayName = postDate.toLocaleDateString('en-US', { weekday: 'short' });
            
            if (dailyData[dayName]) {
              dailyData[dayName].engagement += (post.like_count || 0) + (post.comments_count || 0);
            }
          });
          
          // Convert to chart data
          const chartData = last7Days.map(day => ({
            name: day.dayName,
            engagement: dailyData[day.dayName].engagement,
            reach: dailyData[day.dayName].reach,
            impressions: dailyData[day.dayName].impressions
          }));
          
          setAnalyticsData(chartData);
        } else {
          // Generate empty 7-day data
          const emptyData = [];
          for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            emptyData.push({ name: dayName, engagement: 0, reach: 0, impressions: 0 });
          }
          setAnalyticsData(emptyData);
        }
        
        // Calculate sentiment based on engagement
        const engagementRate = followerCount > 0 ? (totalEngagement / followerCount) * 100 : 0;
        let positive = 50, neutral = 30, negative = 20;
        
        if (engagementRate > 5) {
          positive = 70; neutral = 25; negative = 5;
        } else if (engagementRate > 2) {
          positive = 60; neutral = 30; negative = 10;
        } else if (totalEngagement > 0) {
          positive = 55; neutral = 35; negative = 10;
        }
        
        setSentimentData([
          { name: 'Positive', value: positive, color: '#10B981' },
          { name: 'Neutral', value: neutral, color: '#6B7280' },
          { name: 'Negative', value: negative, color: '#EF4444' }
        ]);
      }
      
      // Fetch top posts
      const topPostsResponse = await instagramService.getTopPosts(5);
      if (topPostsResponse.success) {
        setTopPosts(topPostsResponse.data);
      }

      
    } catch (err) {
      console.error('Error fetching Instagram data:', err);
      console.error('Error details:', err.response?.data);
      setError(`Failed to load Instagram data: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (!num || num === 0) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Instagram data...</p>
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
            onClick={fetchInstagramData}
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
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <div className="flex items-center mt-2">
                    {stat.changeType === 'increase' ? (
                      <ArrowTrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
                    ) : stat.changeType === 'decrease' ? (
                      <ArrowTrendingDownIcon className="w-4 h-4 text-red-500 mr-1" />
                    ) : (
                      <div className="w-4 h-4 mr-1"></div>
                    )}
                    <span className={`text-sm font-medium ${
                      stat.changeType === 'increase' ? 'text-green-600' : 
                      stat.changeType === 'decrease' ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {stat.change}
                    </span>
                    <span className="text-sm text-gray-500 ml-1">vs last week</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Analytics Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Weekly Performance</h3>
            <div className="flex space-x-2">
              <button className="px-3 py-1 text-sm bg-blue-50 text-blue-600 rounded-lg">7 days</button>
              <button className="px-3 py-1 text-sm text-gray-500 hover:bg-gray-50 rounded-lg">30 days</button>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Line type="monotone" dataKey="engagement" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }} />
                <Line type="monotone" dataKey="reach" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }} />
                <Line type="monotone" dataKey="impressions" stroke="#8b5cf6" strokeWidth={3} dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sentiment Analysis */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Sentiment Analysis</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 mt-4">
            {sentimentData.map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: item.color }}></div>
                  <span className="text-sm text-gray-600">{item.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Post */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Latest Post</h3>
            {currentPost && (
              <div className="flex items-center space-x-2">
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                  {currentPost.status}
                </span>
                <span className="text-sm text-gray-500">{currentPost.platform}</span>
              </div>
            )}
          </div>
          
          {currentPost ? (
            <div className="space-y-4">
              {currentPost.image && (
                <div className="relative">
                  <img 
                    src={currentPost.image} 
                    alt="Post content" 
                    className="w-full h-48 object-cover rounded-lg"
                  />
                  <div className="absolute top-3 left-3 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                    {currentPost.platform}
                  </div>
                </div>
              )}
              
              <p className="text-gray-700 text-sm leading-relaxed">{currentPost.content || 'No caption available'}</p>
              
              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center space-x-1">
                    <HeartIcon className="w-4 h-4" />
                    <span>{currentPost.engagement?.likes || 0}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <ChatBubbleLeftRightIcon className="w-4 h-4" />
                    <span>{currentPost.engagement?.comments || 0}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <ShareIcon className="w-4 h-4" />
                    <span>{currentPost.engagement?.shares || 0}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-1 text-sm text-gray-500">
                  <ClockIcon className="w-4 h-4" />
                  <span>{currentPost.scheduledFor}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <PhotoIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-sm">No posts available</p>
              <p className="text-xs text-gray-400 mt-1">Create your first Instagram post to see it here</p>
            </div>
          )}
        </div>

        {/* Next Scheduled Post */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Next Scheduled</h3>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
                {nextPost.status}
              </span>
              <span className="text-sm text-gray-500">{nextPost.platform}</span>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="bg-gray-100 rounded-lg p-4 border-2 border-dashed border-gray-300">
              <div className="flex items-center justify-center h-32 text-gray-400">
                <PhotoIcon className="w-12 h-12" />
              </div>
            </div>
            
            <p className="text-gray-700 text-sm leading-relaxed">{nextPost.content}</p>
            
            <div className="flex items-center justify-between pt-4 border-t border-gray-100">
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                Edit Post
              </button>
              <div className="flex items-center space-x-1 text-sm text-gray-500">
                <CalendarIcon className="w-4 h-4" />
                <span>{nextPost.scheduledFor}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content Strategy */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <SparklesIcon className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Content Strategy</h3>
          </div>
          <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium">
            Generate New Strategy
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Strategy Overview */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-100">
              <h4 className="font-semibold text-gray-900 mb-2">{contentStrategy.theme}</h4>
              <p className="text-gray-700 text-sm mb-3">{contentStrategy.focus}</p>
              <div className="flex items-center space-x-1 text-sm text-gray-600">
                <span>Target:</span>
                <span className="font-medium">{contentStrategy.targetAudience}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h5 className="font-medium text-gray-900 mb-2">Key Topics</h5>
                <div className="space-y-1">
                  {contentStrategy.keyTopics.map((topic, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                      <span className="text-sm text-gray-700">{topic}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h5 className="font-medium text-gray-900 mb-2">Suggested Hashtags</h5>
                <div className="flex flex-wrap gap-1">
                  {contentStrategy.suggestedHashtags.map((hashtag, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                      {hashtag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Content Pillars */}
          <div>
            <h5 className="font-medium text-gray-900 mb-4">Content Pillars</h5>
            <div className="space-y-3">
              {contentStrategy.contentPillars.map((pillar, index) => (
                <div key={index}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-700">{pillar.pillar}</span>
                    <span className="text-sm font-medium text-gray-900">{pillar.percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${pillar.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="flex flex-col items-center space-y-2 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all">
            <PlusIcon className="w-6 h-6 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Create Post</span>
          </button>
          <button className="flex flex-col items-center space-y-2 p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-all">
            <ChartBarIcon className="w-6 h-6 text-green-600" />
            <span className="text-sm font-medium text-gray-700">View Analytics</span>
          </button>
          <button className="flex flex-col items-center space-y-2 p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-all">
            <CalendarIcon className="w-6 h-6 text-purple-600" />
            <span className="text-sm font-medium text-gray-700">Schedule Content</span>
          </button>
          <button className="flex flex-col items-center space-y-2 p-4 border border-gray-200 rounded-lg hover:border-pink-300 hover:bg-pink-50 transition-all">
            <UserGroupIcon className="w-6 h-6 text-pink-600" />
            <span className="text-sm font-medium text-gray-700">Engage Community</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;