import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Create axios instance directly
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Analyze sentiment
export const analyzeSentiment = async (text, reviewId = null) => {
  try {
    const response = await api.post('/analyze', {
      text,
      review_id: reviewId
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing sentiment:', error);
    throw error;
  }
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    return null;
  }
};

// Export api instance if needed elsewhere
export default api;