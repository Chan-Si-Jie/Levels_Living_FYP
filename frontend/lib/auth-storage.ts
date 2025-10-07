// Authentication Storage Utilities
// Handles JWT token storage in localStorage

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user_data'

export interface UserData {
  user_id: string
  email: string
  role: string
}

export const authStorage = {
  // Access Token
  setAccessToken: (token: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token)
    }
  },

  getAccessToken: (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(TOKEN_KEY)
    }
    return null
  },

  removeAccessToken: (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY)
    }
  },

  // Refresh Token
  setRefreshToken: (token: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(REFRESH_TOKEN_KEY, token)
    }
  },

  getRefreshToken: (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(REFRESH_TOKEN_KEY)
    }
    return null
  },

  removeRefreshToken: (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(REFRESH_TOKEN_KEY)
    }
  },

  // User Data
  setUserData: (userData: UserData): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(USER_KEY, JSON.stringify(userData))
    }
  },

  getUserData: (): UserData | null => {
    if (typeof window !== 'undefined') {
      const data = localStorage.getItem(USER_KEY)
      return data ? JSON.parse(data) : null
    }
    return null
  },

  removeUserData: (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(USER_KEY)
    }
  },

  // Clear all auth data
  clearAll: (): void => {
    authStorage.removeAccessToken()
    authStorage.removeRefreshToken()
    authStorage.removeUserData()
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    return !!authStorage.getAccessToken()
  },
}
