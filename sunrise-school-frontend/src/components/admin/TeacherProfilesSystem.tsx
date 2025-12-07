import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Avatar,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
  Snackbar,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Pagination,
  Grid
} from '@mui/material';
import { DEFAULT_PAGE_SIZE, PAGINATION_UI_CONFIG } from '../../config/pagination';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  VpnKey as KeyIcon,
} from '@mui/icons-material';

import { useAuth } from '../../contexts/AuthContext';
import { useServiceConfiguration, useConfiguration } from '../../contexts/ConfigurationContext';
import { teachersAPI } from '../../services/api';
import { useErrorDialog } from '../../hooks/useErrorDialog';
import ErrorDialog from '../common/ErrorDialog';
import CollapsibleFilterSection from '../common/CollapsibleFilterSection';
import ResetPasswordDialog from './ResetPasswordDialog';

// Teacher interface matching the backend structure
interface Teacher {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  father_name?: string;
  date_of_birth: string;
  gender_id: number;
  phone: string;
  email: string;
  aadhar_no?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  position_id?: number;
  position_name?: string;
  position_description?: string;
  department_id?: number;
  department_name?: string;
  department_description?: string;
  // Legacy fields for backward compatibility
  position?: string;
  department?: string;
  subjects?: string;
  qualification_id?: number;
  employment_status_id: number;
  experience_years: number;
  joining_date: string;
  class_teacher_of_id?: number;
  classes_assigned?: string;
  salary?: number;
  is_active: boolean;
  is_deleted?: boolean;
  // Metadata fields
  gender_name?: string;
  gender_description?: string;
  qualification_name?: string;
  qualification_description?: string;
  employment_status_name?: string;
  employment_status_description?: string;
  class_teacher_of_name?: string;
  class_teacher_of_description?: string;
  user_id?: number;
  // Profile Picture
  profile_picture_url?: string;
  profile_picture_cloudinary_id?: string;
}

// Form data interface for teacher forms
interface TeacherFormData {
  employee_id: string;
  first_name: string;
  last_name: string;
  father_name: string;
  date_of_birth: string;
  gender_id: number | string;
  phone: string;
  email: string;
  aadhar_no: string;
  address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relation: string;
  position_id: number | string;
  department_id: number | string;
  subjects: string;
  qualification_id: number | string;
  employment_status_id: number | string;
  experience_years: string;
  joining_date: string;
  class_teacher_of_id: number | string;
  classes_assigned: string;
  salary: string;
  is_active: boolean;
}

