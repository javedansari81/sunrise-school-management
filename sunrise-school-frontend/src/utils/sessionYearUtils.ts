/**
 * Session Year Utility Functions
 * Common utility functions for session year operations across the application
 */

import { 
  SessionYearEnum, 
  SessionYearIdEnum,
  SESSION_YEAR_TO_ID_MAP,
  ID_TO_SESSION_YEAR_MAP,
  getCurrentSessionYear,
  getCurrentSessionYearId,
  DEFAULT_SESSION_YEAR,
  DEFAULT_SESSION_YEAR_ID
} from '../constants/sessionYear';

/**
 * Validates if a session year string is valid
 * @param sessionYear - Session year string (e.g., "2025-26")
 * @returns boolean indicating if the session year is valid
 */
export const isValidSessionYear = (sessionYear: string): boolean => {
  return Object.values(SessionYearEnum).includes(sessionYear as SessionYearEnum);
};

/**
 * Validates if a session year ID is valid
 * @param sessionYearId - Session year ID (1-5)
 * @returns boolean indicating if the session year ID is valid
 */
export const isValidSessionYearId = (sessionYearId: string | number): boolean => {
  const id = typeof sessionYearId === 'string' ? parseInt(sessionYearId) : sessionYearId;
  return Object.values(SessionYearIdEnum).includes(id);
};

/**
 * Gets all available session years as an array of objects
 * @returns Array of session year objects with id and name
 */
export const getAllSessionYears = () => {
  return Object.entries(SESSION_YEAR_TO_ID_MAP).map(([name, id]) => ({
    id: parseInt(id),
    name,
    display_name: name
  }));
};

/**
 * Gets session year options for dropdowns
 * @returns Array of dropdown options
 */
export const getSessionYearOptions = () => {
  return getAllSessionYears().map(sy => ({
    value: sy.id.toString(),
    label: sy.name,
    id: sy.id,
    name: sy.name
  }));
};

/**
 * Formats session year for display
 * @param sessionYear - Session year string or ID
 * @returns Formatted session year string
 */
export const formatSessionYear = (sessionYear: string | number): string => {
  if (typeof sessionYear === 'number' || !isNaN(Number(sessionYear))) {
    return ID_TO_SESSION_YEAR_MAP[sessionYear.toString()] || DEFAULT_SESSION_YEAR;
  }
  return isValidSessionYear(sessionYear) ? sessionYear : DEFAULT_SESSION_YEAR;
};

/**
 * Gets the next session year
 * @param currentSessionYear - Current session year string (optional)
 * @returns Next session year string
 */
export const getNextSessionYear = (currentSessionYear?: string): string => {
  const current = currentSessionYear || getCurrentSessionYear();
  const currentId = SESSION_YEAR_TO_ID_MAP[current];
  
  if (!currentId) return DEFAULT_SESSION_YEAR;
  
  const nextId = (parseInt(currentId) + 1).toString();
  return ID_TO_SESSION_YEAR_MAP[nextId] || DEFAULT_SESSION_YEAR;
};

/**
 * Gets the previous session year
 * @param currentSessionYear - Current session year string (optional)
 * @returns Previous session year string
 */
export const getPreviousSessionYear = (currentSessionYear?: string): string => {
  const current = currentSessionYear || getCurrentSessionYear();
  const currentId = SESSION_YEAR_TO_ID_MAP[current];
  
  if (!currentId) return DEFAULT_SESSION_YEAR;
  
  const prevId = (parseInt(currentId) - 1).toString();
  return ID_TO_SESSION_YEAR_MAP[prevId] || DEFAULT_SESSION_YEAR;
};

/**
 * Checks if a session year is the current academic year
 * @param sessionYear - Session year string to check
 * @returns boolean indicating if it's the current academic year
 */
export const isCurrentAcademicYear = (sessionYear: string): boolean => {
  return sessionYear === getCurrentSessionYear();
};

/**
 * Gets session year range (start and end dates)
 * @param sessionYear - Session year string
 * @returns Object with start and end dates
 */
export const getSessionYearRange = (sessionYear: string) => {
  const [startYear, endYear] = sessionYear.split('-');
  const fullEndYear = `20${endYear}`;
  
  return {
    startDate: `${startYear}-04-01`, // April 1st
    endDate: `${fullEndYear}-03-31`,  // March 31st
    startYear: parseInt(startYear),
    endYear: parseInt(fullEndYear)
  };
};

// Re-export constants for convenience
export {
  SessionYearEnum,
  SessionYearIdEnum,
  SESSION_YEAR_TO_ID_MAP,
  ID_TO_SESSION_YEAR_MAP,
  getCurrentSessionYear,
  getCurrentSessionYearId,
  DEFAULT_SESSION_YEAR,
  DEFAULT_SESSION_YEAR_ID
};
