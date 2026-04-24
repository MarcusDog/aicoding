import { defineStore } from "pinia";

const TOKEN_KEY = "attendance_admin_token";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || "",
    profile: null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    setToken(token) {
      this.token = token;
      localStorage.setItem(TOKEN_KEY, token);
    },
    clearToken() {
      this.token = "";
      this.profile = null;
      localStorage.removeItem(TOKEN_KEY);
    },
    setProfile(profile) {
      this.profile = profile;
    },
  },
});
