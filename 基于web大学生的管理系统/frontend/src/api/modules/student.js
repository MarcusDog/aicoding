import http from '../http';

export const getStudentHome = () => http.get('/student/home');
export const getStudentActivities = (params) => http.get('/student/activities', { params });
export const getStudentActivityDetail = (id) => http.get(`/student/activities/${id}`);
export const applyActivity = (activityId) => http.post(`/student/signups/${activityId}`);
export const cancelSignup = (signupId, payload) => http.put(`/student/signups/${signupId}/cancel`, payload);
export const getMySignups = () => http.get('/student/signups');
export const signIn = (payload) => http.post('/student/sign-in', payload);
export const signOut = (payload) => http.post('/student/sign-out', payload);
export const getMyHours = () => http.get('/student/hours');
export const getMyMessages = () => http.get('/student/messages');
export const getMyProfile = () => http.get('/student/profile');
export const updateMyProfile = (payload) => http.put('/student/profile', payload);
