// Order Service API Functions
// Handles all OrderMS endpoints including scheduling

import { apiClient, ApiResponse } from '../api-client'
import { API_CONFIG } from '../api-config'

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface OrderItem {
  sku: string
  quantity: number
  item_name?: string
  variant?: string
  unit_price?: number
}

export interface CreateOrderRequest {
  customer_id: string
  items: OrderItem[]
  special_instructions?: string
}

export interface Order {
  order_id: string
  order_no: string
  customer_id: string
  status: string
  order_value: number
  order_date: string
  items: OrderItem[]
  delivery_job_id?: string
  customer?: any
  created_at: string
}

export interface UnscheduledOrder {
  order_id: string
  order_no: string
  order_type: 'asap' | 'adhoc' | 'pre_order' | 'custom'
  customer_name: string
  customer_postal_code: string
  customer_street: string
  customer_unit: string
  housing_type: string
  total_items: number
  total_value: number
  order_date: string
  preferred_delivery_date?: string
  preferred_delivery_time?: string
  order_remarks?: string  // Shopify order notes
  remarks?: string  // Internal HQ remarks
  priority_score: number
  items?: OrderItem[]  // Order items with details
}

export interface CreateScheduleRequest {
  order_ids: string[]
  schedule_date: string
  driver_id?: string
  team?: string
}

export interface ScheduledDelivery {
  sequence: number
  order_no: string
  order_type: string
  customer_name: string
  customer_contact: string
  postal_code: string
  address: string
  housing_type: string
  total_items: number
  estimated_arrival?: string
  actual_arrival?: string
  status: string
  requires_warehouse_return: boolean
  latitude?: number
  longitude?: number
}

export interface DeliverySchedule {
  schedule_id: string
  schedule_date: string
  driver_id?: string
  driver_name?: string
  driver_contact?: string
  team?: string
  total_locations: number
  max_locations: number
  remaining_capacity: number
  status: string
  start_time?: string
  estimated_end_time?: string
  route_polyline?: string
  deliveries: ScheduledDelivery[]
}

// ============================================================================
// ORDER SERVICE
// ============================================================================

