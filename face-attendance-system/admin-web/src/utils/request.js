import axios from "axios";

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || "http://localhost:5000/api",
  timeout: 15000,
});

request.interceptors.request.use((config) => {
  const token = localStorage.getItem("attendance_admin_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error?.response?.data?.message || error.message || "请求失败";
    return Promise.reject(new Error(message));
  }
);

export default request;
