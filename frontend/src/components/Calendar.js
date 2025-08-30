import React, { useState } from 'react';
import { 
  ChevronLeftIcon, 
  ChevronRightIcon,
  PlusIcon,
  ClockIcon,
  PhotoIcon,
  VideoCameraIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, isSameDay } from 'date-fns';

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [view, setView] = useState('month'); // month, week, day

  // Sample scheduled posts
  const scheduledPosts = [
    {
      id: 1,
      date: new Date(2025, 0, 15),
      time: '09:00',
      platform: 'Instagram',
      type: 'image',
      title: 'Morning motivation post',
      status: 'scheduled'
    },
    {
      id: 2,
      date: new Date(2025, 0, 15),
      time: '15:00',
      platform: 'LinkedIn',
      type: 'article',
      title: 'Industry insights article',
      status: 'scheduled'
    },
    {
      id: 3,
      date: new Date(2025, 0, 16),
      time: '12:00',
      platform: 'Twitter',
      type: 'text',
      title: 'Product announcement',
      status: 'draft'
    },
    {
      id: 4,
      date: new Date(2025, 0, 17),
      time: '18:00',
      platform: 'Instagram',
      type: 'video',
      title: 'Behind the scenes video',
      status: 'scheduled'
    }
  ];

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const getPostsForDate = (date) => {
    return scheduledPosts.filter(post => isSameDay(post.date, date));
  };

  const getContentTypeIcon = (type) => {
    switch (type) {
      case 'image':
        return <PhotoIcon className="w-4 h-4" />;
      case 'video':
        return <VideoCameraIcon className="w-4 h-4" />;
      case 'article':
        return <DocumentTextIcon className="w-4 h-4" />;
      default:
        return <DocumentTextIcon className="w-4 h-4" />;
    }
  };

  const getPlatformColor = (platform) => {
    const colors = {
      'Instagram': 'bg-pink-100 text-pink-700 border-pink-200',
      'LinkedIn': 'bg-blue-100 text-blue-700 border-blue-200',
      'Twitter': 'bg-sky-100 text-sky-700 border-sky-200',
      'Facebook': 'bg-indigo-100 text-indigo-700 border-indigo-200'
    };
    return colors[platform] || 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  return (
    <div className="p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold text-gray-900">Content Calendar</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigateMonth(-1)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeftIcon className="w-5 h-5 text-gray-600" />
            </button>
            <h3 className="text-lg font-semibold text-gray-700 min-w-[200px] text-center">
              {format(currentDate, 'MMMM yyyy')}
            </h3>
            <button
              onClick={() => navigateMonth(1)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRightIcon className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            {['month', 'week', 'day'].map((viewType) => (
              <button
                key={viewType}
                onClick={() => setView(viewType)}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors capitalize ${
                  view === viewType
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {viewType}
              </button>
            ))}
          </div>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <PlusIcon className="w-4 h-4" />
            <span>Schedule Post</span>
          </button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Calendar Grid */}
        <div className="lg:col-span-3 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          {/* Calendar Header */}
          <div className="grid grid-cols-7 gap-1 mb-4">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
              <div key={day} className="p-3 text-center text-sm font-medium text-gray-500">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Days */}
          <div className="grid grid-cols-7 gap-1">
            {days.map((day) => {
              const postsForDay = getPostsForDate(day);
              const isCurrentMonth = isSameMonth(day, currentDate);
              const isSelected = isSameDay(day, selectedDate);
              const isTodayDate = isToday(day);

              return (
                <div
                  key={day.toString()}
                  onClick={() => setSelectedDate(day)}
                  className={`min-h-[100px] p-2 border border-gray-100 cursor-pointer transition-all hover:bg-gray-50 ${
                    isSelected ? 'bg-blue-50 border-blue-200' : ''
                  } ${!isCurrentMonth ? 'opacity-30' : ''}`}
                >
                  <div className={`text-sm font-medium mb-1 ${
                    isTodayDate ? 'text-blue-600' : isCurrentMonth ? 'text-gray-900' : 'text-gray-400'
                  }`}>
                    {format(day, 'd')}
                  </div>
                  
                  <div className="space-y-1">
                    {postsForDay.slice(0, 2).map((post) => (
                      <div
                        key={post.id}
                        className={`text-xs p-1 rounded border ${getPlatformColor(post.platform)}`}
                      >
                        <div className="flex items-center space-x-1">
                          {getContentTypeIcon(post.type)}
                          <span className="truncate">{post.time}</span>
                        </div>
                      </div>
                    ))}
                    {postsForDay.length > 2 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{postsForDay.length - 2} more
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Date Details */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {format(selectedDate, 'MMM d, yyyy')}
          </h3>
          
          <div className="space-y-3">
            {getPostsForDate(selectedDate).length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <ClockIcon className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No posts scheduled</p>
                <button className="mt-3 px-3 py-1 bg-blue-600 text-white rounded-lg text-xs hover:bg-blue-700 transition-colors">
                  Schedule Post
                </button>
              </div>
            ) : (
              getPostsForDate(selectedDate).map((post) => (
                <div key={post.id} className={`p-3 rounded-lg border ${getPlatformColor(post.platform)}`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getContentTypeIcon(post.type)}
                      <span className="font-medium text-sm">{post.platform}</span>
                    </div>
                    <span className="text-xs">{post.time}</span>
                  </div>
                  <p className="text-sm">{post.title}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      post.status === 'scheduled' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {post.status}
                    </span>
                    <button className="text-xs text-gray-500 hover:text-gray-700">
                      Edit
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Calendar;