/**
 * User Type Constants and Mappings
 * Centralized definitions for user type handling across the application
 * These values correspond to the IDs in the user_types metadata table
 */

// User Type Enum for type safety
export enum UserTypeEnum {
  ADMIN = 'ADMIN',
  TEACHER = 'TEACHER',
  STUDENT = 'STUDENT',
  STAFF = 'STAFF',
  PARENT = 'PARENT',
  SUPER_ADMIN = 'SUPER_ADMIN'
}

// User Type ID Enum for database IDs
export enum UserTypeIdEnum {
  ADMIN = 1,
  TEACHER = 2,
  STUDENT = 3,
  STAFF = 4,
  PARENT = 5,
  SUPER_ADMIN = 6
}

// Mapping from user type string to database ID
export const USER_TYPE_TO_ID_MAP: { [key: string]: number } = {
  [UserTypeEnum.ADMIN]: UserTypeIdEnum.ADMIN,
  [UserTypeEnum.TEACHER]: UserTypeIdEnum.TEACHER,
  [UserTypeEnum.STUDENT]: UserTypeIdEnum.STUDENT,
  [UserTypeEnum.STAFF]: UserTypeIdEnum.STAFF,
  [UserTypeEnum.PARENT]: UserTypeIdEnum.PARENT,
  [UserTypeEnum.SUPER_ADMIN]: UserTypeIdEnum.SUPER_ADMIN
};

// Mapping from database ID to user type string
export const ID_TO_USER_TYPE_MAP: { [key: number]: string } = {
  [UserTypeIdEnum.ADMIN]: UserTypeEnum.ADMIN,
  [UserTypeIdEnum.TEACHER]: UserTypeEnum.TEACHER,
  [UserTypeIdEnum.STUDENT]: UserTypeEnum.STUDENT,
  [UserTypeIdEnum.STAFF]: UserTypeEnum.STAFF,
  [UserTypeIdEnum.PARENT]: UserTypeEnum.PARENT,
  [UserTypeIdEnum.SUPER_ADMIN]: UserTypeEnum.SUPER_ADMIN
};

// Helper function to get user type ID by user type string
export const getUserTypeId = (userType: string): number => {
  return USER_TYPE_TO_ID_MAP[userType.toUpperCase()] ?? UserTypeIdEnum.STUDENT;
};

// Helper function to get user type string by ID
export const getUserTypeByIdFn = (userTypeId: number): string => {
  return ID_TO_USER_TYPE_MAP[userTypeId] ?? UserTypeEnum.STUDENT;
};

// Admin-level roles that have administrative access
export const ADMIN_ROLES = [UserTypeEnum.ADMIN, UserTypeEnum.SUPER_ADMIN];

// Helper function to check if a user type has admin privileges
export const isAdminRole = (userType: string): boolean => {
  const upperType = userType?.toUpperCase();
  return ADMIN_ROLES.includes(upperType as UserTypeEnum);
};

