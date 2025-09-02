import api from './api';

export const instagramService = {
  // Get Instagram account information
  getAccountInfo: async () => {
    return await api.get('/instagram/account');
  },

  // Get recent media posts
  getMediaList: async (limit = 25) => {
    return await api.get(`/instagram/media?limit=${limit}`);
  },

  // Get account insights
  getAccountInsights: async (days = 7) => {
    return await api.get(`/instagram/insights/account?days=${days}`);
  },

  // Get media insights for specific post
  getMediaInsights: async (mediaId) => {
    return await api.get(`/instagram/insights/media/${mediaId}`);
  },

  // Get top performing posts
  getTopPosts: async (limit = 10) => {
    return await api.get(`/instagram/top-posts?limit=${limit}`);
  }
};