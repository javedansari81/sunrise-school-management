/**
 * API Configuration - Centralized API URL Management
 * 
 * This file provides a single source of truth for API configuration.
 * All service files should import from here instead of hardcoding URLs.
 * 
 * Environment Variables:
 * - REACT_APP_API_URL: Backend API base URL (set in .env files)
 * 
 * Default Fallback:
 * - Development: http://localhost:8000/api/v1
 * - Production: Must be set via REACT_APP_API_URL environment variable
 */

/**
 * Get the API base URL from environment variables
 * Falls back to localhost for development if not set
 */
export const getApiBaseUrl = (): string => {
  const apiUrl = process.env.REACT_APP_API_URL;
  
  // In production, API URL must be set
  if (process.env.NODE_ENV === 'production' && !apiUrl) {
    throw new Error('API URL must be configured for production deployment');
  }
  
  // Use environment variable or fallback to localhost for development
  const baseUrl = apiUrl || 'http://localhost:8000/api/v1';

  return baseUrl;
};

/**
 * API Base URL - Use this constant in all service files
 */
export const API_BASE_URL = getApiBaseUrl();

/**
 * API Timeout Configuration (in milliseconds)
 */
export const API_TIMEOUT = 10000; // 10 seconds

/**
 * API Timeout for File Uploads (in milliseconds)
 */
export const API_UPLOAD_TIMEOUT = 60000; // 60 seconds

/**
 * Default API Headers
 */
export const DEFAULT_API_HEADERS = {
  'Content-Type': 'application/json',
};

/**
 * API Configuration Object
 * Use this for creating axios instances
 */
export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: DEFAULT_API_HEADERS,
};

/**
 * API Configuration for File Uploads
 * Use this for upload endpoints
 */
export const uploadApiConfig = {
  baseURL: API_BASE_URL,
  timeout: API_UPLOAD_TIMEOUT,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
};

export default {
  API_BASE_URL,
  API_TIMEOUT,
  API_UPLOAD_TIMEOUT,
  DEFAULT_API_HEADERS,
  apiConfig,
  uploadApiConfig,
  getApiBaseUrl,
};

