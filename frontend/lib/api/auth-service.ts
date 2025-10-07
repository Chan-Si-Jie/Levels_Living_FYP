// Authentication Service API Functions
// Handles all UserMS authentication endpoints

import { apiClient, ApiResponse } from '../api-client'
import { API_CONFIG } from '../api-config'
import { authStorage, UserData } from '../auth-storage'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  message: string
  access_token: string
  refresh_token: string
  session_id: string
  user: UserData
}

export interface RegisterRequest {
  email: string
  password: string
  role: 'admin' | 'driver'
}

export interface RegisterResponse {
  message: string
  user_id: string
  email: string
  role: string
}

export interface ValidateTokenResponse {
  valid: boolean
  user_id: string
  role: string
  email: string
}

export const authService = {
  /**
   * Login user and store tokens
   */
  async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    const response = await apiClient.post<LoginResponse>(
      API_CONFIG.ENDPOINTS.AUTH.LOGIN,
      credentials
    )

    // Store tokens if login successful
    if (response.data) {
      authStorage.setAccessToken(response.data.access_token)
      authStorage.setRefreshToken(response.data.refresh_token)
      authStorage.setUserData(response.data.user)
    }

    return response
  },

  /**
   * Register new user
   */
  async register(data: RegisterRequest): Promise<ApiResponse<RegisterResponse>> {
    return apiClient.post<RegisterResponse>(API_CONFIG.ENDPOINTS.AUTH.REGISTER, data)
  },

  /**
   * Logout user and clear tokens
   */
  async logout(): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>(API_CONFIG.ENDPOINTS.AUTH.LOGOUT)

    // Clear local storage regardless of response
    authStorage.clearAll()

    return response
  },

  /**
   * Get current user profile
   */
  async getProfile(): Promise<ApiResponse<UserData>> {
    return apiClient.get<UserData>(API_CONFIG.ENDPOINTS.AUTH.PROFILE)
  },

  /**
   * Validate current JWT token
   */
  async validateToken(): Promise<ApiResponse<ValidateTokenResponse>> {
    return apiClient.post<ValidateTokenResponse>(API_CONFIG.ENDPOINTS.AUTH.VALIDATE)
  },

  /**
   * Get all users (admin only)
   */
  async getAllUsers(): Promise<ApiResponse<{ users: UserData[] }>> {
    return apiClient.get<{ users: UserData[] }>(API_CONFIG.ENDPOINTS.AUTH.USERS)
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return authStorage.isAuthenticated()
  },

  /**
   * Get current user data from storage
   */
  getCurrentUser(): UserData | null {
    return authStorage.getUserData()
  },
}
