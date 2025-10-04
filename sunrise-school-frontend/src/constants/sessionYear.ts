/**
 * Session Year Constants and Mappings
 * Centralized definitions for session year handling across the application
 */

// Session Year Enum for type safety
export enum SessionYearEnum {
  YEAR_2022_23 = '2022-23',
  YEAR_2023_24 = '2023-24',
  YEAR_2024_25 = '2024-25',
  YEAR_2025_26 = '2025-26',
  YEAR_2026_27 = '2026-27'
}

// Session Year ID Enum for database IDs
export enum SessionYearIdEnum {
  YEAR_2022_23 = 1,
  YEAR_2023_24 = 2,
  YEAR_2024_25 = 3,
  YEAR_2025_26 = 4,
  YEAR_2026_27 = 5
}

// Mapping from session year string to database ID (as string for form compatibility)
export const SESSION_YEAR_TO_ID_MAP: { [key: string]: string } = {
  [SessionYearEnum.YEAR_2022_23]: SessionYearIdEnum.YEAR_2022_23.toString(),
  [SessionYearEnum.YEAR_2023_24]: SessionYearIdEnum.YEAR_2023_24.toString(),
  [SessionYearEnum.YEAR_2024_25]: SessionYearIdEnum.YEAR_2024_25.toString(),
  [SessionYearEnum.YEAR_2025_26]: SessionYearIdEnum.YEAR_2025_26.toString(),
  [SessionYearEnum.YEAR_2026_27]: SessionYearIdEnum.YEAR_2026_27.toString()
};

// Mapping from database ID to session year string
export const ID_TO_SESSION_YEAR_MAP: { [key: string]: string } = {
  [SessionYearIdEnum.YEAR_2022_23.toString()]: SessionYearEnum.YEAR_2022_23,
  [SessionYearIdEnum.YEAR_2023_24.toString()]: SessionYearEnum.YEAR_2023_24,
  [SessionYearIdEnum.YEAR_2024_25.toString()]: SessionYearEnum.YEAR_2024_25,
  [SessionYearIdEnum.YEAR_2025_26.toString()]: SessionYearEnum.YEAR_2025_26,
  [SessionYearIdEnum.YEAR_2026_27.toString()]: SessionYearEnum.YEAR_2026_27
};

// Helper function to get session year ID by session year string
export const getSessionYearId = (sessionYear: string): string => {
  return SESSION_YEAR_TO_ID_MAP[sessionYear] || SessionYearIdEnum.YEAR_2025_26.toString();
};

// Helper function to get session year string by ID
export const getSessionYearById = (id: string | number): string => {
  return ID_TO_SESSION_YEAR_MAP[id.toString()] || SessionYearEnum.YEAR_2025_26;
};

// Helper function to calculate current session year based on date
export const getCurrentSessionYear = (): string => {
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1; // JavaScript months are 0-indexed
  
  // Academic year starts in April (month 4)
  // If current month is April or later, use current year as start year
  // If current month is before April, use previous year as start year
  const sessionStartYear = currentMonth >= 4 ? currentYear : currentYear - 1;
  const sessionEndYear = sessionStartYear + 1;
  
  return `${sessionStartYear}-${sessionEndYear.toString().slice(-2)}`;
};

// Helper function to get current session year ID
export const getCurrentSessionYearId = (): string => {
  const currentSessionYear = getCurrentSessionYear();
  return getSessionYearId(currentSessionYear);
};

// Default session year (fallback)
export const DEFAULT_SESSION_YEAR = SessionYearEnum.YEAR_2025_26;
export const DEFAULT_SESSION_YEAR_ID = SessionYearIdEnum.YEAR_2025_26.toString();
