import React, { useState, useEffect } from 'react';
import { 
  CalendarIcon, 
  PlusIcon, 
  PencilIcon, 
  TrashIcon,
  ClockIcon,
  PhotoIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

const ContentCalendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [scheduledPosts, setScheduledPosts] = useState([]);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);
  const [newPost, setNewPost] = useState({
    content: '',
    platform: 'instagram',
    scheduledTime: '',
    imageUrl: ''
  });

  useEffect(() => {
    loadScheduledPosts();
    
    // Refresh posts every 30 seconds to sync with scheduler
    const interval = setInterval(loadScheduledPosts, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const loadScheduledPosts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/scheduled-posts');
      if (response.ok) {
        const result = await response.json();
        setScheduledPosts(result.data || []);
      }
    } catch (error) {
      console.log('No scheduled posts found');
      setScheduledPosts([]);
    }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getPostsForDay = (date) => {
    if (!date) return [];
    const dateStr = date.toDateString();
    return scheduledPosts.filter(post => {
      const postDate = new Date(post.scheduled_time);
      return postDate.toDateString() === dateStr;
    });
  };

  const handleSchedulePost = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/schedule-post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newPost.content,
          platform: newPost.platform,
          scheduled_time: new Date(newPost.scheduledTime).toISOString(),
          image_url: newPost.imageUrl || null
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setScheduledPosts([...scheduledPosts, result.data]);
        
        // Reset form
        setNewPost({
          content: '',
          platform: 'instagram',
          scheduledTime: '',
          imageUrl: ''
        });
        setShowScheduleModal(false);
      }
    } catch (error) {
      console.error('Error scheduling post:', error);
    }
  };

  const handleEditPost = (post) => {
    setSelectedPost(post);
    setNewPost({
      content: post.content,
      platform: post.platform,
      scheduledTime: new Date(post.scheduled_time).toISOString().slice(0, 16),
      imageUrl: post.media_urls?.[0] || ''
    });
    setShowScheduleModal(true);
  };

  const handleUpdatePost = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/scheduled-posts/${selectedPost.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: selectedPost.id,
          content: newPost.content,
          platform: newPost.platform,
          scheduled_time: new Date(newPost.scheduledTime).toISOString(),
          image_url: newPost.imageUrl || null
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        const updatedPosts = scheduledPosts.map(post => 
          post.id === selectedPost.id ? result.data : post
        );
        
        setScheduledPosts(updatedPosts);
        setShowScheduleModal(false);
        setSelectedPost(null);
        setNewPost({
          content: '',
          platform: 'instagram',
          scheduledTime: '',
          imageUrl: ''
        });
      }
    } catch (error) {
      console.error('Error updating post:', error);
    }
  };

  const handleDeletePost = async (postId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/scheduled-posts/${postId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setScheduledPosts(scheduledPosts.filter(post => post.id !== postId));
      }
    } catch (error) {
      console.error('Error deleting post:', error);
    }
  };

  const formatTime = (dateStr) => {
    return new Date(dateStr).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Content Calendar</h2>
          <p className="text-gray-600">Schedule and manage your social media posts</p>
        </div>
        <button
          onClick={() => setShowScheduleModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Schedule Post</span>
        </button>
      </div>

      {/* Calendar Navigation */}
      <div className="flex items-center justify-between bg-white rounded-lg p-4 shadow-sm border">
        <button
          onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          ←
        </button>
        <h3 className="text-lg font-semibold">
          {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
        </h3>
        <button
          onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          →
        </button>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        {/* Week days header */}
        <div className="grid grid-cols-7 bg-gray-50">
          {weekDays.map(day => (
            <div key={day} className="p-3 text-center text-sm font-medium text-gray-600 border-r border-gray-200 last:border-r-0">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar days */}
        <div className="grid grid-cols-7">
          {getDaysInMonth(currentDate).map((date, index) => (
            <div key={index} className="min-h-32 border-r border-b border-gray-200 last:border-r-0 p-2">
              {date && (
                <>
                  <div className="text-sm font-medium text-gray-900 mb-2">
                    {date.getDate()}
                  </div>
                  <div className="space-y-1">
                    {getPostsForDay(date).map(post => (
                      <div
                        key={post.id}
                        className="bg-blue-100 text-blue-800 text-xs p-1 rounded cursor-pointer hover:bg-blue-200 group"
                        onClick={() => handleEditPost(post)}
                      >
                        <div className="flex items-center justify-between">
                          <span className="truncate flex-1">
                            {formatTime(post.scheduled_time)} - {post.content.substring(0, 20)}...
                          </span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeletePost(post.id);
                            }}
                            className="opacity-0 group-hover:opacity-100 ml-1"
                          >
                            <TrashIcon className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Schedule Post Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {selectedPost ? 'Edit Post' : 'Schedule New Post'}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Content
                </label>
                <textarea
                  value={newPost.content}
                  onChange={(e) => setNewPost({...newPost, content: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={4}
                  placeholder="What's on your mind?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Platform
                </label>
                <select
                  value={newPost.platform}
                  onChange={(e) => setNewPost({...newPost, platform: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="instagram">Instagram</option>
                  <option value="linkedin">LinkedIn</option>
                  <option value="twitter">Twitter</option>
                  <option value="facebook">Facebook</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Schedule Time
                </label>
                <input
                  type="datetime-local"
                  value={newPost.scheduledTime}
                  onChange={(e) => setNewPost({...newPost, scheduledTime: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Image URL (Optional)
                </label>
                <input
                  type="url"
                  value={newPost.imageUrl}
                  onChange={(e) => setNewPost({...newPost, imageUrl: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="https://example.com/image.jpg"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowScheduleModal(false);
                  setSelectedPost(null);
                  setNewPost({
                    content: '',
                    platform: 'instagram',
                    scheduledTime: '',
                    imageUrl: ''
                  });
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={selectedPost ? handleUpdatePost : handleSchedulePost}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {selectedPost ? 'Update' : 'Schedule'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentCalendar;