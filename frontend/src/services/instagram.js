import api from './api';

export const instagramService = {
  // Get Instagram account information
  getAccountInfo: async () => {
    try {
      const response = await api.get('/instagram/account');
      console.log('Account response:', response);
      return response;
    } catch (error) {
      console.error('getAccountInfo error:', error);
      throw error;
    }
  },

  // Get recent media posts
  getMediaList: async (limit = 25) => {
    try {
      const response = await api.get(`/instagram/media?limit=${limit}`);
      console.log('Media response:', response);
      return response;
    } catch (error) {
      console.error('getMediaList error:', error);
      throw error;
    }
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
    try {
      const response = await api.get(`/instagram/top-posts?limit=${limit}`);
      console.log('Top posts response:', response);
      return response;
    } catch (error) {
      console.error('getTopPosts error:', error);
      throw error;
    }
  }
};