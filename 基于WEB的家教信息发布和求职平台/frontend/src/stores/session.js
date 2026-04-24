import { computed, reactive } from 'vue'

const STORAGE_KEY = 'tutor-platform-session'

function loadStoredUser() {
  const rawValue = sessionStorage.getItem(STORAGE_KEY)
  if (!rawValue) {
    return null
  }

  try {
    return JSON.parse(rawValue)
  } catch {
    sessionStorage.removeItem(STORAGE_KEY)
    return null
  }
}

const state = reactive({
  user: loadStoredUser()
})

function persist() {
  if (!state.user) {
    sessionStorage.removeItem(STORAGE_KEY)
    return
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state.user))
}

export function useSession() {
  const isLoggedIn = computed(() => Boolean(state.user))

  function setUser(user) {
    state.user = user
    persist()
  }

  function clearUser() {
    state.user = null
    persist()
  }

  return {
    state,
    isLoggedIn,
    setUser,
    clearUser
  }
}

export function getCurrentUser() {
  return state.user
}
