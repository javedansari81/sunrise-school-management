/**
 * Centralized Pagination Configuration
 * 
 * This file contains all pagination-related constants used throughout the application.
 * Changing values here will automatically affect all pages that use pagination.
 */

/**
 * Default number of records to display per page
 * This is the initial page size when a paginated view loads
 */
export const DEFAULT_PAGE_SIZE = 25;

/**
 * Minimum allowed page size
 * Users cannot select a page size smaller than this
 */
export const MIN_PAGE_SIZE = 10;

/**
 * Maximum allowed page size
 * Users cannot select a page size larger than this
 * This also serves as a safety limit to prevent performance issues
 */
export const MAX_PAGE_SIZE = 100;

/**
 * Available page size options for dropdown selectors
 * These options will be displayed in page size selection dropdowns
 */
export const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

/**
 * Default starting page number (1-indexed)
 */
export const DEFAULT_PAGE_NUMBER = 1;

/**
 * Configuration for pagination UI behavior
 */
export const PAGINATION_UI_CONFIG = {
  /**
   * Show "First" and "Last" buttons in pagination controls
   */
  showFirstLastButtons: true,
  
  /**
   * Show page size selector dropdown
   */
  showPageSizeSelector: false, // Set to true to enable page size selection
  
  /**
   * Color theme for pagination component
   */
  color: 'primary' as const,
  
  /**
   * Show "Showing X-Y of Z records" text
   */
  showRecordCount: true,
  
  /**
   * Position of pagination controls
   */
  position: 'center' as 'left' | 'center' | 'right',
};

/**
 * Helper function to calculate skip/offset value from page number
 * @param page - Current page number (1-indexed)
 * @param pageSize - Number of records per page
 * @returns Skip/offset value for database queries
 */
export const calculateSkip = (page: number, pageSize: number = DEFAULT_PAGE_SIZE): number => {
  return (page - 1) * pageSize;
};

/**
 * Helper function to calculate total pages from total records
 * @param totalRecords - Total number of records
 * @param pageSize - Number of records per page
 * @returns Total number of pages
 */
export const calculateTotalPages = (totalRecords: number, pageSize: number = DEFAULT_PAGE_SIZE): number => {
  return Math.ceil(totalRecords / pageSize);
};

/**
 * Helper function to format record count display text
 * @param page - Current page number
 * @param pageSize - Number of records per page
 * @param totalRecords - Total number of records
 * @returns Formatted string like "Showing 1-25 of 150 records"
 */
export const formatRecordCount = (page: number, pageSize: number, totalRecords: number): string => {
  if (totalRecords === 0) {
    return 'No records found';
  }
  
  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, totalRecords);
  
  return `Showing ${start}-${end} of ${totalRecords} records`;
};

/**
 * Type definition for pagination state
 */
export interface PaginationState {
  page: number;
  pageSize: number;
  totalPages: number;
  totalRecords: number;
}

/**
 * Initial pagination state
 */
export const INITIAL_PAGINATION_STATE: PaginationState = {
  page: DEFAULT_PAGE_NUMBER,
  pageSize: DEFAULT_PAGE_SIZE,
  totalPages: 1,
  totalRecords: 0,
};

/**
 * Helper function to create pagination query parameters
 * @param page - Current page number
 * @param pageSize - Number of records per page
 * @returns URLSearchParams with pagination parameters
 */
export const createPaginationParams = (page: number, pageSize: number = DEFAULT_PAGE_SIZE): URLSearchParams => {
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('per_page', pageSize.toString());
  return params;
};

/**
 * Helper function to add pagination parameters to existing URLSearchParams
 * @param params - Existing URLSearchParams object
 * @param page - Current page number
 * @param pageSize - Number of records per page
 * @returns Updated URLSearchParams with pagination parameters
 */
export const addPaginationParams = (
  params: URLSearchParams,
  page: number,
  pageSize: number = DEFAULT_PAGE_SIZE
): URLSearchParams => {
  params.set('page', page.toString());
  params.set('per_page', pageSize.toString());
  return params;
};

