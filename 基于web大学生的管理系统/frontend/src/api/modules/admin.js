import axios from 'axios';
import http from '../http';

export const getDashboard = () => http.get('/admin/dashboard');
export const getStudents = () => http.get('/admin/students');
export const createStudent = (payload) => http.post('/admin/students', payload);
export const updateStudent = (id, payload) => http.put(`/admin/students/${id}`, payload);
export const getAdmins = () => http.get('/admin/admin-users');
export const createAdmin = (payload) => http.post('/admin/admin-users', payload);
export const updateAdmin = (id, payload) => http.put(`/admin/admin-users/${id}`, payload);
export const getActivities = () => http.get('/admin/activities');
export const createActivity = (payload) => http.post('/admin/activities', payload);
export const updateActivity = (id, payload) => http.put(`/admin/activities/${id}`, payload);
export const publishActivity = (id) => http.post(`/admin/activities/${id}/publish`);
export const cancelActivity = (id) => http.post(`/admin/activities/${id}/cancel`);
export const getSignups = () => http.get('/admin/signups');
export const approveSignup = (id, payload) => http.post(`/admin/signups/${id}/approve`, payload);
export const rejectSignup = (id, payload) => http.post(`/admin/signups/${id}/reject`, payload);
export const getSigns = () => http.get('/admin/signs');
export const fixSign = (id, payload) => http.post(`/admin/signs/${id}/fix`, payload);
export const getHours = () => http.get('/admin/hours');
export const confirmHours = (id, payload) => http.post(`/admin/hours/${id}/confirm`, payload);
export const revokeHours = (id, payload) => http.post(`/admin/hours/${id}/revoke`, payload);
export const getNotices = () => http.get('/admin/notices');
export const createNotice = (payload) => http.post('/admin/notices', payload);
export const updateNotice = (id, payload) => http.put(`/admin/notices/${id}`, payload);
export const getActivityReport = () => http.get('/admin/reports/activity');
export const getStudentHoursReport = () => http.get('/admin/reports/student-hours');
export const getMonthlyReport = () => http.get('/admin/reports/monthly');

const downloadReport = (path) => {
  const token = localStorage.getItem('volunteer-token');
  return axios.get(`/api${path}`, {
    responseType: 'blob',
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  });
};

export const exportActivityReport = () => downloadReport('/admin/reports/export/activity');
export const exportStudentHoursReport = () => downloadReport('/admin/reports/export/student-hours');
