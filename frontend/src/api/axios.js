import axios from 'axios';

// Debug: Log environment info
console.log('🔍 DEBUG: Environment Detection');
console.log('   hostname:', window.location.hostname);
console.log('   protocol:', window.location.protocol);
console.log('   isDevelopment:', window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

// Determine the correct base URL based on environment
let API_URL = import.meta.env.VITE_API_BASE_URL;

console.log('🔍 DEBUG: Env Variable Check');
console.log('   VITE_API_BASE_URL from env:', import.meta.env.VITE_API_BASE_URL);
console.log('   API_URL before logic:', API_URL);
console.log('   API_URL is falsy:', !API_URL);

if (!API_URL) {
  // Use localhost for development, Railway for production
  const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  console.log('🔍 DEBUG: API_URL is empty, using fallback logic');
  console.log('   isDevelopment:', isDevelopment);
  
  if (isDevelopment) {
    API_URL = 'http://localhost:8000/api/v1';
    console.log('   ✅ Set to localhost');
  } else {
    // Fallback to Railway backend URL (production)
    API_URL = 'https://wazeenterpriseswaterproject-production.up.railway.app/api/v1';
    console.log('   ✅ Set to Railway HTTPS');
  }
} else {
  console.log('🔍 DEBUG: API_URL from env var is set:', API_URL);
}

// Force HTTPS in production to prevent mixed content errors
console.log('🔍 DEBUG: HTTPS Enforcement Check');
console.log('   API_URL before HTTPS check:', API_URL);
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
if (!isLocalhost && API_URL && API_URL.startsWith('http://')) {
  const originalURL = API_URL;
  API_URL = API_URL.replace('http://', 'https://');
  console.log('   🔒 CONVERTED: ' + originalURL + ' → ' + API_URL);
} else if (!isLocalhost) {
  console.log('   ✅ Already HTTPS or localhost - no conversion needed');
}

console.log('📡 FINAL API Base URL:', API_URL);
console.log('🔗 Full URL will be used for all API calls');

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token and log requests
api.interceptors.request.use(config => {
  // CRITICAL: Force HTTPS on all non-localhost URLs
  if (config.url && !config.url.startsWith('/')) {
    // Absolute URL
    if (config.url.startsWith('http://')) {
      config.url = config.url.replace('http://', 'https://');
      console.log('🔒 FORCED HTTPS in config.url:', config.url);
    }
  }
  if (config.baseURL && config.baseURL.startsWith('http://')) {
    config.baseURL = config.baseURL.replace('http://', 'https://');
    console.log('🔒 FORCED HTTPS in config.baseURL:', config.baseURL);
  }
  
  console.log('🌐 API Request:', {
    method: config.method,
    url: config.url,
    baseURL: config.baseURL,
    fullURL: config.baseURL + config.url,
    hasToken: !!localStorage.getItem("token")
  });
  
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Don't force JSON content-type for blob requests
  if (!config.responseType || config.responseType !== 'blob') {
    config.headers['Content-Type'] = 'application/json';
  }
  return config;
});


// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      message: error.message,
      data: error.response?.data
    });
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
