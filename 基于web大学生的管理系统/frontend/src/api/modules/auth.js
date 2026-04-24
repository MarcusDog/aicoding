import http from '../http';

export const login = (payload) => http.post('/auth/login', payload);
export const getCurrentUser = () => http.get('/auth/me');
