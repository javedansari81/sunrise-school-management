/**
 * Alert/Notification Service
 * Provides API calls for alert management
 */

import api from './api';
import {
  Alert,
  AlertListResponse,
  AlertWithDetails,
  AlertStats,
  AlertUnreadCountResponse,
  AlertActionResponse,
  AlertFilters,
} from '../types/alert';

/**
 * Alert API service
 */
export const alertAPI = {
  /**
   * Get alerts for the current user with filtering and pagination
   */
  getAlerts: async (params?: {
    alert_type_id?: number;
    alert_status_id?: number;
    category?: string;
    entity_type?: string;
    priority_level?: number;
    is_read?: boolean;
    page?: number;
    per_page?: number;
  }): Promise<AlertListResponse> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
    }
    const response = await api.get(`/alerts?${queryParams.toString()}`);
    return response.data;
  },

  /**
   * Get unread alert count for the current user
   */
  getUnreadCount: async (): Promise<AlertUnreadCountResponse> => {
    const response = await api.get('/alerts/unread-count');
    return response.data;
  },

  /**
   * Get alert statistics for dashboard
   */
  getStats: async (): Promise<AlertStats> => {
    const response = await api.get('/alerts/stats');
    return response.data;
  },

  /**
   * Get a specific alert by ID
   */
  getAlert: async (alertId: number): Promise<AlertWithDetails> => {
    const response = await api.get(`/alerts/${alertId}`);
    return response.data;
  },

  /**
   * Mark a specific alert as read
   */
  markAsRead: async (alertId: number): Promise<AlertActionResponse> => {
    const response = await api.patch(`/alerts/${alertId}/read`);
    return response.data;
  },

  /**
   * Mark all alerts as read for the current user
   */
  markAllAsRead: async (): Promise<AlertActionResponse> => {
    const response = await api.patch('/alerts/mark-all-read');
    return response.data;
  },

  /**
   * Acknowledge an alert (for alerts requiring acknowledgment)
   */
  acknowledgeAlert: async (alertId: number): Promise<AlertActionResponse> => {
    const response = await api.patch(`/alerts/${alertId}/acknowledge`);
    return response.data;
  },

  /**
   * Dismiss/soft-delete an alert
   */
  dismissAlert: async (alertId: number): Promise<AlertActionResponse> => {
    const response = await api.delete(`/alerts/${alertId}`);
    return response.data;
  },
};

export default alertAPI;

