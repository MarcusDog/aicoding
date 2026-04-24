const SESSION_KEY = 'tutor-platform-user';

function loadUser() {
  const raw = sessionStorage.getItem(SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}

function persistUser(user) {
  if (!user) {
    sessionStorage.removeItem(SESSION_KEY);
    return;
  }
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(user));
}

export const state = window.Vue.reactive({
  user: loadUser(),
  notice: '',
  error: '',
  loading: false
});

export function setUser(user) {
  state.user = user;
  persistUser(user);
}

export function flashNotice(message) {
  state.notice = message;
  state.error = '';
}

export function flashError(message) {
  state.error = message;
  state.notice = '';
}

export function clearMessages() {
  state.notice = '';
  state.error = '';
}

export function setLoading(loading) {
  state.loading = loading;
}

export function logoutUser() {
  setUser(null);
  flashNotice('已退出登录。');
}
