import axios from 'axios';

const http = axios.create({
  baseURL: '/api',
  timeout: 10000
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('volunteer-token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use((response) => {
  const payload = response.data;
  if (!payload.success) {
    return Promise.reject(new Error(payload.message || '请求失败'));
  }
  return payload.data;
}, (error) => Promise.reject(error));

export default http;