export const orderService = {
  // ------------------------------------------------------------------------
  // BASIC ORDER OPERATIONS
  // ------------------------------------------------------------------------

  /**
   * Create a new order
   */
  async createOrder(orderData: CreateOrderRequest): Promise<ApiResponse<Order>> {
    return apiClient.post<Order>(API_CONFIG.ENDPOINTS.ORDERS.CREATE, orderData)
  },

  /**
   * Get all orders with pagination
   */
  async listOrders(page: number = 1, perPage: number = 10): Promise<ApiResponse<{
    page: number
    per_page: number
    total: number
    orders: Order[]
  }>> {
    return apiClient.get(API_CONFIG.ENDPOINTS.ORDERS.LIST, {
      page: page.toString(),
      per_page: perPage.toString(),
    })
  },

  /**
   * Get order details by ID
   */
  async getOrderById(orderId: string): Promise<ApiResponse<{
    order: Order
    items: OrderItem[]
    delivery?: any
  }>> {
    return apiClient.get(API_CONFIG.ENDPOINTS.ORDERS.GET_BY_ID(orderId))
  },

  /**
   * Update order status
   */
  async updateOrderStatus(
    orderId: string,
    status: string
  ): Promise<ApiResponse<{ message: string }>> {
    return apiClient.put(API_CONFIG.ENDPOINTS.ORDERS.UPDATE_STATUS(orderId), { status })
  },

  /**
   * Update order type (pre_order, asap, adhoc, custom)
   */
  async updateOrderType(
    orderId: string,
    orderType: 'pre_order' | 'asap' | 'adhoc' | 'custom'
  ): Promise<ApiResponse<{ message: string; order_id: string; order_type: string }>> {
    return apiClient.patch(API_CONFIG.ENDPOINTS.ORDERS.UPDATE_ORDER_TYPE(orderId), { order_type: orderType })
  },

  /**
   * Update delivery preferences (remarks, preferred date/time)
   */
  async updateDeliveryPreferences(
    orderId: string,
    data: {
      remarks?: string
      preferred_delivery_date?: string
      preferred_delivery_time?: string
    }
  ): Promise<ApiResponse<{ success: boolean; message: string; order_id: string }>> {
    return apiClient.patch(API_CONFIG.ENDPOINTS.ORDERS.UPDATE_DELIVERY_PREFERENCES(orderId), data)
  },

  /**
   * Get orders by customer ID
   */
  async getOrdersByCustomer(customerId: string): Promise<ApiResponse<{ orders: Order[] }>> {
    return apiClient.get(API_CONFIG.ENDPOINTS.ORDERS.BY_CUSTOMER(customerId))
  },

  /**
   * Mark delivery as completed
   */
  async completeDelivery(orderId: string): Promise<ApiResponse<{
    success: boolean
    message: string
    order_id: string
    order_no: string
  }>> {
    return apiClient.patch(API_CONFIG.ENDPOINTS.ORDERS.COMPLETE_DELIVERY(orderId))
  },

  // ------------------------------------------------------------------------
  // DELIVERY SCHEDULING
  // ------------------------------------------------------------------------

  /**
   * Get all unscheduled orders ready for scheduling
   */
  async getUnscheduledOrders(): Promise<ApiResponse<{
    success: boolean
    count: number
    orders: UnscheduledOrder[]
  }>> {
    return apiClient.get(API_CONFIG.ENDPOINTS.ORDERS.UNSCHEDULED)
  },

  /**
   * Create a delivery schedule from selected orders
   */
  async createSchedule(scheduleData: CreateScheduleRequest): Promise<ApiResponse<{
    success: boolean
    message: string
    schedule_id: string
    schedule_date: string
    total_locations: number
    orders: Array<{
      order_no: string
      sequence: number
      customer: string
      postal_code: string
    }>
    route?: {
      polyline?: string
      distance_meters?: number
      duration_seconds?: number
      estimated_end_time?: string
    }
  }>> {
    return apiClient.post(API_CONFIG.ENDPOINTS.ORDERS.CREATE_SCHEDULE, scheduleData)
  },

  /**
   * Get all delivery schedules with optional filters
   */
  async getSchedules(filters?: {
    date?: string
    status?: 'draft' | 'confirmed' | 'in_progress' | 'completed'
  }): Promise<ApiResponse<{
    success: boolean
    count: number
    schedules: Array<{
      schedule_id: string
      schedule_date: string
      driver_id?: string
      team?: string
      total_locations: number
      status: string
      start_time?: string
      estimated_end_time?: string
      total_distance_meters?: number
      total_duration_seconds?: number
      created_at: string
      order_count: number
      delivered_count: number
    }>
  }>> {
    const params: Record<string, string> = {}
    if (filters?.date) params.date = filters.date
    if (filters?.status) params.status = filters.status

    return apiClient.get(API_CONFIG.ENDPOINTS.ORDERS.GET_SCHEDULES, params)
  },

  /**
   * Get scheduled deliveries for a specific date
   */
  async getScheduleByDate(date: string): Promise<ApiResponse<{
    success: boolean
    schedule_date: string
    schedules: DeliverySchedule[]
  }>> {
    return apiClient.get(API_CONFIG.ENDPOINTS.ORDERS.GET_SCHEDULE_BY_DATE(date))
  },

  /**
   * Unschedule a single order (for mockup/testing)
   */
  async unscheduleOrder(orderId: string): Promise<ApiResponse<{
    success: boolean
    message: string
    order_id: string
    order_no: string
  }>> {
    return apiClient.patch(API_CONFIG.ENDPOINTS.ORDERS.UNSCHEDULE_ORDER(orderId))
  },

  /**
   * Reset all delivered orders back to ready_for_delivery (for mockup/testing)
   */
  async resetDeliveredOrders(): Promise<ApiResponse<{
    success: boolean
    message: string
    orders_reset: number
  }>> {
    return apiClient.post(API_CONFIG.ENDPOINTS.ORDERS.RESET_DELIVERED)
  },

  /**
   * Delete a delivery schedule
   */
  async deleteSchedule(scheduleId: string): Promise<ApiResponse<{
    success: boolean
    message: string
    schedule_id: string
    orders_unscheduled: number
  }>> {
    return apiClient.delete(API_CONFIG.ENDPOINTS.ORDERS.DELETE_SCHEDULE(scheduleId))
  },
}

export const hasError = (response: any): boolean => {
  return response?.error !== undefined;
};