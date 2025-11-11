import axios from 'axios';
import { apiConfig } from '../config/apiConfig';

// Create axios instance with base configuration
const api = axios.create(apiConfig);

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// =====================================================
// Type Definitions
// =====================================================

export interface InventoryItemType {
  id: number;
  name: string;
  description: string;
  category: string;
  image_url?: string;
  is_active: boolean;
}

export interface InventorySizeType {
  id: number;
  name: string;
  description: string;
  sort_order: number;
  is_active: boolean;
}

export interface InventoryPricing {
  id: number;
  inventory_item_type_id: number;
  size_type_id?: number;
  class_id?: number;
  session_year_id: number;
  unit_price: number;
  description?: string;
  effective_from?: string;
  effective_to?: string;
  is_active: boolean;
  item_type_name: string;
  item_type_description: string;
  item_image_url?: string;
  size_name?: string;
  class_name?: string;
  session_year_name: string;
  created_at: string;
}

export interface InventoryPurchaseItem {
  id?: number;
  inventory_item_type_id: number;
  size_type_id?: number;
  quantity: number;
  unit_price: number;
  total_price: number;
  item_type_name?: string;
  item_type_description?: string;
  item_image_url?: string;
  size_name?: string;
  created_at?: string;
}

export interface InventoryPurchase {
  id: number;
  student_id: number;
  session_year_id: number;
  purchase_date: string;
  total_amount: number;
  payment_method_id: number;
  payment_date?: string;
  transaction_id?: string;
  receipt_number: string;
  remarks?: string;
  purchased_by?: string;
  contact_number?: string;
  student_name: string;
  student_admission_number: string;
  student_class_name: string;
  student_roll_number?: string;
  session_year_name: string;
  payment_method_name: string;
  items: InventoryPurchaseItem[];
  created_at: string;
}

export interface InventoryPurchaseListResponse {
  purchases: InventoryPurchase[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface InventoryStatistics {
  total_purchases: number;
  total_revenue: number;
  total_students: number;
  items_sold_by_type: Array<{
    item_name: string;
    quantity: number;
    revenue: number;
  }>;
  purchases_by_month: Array<{
    month: string;
    count: number;
    revenue: number;
  }>;
  top_selling_items: Array<{
    item_name: string;
    quantity: number;
  }>;
}

// =====================================================
// Pricing API Functions
// =====================================================

export const getPricing = async (params?: {
  session_year_id?: number;
  item_type_id?: number;
  class_id?: number;
  is_active?: boolean;
}): Promise<InventoryPricing[]> => {
  const response = await api.get('/inventory/pricing/', { params });
  return response.data;
};

export const createPricing = async (data: {
  inventory_item_type_id: number;
  size_type_id?: number;
  class_id?: number;
  session_year_id: number;
  unit_price: number;
  description?: string;
  effective_from?: string;
  effective_to?: string;
  is_active?: boolean;
}): Promise<InventoryPricing> => {
  const response = await api.post('/inventory/pricing/', data);
  return response.data;
};

export const updatePricing = async (
  pricingId: number,
  data: {
    unit_price?: number;
    description?: string;
    effective_from?: string;
    effective_to?: string;
    is_active?: boolean;
  }
): Promise<InventoryPricing> => {
  const response = await api.put(`/inventory/pricing/${pricingId}`, data);
  return response.data;
};

// =====================================================
// Item Type Image Upload
// =====================================================

export const uploadItemTypeImage = async (
  itemTypeId: number,
  file: File
): Promise<{ message: string; item_type_id: number; image_url: string }> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post(
    `/inventory/item-types/${itemTypeId}/upload-image`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for file upload
    }
  );
  return response.data;
};

// =====================================================
// Purchase API Functions
// =====================================================

export const getPurchases = async (params?: {
  session_year_id?: number;
  student_id?: number;
  class_id?: number;
  from_date?: string;
  to_date?: string;
  search?: string;
  page?: number;
  per_page?: number;
}): Promise<InventoryPurchaseListResponse> => {
  const response = await api.get('/inventory/purchases/', { params });
  return response.data;
};

export const createPurchase = async (data: {
  student_id: number;
  session_year_id: number;
  purchase_date: string;
  payment_method_id: number;
  payment_date?: string;
  transaction_id?: string;
  remarks?: string;
  purchased_by?: string;
  contact_number?: string;
  items: Array<{
    inventory_item_type_id: number;
    size_type_id?: number;
    quantity: number;
    unit_price: number;
  }>;
}): Promise<InventoryPurchase> => {
  const response = await api.post('/inventory/purchases/', data);
  return response.data;
};

