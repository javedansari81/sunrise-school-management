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

// ============================================
// Type Definitions
// ============================================

export interface AttendanceStatus {
  id: number;
  name: string;
  description: string;
  color_code: string;
  affects_attendance_percentage: boolean;
  is_active: boolean;
}

export interface AttendancePeriod {
  id: number;
  name: string;
  description: string;
  start_time?: string;
  end_time?: string;
  is_active: boolean;
}

export interface AttendanceRecord {
  id: number;
  student_id: number;
  student_name?: string;
  admission_number?: string;
  class_id: number;
  class_name?: string;
  session_year_id: number;
  session_year_name?: string;
  attendance_date: string;
  attendance_status_id: number;
  attendance_status_name?: string;
  attendance_status_description?: string;
  attendance_status_color?: string;
  attendance_period_id: number;
  attendance_period_name?: string;
  check_in_time?: string;
  check_out_time?: string;
  remarks?: string;
  marked_by: number;
  marked_by_name?: string;
  leave_request_id?: number;
  created_at: string;
  updated_at: string;
}

export interface AttendanceFilters {
  from_date?: string;
  to_date?: string;
  class_id?: number;
  student_id?: number;
  attendance_status_id?: number;
  attendance_period_id?: number;
  session_year_id?: number;
  search?: string;
  page?: number;
  per_page?: number;
}

export interface AttendanceListResponse {
  records: AttendanceRecord[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface BulkAttendanceItem {
  student_id: number;
  attendance_status_id: number;
  remarks?: string;
}

export interface BulkAttendanceCreate {
  class_id: number;
  session_year_id: number;
  attendance_date: string;
  attendance_period_id: number;
  records: BulkAttendanceItem[];
}

export interface StudentAttendanceSummary {
  student_id: number;
  student_name: string;
  admission_number: string;
  class_name: string;
  session_year_name: string;
  total_school_days: number;
  days_present: number;
  days_absent: number;
  days_late: number;
  days_half_day: number;
  days_excused: number;
  attendance_percentage: number;
  from_date?: string;
  to_date?: string;
}

export interface ClassAttendanceByDate {
  class_id: number;
  attendance_date: string;
  session_year_id: number;
  students: any[];
  total_students: number;
  marked_count: number;
}

export interface AttendanceStatistics {
  total_records: number;
  total_present: number;
  total_absent: number;
  total_late: number;
  overall_attendance_percentage: number;
  date_range: string;
}

// ============================================
// API Functions
// ============================================

class AttendanceService {
  // List attendance records with filters
  async listAttendance(filters: AttendanceFilters = {}): Promise<AttendanceListResponse> {
    const response = await api.get('/attendance/', { params: filters });
    return response.data;
  }

  // Get single attendance record
  async getAttendance(id: number): Promise<AttendanceRecord> {
    const response = await api.get(`/attendance/${id}`);
    return response.data;
  }

  // Create attendance record
  async createAttendance(data: {
    student_id: number;
    class_id: number;
    session_year_id: number;
    attendance_date: string;
    attendance_status_id: number;
    attendance_period_id: number;
    check_in_time?: string;
    check_out_time?: string;
    remarks?: string;
    leave_request_id?: number;
  }): Promise<AttendanceRecord> {
    const response = await api.post('/attendance/', data);
    return response.data;
  }

  // Update attendance record
  async updateAttendance(id: number, data: {
    attendance_status_id?: number;
    attendance_period_id?: number;
    check_in_time?: string;
    check_out_time?: string;
    remarks?: string;
  }): Promise<AttendanceRecord> {
    const response = await api.put(`/attendance/${id}`, data);
    return response.data;
  }

  // Delete attendance record
  async deleteAttendance(id: number): Promise<void> {
    await api.delete(`/attendance/${id}`);
  }

  // Bulk attendance marking
  async bulkCreateAttendance(data: BulkAttendanceCreate): Promise<{
    message: string;
    created: number;
    updated: number;
    total_processed: number;
    errors: any[];
  }> {
    const response = await api.post('/attendance/bulk', data);
    return response.data;
  }

  // Get student attendance summary
  async getStudentSummary(
    studentId: number,
    sessionYearId: number = 4,
    fromDate?: string,
    toDate?: string
  ): Promise<StudentAttendanceSummary> {
    const response = await api.get(`/attendance/student/${studentId}/summary`, {
      params: { session_year_id: sessionYearId, from_date: fromDate, to_date: toDate }
    });
    return response.data;
  }

  // Get class attendance by date
  async getClassAttendanceByDate(
    classId: number,
    attendanceDate: string,
    sessionYearId: number = 4
  ): Promise<ClassAttendanceByDate> {
    const response = await api.get(`/attendance/class/${classId}/date/${attendanceDate}`, {
      params: { session_year_id: sessionYearId }
    });
    return response.data;
  }

  // Get attendance statistics
  async getStatistics(
    classId?: number,
    fromDate?: string,
    toDate?: string,
    sessionYearId: number = 4
  ): Promise<AttendanceStatistics> {
    const response = await api.get('/attendance/statistics/summary', {
      params: { class_id: classId, from_date: fromDate, to_date: toDate, session_year_id: sessionYearId }
    });
    return response.data;
  }

  // ============================================
  // Student-Specific Methods
  // ============================================

  // Get my attendance records (for logged-in students)
  async getMyAttendance(
    month?: number,
    year?: number,
    fromDate?: string,
    toDate?: string,
    sessionYearId: number = 4,
    page: number = 1,
    perPage: number = 100
  ): Promise<AttendanceListResponse> {
    const response = await api.get('/attendance/my-attendance', {
      params: {
        month,
        year,
        from_date: fromDate,
        to_date: toDate,
        session_year_id: sessionYearId,
        page,
        per_page: perPage
      }
    });
    return response.data;
  }

  // Get my attendance summary (for logged-in students)
  async getMyAttendanceSummary(
    sessionYearId: number = 4,
    fromDate?: string,
    toDate?: string
  ): Promise<StudentAttendanceSummary> {
    const response = await api.get('/attendance/my-attendance/summary', {
      params: { session_year_id: sessionYearId, from_date: fromDate, to_date: toDate }
    });
    return response.data;
  }
}

// Export singleton instance
export const attendanceService = new AttendanceService();
export default attendanceService;

