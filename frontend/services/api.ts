import axios from 'axios';

// Use relative path in browser for proxy rewrites, full URL on server side
const isDev = process.env.NODE_ENV === 'development';
const defaultBackend = isDev ? 'http://127.0.0.1:8000' : 'https://customer-churn-predictor-3p9a.onrender.com';
const API_URL = typeof window !== 'undefined'
  ? '/api/v1'
  : (process.env.BACKEND_API_URL || defaultBackend) + '/api/v1';

// Create a configured Axios instance
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach the JWT authorization token automatically
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle global response errors (e.g. 401 Unauthorized token expiry)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (typeof window !== 'undefined') {
        // Clear expired credentials and redirect to login page
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
