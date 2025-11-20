/**
 * Date utility functions for handling date formatting and conversions
 */

/**
 * Formats a Date object to YYYY-MM-DD string format without timezone conversion
 * This ensures the date stays the same regardless of timezone
 * 
 * @param date - The Date object to format
 * @returns Formatted date string in YYYY-MM-DD format
 * 
 * @example
 * const date = new Date(2025, 10, 20); // November 20, 2025
 * formatDateForAPI(date); // Returns "2025-11-20"
 */
export const formatDateForAPI = (date: Date | null | undefined): string | null => {
  if (!date) return null;
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
};

/**
 * Parses a date string (YYYY-MM-DD) to a Date object
 * 
 * @param dateString - The date string to parse
 * @returns Date object or null if invalid
 */
export const parseDateFromAPI = (dateString: string | null | undefined): Date | null => {
  if (!dateString) return null;
  
  try {
    const [year, month, day] = dateString.split('-').map(Number);
    return new Date(year, month - 1, day);
  } catch {
    return null;
  }
};

/**
 * Formats a date for display in a human-readable format
 * 
 * @param date - The Date object to format
 * @param locale - The locale to use for formatting (default: 'en-IN')
 * @returns Formatted date string
 */
export const formatDateForDisplay = (
  date: Date | string | null | undefined,
  locale: string = 'en-IN'
): string => {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? parseDateFromAPI(date) : date;
  if (!dateObj) return '';
  
  return dateObj.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