export const getPurchaseById = async (purchaseId: number): Promise<InventoryPurchase> => {
  const response = await api.get(`/inventory/purchases/${purchaseId}`);
  return response.data;
};

// =====================================================
// Statistics API Functions
// =====================================================

export const getStatistics = async (params?: {
  session_year_id?: number;
  from_date?: string;
  to_date?: string;
}): Promise<InventoryStatistics> => {
  const response = await api.get('/inventory/statistics/', { params });
  return response.data;
};

// =====================================================
// Helper Functions
// =====================================================

export const calculateItemTotal = (quantity: number, unitPrice: number): number => {
  return quantity * unitPrice;
};

// =====================================================
// Stock Management Type Definitions
// =====================================================

export interface InventoryStock {
  id: number;
  inventory_item_type_id: number;
  size_type_id?: number;
  current_quantity: number;
  minimum_threshold: number;
  reorder_quantity: number;
  item_type_name: string;
  item_type_description: string;
  item_category?: string;
  item_image_url?: string;
  size_name?: string;
  last_restocked_date?: string;
  last_updated: string;
  is_low_stock: boolean;
}

export interface LowStockAlert {
  stock_id: number;
  inventory_item_type_id: number;
  size_type_id?: number;
  item_type_name: string;
  item_type_description: string;
  size_name?: string;
  current_quantity: number;
  minimum_threshold: number;
  reorder_quantity: number;
  shortage: number;
  alert_level: 'WARNING' | 'CRITICAL';
}

export interface InventoryStockProcurementItem {
  id?: number;
  inventory_item_type_id: number;
  size_type_id?: number;
  quantity: number;
  unit_cost: number;
  total_cost?: number;
  item_type_name?: string;
  item_type_description?: string;
  item_image_url?: string;
  size_name?: string;
  created_at?: string;
}

export interface InventoryStockProcurement {
  id: number;
  vendor_id?: number;
  procurement_date: string;
  invoice_number?: string;
  total_amount: number;
  payment_method_id: number;
  payment_status_id: number;
  payment_date?: string;
  payment_reference?: string;
  remarks?: string;
  invoice_url?: string;
  vendor_name?: string;
  payment_method_name: string;
  payment_status_name: string;
  items: InventoryStockProcurementItem[];
  created_at: string;
}

export interface InventoryStockProcurementListResponse {
  procurements: InventoryStockProcurement[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// =====================================================
// Stock Management API Functions
// =====================================================

export const getStockLevels = async (params?: {
  item_type_id?: number;
  size_type_id?: number;
  low_stock_only?: boolean;
  page?: number;
  per_page?: number;
}): Promise<InventoryStock[]> => {
  const response = await api.get('/inventory/stock/levels/', { params });
  return response.data;
};

export const getLowStockAlerts = async (): Promise<LowStockAlert[]> => {
  const response = await api.get('/inventory/stock/low-stock-alerts/');
  return response.data;
};

export const updateStockThreshold = async (
  stockId: number,
  data: {
    current_quantity?: number;
    minimum_threshold?: number;
    reorder_quantity?: number;
  }
): Promise<InventoryStock> => {
  const response = await api.put(`/inventory/stock/${stockId}/threshold/`, data);
  return response.data;
};

// =====================================================
// Stock Procurement API Functions
// =====================================================

export const getStockProcurements = async (params?: {
  vendor_id?: number;
  from_date?: string;
  to_date?: string;
  payment_status_id?: number;
  page?: number;
  per_page?: number;
}): Promise<InventoryStockProcurementListResponse> => {
  const response = await api.get('/inventory/stock/procurements/', { params });
  return response.data;
};

export const createStockProcurement = async (data: {
  vendor_id?: number;
  procurement_date: string;
  invoice_number?: string;
  payment_method_id: number;
  payment_status_id?: number;
  payment_date?: string;
  payment_reference?: string;
  remarks?: string;
  invoice_url?: string;
  items: Array<{
    inventory_item_type_id: number;
    size_type_id?: number;
    quantity: number;
    unit_cost: number;
  }>;
}): Promise<InventoryStockProcurement> => {
  const response = await api.post('/inventory/stock/procurements/', data);
  return response.data;
};

export const calculatePurchaseTotal = (items: Array<{ quantity: number; unit_price: number }>): number => {
  return items.reduce((total, item) => total + (item.quantity * item.unit_price), 0);
};

export const formatReceiptNumber = (receiptNumber: string): string => {
  return receiptNumber;
};

export const formatItemDescription = (itemName: string, sizeName?: string): string => {
  if (sizeName && sizeName !== 'FREE_SIZE') {
    return `${itemName} (${sizeName})`;
  }
  return itemName;
};