const TeacherProfilesSystem: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const {
    isLoaded: configLoaded,
    isLoading: configLoading,
    error: configError
  } = useServiceConfiguration('teacher-management');

  const { getServiceConfiguration } = useConfiguration();
  const configuration = getServiceConfiguration('teacher-management');

  // Error dialog hook
  const errorDialog = useErrorDialog();

  // State management
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  // Pagination state
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTeachers, setTotalTeachers] = useState(0);
  const perPage = DEFAULT_PAGE_SIZE;

  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('all');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all');

  // Dialog states
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogLoading, setDialogLoading] = useState(false);

  // View/Edit dialog state
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedTeacher, setSelectedTeacher] = useState<Teacher | null>(null);
  const [editFormData, setEditFormData] = useState<Record<string, any>>({});

  // Password reset state
  const [resetPasswordDialogOpen, setResetPasswordDialogOpen] = useState(false);
  const [selectedUserForReset, setSelectedUserForReset] = useState<any>(null);

  // Form state for new teacher
  const [formData, setFormData] = useState<TeacherFormData>({
    employee_id: '',
    first_name: '',
    last_name: '',
    father_name: '',
    date_of_birth: '',
    gender_id: '',
    phone: '',
    email: '',
    aadhar_no: '',
    address: '',
    city: '',
    state: 'Uttar Pradesh',
    postal_code: '',
    country: 'India',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    emergency_contact_relation: '',
    position_id: '',
    department_id: '',
    subjects: '',
    qualification_id: '',
    employment_status_id: '',
    experience_years: '',
    joining_date: '',
    class_teacher_of_id: '',
    classes_assigned: '',
    salary: '',
    is_active: true
  });

  // Form validation errors
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Load teachers
  const loadTeachers = useCallback(async () => {
    if (!configLoaded || !isAuthenticated) return;

    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('per_page', perPage.toString());

      if (searchTerm) params.append('search', searchTerm);
      if (filterDepartment !== 'all') params.append('department_filter', filterDepartment);

      // Add is_active filter based on status filter
      if (filterStatus === 'active') {
        params.append('is_active', 'true');
      } else if (filterStatus === 'inactive') {
        params.append('is_active', 'false');
      }
      // When 'all', don't add is_active filter to get both active and inactive

      const response = await teachersAPI.getTeachers(params.toString());
      setTeachers(response.data.teachers || []);
      setTotalPages(response.data.total_pages || 1);
      setTotalTeachers(response.data.total || 0);
    } catch (err: any) {
      console.error('Error loading teachers:', err);
      errorDialog.handleApiError(err, 'data_fetch');
    } finally {
      setLoading(false);
    }
  }, [configLoaded, isAuthenticated, searchTerm, filterDepartment, filterStatus, page, perPage]);

  // Load teachers when dependencies change
  useEffect(() => {
    if (!configLoading && configLoaded && isAuthenticated) {
      loadTeachers();
    }
  }, [configLoading, configLoaded, isAuthenticated, loadTeachers]);

  // Handle filter changes - reset to page 1
  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    setPage(1);
  };

  const handleDepartmentFilterChange = (value: string) => {
    setFilterDepartment(value);
    setPage(1);
  };

  const handleStatusFilterChange = (value: string) => {
    setFilterStatus(value as 'all' | 'active' | 'inactive');
    setPage(1);
  };

  // Dialog handlers
  const handleOpenDialog = async () => {
    // Fetch next employee ID when opening create dialog
    try {
      const response = await teachersAPI.getNextEmployeeId();
      const nextEmployeeId = response.data?.next_employee_id || '';

      setFormData({
        employee_id: nextEmployeeId,
        first_name: '',
        last_name: '',
        father_name: '',
        date_of_birth: '',
        gender_id: '',
        phone: '',
        email: '',
        aadhar_no: '',
        address: '',
        city: '',
        state: '',
        postal_code: '',
        country: 'India',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        emergency_contact_relation: '',
        position_id: '',
        department_id: '',
        subjects: '',
        qualification_id: '',
        employment_status_id: '',
        experience_years: '',
        joining_date: '',
        class_teacher_of_id: '',
        classes_assigned: '',
        salary: '',
        is_active: true
      });
    } catch (error) {
      console.error('Error fetching next employee ID:', error);
      // If error, just use empty string
      setFormData({
        employee_id: '',
        first_name: '',
        last_name: '',
        father_name: '',
        date_of_birth: '',
        gender_id: '',
        phone: '',
        email: '',
        aadhar_no: '',
        address: '',
        city: '',
        state: '',
        postal_code: '',
        country: 'India',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        emergency_contact_relation: '',
        position_id: '',
        department_id: '',
        subjects: '',
        qualification_id: '',
        employment_status_id: '',
        experience_years: '',
        joining_date: '',
        class_teacher_of_id: '',
        classes_assigned: '',
        salary: '',
        is_active: true
      });
    }

    setOpenDialog(true);
    setFormErrors({});
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({
      employee_id: '',
      first_name: '',
      last_name: '',
      father_name: '',
      date_of_birth: '',
      gender_id: '',
      phone: '',
      email: '',
      aadhar_no: '',
      address: '',
      city: '',
      state: '',
      postal_code: '',
      country: 'India',
      emergency_contact_name: '',
      emergency_contact_phone: '',
      emergency_contact_relation: '',
      position_id: '',
      department_id: '',
      subjects: '',
      qualification_id: '',
      employment_status_id: '',
      experience_years: '',
      joining_date: '',
      class_teacher_of_id: '',
      classes_assigned: '',
      salary: '',
      is_active: true
    });
    setFormErrors({});
  };

  // Form handlers
  const handleFormChange = (field: string, value: any) => {
    setFormData((prev: TeacherFormData) => ({
      ...prev,
      [field]: value
    }));
    // Clear error when user starts typing
    if (formErrors[field]) {
      setFormErrors((prev: Record<string, string>) => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  // Form validation
  const validateForm = () => {
    const errors: Record<string, string> = {};

    // Required fields
    if (!formData.employee_id.trim()) errors.employee_id = 'Employee ID is required';
    if (!formData.first_name.trim()) errors.first_name = 'First name is required';
    if (!formData.last_name.trim()) errors.last_name = 'Last name is required';
    if (!formData.date_of_birth) errors.date_of_birth = 'Date of birth is required';
    if (!formData.gender_id) errors.gender_id = 'Gender is required';
    if (!formData.phone.trim()) errors.phone = 'Phone number is required';
    // Email is no longer required - will be auto-generated
    if (!formData.position_id) errors.position_id = 'Position is required';
    if (!formData.employment_status_id) errors.employment_status_id = 'Employment status is required';
    if (!formData.joining_date) errors.joining_date = 'Joining date is required';

    // Email validation (only if provided)
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Phone validation (basic)
    if (formData.phone && !/^\d{10}$/.test(formData.phone.replace(/\D/g, ''))) {
      errors.phone = 'Please enter a valid 10-digit phone number';
    }

    // Experience years validation
    if (formData.experience_years && (isNaN(Number(formData.experience_years)) || Number(formData.experience_years) < 0)) {
      errors.experience_years = 'Experience years must be a valid number';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Helper function to get user-friendly error messages
  const getErrorMessage = (error: any): string => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail;
    const message = error.response?.data?.message;

    // Handle specific HTTP status codes
    switch (status) {
      case 400:
        // Handle specific 400 error cases
        if (detail?.includes('employee ID already exists') || detail?.includes('employee_id')) {
          return 'A teacher with this employee ID already exists. Please use a different employee ID.';
        }
        if (detail?.includes('email already exists') || detail?.includes('email')) {
          return 'A teacher with this email address already exists. Please use a different email.';
        }
        return detail || message || 'Invalid data provided. Please check your input and try again.';

      case 422:
        return 'Please check the form data and ensure all required fields are filled correctly.';

      case 409:
        return 'A teacher with this information already exists. Please check for duplicates.';

      case 500:
        return 'Unable to create teacher due to a server error. Please try again later.';

      case 503:
        return 'Service temporarily unavailable. Please try again in a few moments.';

      default:
        // Fallback to detail or message from API
        if (detail) return detail;
        if (message) return message;

        // Network or other errors
        if (error.code === 'NETWORK_ERROR' || !error.response) {
          return 'Network error. Please check your connection and try again.';
        }

        return 'An unexpected error occurred. Please try again.';
    }
  };

  // Save teacher with comprehensive error handling
  const handleSaveTeacher = async () => {
    if (!validateForm()) {
      setSnackbar({
        open: true,
        message: 'Please fix the form errors before submitting',
        severity: 'error'
      });
      return;
    }

    setDialogLoading(true);
    try {
      // Prepare data for API
      const teacherData = {
        ...formData,
        gender_id: Number(formData.gender_id),
        position_id: formData.position_id ? Number(formData.position_id) : null,
        department_id: formData.department_id ? Number(formData.department_id) : null,
        qualification_id: formData.qualification_id ? Number(formData.qualification_id) : null,
        employment_status_id: Number(formData.employment_status_id),
        experience_years: Number(formData.experience_years) || 0,
        class_teacher_of_id: formData.class_teacher_of_id ? Number(formData.class_teacher_of_id) : null,
        salary: formData.salary ? Number(formData.salary) : null
      };

      const response = await teachersAPI.createTeacher(teacherData);

      // Extract generated email from response for success message
      const generatedEmail = response.data?.email || 'Email auto-generated';

      setSnackbar({
        open: true,
        message: `Teacher created successfully! Login email: ${generatedEmail}`,
        severity: 'success'
      });

      handleCloseDialog();
      loadTeachers(); // Refresh the list
    } catch (err: any) {
      console.error('Error creating teacher:', err);
      errorDialog.handleApiError(err, 'teacher_creation');
      // Don't close dialog on error - allow user to fix and retry
    } finally {
      setDialogLoading(false);
    }
  };

  // Handle reset password
  const handleResetPassword = (teacher: Teacher) => {
    // Check if teacher has a user account
    if (!teacher.user_id) {
      setSnackbar({
        open: true,
        message: 'This teacher does not have a user account. Cannot reset password.',
        severity: 'error'
      });
      return;
    }

    // Prepare user data for reset dialog
    const userData = {
      id: teacher.user_id,
      email: teacher.email,
      first_name: teacher.first_name,
      last_name: teacher.last_name,
      user_type: 'TEACHER'
    };
    setSelectedUserForReset(userData);
    setResetPasswordDialogOpen(true);
  };

  const handlePasswordResetSuccess = () => {
    setSnackbar({
      open: true,
      message: 'Password reset successfully',
      severity: 'success'
    });
  };

  // Handle delete teacher (soft delete)
  const handleDeleteTeacher = async (teacher: Teacher) => {
    if (window.confirm(`Are you sure you want to delete ${teacher.first_name} ${teacher.last_name}? This action cannot be undone.`)) {
      try {
        setLoading(true);
        await teachersAPI.deleteTeacher(teacher.id);
        setSnackbar({
          open: true,
          message: `Teacher ${teacher.first_name} ${teacher.last_name} deleted successfully`,
          severity: 'success'
        });
        loadTeachers();
      } catch (err: any) {
        console.error('Error deleting teacher:', err);
        errorDialog.handleApiError(err, 'data_delete');
      } finally {
        setLoading(false);
      }
    }
  };

  // View teacher handler
  const handleViewTeacher = async (teacher: Teacher) => {
    try {
      setDialogLoading(true);
      const response = await teachersAPI.getTeacher(teacher.id);
      setSelectedTeacher(response.data);
      setViewDialogOpen(true);
    } catch (err: any) {
      console.error('Error loading teacher details:', err);
      errorDialog.handleApiError(err, 'data_fetch');
    } finally {
      setDialogLoading(false);
    }
  };

  // Edit teacher handler
  const handleEditTeacher = async (teacher: Teacher) => {
    try {
      setDialogLoading(true);
      const response = await teachersAPI.getTeacher(teacher.id);
      const teacherData = response.data;

      // Prepare form data for editing
      setEditFormData({
        employee_id: teacherData.employee_id || '',
        first_name: teacherData.first_name || '',
        last_name: teacherData.last_name || '',
        father_name: teacherData.father_name || '',
        date_of_birth: teacherData.date_of_birth || '',
        gender_id: teacherData.gender_id || '',
        phone: teacherData.phone || '',
        email: teacherData.email || '',
        aadhar_no: teacherData.aadhar_no || '',
        address: teacherData.address || '',
        city: teacherData.city || '',
        state: teacherData.state || '',
        postal_code: teacherData.postal_code || '',
        country: teacherData.country || 'India',
        emergency_contact_name: teacherData.emergency_contact_name || '',
        emergency_contact_phone: teacherData.emergency_contact_phone || '',
        emergency_contact_relation: teacherData.emergency_contact_relation || '',
        position_id: teacherData.position_id || '',
        department_id: teacherData.department_id || '',
        subjects: teacherData.subjects || '',
        qualification_id: teacherData.qualification_id || '',
        employment_status_id: teacherData.employment_status_id || '',
        experience_years: teacherData.experience_years || '',
        joining_date: teacherData.joining_date || '',
        class_teacher_of_id: teacherData.class_teacher_of_id || '',
        classes_assigned: teacherData.classes_assigned || '',
        salary: teacherData.salary || '',
        is_active: teacherData.is_active !== undefined ? teacherData.is_active : true
      });

      setSelectedTeacher(teacherData);
      setEditDialogOpen(true);
    } catch (err: any) {
      console.error('Error loading teacher details:', err);

      // Use the same error message helper for consistency
      const errorMessage = getErrorMessage(err);

      setSnackbar({
        open: true,
        message: `Failed to load teacher details: ${errorMessage}`,
        severity: 'error'
      });
    } finally {
      setDialogLoading(false);
    }
  };

  // Edit form handlers
  const handleEditFormChange = (field: string, value: any) => {
    setEditFormData((prev: Record<string, any>) => ({
      ...prev,
      [field]: value
    }));
    // Clear error when user starts typing
    if (formErrors[field]) {
      setFormErrors((prev: Record<string, string>) => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleSaveEditTeacher = async () => {
    if (!selectedTeacher) return;

    // Validate form
    if (!validateEditForm()) {
      setSnackbar({
        open: true,
        message: 'Please fix the form errors before submitting',
        severity: 'error'
      });
      return;
    }

    setDialogLoading(true);
    try {
      // Prepare data for API
      const teacherData = {
        ...editFormData,
        gender_id: Number(editFormData.gender_id),
        position_id: editFormData.position_id ? Number(editFormData.position_id) : null,
        department_id: editFormData.department_id ? Number(editFormData.department_id) : null,
        qualification_id: editFormData.qualification_id ? Number(editFormData.qualification_id) : null,
        employment_status_id: Number(editFormData.employment_status_id),
        experience_years: Number(editFormData.experience_years) || 0,
        class_teacher_of_id: editFormData.class_teacher_of_id ? Number(editFormData.class_teacher_of_id) : null,
        salary: editFormData.salary ? Number(editFormData.salary) : null
      };

      await teachersAPI.updateTeacher(selectedTeacher.id, teacherData);

      setSnackbar({
        open: true,
        message: 'Teacher updated successfully!',
        severity: 'success'
      });

      handleCloseEditDialog();
      loadTeachers(); // Refresh the list
    } catch (err: any) {
      console.error('Error updating teacher:', err);

      // Use the same error message helper for consistency
      const errorMessage = getErrorMessage(err);

      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });

      // Don't close dialog on error - allow user to fix and retry
    } finally {
      setDialogLoading(false);
    }
  };

  const validateEditForm = () => {
    const errors: Record<string, string> = {};

    // Required fields
    if (!editFormData.employee_id?.trim()) errors.employee_id = 'Employee ID is required';
    if (!editFormData.first_name?.trim()) errors.first_name = 'First name is required';
    if (!editFormData.last_name?.trim()) errors.last_name = 'Last name is required';
    if (!editFormData.date_of_birth) errors.date_of_birth = 'Date of birth is required';
    if (!editFormData.gender_id) errors.gender_id = 'Gender is required';
    if (!editFormData.phone?.trim()) errors.phone = 'Phone number is required';
    // Email is system-generated and read-only, no validation needed
    if (!editFormData.position_id) errors.position_id = 'Position is required';
    if (!editFormData.employment_status_id) errors.employment_status_id = 'Employment status is required';
    if (!editFormData.joining_date) errors.joining_date = 'Joining date is required';

    // Email validation (only if somehow modified)
    if (editFormData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editFormData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Phone validation (basic)
    if (editFormData.phone && !/^\d{10}$/.test(editFormData.phone.replace(/\D/g, ''))) {
      errors.phone = 'Please enter a valid 10-digit phone number';
    }

    // Experience years validation
    if (editFormData.experience_years && (isNaN(Number(editFormData.experience_years)) || Number(editFormData.experience_years) < 0)) {
      errors.experience_years = 'Experience years must be a valid number';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCloseViewDialog = () => {
    setViewDialogOpen(false);
    setSelectedTeacher(null);
  };

  const handleCloseEditDialog = () => {
    setEditDialogOpen(false);
    setSelectedTeacher(null);
    setEditFormData({});
    setFormErrors({});
  };

  // Filter teachers based on current filters and search
  const filteredTeachers = teachers.filter(teacher => {
    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = 
        teacher.first_name.toLowerCase().includes(searchLower) ||
        teacher.last_name.toLowerCase().includes(searchLower) ||
        teacher.employee_id.toLowerCase().includes(searchLower) ||
        teacher.email.toLowerCase().includes(searchLower) ||
        teacher.phone.includes(searchTerm);
      
      if (!matchesSearch) return false;
    }

    // Department filter (comparing by ID)
    if (filterDepartment !== 'all' && teacher.department_id?.toString() !== filterDepartment) {
      return false;
    }

    return true;
  });

  // Loading and error states
  if (configLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Loading teacher management configuration...
        </Typography>
      </Box>
    );
  }

  if (configError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Configuration Error: {configError}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Filters Section */}
      <CollapsibleFilterSection
        title="Filters"
        defaultExpanded={true}
        persistKey="teacher-profiles-filters"
        actionButtons={
          <Button
            variant="contained"
            size="small"
            startIcon={<AddIcon />}
            onClick={handleOpenDialog}
            sx={{
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              padding: { xs: '4px 8px', sm: '6px 12px' },
              whiteSpace: 'nowrap'
            }}
          >
            New Teacher
          </Button>
        }
      >
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField
              fullWidth
              label="Search Teachers"
              variant="outlined"
              value={searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              slotProps={{
                input: {
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }
              }}
              placeholder="Name, Employee ID, Email..."
              size="small"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Department</InputLabel>
              <Select
                value={filterDepartment}
                label="Department"
                onChange={(e) => handleDepartmentFilterChange(e.target.value)}
              >
                <MenuItem value="all">All Departments</MenuItem>
                {configuration?.departments?.map((dept: any) => (
                  <MenuItem key={dept.id} value={dept.id.toString()}>
                    {dept.description}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => handleStatusFilterChange(e.target.value)}
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </CollapsibleFilterSection>

      {/* Teacher Table */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <TableContainer sx={{ maxHeight: { xs: '60vh', sm: '70vh' }, overflow: 'auto', overflowX: 'auto' }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ backgroundColor: 'white', fontSize: { xs: '0.75rem', sm: '0.875rem' }, fontWeight: 600, minWidth: { xs: 140, sm: 180 } }}>Teacher</TableCell>
                <TableCell sx={{ backgroundColor: 'white', fontSize: { xs: '0.75rem', sm: '0.875rem' }, fontWeight: 600, display: { xs: 'none', sm: 'table-cell' } }}>Employee ID</TableCell>
                <TableCell sx={{ backgroundColor: 'white', fontSize: { xs: '0.75rem', sm: '0.875rem' }, fontWeight: 600, display: { xs: 'none', md: 'table-cell' } }}>Department</TableCell>
                <TableCell sx={{ backgroundColor: 'white', fontSize: { xs: '0.75rem', sm: '0.875rem' }, fontWeight: 600, display: { xs: 'none', md: 'table-cell' } }}>Position</TableCell>
                <TableCell sx={{ backgroundColor: 'white', fontSize: { xs: '0.75rem', sm: '0.875rem' }, fontWeight: 600, display: { xs: 'none', md: 'table-cell' } }}>Contact</TableCell>
                <TableCell sx={{ backgroundColor: 'white', fontSize: { xs: '0.75rem', sm: '0.875rem' }, fontWeight: 600 }}>Status</TableCell>
                <TableCell sx={{ backgroundColor: 'white', fontSize: { xs: '0.75rem', sm: '0.875rem' }, fontWeight: 600 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : filteredTeachers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No teachers found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredTeachers.map((teacher) => (
                  <TableRow key={teacher.id}>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                      <Box display="flex" alignItems="center" gap={{ xs: 1, sm: 2 }}>
                        <Avatar
                          src={teacher.profile_picture_url || undefined}
                          sx={{ bgcolor: teacher.is_active ? 'primary.main' : 'grey.500', width: { xs: 32, sm: 40 }, height: { xs: 32, sm: 40 } }}
                        >
                          {!teacher.profile_picture_url && `${teacher.first_name[0]}${teacher.last_name[0]}`}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="bold" sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                            {teacher.first_name} {teacher.last_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}>
                            {teacher.qualification_name || 'Not Specified'}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, display: { xs: 'none', sm: 'table-cell' } }}>{teacher.employee_id}</TableCell>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, display: { xs: 'none', md: 'table-cell' } }}>{teacher.department_description || teacher.department_name || teacher.department || 'Not Assigned'}</TableCell>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, display: { xs: 'none', md: 'table-cell' } }}>{teacher.position_description || teacher.position_name || teacher.position || 'Not Assigned'}</TableCell>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, display: { xs: 'none', md: 'table-cell' } }}>
                      <Box display="flex" flexDirection="column" gap={0.5}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <PhoneIcon sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }} color="action" />
                          <Typography variant="caption" sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}>{teacher.phone}</Typography>
                        </Box>
                        <Box display="flex" alignItems="center" gap={1}>
                          <EmailIcon sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }} color="action" />
                          <Typography variant="caption" sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}>{teacher.email}</Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                      <Chip
                        label={teacher.is_active ? 'Active' : 'Inactive'}
                        color={teacher.is_active ? 'success' : 'default'}
                        size="small"
                        sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}
                      />
                    </TableCell>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                      <Box display="flex" gap={{ xs: 0.25, sm: 0.5 }} flexWrap="wrap">
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => handleViewTeacher(teacher)} sx={{ minWidth: 36, minHeight: 36 }}>
                            <ViewIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit Teacher">
                          <IconButton size="small" onClick={() => handleEditTeacher(teacher)} sx={{ minWidth: 36, minHeight: 36 }}>
                            <EditIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title={!teacher.user_id ? "No user account" : "Reset Password"}>
                          <span>
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleResetPassword(teacher)}
                              disabled={!teacher.user_id}
                              sx={{ minWidth: 36, minHeight: 36 }}
                            >
                              <KeyIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                            </IconButton>
                          </span>
                        </Tooltip>
                        <Tooltip title="Delete Teacher">
                          <IconButton size="small" color="error" onClick={() => handleDeleteTeacher(teacher)} sx={{ minWidth: 36, minHeight: 36 }}>
                            <DeleteIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        {totalPages > 1 && (
          <Box display="flex" justifyContent="center" mt={3}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(_, newPage) => setPage(newPage)}
              color={PAGINATION_UI_CONFIG.color}
              showFirstButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
              showLastButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
            />
          </Box>
        )}
      </Paper>

      {/* Add New Teacher Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        slotProps={{
          paper: {
            sx: { maxHeight: '90vh' }
          }
        }}
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight="bold">
            Add New Teacher
          </Typography>
        </DialogTitle>
        <DialogContent dividers>
          <Box sx={{ pt: 2 }}>
            {/* Personal Information Section */}
            <Typography variant="h6" color="primary" gutterBottom>
              Personal Information
            </Typography>

            <Box display="flex" flexDirection="column" gap={2} mb={3}>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="Employee ID"
                  value={formData.employee_id}
                  onChange={(e) => handleFormChange('employee_id', e.target.value)}
                  error={!!formErrors.employee_id}
                  helperText={formErrors.employee_id || 'Auto-generated (editable)'}
                  size="small"
                  required
                />
                <Box flex={1} /> {/* Spacer */}
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="First Name"
                  value={formData.first_name}
                  onChange={(e) => handleFormChange('first_name', e.target.value)}
                  error={!!formErrors.first_name}
                  helperText={formErrors.first_name}
                  size="small"
                  required
                />
                <TextField
                  fullWidth
                  label="Last Name"
                  value={formData.last_name}
                  onChange={(e) => handleFormChange('last_name', e.target.value)}
                  error={!!formErrors.last_name}
                  helperText={formErrors.last_name}
                  size="small"
                  required
                />
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="Date of Birth"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => handleFormChange('date_of_birth', e.target.value)}
                  error={!!formErrors.date_of_birth}
                  helperText={formErrors.date_of_birth}
                  slotProps={{
                    inputLabel: { shrink: true }
                  }}
                  size="small"
                  required
                />
                <FormControl fullWidth size="small" error={!!formErrors.gender_id} required>
                  <InputLabel>Gender</InputLabel>
                  <Select
                    value={formData.gender_id}
                    label="Gender"
                    onChange={(e) => handleFormChange('gender_id', e.target.value)}
                  >
                    {configuration?.genders?.map((gender: any) => (
                      <MenuItem key={gender.id} value={gender.id}>
                        {gender.description || gender.name}
                      </MenuItem>
                    ))}
                  </Select>
                  {formErrors.gender_id && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                      {formErrors.gender_id}
                    </Typography>
                  )}
                </FormControl>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="Aadhar Number"
                  value={formData.aadhar_no}
                  onChange={(e) => handleFormChange('aadhar_no', e.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Father's Name"
                  value={formData.father_name}
                  onChange={(e) => handleFormChange('father_name', e.target.value)}
                  size="small"
                />
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="Phone Number"
                  value={formData.phone}
                  onChange={(e) => handleFormChange('phone', e.target.value)}
                  error={!!formErrors.phone}
                  helperText={formErrors.phone}
                  size="small"
                  required
                />
                <Box flex={1} /> {/* Spacer */}
              </Box>
            </Box>

            {/* Address Information Section */}
            <Typography variant="h6" color="primary" gutterBottom>
              Address Information
            </Typography>

            <Box display="flex" flexDirection="column" gap={2}>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="Address"
                  value={formData.address}
                  onChange={(e) => handleFormChange('address', e.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="City"
                  value={formData.city}
                  onChange={(e) => handleFormChange('city', e.target.value)}
                  size="small"
                />
              </Box>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="State"
                  value={formData.state || 'Uttar Pradesh'}
                  onChange={(e) => handleFormChange('state', e.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Postal Code"
                  value={formData.postal_code}
                  onChange={(e) => handleFormChange('postal_code', e.target.value)}
                  size="small"
                />
              </Box>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="Country"
                  value={formData.country}
                  onChange={(e) => handleFormChange('country', e.target.value)}
                  size="small"
                />
                <Box flex={1} /> {/* Spacer */}
              </Box>
            </Box>

            {/* Professional Information Section */}
            <Typography variant="h6" color="primary" gutterBottom>
              Professional Information
            </Typography>

            <Box display="flex" flexDirection="column" gap={2}>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <FormControl fullWidth size="small" error={!!formErrors.position_id} required>
                  <InputLabel>Position</InputLabel>
                  <Select
                    value={formData.position_id}
                    label="Position"
                    onChange={(e) => handleFormChange('position_id', e.target.value)}
                  >
                    {configuration?.positions?.map((pos: any) => (
                      <MenuItem key={pos.id} value={pos.id}>
                        {pos.description}
                      </MenuItem>
                    ))}
                  </Select>
                  {formErrors.position_id && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                      {formErrors.position_id}
                    </Typography>
                  )}
                </FormControl>
                <FormControl fullWidth size="small">
                  <InputLabel>Department</InputLabel>
                  <Select
                    value={formData.department_id}
                    label="Department"
                    onChange={(e) => handleFormChange('department_id', e.target.value)}
                  >
                    <MenuItem value="">
                      <em>Not Assigned</em>
                    </MenuItem>
                    {configuration?.departments?.map((dept: any) => (
                      <MenuItem key={dept.id} value={dept.id}>
                        {dept.description}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <FormControl fullWidth size="small" error={!!formErrors.employment_status_id} required>
                  <InputLabel>Employment Status</InputLabel>
                  <Select
                    value={formData.employment_status_id}
                    label="Employment Status"
                    onChange={(e) => handleFormChange('employment_status_id', e.target.value)}
                  >
                    {configuration?.employment_statuses?.map((status: any) => (
                      <MenuItem key={status.id} value={status.id}>
                        {status.description}
                      </MenuItem>
                    ))}
                  </Select>
                  {formErrors.employment_status_id && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                      {formErrors.employment_status_id}
                    </Typography>
                  )}
                </FormControl>
                <FormControl fullWidth size="small">
                  <InputLabel>Qualification</InputLabel>
                  <Select
                    value={formData.qualification_id}
                    label="Qualification"
                    onChange={(e) => handleFormChange('qualification_id', e.target.value)}
                  >
                    <MenuItem value="">
                      <em>Not Specified</em>
                    </MenuItem>
                    {configuration?.qualifications?.map((qual: any) => (
                      <MenuItem key={qual.id} value={qual.id}>
                        {qual.description}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="Experience (Years)"
                  type="number"
                  value={formData.experience_years}
                  onChange={(e) => handleFormChange('experience_years', e.target.value)}
                  error={!!formErrors.experience_years}
                  helperText={formErrors.experience_years}
                  size="small"
                />
                <Box flex={1} /> {/* Spacer to balance the layout */}
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <TextField
                  fullWidth
                  label="Joining Date"
                  type="date"
                  value={formData.joining_date}
                  onChange={(e) => handleFormChange('joining_date', e.target.value)}
                  error={!!formErrors.joining_date}
                  helperText={formErrors.joining_date}
                  slotProps={{
                    inputLabel: { shrink: true }
                  }}
                  size="small"
                  required
                />
                <TextField
                  fullWidth
                  label="Subjects"
                  value={formData.subjects}
                  onChange={(e) => handleFormChange('subjects', e.target.value)}
                  size="small"
                  placeholder="e.g., Mathematics, Physics"
                />
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Class Teacher Of</InputLabel>
                  <Select
                    value={formData.class_teacher_of_id}
                    label="Class Teacher Of"
                    onChange={(e) => handleFormChange('class_teacher_of_id', e.target.value)}
                  >
                    <MenuItem value="">
                      <em>None</em>
                    </MenuItem>
                    {configuration?.classes?.map((cls: any) => (
                      <MenuItem key={cls.id} value={cls.id}>
                        {cls.description}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.is_active ? 'true' : 'false'}
                    label="Status"
                    onChange={(e) => handleFormChange('is_active', e.target.value === 'true')}
                  >
                    <MenuItem value="true">Active</MenuItem>
                    <MenuItem value="false">Inactive</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button
            onClick={handleCloseDialog}
            disabled={dialogLoading}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSaveTeacher}
            disabled={dialogLoading}
            startIcon={dialogLoading ? <CircularProgress size={16} /> : null}
          >
            {dialogLoading ? 'Creating...' : 'Create Teacher'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Teacher Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={handleCloseViewDialog}
        maxWidth="md"
        fullWidth
        slotProps={{
          paper: {
            sx: { maxHeight: '90vh' }
          }
        }}
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight="bold">
            Teacher Details
          </Typography>
        </DialogTitle>
        <DialogContent dividers>
          {selectedTeacher && (
            <Box sx={{ pt: 2 }}>
              {/* Personal Information Section */}
              <Typography variant="h6" color="primary" gutterBottom>
                Personal Information
              </Typography>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Employee ID</Typography>
                  <Typography variant="body1" fontWeight="medium">{selectedTeacher.employee_id}</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Full Name</Typography>
                  <Typography variant="body1" fontWeight="medium">{selectedTeacher.first_name} {selectedTeacher.last_name}</Typography>
                </Box>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Date of Birth</Typography>
                  <Typography variant="body1">{selectedTeacher.date_of_birth || 'Not specified'}</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Gender</Typography>
                  <Typography variant="body1">{selectedTeacher.gender_description || selectedTeacher.gender_name || 'Not specified'}</Typography>
                </Box>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Aadhar Number</Typography>
                  <Typography variant="body1">{selectedTeacher.aadhar_no || 'Not specified'}</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Father's Name</Typography>
                  <Typography variant="body1">{selectedTeacher.father_name || 'Not specified'}</Typography>
                </Box>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Phone</Typography>
                  <Typography variant="body1">{selectedTeacher.phone}</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Email</Typography>
                  <Typography variant="body1">{selectedTeacher.email}</Typography>
                </Box>
              </Box>

              {/* Professional Information Section */}
              <Typography variant="h6" color="primary" gutterBottom sx={{ mt: 3 }}>
                Professional Information
              </Typography>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Position</Typography>
                  <Typography variant="body1" fontWeight="medium">{selectedTeacher.position_description || selectedTeacher.position_name || selectedTeacher.position || 'Not specified'}</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Department</Typography>
                  <Typography variant="body1">{selectedTeacher.department_description || selectedTeacher.department_name || selectedTeacher.department || 'Not specified'}</Typography>
                </Box>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Employment Status</Typography>
                  <Typography variant="body1">{selectedTeacher.employment_status_description || selectedTeacher.employment_status_name || 'Not specified'}</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Qualification</Typography>
                  <Typography variant="body1">{selectedTeacher.qualification_description || selectedTeacher.qualification_name || 'Not specified'}</Typography>
                </Box>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Experience Years</Typography>
                  <Typography variant="body1">{selectedTeacher.experience_years || 0} years</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Joining Date</Typography>
                  <Typography variant="body1">{selectedTeacher.joining_date}</Typography>
                </Box>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Class Teacher Of</Typography>
                  <Typography variant="body1">{selectedTeacher.class_teacher_of_description || selectedTeacher.class_teacher_of_name || 'Not assigned'}</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Subjects</Typography>
                  <Typography variant="body1">{selectedTeacher.subjects || 'Not specified'}</Typography>
                </Box>
              </Box>

              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip
                    label={selectedTeacher.is_active ? 'Active' : 'Inactive'}
                    color={selectedTeacher.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
                <Box flex={1} /> {/* Spacer to balance the layout */}
              </Box>

              {/* Address Information Section */}
              <Typography variant="h6" color="primary" gutterBottom sx={{ mt: 3 }}>
                Address Information
              </Typography>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Address</Typography>
                  <Typography variant="body1">{selectedTeacher.address || 'Not specified'}</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">City</Typography>
                  <Typography variant="body1">{selectedTeacher.city || 'Not specified'}</Typography>
                </Box>
              </Box>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">State</Typography>
                  <Typography variant="body1">{selectedTeacher.state || 'Not specified'}</Typography>
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Postal Code</Typography>
                  <Typography variant="body1">{selectedTeacher.postal_code || 'Not specified'}</Typography>
                </Box>
              </Box>
              <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">Country</Typography>
                  <Typography variant="body1">{selectedTeacher.country || 'Not specified'}</Typography>
                </Box>
                <Box flex={1} /> {/* Spacer to balance the layout */}
              </Box>

              {(selectedTeacher.emergency_contact_name || selectedTeacher.emergency_contact_phone) && (
                <>
                  <Typography variant="h6" color="primary" gutterBottom sx={{ mt: 3 }}>
                    Emergency Contact
                  </Typography>
                  <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
                    <Box flex={1}>
                      <Typography variant="body2" color="text.secondary">Contact Name</Typography>
                      <Typography variant="body1">{selectedTeacher.emergency_contact_name || 'Not specified'}</Typography>
                    </Box>
                    <Box flex={1}>
                      <Typography variant="body2" color="text.secondary">Contact Phone</Typography>
                      <Typography variant="body1">{selectedTeacher.emergency_contact_phone || 'Not specified'}</Typography>
                    </Box>
                  </Box>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleCloseViewDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Teacher Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={handleCloseEditDialog}
        maxWidth="md"
        fullWidth
        slotProps={{
          paper: {
            sx: { maxHeight: '90vh' }
          }
        }}
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight="bold">
            Edit Teacher
          </Typography>
        </DialogTitle>
        <DialogContent dividers>
          <Box sx={{ pt: 2 }}>
            {/* Personal Information Section */}
            <Typography variant="h6" color="primary" gutterBottom>
              Personal Information
            </Typography>
            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <TextField
                fullWidth
                size="small"
                label="Employee ID"
                value={editFormData.employee_id || ''}
                onChange={(e) => handleEditFormChange('employee_id', e.target.value)}
                error={!!formErrors.employee_id}
                helperText={formErrors.employee_id}
                required
              />
              <Box flex={1} /> {/* Spacer */}
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <TextField
                fullWidth
                size="small"
                label="First Name"
                value={editFormData.first_name || ''}
                onChange={(e) => handleEditFormChange('first_name', e.target.value)}
                error={!!formErrors.first_name}
                helperText={formErrors.first_name}
                required
              />
              <TextField
                fullWidth
                size="small"
                label="Last Name"
                value={editFormData.last_name || ''}
                onChange={(e) => handleEditFormChange('last_name', e.target.value)}
                error={!!formErrors.last_name}
                helperText={formErrors.last_name}
                required
              />
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <TextField
                fullWidth
                size="small"
                label="Date of Birth"
                type="date"
                value={editFormData.date_of_birth || ''}
                onChange={(e) => handleEditFormChange('date_of_birth', e.target.value)}
                error={!!formErrors.date_of_birth}
                helperText={formErrors.date_of_birth}
                slotProps={{
                  inputLabel: { shrink: true }
                }}
                required
              />
              <FormControl fullWidth size="small" error={!!formErrors.gender_id} required>
                <InputLabel>Gender</InputLabel>
                <Select
                  value={editFormData.gender_id || ''}
                  label="Gender"
                  onChange={(e) => handleEditFormChange('gender_id', e.target.value)}
                >
                  {configuration?.genders?.map((gender: any) => (
                    <MenuItem key={gender.id} value={gender.id}>
                      {gender.description || gender.name}
                    </MenuItem>
                  ))}
                </Select>
                {formErrors.gender_id && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                    {formErrors.gender_id}
                  </Typography>
                )}
              </FormControl>
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <TextField
                fullWidth
                size="small"
                label="Aadhar Number"
                value={editFormData.aadhar_no || ''}
                onChange={(e) => handleEditFormChange('aadhar_no', e.target.value)}
              />
              <TextField
                fullWidth
                size="small"
                label="Father's Name"
                value={editFormData.father_name || ''}
                onChange={(e) => handleEditFormChange('father_name', e.target.value)}
              />
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
              <TextField
                fullWidth
                size="small"
                label="Phone"
                value={editFormData.phone || ''}
                onChange={(e) => handleEditFormChange('phone', e.target.value)}
                error={!!formErrors.phone}
                helperText={formErrors.phone}
                required
              />
              <TextField
                fullWidth
                size="small"
                label="Email (System Generated)"
                type="email"
                value={editFormData.email || ''}
                disabled={true}
              />
            </Box>

            {/* Address Information Section */}
            <Typography variant="h6" color="primary" gutterBottom>
              Address Information
            </Typography>
            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <TextField
                fullWidth
                size="small"
                label="Address"
                value={editFormData.address || ''}
                onChange={(e) => handleEditFormChange('address', e.target.value)}
              />
              <TextField
                fullWidth
                size="small"
                label="City"
                value={editFormData.city || ''}
                onChange={(e) => handleEditFormChange('city', e.target.value)}
              />
            </Box>
            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <TextField
                fullWidth
                size="small"
                label="State"
                value={editFormData.state || 'Uttar Pradesh'}
                onChange={(e) => handleEditFormChange('state', e.target.value)}
              />
              <TextField
                fullWidth
                size="small"
                label="Postal Code"
                value={editFormData.postal_code || ''}
                onChange={(e) => handleEditFormChange('postal_code', e.target.value)}
              />
            </Box>
            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
              <TextField
                fullWidth
                size="small"
                label="Country"
                value={editFormData.country || 'India'}
                onChange={(e) => handleEditFormChange('country', e.target.value)}
              />
              <Box flex={1} /> {/* Spacer */}
            </Box>

            {/* Professional Information Section */}
            <Typography variant="h6" color="primary" gutterBottom>
              Professional Information
            </Typography>
            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <FormControl fullWidth size="small" error={!!formErrors.position_id} required>
                <InputLabel>Position</InputLabel>
                <Select
                  value={editFormData.position_id || ''}
                  label="Position"
                  onChange={(e) => handleEditFormChange('position_id', e.target.value)}
                >
                  {configuration?.positions?.map((pos: any) => (
                    <MenuItem key={pos.id} value={pos.id}>
                      {pos.description}
                    </MenuItem>
                  ))}
                </Select>
                {formErrors.position_id && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                    {formErrors.position_id}
                  </Typography>
                )}
              </FormControl>
              <FormControl fullWidth size="small">
                <InputLabel>Department</InputLabel>
                <Select
                  value={editFormData.department_id || ''}
                  label="Department"
                  onChange={(e) => handleEditFormChange('department_id', e.target.value)}
                >
                  <MenuItem value="">
                    <em>Not Assigned</em>
                  </MenuItem>
                  {configuration?.departments?.map((dept: any) => (
                    <MenuItem key={dept.id} value={dept.id}>
                      {dept.description}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <FormControl fullWidth size="small" error={!!formErrors.employment_status_id} required>
                <InputLabel>Employment Status</InputLabel>
                <Select
                  value={editFormData.employment_status_id || ''}
                  label="Employment Status"
                  onChange={(e) => handleEditFormChange('employment_status_id', e.target.value)}
                >
                  {configuration?.employment_statuses?.map((status: any) => (
                    <MenuItem key={status.id} value={status.id}>
                      {status.description}
                    </MenuItem>
                  ))}
                </Select>
                {formErrors.employment_status_id && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                    {formErrors.employment_status_id}
                  </Typography>
                )}
              </FormControl>
              <FormControl fullWidth size="small">
                <InputLabel>Qualification</InputLabel>
                <Select
                  value={editFormData.qualification_id || ''}
                  label="Qualification"
                  onChange={(e) => handleEditFormChange('qualification_id', e.target.value)}
                >
                  <MenuItem value="">
                    <em>Not Specified</em>
                  </MenuItem>
                  {configuration?.qualifications?.map((qual: any) => (
                    <MenuItem key={qual.id} value={qual.id}>
                      {qual.description}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <TextField
                fullWidth
                size="small"
                label="Experience Years"
                type="number"
                value={editFormData.experience_years || ''}
                onChange={(e) => handleEditFormChange('experience_years', e.target.value)}
                error={!!formErrors.experience_years}
                helperText={formErrors.experience_years}
                slotProps={{
                  htmlInput: { min: 0 }
                }}
              />
              <Box flex={1} /> {/* Spacer to balance the layout */}
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <TextField
                fullWidth
                size="small"
                label="Joining Date"
                type="date"
                value={editFormData.joining_date || ''}
                onChange={(e) => handleEditFormChange('joining_date', e.target.value)}
                error={!!formErrors.joining_date}
                helperText={formErrors.joining_date}
                slotProps={{
                  inputLabel: { shrink: true }
                }}
                required
              />
              <TextField
                fullWidth
                size="small"
                label="Subjects"
                value={editFormData.subjects || ''}
                onChange={(e) => handleEditFormChange('subjects', e.target.value)}
                placeholder="e.g., Mathematics, Physics"
              />
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Class Teacher Of</InputLabel>
                <Select
                  value={editFormData.class_teacher_of_id || ''}
                  label="Class Teacher Of"
                  onChange={(e) => handleEditFormChange('class_teacher_of_id', e.target.value)}
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {configuration?.classes?.map((cls: any) => (
                    <MenuItem key={cls.id} value={cls.id}>
                      {cls.description}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={editFormData.is_active ? 'true' : 'false'}
                  label="Status"
                  onChange={(e) => handleEditFormChange('is_active', e.target.value === 'true')}
                >
                  <MenuItem value="true">Active</MenuItem>
                  <MenuItem value="false">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button
            onClick={handleCloseEditDialog}
            disabled={dialogLoading}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSaveEditTeacher}
            disabled={dialogLoading}
            startIcon={dialogLoading ? <CircularProgress size={16} /> : null}
          >
            {dialogLoading ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reset Password Dialog */}
      <ResetPasswordDialog
        open={resetPasswordDialogOpen}
        onClose={() => {
          setResetPasswordDialogOpen(false);
          setSelectedUserForReset(null);
        }}
        user={selectedUserForReset}
        onSuccess={handlePasswordResetSuccess}
      />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={snackbar.severity === 'error' ? 8000 : 6000} // Longer duration for errors
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }} // Position in bottom-right
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{
            width: '100%',
            maxWidth: '500px', // Limit width for better readability
            '& .MuiAlert-message': {
              fontSize: '0.875rem',
              lineHeight: 1.4
            }
          }}
          variant="filled" // Use filled variant for better visibility
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Error Dialog */}
      <ErrorDialog {...errorDialog.dialogProps} />
    </Box>
  );
};

export default TeacherProfilesSystem;
