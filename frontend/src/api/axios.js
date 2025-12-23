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

// ⚠️ CRITICAL: Force HTTPS in production to prevent mixed content errors
// This is essential because HTTPS pages CANNOT make requests to HTTP endpoints
console.log('🔍 DEBUG: HTTPS Enforcement Check');
console.log('   API_URL before HTTPS check:', API_URL);
const isFrontendSecure = window.location.protocol === 'https:';
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

console.log(`   Frontend Protocol: ${window.location.protocol} (is HTTPS: ${isFrontendSecure})`);
console.log(`   Is Localhost: ${isLocalhost}`);

// IMPORTANT: If frontend is HTTPS, backend MUST be HTTPS (no exceptions)
if (isFrontendSecure && !isLocalhost && API_URL) {
  if (API_URL.startsWith('http://')) {
    const originalURL = API_URL;
    API_URL = API_URL.replace(/^http:/, 'https:');
    console.log('   🔒 CRITICAL FIX - HTTPS Frontend needs HTTPS Backend:');
    console.log('      ' + originalURL + ' → ' + API_URL);
  } else {
    console.log('   ✅ Frontend is HTTPS, API_URL is already HTTPS');
  }
} else if (!isLocalhost && API_URL && API_URL.startsWith('http://')) {
  // Fallback for other non-localhost scenarios
  const originalURL = API_URL;
  API_URL = API_URL.replace('http://', 'https://');
  console.log('   🔒 Fallback HTTPS conversion:', originalURL + ' → ' + API_URL);
}

// ⚠️ CRITICAL: Only convert HTTP to HTTPS for production (non-localhost) URLs
// Localhost should stay as HTTP for local development
if (API_URL && API_URL.startsWith('http://') && !API_URL.includes('localhost') && !API_URL.includes('127.0.0.1')) {
  const original = API_URL;
  API_URL = API_URL.replace('http://', 'https://');
  console.log('🔒 CRITICAL FIX before axios creation (production only):', original, '→', API_URL);
}

console.log('📡 FINAL API Base URL:', API_URL);
console.log('🔗 All API calls will use this HTTPS baseURL');

// Create axios instance with HTTPS baseURL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // CRITICAL: Prevent axios from modifying URLs
  withCredentials: false,
});

// Request interceptor to add token and enforce HTTPS
api.interceptors.request.use(config => {
  // Only enforce HTTPS for production (non-localhost) URLs
  if (config.baseURL && config.baseURL.startsWith('http://') && !config.baseURL.includes('localhost') && !config.baseURL.includes('127.0.0.1')) {
    console.error('🚨 CRITICAL ERROR: Production baseURL is HTTP! Converting to HTTPS');
    config.baseURL = config.baseURL.replace('http://', 'https://');
  }
  
  // Build full URL and verify it's HTTPS (only for production)
  const fullURL = (config.baseURL || '') + (config.url || '');
  if (fullURL.startsWith('http://') && !fullURL.includes('localhost') && !fullURL.includes('127.0.0.1')) {
    console.error('🚨 CRITICAL ERROR: Production URL is HTTP! Converting to HTTPS');
    if (config.baseURL) {
      config.baseURL = config.baseURL.replace('http://', 'https://');
    }
  }
  
  console.log('🌐 API Request:', {
    method: config.method,
    url: config.url,
    baseURL: config.baseURL,
    fullURL: fullURL,
    isHttps: fullURL.startsWith('https://'),
    hasToken: !!localStorage.getItem("token")
  });
  
  // Add auth token
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Add content type for non-blob requests
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
    const errorInfo = {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      message: error.message,
      data: error.response?.data,
      code: error.code,
      isNetworkError: !error.response,
      isTimeoutError: error.code === 'ECONNABORTED'
    };
    
    console.error('❌ API Error:', errorInfo);
    
    // Log full error details
    if (!error.response) {
      console.error('🌐 Network Error Details:', {
        message: error.message,
        code: error.code,
        errno: error.errno
      });
    }
    
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
