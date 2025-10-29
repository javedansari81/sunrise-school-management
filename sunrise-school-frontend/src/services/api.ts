import axios from 'axios';
import { sessionService } from './sessionService';
import { apiConfig } from '../config/apiConfig';

// Create axios instance with base configuration
const api = axios.create(apiConfig);

// Create a separate axios instance for public endpoints (no auth required)
const publicApi = axios.create(apiConfig);

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      // Check if token is expired before making request
      if (sessionService.isTokenExpired(token)) {
        sessionService.handleSessionInvalid();
        return Promise.reject(new Error('Session expired'));
      }
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access - session expired or invalid
      sessionService.handleSessionInvalid();

      // Don't redirect here - let the session service callbacks handle it
      // This allows for more controlled handling through the AuthContext
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login-json', { email, password }),
  register: (userData: any) =>
    api.post('/auth/register', userData),
  getCurrentUser: () =>
    api.get('/auth/me'),
  logout: () =>
    api.post('/auth/logout'),
  // Profile management
  getProfile: () =>
    api.get('/auth/profile'),
  updateProfile: (profileData: any) =>
    api.put('/auth/profile/update', profileData),
};

// Enhanced Fee Management APIs
export const enhancedFeesAPI = {
  getEnhancedStudentsSummary: (params: any) =>
    api.get('/fees/enhanced-students-summary', { params }),

  getEnhancedMonthlyHistory: (studentId: number, sessionYearId: number) =>
    api.get(`/fees/enhanced-monthly-history/${studentId}`, {
      params: { session_year_id: sessionYearId }
    }),

  getPaymentHistory: (studentId: number, sessionYear: string = '2025-26') =>
    api.get(`/fees/payments/history/${studentId}`, {
      params: { session_year: sessionYear }
    }),

  enableMonthlyTracking: (data: any) =>
    api.post('/fees/enable-monthly-tracking', data),

  // Enhanced Monthly Payment System APIs
  getAvailableMonths: (studentId: number, sessionYear: string = '2025-26') =>
    api.get(`/fees/available-months/${studentId}`, {
      params: { session_year: sessionYear }
    }),

  makeEnhancedPayment: (studentId: number, data: any) =>
    api.post(`/fees/pay-monthly-enhanced/${studentId}`, data),

  // Fee Structure API
  getFeeStructure: () =>
    api.get('/fees/structure'),

  // Admin Dashboard Statistics (moved to dashboard endpoints)
  getAdminDashboardStats: (sessionYearId?: number) =>
    api.get('/dashboard/admin-dashboard-stats', {
      params: { session_year_id: sessionYearId || 4 }
    }),

  // Enhanced Admin Dashboard Statistics (moved to dashboard endpoints)
  getAdminDashboardEnhancedStats: (sessionYearId?: number) =>
    api.get('/dashboard/admin-dashboard-enhanced-stats', {
      params: { session_year_id: sessionYearId || 4 }
    }),
};

// Users API - REMOVED: These endpoints are not used anywhere in the frontend
// User management is handled through student/teacher specific endpoints
// If user management is needed in the future, implement through admin interface



