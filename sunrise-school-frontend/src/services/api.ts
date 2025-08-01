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

  enableMonthlyTracking: (data: any) =>
    api.post('/fees/enable-monthly-tracking', data),
};

// Users API
export const usersAPI = {
  getUsers: () => api.get('/users'),
  getUser: (id: number) => api.get(`/users/${id}`),
  createUser: (userData: any) => api.post('/users', userData),
  updateUser: (id: number, userData: any) => api.put(`/users/${id}`, userData),
  deleteUser: (id: number) => api.delete(`/users/${id}`),
};

// Teachers API
export const teachersAPI = {
  getTeachers: () => api.get('/teachers'),
  getTeacher: (id: number) => api.get(`/teachers/${id}`),
  createTeacher: (teacherData: any) => api.post('/teachers', teacherData),
  updateTeacher: (id: number, teacherData: any) => api.put(`/teachers/${id}`, teacherData),
  deleteTeacher: (id: number) => api.delete(`/teachers/${id}`),
};

// Students API (to be implemented in backend)
export const studentsAPI = {
  getStudents: () => api.get('/students'),
  getStudent: (id: number) => api.get(`/students/${id}`),
  createStudent: (studentData: any) => api.post('/students', studentData),
  updateStudent: (id: number, studentData: any) => api.put(`/students/${id}`, studentData),
  deleteStudent: (id: number) => api.delete(`/students/${id}`),
};



// Leave API (to be implemented in backend)
export const leaveAPI = {
  getLeaves: (filters?: any) => api.get('/leaves', { params: filters }),
  createLeave: (leaveData: any) => api.post('/leaves', leaveData),
  updateLeave: (id: number, leaveData: any) => api.put(`/leaves/${id}`, leaveData),
  approveLeave: (id: number) => api.patch(`/leaves/${id}/approve`),
  rejectLeave: (id: number) => api.patch(`/leaves/${id}/reject`),
};

// Expenses API (to be implemented in backend)
export const expensesAPI = {
  getExpenses: (filters?: any) => api.get('/expenses', { params: filters }),
  createExpense: (expenseData: any) => api.post('/expenses', expenseData),
  updateExpense: (id: number, expenseData: any) => api.put(`/expenses/${id}`, expenseData),
  deleteExpense: (id: number) => api.delete(`/expenses/${id}`),
  getExpenseCategories: () => api.get('/expenses/categories'),
};

// Configuration API
export const configurationAPI = {
  getConfiguration: () => api.get('/configuration/'),
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
