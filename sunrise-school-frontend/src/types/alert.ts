/**
 * TypeScript types for Alert/Notification system
 * Matches backend schemas in sunrise-backend-fastapi/app/schemas/alert.py
 */

// Alert Type metadata
export interface AlertType {
  id: number;
  name: string;
  description?: string;
  category: string;
  icon?: string;
  color_code?: string;
  priority_level: number;
  default_expiry_days: number;
  requires_acknowledgment: boolean;
  is_active: boolean;
}

// Alert Status metadata
export interface AlertStatus {
  id: number;
  name: string;
  description?: string;
  color_code?: string;
  is_final: boolean;
  is_active: boolean;
}

// Main Alert interface
export interface Alert {
  id: number;
  alert_type_id: number;
  alert_status_id: number;
  title: string;
  message: string;
  entity_type: string;
  entity_id: number;
  entity_display_name?: string;
  target_role?: string;
  target_user_id?: number;
  alert_metadata?: Record<string, any>;
  priority_level: number;
  actor_user_id?: number;
  actor_type?: string;
  actor_name?: string;
  read_at?: string;
  read_by?: number;
  acknowledged_at?: string;
  acknowledged_by?: number;
  expires_at?: string;
  created_at: string;
  updated_at?: string;
  // Enriched fields from relationships
  alert_type_name?: string;
  alert_type_icon?: string;
  alert_type_color?: string;
  alert_type_category?: string;
  alert_status_name?: string;
  alert_status_color?: string;
}

// Alert with full metadata details
export interface AlertWithDetails extends Alert {
  alert_type?: AlertType;
  alert_status?: AlertStatus;
}

// Paginated alert list response
export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  unread_count: number;
}

// Alert filters for queries
export interface AlertFilters {
  alert_type_id?: number;
  alert_status_id?: number;
  category?: string;
  entity_type?: string;
  target_role?: string;
  priority_level?: number;
  from_date?: string;
  to_date?: string;
  is_read?: boolean;
}

// Alert statistics for dashboard
export interface AlertStats {
  total_alerts: number;
  unread_count: number;
  by_category: Record<string, number>;
  by_priority: Record<string, number>;
  recent_count: number;
}

// Unread count response
export interface AlertUnreadCountResponse {
  unread_count: number;
}

// Action response (mark read, acknowledge, etc.)
export interface AlertActionResponse {
  message: string;
  alert_id?: number;
  count?: number;
}

// Alert category enum values
export type AlertCategory = 
  | 'LEAVE_MANAGEMENT'
  | 'FINANCIAL'
  | 'ACADEMIC'
  | 'ADMINISTRATIVE'
  | 'SYSTEM';

// Alert entity type enum values
export type AlertEntityType =
  | 'LEAVE_REQUEST'
  | 'FEE_PAYMENT'
  | 'TRANSPORT_PAYMENT'
  | 'COMBINED_PAYMENT'
  | 'STUDENT'
  | 'TEACHER'
  | 'ATTENDANCE'
  | 'INVENTORY';

// Alert status IDs (from database)
export const ALERT_STATUS = {
  UNREAD: 1,
  READ: 2,
  ACKNOWLEDGED: 3,
  DISMISSED: 4,
  EXPIRED: 5,
} as const;

// Priority levels
export const ALERT_PRIORITY = {
  LOW: 1,
  NORMAL: 2,
  HIGH: 3,
  CRITICAL: 4,
} as const;

