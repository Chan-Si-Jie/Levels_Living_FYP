// API Client for making authenticated requests to backend services

import { API_CONFIG, HTTP_METHODS } from './api-config'
import { authStorage } from './auth-storage'

export interface ApiError {
  error: string
  status?: number
}

export interface ApiResponse<T> {
  data?: T
  error?: ApiError
  status: number
}

class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL
  }

  /**
   * Make an authenticated API request
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`

    // Get access token
    const token = authStorage.getAccessToken()

    // Default headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    }

    // Add Authorization header if token exists
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      const status = response.status
      let data: T | undefined

      // Try to parse JSON response
      try {
        const text = await response.text()
        data = text ? JSON.parse(text) : undefined
      } catch {
        // Response is not JSON
        data = undefined
      }

      // Handle successful responses
      if (response.ok) {
        return { data, status }
      }

      // Handle error responses
      const error: ApiError = {
        error: (data as any)?.error || response.statusText || 'Unknown error',
        status,
      }

      // Handle 401 Unauthorized - clear auth data
      if (status === 401) {
        authStorage.clearAll()
        // Only redirect to login if not already on login page
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
      }

      return { error, status }
    } catch (err) {
      // Network or other errors
      const error: ApiError = {
        error: err instanceof Error ? err.message : 'Network error',
        status: 0,
      }
      return { error, status: 0 }
    }
  }

  // HTTP Methods
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<ApiResponse<T>> {
    let url = endpoint
    if (params) {
      const queryString = new URLSearchParams(params).toString()
      url = `${endpoint}?${queryString}`
    }

    return this.request<T>(url, {
      method: HTTP_METHODS.GET,
    })
  }

  async post<T>(endpoint: string, body?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: HTTP_METHODS.POST,
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async put<T>(endpoint: string, body?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: HTTP_METHODS.PUT,
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async patch<T>(endpoint: string, body?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: HTTP_METHODS.PATCH,
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: HTTP_METHODS.DELETE,
    })
  }
}

// Export singleton instance
export const apiClient = new ApiClient()

// Convenience function to check if response has error
export function hasError<T>(response: ApiResponse<T>): response is { error: ApiError; status: number } {
  return response.error !== undefined
}
