import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.log('API Error intercepted:', error.response?.status, error.response?.data);
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.log('401 Unauthorized - removing token and redirecting');
      localStorage.removeItem('authToken');
      window.location.href = '/admin/login';
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
};

// Users API
export const usersAPI = {
  getUsers: () => api.get('/users'),
  getUser: (id: number) => api.get(`/users/${id}`),
  createUser: (userData: any) => api.post('/users', userData),
  updateUser: (id: number, userData: any) => api.put(`/users/${id}`, userData),
  deleteUser: (id: number) => api.delete(`/users/${id}`),
};



// Students API (to be implemented in backend)
export const studentsAPI = {
  getStudents: () => api.get('/students'),
  getStudent: (id: number) => api.get(`/students/${id}`),
  createStudent: (studentData: any) => api.post('/students', studentData),
  updateStudent: (id: number, studentData: any) => api.put(`/students/${id}`, studentData),
  deleteStudent: (id: number) => api.delete(`/students/${id}`),
  // Student profile management
  getMyProfile: () => api.get('/students/my-profile'),
  updateMyProfile: (profileData: any) => api.put('/students/my-profile', profileData),
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
  // Dashboard and statistics
  getDashboardStats: () => api.get('/teachers/dashboard/stats'),
  // Search and filters
  searchTeachers: (searchTerm: string, limit: number = 20) =>
    api.get(`/teachers/search?q=${encodeURIComponent(searchTerm)}&limit=${limit}`),
  getTeachersByDepartment: (department: string) => api.get(`/teachers/department/${encodeURIComponent(department)}`),
  getTeachersBySubject: (subject: string) => api.get(`/teachers/subject/${encodeURIComponent(subject)}`),
  // Options for dropdowns
  getDepartments: () => api.get('/teachers/options/departments'),
  getPositions: () => api.get('/teachers/options/positions'),
  getQualifications: () => api.get('/teachers/options/qualifications'),
  getEmploymentStatuses: () => api.get('/teachers/options/employment-status'),
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

  // Teacher-specific convenience methods
  getMyLeaveRequests: async () => {
    try {
      // First get teacher profile to get teacher ID
      const profileResponse = await teachersAPI.getMyProfile();
      const teacherId = profileResponse.data.id;

      // Then get leave requests for this teacher
      return await leaveAPI.getLeavesByApplicant('teacher', teacherId);
    } catch (error) {
      console.error('Error getting teacher leave requests:', error);
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
      console.error('Error creating teacher leave request:', error);
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

  // Get expense statistics
  getStatistics: () =>
    api.get('/expenses/statistics').then(response => response.data),

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
    console.warn('⚠️ DEPRECATED: getConfiguration() is deprecated. Use service-specific configuration endpoints instead.');
    return Promise.reject(new Error('This endpoint has been deprecated. Use service-specific configuration endpoints.'));
  },
  refreshConfiguration: () => api.post('/configuration/refresh'),
};

// Events API
export const eventsAPI = {
  getEvents: () => api.get('/events'),
  getEvent: (id: number) => api.get(`/events/${id}`),
  createEvent: (eventData: any) => api.post('/events', eventData),
  updateEvent: (id: number, eventData: any) => api.put(`/events/${id}`, eventData),
  deleteEvent: (id: number) => api.delete(`/events/${id}`),
};

export default api;
