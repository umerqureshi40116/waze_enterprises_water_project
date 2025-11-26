import axios from 'axios';

// Determine the correct base URL based on environment
let API_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_URL) {
  // Fallback to Railway backend URL (must be HTTPS for Vercel)
  API_URL = 'https://wazeenterpriseswaterproject-production.up.railway.app/api/v1';
}

console.log('📡 API Base URL:', API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(config => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('❌ API Error:', error.response?.status, error.response?.data);
    if (error.response?.status === 401) {
      console.log('🚫 Unauthorized - redirecting to login');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
