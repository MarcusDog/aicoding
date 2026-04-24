import { defineStore } from 'pinia';
import { getCurrentUser, login } from '../api/modules/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('volunteer-token') || '',
    user: JSON.parse(localStorage.getItem('volunteer-user') || 'null')
  }),
  getters: {
    isAdmin: (state) => state.user?.roleCode === 'ADMIN',
    isStudent: (state) => state.user?.roleCode === 'STUDENT'
  },
  actions: {
    async login(payload) {
      const data = await login(payload);
      this.token = data.token;
      this.user = data.user;
      localStorage.setItem('volunteer-token', data.token);
      localStorage.setItem('volunteer-user', JSON.stringify(data.user));
    },
    async restore() {
      if (!this.token) {
        return;
      }
      try {
        this.user = await getCurrentUser();
        localStorage.setItem('volunteer-user', JSON.stringify(this.user));
      } catch (error) {
        this.logout();
      }
    },
    logout() {
      this.token = '';
      this.user = null;
      localStorage.removeItem('volunteer-token');
      localStorage.removeItem('volunteer-user');
    }
  }
});
