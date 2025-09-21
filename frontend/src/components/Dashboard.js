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
import { cacheService } from '../services/cache';

const Dashboard = ({ onNavigate }) => {
  const [analyticsData, setAnalyticsData] = useState([]);
  const [accountInfo, setAccountInfo] = useState(null);
  const [topPosts, setTopPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [error, setError] = useState(null);
  const [dataLoaded, setDataLoaded] = useState(false);
  const [allPosts, setAllPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [postInsights, setPostInsights] = useState(null);

  const [sentimentData, setSentimentData] = useState([
    { name: 'Positive', value: 70, color: '#10B981' },
    { name: 'Neutral', value: 25, color: '#6B7280' },
    { name: 'Negative', value: 5, color: '#EF4444' }
  ]);

  const [currentPost, setCurrentPost] = useState(null);
  const [nextPost, setNextPost] = useState(null);
  const [stats, setStats] = useState([]);

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

  useEffect(() => {
    loadDefaultData();
    
    const timer = setTimeout(() => {
      if (!dataLoaded) {
        fetchInstagramData();
        fetchNextScheduledPost();
      }
    }, 100);
    
    const interval = setInterval(fetchNextScheduledPost, 30000);
    
    return () => {
      clearTimeout(timer);
      clearInterval(interval);
    };
  }, []);

  const loadDefaultData = () => {
    setStats([
      {
        name: 'Followers',
        value: '...',
        change: 'Loading...',
        changeType: 'neutral',
        icon: UserGroupIcon,
        color: 'text-blue-600',
        bgColor: 'bg-blue-50'
      },
      {
        name: 'Posts',
        value: '...',
        change: 'Loading...',
        changeType: 'neutral',
        icon: PhotoIcon,
        color: 'text-green-600',
        bgColor: 'bg-green-50'
      },
      {
        name: 'Total Likes',
        value: '...',
        change: 'Loading...',
        changeType: 'neutral',
        icon: HeartIcon,
        color: 'text-pink-600',
        bgColor: 'bg-pink-50'
      },
      {
        name: 'Total Comments',
        value: '...',
        change: 'Loading...',
        changeType: 'neutral',
        icon: ChatBubbleLeftRightIcon,
        color: 'text-purple-600',
        bgColor: 'bg-purple-50'
      }
    ]);
    
    const emptyData = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
      emptyData.push({ name: dayName, engagement: 0, reach: 0, impressions: 0, views: 0 });
    }
    setAnalyticsData(emptyData);
  };

  const fetchInstagramData = async () => {
    try {
      setLoading(true);
      setLoadingProgress(10);
      
      const cachedData = cacheService.get('dashboard_data');
      if (cachedData) {
        processDashboardData(cachedData);
        setDataLoaded(true);
        setLoading(false);
        return;
      }
      
      const response = await fetch('http://localhost:8000/dashboard/data', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(25000)
      });
      
      setLoadingProgress(50);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      setLoadingProgress(70);
      
      if (!result.success) {
        throw new Error('Dashboard data fetch failed');
      }
      
      cacheService.set('dashboard_data', result, 3 * 60 * 1000);
      processDashboardData(result);
      setLoadingProgress(100);
      setDataLoaded(true);
      
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      let errorMessage = 'Failed to load Instagram data';
      
      if (err.name === 'TimeoutError' || err.message.includes('timeout')) {
        errorMessage = 'Request timed out after 25 seconds. The Instagram API is slow. Please try again.';
      } else if (err.message.includes('Failed to fetch')) {
        errorMessage = 'Network error. Please check your connection and try again.';
      } else {
        errorMessage = `Failed to load data: ${err.message}`;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
      setLoadingProgress(0);
    }
  };

  const processDashboardData = (result) => {
    const { account, media, top_posts, sentiment } = result.data;
    
    if (account.success) {
      setAccountInfo(account.data);
      
      let totalLikes = 0;
      let totalComments = 0;
      let posts = [];
      
      if (media.success && media.data?.data?.length > 0) {
        posts = media.data.data.map(p => {
          // Normalize timestamp field to be flexible with backend names
          const timestamp = p.timestamp || p.created_time || p.published_at || p.date || null;
          return { ...p, timestamp };
        });
        setAllPosts(posts);
        const latestPost = posts[0];
        
        posts.forEach(post => {
          totalLikes += post.like_count || 0;
          totalComments += post.comments_count || 0;
        });
        
        setCurrentPost({
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
        });
      }
      
      const followerCount = account.data.followers_count || 0;
      const mediaCount = account.data.media_count || 0;
      
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
      
      // Fetch real weekly insights data
      fetchWeeklyInsights();
    }
    
    if (top_posts.success) {
      setTopPosts(top_posts.data);
    }
    
    if (sentiment.success && sentiment.data) {
      const data = sentiment.data;
      let positive = Math.max(data.positive_percentage || 0, 0);
      let neutral = Math.max(data.neutral_percentage || 0, 0);
      let negative = Math.max(data.negative_percentage || 0, 0);
      
      if (data.total_comments === 0 || positive + neutral + negative === 0) {
        positive = 0;
        neutral = 100;
        negative = 0;
      }
      
      setSentimentData([
        { name: 'Positive', value: positive, color: '#10B981' },
        { name: 'Neutral', value: neutral, color: '#6B7280' },
        { name: 'Negative', value: negative, color: '#EF4444' }
      ]);
    }
  };

  const fetchPostInsights = async (postId) => {
    try {
      const response = await fetch(`http://localhost:8000/instagram/insights/media/${postId}`);
      if (response.ok) {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.error('Error fetching post insights:', error);
    }
  };
  
  const fetchWeeklyInsights = async () => {
    try {
      // Prefer server-provided weekly insights when available
      const response = await fetch('http://localhost:8000/instagram/insights/performance');
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data && Array.isArray(result.data) && result.data.length > 0) {
          const normalized = normalizePerformanceData(result.data);
          setAnalyticsData(ensureSevenDays(normalized));
          return;
        }
      }

      // Fallback: compute weekly per-day engagement and views from local media list
  const aggregated = await computeWeeklyFromPosts(allPosts);
  setAnalyticsData(ensureSevenDays(aggregated));
    } catch (error) {
      console.error('Error fetching weekly insights:', error);
    }
  };

  // Normalize different backend shapes to chart-friendly array
  const normalizePerformanceData = (arr) => {
    // arr: array of objects possibly shaped as { name, date, end_time, engagement, reach, impressions, views }
    return arr.map(item => {
      let name = item.name || item.day || item.label || null;
      // handle date fields
      if (!name) {
        const dateStr = item.date || item.end_time || item.timestamp || item.time || null;
        if (dateStr) {
          const d = new Date(dateStr);
          if (!isNaN(d)) name = d.toLocaleDateString('en-US', { weekday: 'short' });
        }
      }
      if (!name) name = item.label || '';

      const engagement = Number(item.engagement ?? item.total_engagement ?? item.engagements ?? 0) || 0;
      const reach = Number(item.reach ?? item.total_reach ?? item.reach_count ?? 0) || 0;
      const impressions = Number(item.impressions ?? item.total_impressions ?? 0) || 0;
      const views = Number(item.views ?? item.total_views ?? item.video_views ?? item.view_count ?? 0) || 0;

      return { name, engagement, reach, impressions, views };
    });
  };

  // Ensure array contains exactly 7 daily entries (from 6 days ago to today)
  const ensureSevenDays = (dataArr) => {
    if (!Array.isArray(dataArr)) return [];
    if (dataArr.length === 7) return dataArr;

    // Build default 7-day template
    const template = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const name = d.toLocaleDateString('en-US', { weekday: 'short' });
      template.push({ name, engagement: 0, reach: 0, impressions: 0, views: 0 });
    }

    // Map provided data by name (best-effort) and merge into template
    const mapByName = {};
    dataArr.forEach(item => {
      if (!item) return;
      const n = item.name || item.day || item.label;
      if (n) mapByName[n] = item;
    });

    const merged = template.map(t => {
      const src = mapByName[t.name];
      if (!src) return t;
      return {
        name: t.name,
        engagement: Number(src.engagement ?? src.total_engagement ?? 0) || 0,
        reach: Number(src.reach ?? 0) || 0,
        impressions: Number(src.impressions ?? 0) || 0,
        views: Number(src.views ?? 0) || 0
      };
    });

    return merged;
  };

  // Helper: aggregate last 7 days' engagement and views from posts
  const computeWeeklyFromPosts = async (posts) => {
    // Build 7-day buckets (from 6 days ago to today)
    const buckets = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setHours(0,0,0,0);
      date.setDate(date.getDate() - i);
      const dayKey = date.toISOString().slice(0,10); // YYYY-MM-DD
      const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
      buckets.push({ key: dayKey, name: dayName, engagement: 0, reach: 0, impressions: 0, views: 0 });
    }

    if (!posts || posts.length === 0) return buckets.map(b => ({ name: b.name, engagement: 0, reach: 0, impressions: 0, views: 0 }));

    // Map posts by day; for posts missing views, fetch per-post insights (but only once per post)
    const insightsCache = {};

    const needToFetch = [];
    posts.forEach(post => {
      const ts = post.timestamp || post.created_time || post.published_at || post.date || null;
      if (!ts) return;
      const postDate = new Date(ts);
      postDate.setHours(0,0,0,0);
      const key = postDate.toISOString().slice(0,10);
      const bucket = buckets.find(b => b.key === key);
      if (!bucket) return; // outside 7-day window

      const likes = post.like_count || post.likes_count || (post.engagement?.likes) || 0;
      const comments = post.comments_count || post.comments || (post.engagement?.comments) || 0;
      const engagement = (likes || 0) + (comments || 0);
      bucket.engagement += engagement;

      // Prefer direct per-post view fields when available
      const directFields = ['views','view_count','video_views','play_count','impressions','reach'];
      let directView = null;
      for (const f of directFields) {
        if (typeof post[f] === 'number') { directView = post[f]; break; }
      }
      if (directView !== null) {
        bucket.views += directView;
      } else {
        // No direct view field present. Only fetch insights for IMAGE or CAROUSEL posts.
        if ((post.media_type === 'IMAGE' || post.media_type === 'CAROUSEL_ALBUM') && post.id) {
          needToFetch.push({ id: post.id, bucketKey: key, media_type: post.media_type });
        }
        // For videos with no direct field, skip fetching to avoid triggering unsupported video_views metric
      }
    });

    // Fetch insights for posts that need views (limit to avoid many calls)
    const uniqueFetchById = {};
  // Only fetch insights for unique IDs (we already limited to image/carousel posts when adding to needToFetch)
  needToFetch.forEach(item => { uniqueFetchById[item.id] = true; });
    const idsToFetch = Object.keys(uniqueFetchById).slice(0, 30); // cap to 30 calls

    await Promise.all(idsToFetch.map(async (id) => {
      try {
        const res = await fetch(`http://localhost:8000/instagram/insights/media/${id}`);
        if (!res.ok) return;
        const json = await res.json();
        // Expecting structure { success: true, data: [ { name: 'video_views', values: [{value: N}] }, ... ] }
          if (json && json.success && Array.isArray(json.data)) {
            insightsCache[id] = json.data;
          }
      } catch (err) {
        // ignore per-post fetch errors
      }
    }));

    // Apply fetched insights to buckets — prefer impressions/reach for images
    needToFetch.forEach(item => {
      const insights = insightsCache[item.id];
      if (!insights) return;
      let viewsValue = 0;
      // prefer impressions/reach for image/carousel posts
      const impressionsInsight = insights.find(i => /impression/i.test(i.name));
      const reachInsight = insights.find(i => /reach/i.test(i.name));
      const viewLikeInsight = impressionsInsight || reachInsight || insights.find(i => /view/i.test(i.name) || /plays?/i.test(i.name) || /video_views/i.test(i.name));
      if (viewLikeInsight && Array.isArray(viewLikeInsight.values)) {
        const lastVal = viewLikeInsight.values[viewLikeInsight.values.length - 1];
        viewsValue = (lastVal && typeof lastVal.value === 'number') ? lastVal.value : (lastVal && lastVal.value && lastVal.value.total) || 0;
      }
      const bucket = buckets.find(b => b.key === item.bucketKey);
      if (bucket) bucket.views += viewsValue || 0;
    });

    // Transform to chart-friendly shape (name, engagement, reach, impressions, views)
    return buckets.map(b => ({ name: b.name, engagement: b.engagement, reach: b.reach || 0, impressions: b.impressions || 0, views: b.views }));
  };

  const fetchNextScheduledPost = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/scheduled-posts');
      if (response.ok) {
        const result = await response.json();
        const scheduledPosts = result.data || [];
        
        const now = new Date();
        const futurePosts = scheduledPosts
          .filter(post => post.status === 'scheduled')
          .filter(post => new Date(post.scheduled_time) > now)
          .sort((a, b) => new Date(a.scheduled_time) - new Date(b.scheduled_time));
        
        if (futurePosts.length > 0) {
          const next = futurePosts[0];
          setNextPost({
            platform: next.platform.charAt(0).toUpperCase() + next.platform.slice(1),
            content: next.content,
            scheduledFor: new Date(next.scheduled_time).toLocaleString('en-US', {
              weekday: 'long',
              hour: 'numeric',
              minute: '2-digit',
              hour12: true
            }),
            status: 'scheduled',
            image: next.media_urls?.[0] || null
          });
        } else {
          setNextPost(null);
        }
      }
    } catch (error) {
      console.error('Error fetching next scheduled post:', error);
      setNextPost(null);
    }
  };

  const formatNumber = (num) => {
    if (!num || num === 0) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

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
    <div className="p-6 space-y-6 overflow-y-auto h-full relative">
      {loading && (
        <div className="fixed top-4 right-4 z-50 bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <div>
              <p className="text-sm font-medium text-gray-900">Loading data...</p>
              <div className="w-32 bg-gray-200 rounded-full h-1 mt-1">
                <div 
                  className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                  style={{ width: `${loadingProgress}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      )}

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
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Weekly Performance</h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="engagement" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }} />
                <Line type="monotone" dataKey="reach" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }} />
                <Line type="monotone" dataKey="views" stroke="#f59e0b" strokeWidth={3} dot={{ fill: '#f59e0b', strokeWidth: 2, r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

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
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-sm text-gray-600">{item.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Latest Post</h3>
          </div>
          
          {currentPost ? (
            <div className="space-y-4">
              {currentPost.image && (
                <img 
                  src={currentPost.image} 
                  alt="Post content" 
                  className="w-full h-48 object-cover rounded-lg"
                />
              )}
              
              <p className="text-gray-700 text-sm leading-relaxed">{currentPost.content}</p>
              
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
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <PhotoIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-sm">No posts available</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Next Scheduled</h3>
          </div>
          
          {nextPost ? (
            <div className="space-y-4">
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
          ) : (
            <div className="text-center py-8 text-gray-500">
              <CalendarIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-sm">No scheduled posts</p>
            </div>
          )}
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
          <button 
            onClick={() => onNavigate && onNavigate('agents')}
            className="flex flex-col items-center space-y-2 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all"
          >
            <PlusIcon className="w-6 h-6 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Create Post</span>
          </button>
          <button 
            onClick={() => onNavigate && onNavigate('analytics')}
            className="flex flex-col items-center space-y-2 p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-all"
          >
            <ChartBarIcon className="w-6 h-6 text-green-600" />
            <span className="text-sm font-medium text-gray-700">View Analytics</span>
          </button>
          <button 
            onClick={() => onNavigate && onNavigate('calendar')}
            className="flex flex-col items-center space-y-2 p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-all"
          >
            <CalendarIcon className="w-6 h-6 text-purple-600" />
            <span className="text-sm font-medium text-gray-700">Schedule Content</span>
          </button>
          <button 
            onClick={() => onNavigate && onNavigate('community')}
            className="flex flex-col items-center space-y-2 p-4 border border-gray-200 rounded-lg hover:border-pink-300 hover:bg-pink-50 transition-all"
          >
            <UserGroupIcon className="w-6 h-6 text-pink-600" />
            <span className="text-sm font-medium text-gray-700">Engage Community</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;