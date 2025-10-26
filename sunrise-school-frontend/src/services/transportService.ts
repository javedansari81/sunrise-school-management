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

// Transport Types
export interface TransportType {
  id: number;
  name: string;
  description: string;
  base_monthly_fee: number;
  capacity: number;
  is_active: boolean;
}

// Distance Slabs
export interface TransportDistanceSlab {
  id: number;
  transport_type_id: number;
  distance_from_km: number;
  distance_to_km: number;
  monthly_fee: number;
  is_active: boolean;
}

// Student Transport Enrollment
export interface StudentTransportEnrollment {
  id: number;
  student_id: number;
  session_year_id: number;
  transport_type_id: number;
  enrollment_date: string;
  discontinue_date?: string;
  is_active: boolean;
  distance_km?: number;
  monthly_fee: number;
  pickup_location?: string;
  drop_location?: string;
  created_at: string;
  updated_at: string;
}

// Enhanced Student Transport Summary
export interface EnhancedStudentTransportSummary {
  student_id: number;
  admission_number: string;
  student_name: string;
  class_name: string;
  session_year: string;
  enrollment_id?: number;
  transport_type_id?: number;
  transport_type_name?: string;
  enrollment_date?: string;
  discontinue_date?: string;
  is_enrolled: boolean;
  distance_km?: number;
  monthly_fee?: number;
  pickup_location?: string;
  drop_location?: string;
  total_months_tracked: number;
  enabled_months: number;
  paid_months: number;
  pending_months: number;
  overdue_months: number;
  total_amount: number;
  total_paid: number;
  total_balance: number;
  collection_percentage: number;
  has_monthly_tracking: boolean;
}

// Monthly Tracking
export interface TransportMonthlyTracking {
  id: number;
  enrollment_id: number;
  student_id: number;
  session_year_id: number;
  academic_month: number;
  academic_year: number;
  month_name: string;
  is_service_enabled: boolean;
  monthly_amount: number;
  paid_amount: number;
  balance_amount: number;
  due_date?: string;
  payment_status_id: number;
  payment_status?: string;
  created_at: string;
  updated_at: string;
}

// Student Transport Monthly History
export interface StudentTransportMonthlyHistory {
  student_id: number;
  student_name: string;
  class_name: string;
  session_year: string;
  transport_type_name: string;
  monthly_fee_amount: number;

  // Monthly records
  monthly_history: TransportMonthlyTracking[];

  // Summary fields (flat structure, not nested)
  total_months: number;
  enabled_months: number;
  paid_months: number;
  pending_months: number;
  overdue_months: number;
  total_paid: number;
  total_balance: number;
  collection_percentage: number;
}

// Request Types
export interface EnrollStudentRequest {
  student_id: number;
  session_year_id: number;
  transport_type_id: number;
  enrollment_date: string;
  monthly_fee: number;
  distance_km?: number;
  pickup_location?: string;
  drop_location?: string;
}

export interface UpdateEnrollmentRequest {
  transport_type_id?: number;
  distance_km?: number;
  monthly_fee?: number;
  pickup_location?: string;
  drop_location?: string;
}

export interface EnableMonthlyTrackingRequest {
  enrollment_ids: number[];
  start_month: number;
  start_year: number;
}

export interface TransportPaymentRequest {
  amount: number;
  payment_method_id: number;
  selected_months: number[];
  transaction_id?: string;
  remarks?: string;
}

// API Functions
const transportService = {
  // Get all transport types
  getTransportTypes: async (): Promise<TransportType[]> => {
    const response = await api.get('/transport/transport-types');
    return response.data;
  },

  // Get distance slabs for a transport type
  getDistanceSlabs: async (transportTypeId: number): Promise<TransportDistanceSlab[]> => {
    const response = await api.get(`/transport/distance-slabs/${transportTypeId}`);
    return response.data;
  },

  // Enroll student in transport
  enrollStudent: async (data: EnrollStudentRequest): Promise<StudentTransportEnrollment> => {
    const response = await api.post('/transport/enroll', data);
    return response.data;
  },

  // Update enrollment
  updateEnrollment: async (enrollmentId: number, data: UpdateEnrollmentRequest): Promise<StudentTransportEnrollment> => {
    const response = await api.put(`/transport/enrollment/${enrollmentId}`, data);
    return response.data;
  },

  // Discontinue transport service
  discontinueService: async (enrollmentId: number, discontinueDate: string): Promise<any> => {
    const response = await api.post(`/transport/discontinue/${enrollmentId}`, null, {
      params: { discontinue_date: discontinueDate }
    });
    return response.data;
  },

  // Get all students with transport status
  getStudents: async (params: {
    session_year?: string;
    class_id?: number;
    enrollment_status?: string;
    student_name?: string;
    skip?: number;
    limit?: number;
  }): Promise<EnhancedStudentTransportSummary[]> => {
    const response = await api.get('/transport/students', { params });
    return response.data;
  },

  // Enable monthly tracking
  enableMonthlyTracking: async (data: EnableMonthlyTrackingRequest): Promise<any> => {
    const response = await api.post('/transport/enable-monthly-tracking', data);
    return response.data;
  },

  // Get monthly history for a student
  getMonthlyHistory: async (studentId: number, sessionYearId: number): Promise<StudentTransportMonthlyHistory> => {
    const response = await api.get(`/transport/monthly-history/${studentId}`, {
      params: { session_year_id: sessionYearId }
    });
    return response.data;
  },

  // Process payment
  processPayment: async (studentId: number, sessionYearId: number, data: TransportPaymentRequest): Promise<any> => {
    const response = await api.post(`/transport/pay-monthly/${studentId}?session_year_id=${sessionYearId}`, data);
    return response.data;
  },

  // Get transport management configuration
  getConfiguration: async (): Promise<any> => {
    const response = await api.get('/configuration/transport-management/');
    return response.data;
  }
};

export default transportService;

