import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Set default timeout to 15 seconds
axios.defaults.timeout = 15000;

export const dashboardService = {
  async getDashboardData() {
    try {
      const response = await axios.get(`${API_BASE_URL}/dashboard/data`);
      return response.data;
    } catch (error) {
      console.error('Dashboard API error:', error);
      throw error;
    }
  }
};