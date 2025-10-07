// API Configuration for Backend Services via Kong API Gateway

export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',

  // Service endpoints (via Kong Gateway)
  ENDPOINTS: {
    // UserMS - Authentication & User Management (Port 5001)
    AUTH: {
      LOGIN: '/auth/login',
      REGISTER: '/auth/register',
      LOGOUT: '/auth/logout',
      PROFILE: '/auth/profile',
      VALIDATE: '/auth/validate',
      USERS: '/auth/users',
    },

    // CustomerMS (Port 5002)
    CUSTOMERS: {
      CREATE: '/customers',
      GET_BY_ID: (id: string) => `/customers/${id}`,
      GET_BY_CONTACT: (contact: string) => `/customers/contact/${contact}`,
      SEARCH: '/customers',
      VALIDATE: '/customers/validate',
    },

    // InventoryMS (Port 5003)
    INVENTORY: {
      PRODUCTS: '/inventory/products',
      GET_PRODUCT: (sku: string) => `/inventory/products/${sku}`,
      DELIVERY_REQUIREMENTS: '/inventory/delivery-requirements',
      DELIVERY_TYPES: '/inventory/delivery-types',
    },

    // DeliveryMS (Port 5004)
    DELIVERY: {
      CREATE: '/deliveries',
      GET_DELIVERY: (jobId: string) => `/deliveries/${jobId}`,
      UPDATE_STATUS: (jobId: string) => `/deliveries/${jobId}/status`,
      TRACKING: (jobId: string) => `/tracking/${jobId}`,
      OPTIMIZE_ROUTE: '/optimize-route',
      GEOCODE: '/geocode',
      DRIVERS: '/drivers',
      UPDATE_DRIVER_LOCATION: (driverId: string) => `/drivers/${driverId}/location`,
    },

    // OrderMS (Port 5005)
    ORDERS: {
      CREATE: '/create_order',
      LIST: '/orders',
      GET_BY_ID: (orderId: string) => `/orders/${orderId}`,
      UPDATE_STATUS: (orderId: string) => `/orders/${orderId}/status`,
      UPDATE_ORDER_TYPE: (orderId: string) => `/orders/${orderId}/order-type`,
      UPDATE_DELIVERY_PREFERENCES: (orderId: string) => `/orders/${orderId}/delivery-preferences`,
      BY_CUSTOMER: (customerId: string) => `/orders/customer/${customerId}`,
      INITIATE_DELIVERY: (orderId: string) => `/orders/${orderId}/deliver`,
      TRACKING: (orderId: string) => `/orders/${orderId}/tracking`,
      COMPLETE_DELIVERY: (orderId: string) => `/orders/${orderId}/complete`,

      // Scheduling endpoints
      UNSCHEDULED: '/orders/unscheduled',
      CREATE_SCHEDULE: '/orders/schedule',
      GET_SCHEDULES: '/schedules',
      GET_SCHEDULE_BY_DATE: (date: string) => `/schedules/${date}`,
      DELETE_SCHEDULE: (scheduleId: string) => `/schedules/${scheduleId}`,
      UNSCHEDULE_ORDER: (orderId: string) => `/orders/${orderId}/unschedule`,
      RESET_DELIVERED: '/orders/reset-delivered',
    },
  },
} as const

// HTTP Methods
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  PATCH: 'PATCH',
  DELETE: 'DELETE',
} as const

// Response status codes
export const STATUS_CODES = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_ERROR: 500,
} as const
