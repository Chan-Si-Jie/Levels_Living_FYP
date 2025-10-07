// Inventory Service API Functions
// Handles all InventoryMS endpoints

import { apiClient, ApiResponse } from '../api-client'
import { API_CONFIG } from '../api-config'

export interface InventoryProduct {
  sku: string
  item_name: string
  variant?: string
  category?: string
  subcategory?: string
  description?: string
  unit_price?: number
  weight_per_unit?: number
  volume_per_unit?: number
  dimensions?: any
  delivery_type: string
  special_handling_required?: boolean
  assembly_required?: boolean
  showroom_item?: boolean
  handling_instructions?: string
  storage_location?: string
  supplier?: string
  supplier_sku?: string
  image_urls?: string[]
  product_tags?: string[]
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

export interface InventoryListResponse {
  products: InventoryProduct[]
  pagination: {
    total: number
    limit: number
    offset: number
    has_more: boolean
  }
}

export const inventoryService = {
  /**
   * Get all inventory products with pagination
   */
  async getProducts(params?: {
    limit?: number
    offset?: number
    category?: string
    delivery_type?: string
    search_term?: string
  }): Promise<ApiResponse<InventoryListResponse>> {
    const queryParams: Record<string, string> = {}

    if (params?.limit) queryParams.limit = params.limit.toString()
    if (params?.offset) queryParams.offset = params.offset.toString()
    if (params?.category) queryParams.category = params.category
    if (params?.delivery_type) queryParams.delivery_type = params.delivery_type
    if (params?.search_term) queryParams.search_term = params.search_term

    return apiClient.get<InventoryListResponse>(
      API_CONFIG.ENDPOINTS.INVENTORY.PRODUCTS,
      queryParams
    )
  },

  /**
   * Get product by SKU
   */
  async getProductBySku(sku: string): Promise<ApiResponse<InventoryProduct>> {
    return apiClient.get<InventoryProduct>(
      API_CONFIG.ENDPOINTS.INVENTORY.GET_PRODUCT(sku)
    )
  },

  /**
   * Create new product
   */
  async createProduct(productData: Partial<InventoryProduct>): Promise<ApiResponse<{ message: string; product: InventoryProduct }>> {
    return apiClient.post<{ message: string; product: InventoryProduct }>(
      API_CONFIG.ENDPOINTS.INVENTORY.PRODUCTS,
      productData
    )
  },

  /**
   * Update product
   */
  async updateProduct(sku: string, productData: Partial<InventoryProduct>): Promise<ApiResponse<{ message: string; product: InventoryProduct }>> {
    return apiClient.put<{ message: string; product: InventoryProduct }>(
      API_CONFIG.ENDPOINTS.INVENTORY.GET_PRODUCT(sku),
      productData
    )
  },

  /**
   * Get delivery types
   */
  async getDeliveryTypes(): Promise<ApiResponse<{ delivery_types: any }>> {
    return apiClient.get<{ delivery_types: any }>(
      API_CONFIG.ENDPOINTS.INVENTORY.DELIVERY_TYPES
    )
  },
}