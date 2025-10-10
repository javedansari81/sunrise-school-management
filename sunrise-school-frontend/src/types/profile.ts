// Profile data type definitions

export interface UserInfo {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  user_type: string;
  user_type_id: number;
  created_at: string;
  updated_at?: string;
  is_active: boolean;
}

export interface StudentProfile {
  id: number;
  admission_number: string;
  roll_number?: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  blood_group?: string;
  
  // Contact Information
  phone?: string;
  email?: string;
  aadhar_no?: string;
  
  // Address Information
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  
  // Academic Information
  class_id?: number;
  class_name?: string;
  class_description?: string;
  section?: string;
  session_year_id?: number;
  session_year_name?: string;
  session_year_description?: string;
  admission_date?: string;
  
  // Gender Information
  gender_id?: number;
  gender_name?: string;
  gender_description?: string;
  
  // Parent/Guardian Information
  father_name?: string;
  father_phone?: string;
  father_email?: string;
  father_occupation?: string;
  mother_name?: string;
  mother_phone?: string;
  mother_email?: string;
  mother_occupation?: string;
  guardian_name?: string;
  guardian_phone?: string;
  guardian_email?: string;
  guardian_relation?: string;
  
  // Status
  is_active: boolean;
}

export interface TeacherProfile {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  
  // Contact Information
  phone?: string;
  email?: string;
  aadhar_no?: string;
  
  // Address Information
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  
  // Emergency Contact
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  
  // Professional Information
  department_id?: number;
  department_name?: string;
  department_description?: string;
  position_id?: number;
  position_name?: string;
  position_description?: string;
  qualification_id?: number;
  qualification_name?: string;
  qualification_description?: string;
  employment_status_id?: number;
  employment_status_name?: string;
  employment_status_description?: string;
  experience_years?: number;
  joining_date?: string;
  subjects?: string;
  classes_assigned?: string;
  class_teacher_of_id?: number;
  class_teacher_of_name?: string;
  salary?: number;
  
  // Gender Information
  gender_id?: number;
  gender_name?: string;
  gender_description?: string;
  
  // Status
  is_active: boolean;
}

export interface AdminProfile {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  
  // Contact Information
  phone?: string;
  email?: string;
  aadhar_no?: string;
  
  // Address Information
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  
  // Professional Information
  department_id?: number;
  department_name?: string;
  department_description?: string;
  position_id?: number;
  position_name?: string;
  position_description?: string;
  qualification_id?: number;
  qualification_name?: string;
  qualification_description?: string;
  employment_status_id?: number;
  employment_status_name?: string;
  employment_status_description?: string;
  experience_years?: number;
  joining_date?: string;
  
  // Gender Information
  gender_id?: number;
  gender_name?: string;
  gender_description?: string;
  
  // Status
  is_active: boolean;
}

export interface ProfileData {
  user_info: UserInfo;
  student_profile?: StudentProfile;
  teacher_profile?: TeacherProfile;
  admin_profile?: AdminProfile;
}

export interface ProfileUpdateData {
  first_name?: string;
  last_name?: string;
  phone?: string;
  student_profile?: Partial<StudentProfile>;
  teacher_profile?: Partial<TeacherProfile>;
  admin_profile?: Partial<AdminProfile>;
}

// Configuration data for dropdowns
export interface ConfigurationOption {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
}

export interface ProfileConfiguration {
  genders: ConfigurationOption[];
  classes: ConfigurationOption[];
  session_years: ConfigurationOption[];
  departments: ConfigurationOption[];
  positions: ConfigurationOption[];
  qualifications: ConfigurationOption[];
  employment_statuses: ConfigurationOption[];
}