// Students API (to be implemented in backend)
export const studentsAPI = {
  getStudents: (params?: URLSearchParams) => api.get(`/students${params ? `?${params.toString()}` : ''}`),
  getStudent: (id: number) => api.get(`/students/${id}`),
  createStudent: (studentData: any) => api.post('/students', studentData),
  updateStudent: (id: number, studentData: any) => api.put(`/students/${id}`, studentData),
  deleteStudent: (id: number) => api.delete(`/students/${id}`),
  // Student profile management
  getMyProfile: () => api.get('/students/my-profile'),
  updateMyProfile: (profileData: any) => api.put('/students/my-profile', profileData),
  // Profile picture management
  uploadMyProfilePicture: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/students/my-profile/upload-picture', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  deleteMyProfilePicture: () => api.delete('/students/my-profile/delete-picture'),
  uploadProfilePictureById: (studentId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/students/${studentId}/upload-picture`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  deleteProfilePictureById: (studentId: number) => api.delete(`/students/${studentId}/delete-picture`),
};

// Teachers API
export const teachersAPI = {
  getTeachers: (params?: string) => api.get(`/teachers${params ? `?${params}` : ''}`),
  getTeacher: (id: number) => api.get(`/teachers/${id}`),
  createTeacher: (teacherData: any) => api.post('/teachers', teacherData),
  updateTeacher: (id: number, teacherData: any) => api.put(`/teachers/${id}`, teacherData),
  deleteTeacher: (id: number) => api.delete(`/teachers/${id}`),
  // Teacher profile management
  getMyProfile: () => api.get('/teachers/my-profile'),
  updateMyProfile: (profileData: any) => api.put('/teachers/my-profile', profileData),
  // Profile picture management
  uploadMyProfilePicture: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/teachers/my-profile/upload-picture', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  deleteMyProfilePicture: () => api.delete('/teachers/my-profile/delete-picture'),
  uploadProfilePictureById: (teacherId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/teachers/${teacherId}/upload-picture`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  deleteProfilePictureById: (teacherId: number) => api.delete(`/teachers/${teacherId}/delete-picture`),
  // Dashboard and statistics
  getDashboardStats: () => api.get('/teachers/dashboard/stats'),
  // Search and filters
  searchTeachers: (searchTerm: string, limit: number = 20) =>
    api.get(`/teachers/search?q=${encodeURIComponent(searchTerm)}&limit=${limit}`),
  getTeachersByDepartment: (department: string) => api.get(`/teachers/department/${encodeURIComponent(department)}`),
  getTeachersBySubject: (subject: string) => api.get(`/teachers/subject/${encodeURIComponent(subject)}`),
  // NOTE: Teacher options moved to service-specific configuration
  // Use configurationAPI.getTeacherManagementConfiguration() instead
  // Provides departments, positions, qualifications, employment_statuses with better performance
  // Public faculty endpoint (no authentication required)
  getPublicFaculty: () => publicApi.get('/public/faculty'),
};



// Leave Management API
export const leaveAPI = {
  // Get leave requests with filters and pagination
  getLeaves: (params?: URLSearchParams) =>
    api.get('/leaves', { params }).then(response => response.data),

  // Get single leave request with details
  getLeave: (id: number) =>
    api.get(`/leaves/${id}`).then(response => response.data),

  // Create new leave request
  createLeave: (leaveData: any) =>
    api.post('/leaves', leaveData).then(response => response.data),

  // Create new leave request with friendly identifiers
  createLeaveFriendly: (leaveData: any) =>
    api.post('/leaves/friendly', leaveData).then(response => response.data),

  // Update leave request
  updateLeave: (id: number, leaveData: any) =>
    api.put(`/leaves/${id}`, leaveData).then(response => response.data),

  // Delete leave request
  deleteLeave: (id: number) =>
    api.delete(`/leaves/${id}`).then(response => response.data),

  // Approve/reject leave request
  approveLeave: (id: number, approvalData: { leave_status_id: number, review_comments?: string }) =>
    api.patch(`/leaves/${id}/approve`, approvalData).then(response => response.data),

  // Get pending leave requests
  getPendingLeaves: () =>
    api.get('/leaves/pending').then(response => response.data),

  // Get leave requests by applicant
  getLeavesByApplicant: (applicantType: string, applicantId: number, limit: number = 50) =>
    api.get(`/leaves/applicant/${applicantType}/${applicantId}`, { params: { limit } }).then(response => response.data),

  // Get leave statistics
  getLeaveStatistics: (year?: number) =>
    api.get('/leaves/statistics', { params: year ? { year } : {} }).then(response => response.data),

  // Get leave balance
  getLeaveBalance: (applicantType: string, applicantId: number) =>
    api.get(`/leaves/balance/${applicantType}/${applicantId}`).then(response => response.data),

  // Get leave policies
  getLeavePolicies: (applicantType?: string) =>
    api.get('/leaves/policies', { params: applicantType ? { applicant_type: applicantType } : {} }).then(response => response.data),

  // Get leave summary report
  getLeaveSummaryReport: (year?: number) =>
    api.get('/leaves/reports/summary', { params: year ? { year } : {} }).then(response => response.data),

  // Class teacher methods - for managing student leaves
  getClassStudentLeaves: (params?: {
    leave_status_id?: number,
    leave_type_id?: number,
    page?: number,
    per_page?: number
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.leave_status_id) searchParams.append('leave_status_id', params.leave_status_id.toString());
    if (params?.leave_type_id) searchParams.append('leave_type_id', params.leave_type_id.toString());
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.per_page) searchParams.append('per_page', params.per_page.toString());

    return api.get('/leaves/class-students', { params: searchParams }).then(response => response.data);
  },

  // Teacher-specific convenience methods
  getMyLeaveRequests: async () => {
    try {
      // First get teacher profile to get teacher ID
      const profileResponse = await teachersAPI.getMyProfile();
      const teacherId = profileResponse.data.id;

      // Then get leave requests for this teacher
      return await leaveAPI.getLeavesByApplicant('teacher', teacherId);
    } catch (error) {
      throw error;
    }
  },

  createMyLeaveRequest: async (leaveData: any) => {
    try {
      // Get teacher profile to get teacher ID
      const profileResponse = await teachersAPI.getMyProfile();
      const teacherId = profileResponse.data.id;

      // Create leave request with teacher ID
      const requestData = {
        ...leaveData,
        applicant_id: teacherId,
        applicant_type: 'teacher'
      };

      return await leaveAPI.createLeave(requestData);
    } catch (error) {
      throw error;
    }
  },

};

// Student-specific leave API methods
export const studentLeaveAPI = {
  getMyLeaveRequests: async () => {
    try {
      // First get student profile to get student ID
      const profileResponse = await studentsAPI.getMyProfile();
      const studentId = profileResponse.data.id;

      // Then get leave requests for this student
      return await leaveAPI.getLeavesByApplicant('student', studentId);
    } catch (error) {
      throw error;
    }
  },

  createMyLeaveRequest: async (leaveData: any) => {
    try {
      // Get student profile to get student ID
      const profileResponse = await studentsAPI.getMyProfile();
      const studentId = profileResponse.data.id;

      // Create leave request with student ID
      const requestData = {
        ...leaveData,
        applicant_id: studentId,
        applicant_type: 'student'
      };

      return await leaveAPI.createLeave(requestData);
    } catch (error) {
      throw error;
    }
  },
};

// Student-specific fee API methods
export const studentFeeAPI = {
  /**
   * Get fee information for the currently logged-in student
   * Returns comprehensive fee statistics and monthly history
   */
  getMyFees: async (sessionYearId: number = 4) => {
    try {
      const response = await api.get('/fees/my-fees', {
        params: { session_year_id: sessionYearId }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get detailed monthly fee history for the currently logged-in student
   * Returns month-wise payment status and history
   */
  getMyMonthlyHistory: async (sessionYearId: number = 4) => {
    try {
      const response = await api.get('/fees/my-monthly-history', {
        params: { session_year_id: sessionYearId }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

// Expense Management API
export const expenseAPI = {
  // Get expenses with filters and pagination
  getExpenses: (params?: URLSearchParams) =>
    api.get('/expenses', { params }).then(response => response.data),

  // Get single expense with details
  getExpense: (id: number) =>
    api.get(`/expenses/${id}`).then(response => response.data),

  // Create new expense
  createExpense: (expenseData: any) =>
    api.post('/expenses', expenseData).then(response => response.data),

  // Update expense
  updateExpense: (id: number, expenseData: any) =>
    api.put(`/expenses/${id}`, expenseData).then(response => response.data),

  // Delete expense
  deleteExpense: (id: number) =>
    api.delete(`/expenses/${id}`).then(response => response.data),

  // Approve/reject expense
  approveExpense: (id: number, approvalData: { expense_status_id: number, approval_comments?: string }) =>
    api.patch(`/expenses/${id}/approve`, approvalData).then(response => response.data),

  // Get pending expenses
  getPendingExpenses: () =>
    api.get('/expenses/pending').then(response => response.data),

  // Get user's expenses
  getMyExpenses: (limit: number = 50) =>
    api.get('/expenses/my-expenses', { params: { limit } }).then(response => response.data),

  // Get expense dashboard data
  getDashboard: () =>
    api.get('/expenses/dashboard').then(response => response.data),

  // Get monthly report
  getMonthlyReport: (year: number) =>
    api.get('/expenses/reports/monthly', { params: { year } }).then(response => response.data),

  // Get yearly report
  getYearlyReport: (year?: number) =>
    api.get('/expenses/reports/yearly', { params: year ? { year } : {} }).then(response => response.data),
};

// Vendor Management API
export const vendorAPI = {
  // Get all vendors
  getVendors: () =>
    api.get('/expenses/vendors').then(response => response.data),

  // Get single vendor
  getVendor: (id: number) =>
    api.get(`/expenses/vendors/${id}`).then(response => response.data),

  // Create vendor
  createVendor: (vendorData: any) =>
    api.post('/expenses/vendors', vendorData).then(response => response.data),

  // Update vendor
  updateVendor: (id: number, vendorData: any) =>
    api.put(`/expenses/vendors/${id}`, vendorData).then(response => response.data),

  // Delete vendor
  deleteVendor: (id: number) =>
    api.delete(`/expenses/vendors/${id}`).then(response => response.data),

  // Get active vendors
  getActiveVendors: () =>
    api.get('/expenses/vendors/active').then(response => response.data),
};

// Configuration API (DEPRECATED - Use service-specific endpoints instead)
// These endpoints are deprecated and will be removed in a future version
// Use configurationAPI from configurationService.ts for service-specific endpoints
export const configurationAPI = {
  // DEPRECATED: Use service-specific endpoints instead
  getConfiguration: () => {
    return Promise.reject(new Error('This endpoint has been deprecated. Use service-specific configuration endpoints.'));
  },
  refreshConfiguration: () => api.post('/configuration/refresh'),
};

// Events API - REMOVED: No backend implementation exists for these endpoints
// If events functionality is needed, implement backend endpoints first
// Current frontend defines these methods but backend has no /events routes

// Gallery Management API
export const galleryAPI = {
  // Get all gallery images (with optional filters)
  getImages: (params?: URLSearchParams) =>
    api.get('/gallery/images', { params }).then(response => response.data),

  // Get single image
  getImage: (id: number) =>
    api.get(`/gallery/images/${id}`).then(response => response.data),

  // Upload image to Cloudinary
  uploadImage: (formData: FormData) =>
    api.post('/gallery/images/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for file upload
    }).then(response => response.data),

  // Update image metadata
  updateImage: (id: number, imageData: any) =>
    api.put(`/gallery/images/${id}`, imageData).then(response => response.data),

  // Delete image (also deletes from Cloudinary)
  deleteImage: (id: number) =>
    api.delete(`/gallery/images/${id}`).then(response => response.data),

  // Toggle home page visibility
  toggleHomePage: (id: number, isVisible: boolean) =>
    api.patch(`/gallery/images/${id}/toggle-home-page`, { is_visible_on_home_page: isVisible }).then(response => response.data),

  // Get gallery statistics
  getStatistics: () =>
    api.get('/gallery/statistics').then(response => response.data),

  // Get home page featured images
  getHomePageImages: () =>
    publicApi.get('/gallery/images/home-page').then(response => response.data),

  // Get gallery categories (public endpoint)
  getCategories: () =>
    publicApi.get('/gallery/categories').then(response => response.data),

  // Create gallery category (admin only)
  createCategory: (categoryData: any) =>
    api.post('/gallery/categories', categoryData).then(response => response.data),
};

export default api;
