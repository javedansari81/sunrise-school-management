import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Chip,
  IconButton,
  Grid,
  FormControl,
  InputLabel,
  Select,
  Tooltip,
  Alert,
  CircularProgress,
  Snackbar,
  Stack,
  Pagination
} from '@mui/material';
import { DEFAULT_PAGE_SIZE, PAGINATION_UI_CONFIG } from '../../config/pagination';
import {
  Visibility as ViewIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Delete as DeleteIcon,
  School,
  Work
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useServiceConfiguration, useConfiguration } from '../../contexts/ConfigurationContext';
import { useAuth } from '../../contexts/AuthContext';
import { leaveAPI } from '../../services/api';
import { ClassDropdown } from '../../components/common/MetadataDropdown';
import CollapsibleFilterSection from '../common/CollapsibleFilterSection';

// Types
interface LeaveRequest {
  id: number;
  applicant_id: number;
  applicant_type: 'student' | 'teacher';
  applicant_name: string;
  applicant_details: string;
  applicant_employee_id?: string;  // Employee ID for teachers
  applicant_roll_number?: number;  // Roll number for students
  applicant_class_id?: number;  // Class ID for students
  leave_type_id: number;
  leave_type_name: string;
  leave_status_id: number;
  leave_status_name: string;
  leave_status_color: string;
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  review_comments?: string;
  reviewer_name?: string;
  created_at: string;
}

const LeaveManagementSystem: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const { isLoading: configLoading, isLoaded: configLoaded, error: configError } = useServiceConfiguration('leave-management');
  const { getServiceConfiguration } = useConfiguration();

  // Get the service configuration
  const configuration = getServiceConfiguration('leave-management');
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState<LeaveRequest | null>(null);
  const [isViewMode, setIsViewMode] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [searchInput, setSearchInput] = useState('');

  // Pagination state
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalLeaves, setTotalLeaves] = useState(0);
  const perPage = DEFAULT_PAGE_SIZE;


  
  // Form state - Updated for user-friendly identifiers
  const [leaveForm, setLeaveForm] = useState({
    // Removed applicant_id - replaced with user-friendly identifiers
    applicant_type: 'student' as 'student' | 'teacher',
    // Student identifiers
    roll_number: '',
    class_id: '',
    // Teacher identifier
    employee_id: '',
    // Common fields
    leave_type_id: '',
    start_date: null as Date | null,
    end_date: null as Date | null,
    reason: '',
    parent_consent: false,
    emergency_contact_name: '',
    emergency_contact_phone: '',
    substitute_teacher_id: '',
    substitute_arranged: false
  });

  // Filters
  const [filters, setFilters] = useState({
    applicant_type: '',
    leave_status_id: '',
    leave_type_id: '',
    applicant_name: '',
    department: ''
  });

  const loadLeaveRequests = useCallback(async () => {
    if (!isAuthenticated) {
      setSnackbar({
        open: true,
        message: 'Please login to access leave management',
        severity: 'error'
      });
      return;
    }

    try {
      setLoading(true);
      const queryParams = new URLSearchParams();

      // Add pagination parameters
      queryParams.append('page', page.toString());
      queryParams.append('per_page', perPage.toString());

      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      console.log('🌐 Loading leave requests with params:', Object.fromEntries(queryParams));
      console.log('🔑 User authenticated:', isAuthenticated);
      console.log('👤 Current user:', user);

      const data = await leaveAPI.getLeaves(queryParams);
      console.log('✅ Leave requests loaded:', data);
      setLeaveRequests(Array.isArray(data.leaves) ? data.leaves : []);
      setTotalPages(data.total_pages || 1);
      setTotalLeaves(data.total || 0);
    } catch (error: any) {
      console.error('Error loading leave requests:', error);
      setLeaveRequests([]); // Ensure we set an empty array on error

      let errorMessage = 'Error loading leave requests';

      if (error.code === 'ERR_NETWORK') {
        errorMessage = 'Network connection error. Please check your internet connection and try again.';
      } else if (error.response?.status === 401 || error.response?.status === 403) {
        errorMessage = 'Authentication required. Please log in again.';
        // Redirect to login if not authenticated
        localStorage.removeItem('authToken');
        window.location.href = '/admin/login';
        return;
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error. Please try again later or contact support.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }

      setSnackbar({ open: true, message: errorMessage, severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, [filters, isAuthenticated, user, page, perPage]);

  // Load leave requests
  // Fixed: Removed 'filters', 'loadLeaveRequests' from dependencies
  // to prevent infinite re-render loop. These functions are stable via useCallback.
  useEffect(() => {
    console.log('🔧 LeaveManagementSystem useEffect triggered:', {
      configLoading,
      configLoaded,
      configError,
      isAuthenticated,
      timestamp: new Date().toISOString()
    });

    if (!configLoading && configLoaded && isAuthenticated) {
      console.log('🚀 Triggering data load for leave management');
      loadLeaveRequests();
    } else if (configError) {
      console.error('❌ Configuration error in leave management:', configError);
      setSnackbar({
        open: true,
        message: `Configuration error: ${configError}`,
        severity: 'error'
      });
    }
  }, [configLoading, configLoaded, configError, isAuthenticated]);

  // Separate useEffect to reload data when filters or page change
  // This ensures data is refreshed when user interacts with filters/pagination
  useEffect(() => {
    if (configLoaded && isAuthenticated) {
      console.log('🔄 Reloading leave requests due to filter/page change');
      loadLeaveRequests();
    }
  }, [filters, page, configLoaded, isAuthenticated, loadLeaveRequests]);

  // Debounced search effect
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters(prev => ({ ...prev, applicant_name: searchInput }));
      if (searchInput !== '') {
        setPage(1);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput]);

  // Handle filter changes - reset to page 1
  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
    setPage(1);
  };

  const handleOpenDialog = (leave?: LeaveRequest, viewMode = true) => {
    if (leave) {
      setSelectedLeave(leave);

      // Admin interface is now view-only
      setLeaveForm({
        applicant_type: leave.applicant_type,
        roll_number: leave.applicant_roll_number?.toString() || '',
        class_id: leave.applicant_class_id?.toString() || '',
        employee_id: leave.applicant_employee_id || '',
        leave_type_id: leave.leave_type_id.toString(),
        start_date: new Date(leave.start_date),
        end_date: new Date(leave.end_date),
        reason: leave.reason,
        parent_consent: false,
        emergency_contact_name: '',
        emergency_contact_phone: '',
        substitute_teacher_id: '',
        substitute_arranged: false
      });
      setIsViewMode(true); // Always view mode for admin
      setDialogOpen(true);
    }
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedLeave(null);
    setIsViewMode(false);
  };

  const handleFormChange = (field: string, value: any) => {
    setLeaveForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Admin interface is now review-only - no form submission needed

  const handleApprove = async (leaveId: number, statusId: number, comments?: string) => {
    try {
      await leaveAPI.approveLeave(leaveId, {
        leave_status_id: statusId,
        review_comments: comments
      });

      setSnackbar({
        open: true,
        message: statusId === 2 ? 'Leave request approved' : 'Leave request rejected',
        severity: 'success'
      });
      loadLeaveRequests();
    } catch (error: any) {
      console.error('Error updating leave request:', error);
      const errorMessage = typeof error.response?.data?.detail === 'string'
        ? error.response.data.detail
        : error.message || 'Error updating leave request';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    }
  };

  const handleDelete = async (leaveId: number) => {
    if (!window.confirm('Are you sure you want to delete this leave request?')) return;

    try {
      await leaveAPI.deleteLeave(leaveId);
      setSnackbar({ open: true, message: 'Leave request deleted successfully', severity: 'success' });
      loadLeaveRequests();
    } catch (error: any) {
      console.error('Error deleting leave request:', error);
      const errorMessage = typeof error.response?.data?.detail === 'string'
        ? error.response.data.detail
        : error.message || 'Error deleting leave request';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    }
  };

  const getStatusColor = (statusName: string, statusColor?: string) => {
    if (statusColor) return statusColor;
    switch (statusName.toLowerCase()) {
      case 'pending': return '#FFA500';
      case 'approved': return '#00FF00';
      case 'rejected': return '#FF0000';
      default: return '#808080';
    }
  };

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          Please login to access the leave management system.
        </Alert>
        <Button
          variant="contained"
          onClick={() => window.location.href = '/admin/login'}
        >
          Go to Login
        </Button>
      </Box>
    );
  }

  // Show loading if configuration is still loading
  if (configLoading) {
    return (
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={40} />
        <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
          Loading leave management configuration...
        </Typography>
      </Box>
    );
  }

  // Show error if configuration failed to load
  if (configError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="subtitle2">Configuration Error</Typography>
          <Typography variant="body2">{configError}</Typography>
        </Alert>
        <Button
          variant="outlined"
          onClick={() => window.location.reload()}
        >
          Reload Page
        </Button>
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ width: '100%' }}>
        {/* Filters Section - Above Tabs */}
        <CollapsibleFilterSection
          title="Filters"
          defaultExpanded={true}
          persistKey="leave-management-filters"
        >
          <Box sx={{
            display: 'flex',
            gap: { xs: 1.5, sm: 2 },
            alignItems: { xs: 'stretch', sm: 'center' },
            flexWrap: 'wrap',
            flexDirection: { xs: 'column', sm: 'row' }
          }}>

            <FormControl
              size="small"
              sx={{
                flex: { xs: '1 1 100%', sm: '1 1 auto' },
                minWidth: { xs: '100%', sm: 'auto' },
                order: { xs: 2, sm: 0 }
              }}
            >
              <InputLabel>Applicant Type</InputLabel>
              <Select
                value={filters.applicant_type}
                label="Applicant Type"
                onChange={(e) => {
                  setFilters(prev => ({ ...prev, applicant_type: e.target.value }));
                  setPage(1);
                }}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="student">Students</MenuItem>
                <MenuItem value="teacher">Teachers</MenuItem>
              </Select>
            </FormControl>

            <FormControl
              size="small"
              sx={{
                flex: { xs: '1 1 100%', sm: '1 1 auto' },
                minWidth: { xs: '100%', sm: 'auto' },
                order: { xs: 3, sm: 0 }
              }}
            >
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.leave_status_id}
                label="Status"
                onChange={(e) => {
                  setFilters(prev => ({ ...prev, leave_status_id: e.target.value }));
                  setPage(1);
                }}
              >
                <MenuItem value="">All</MenuItem>
                {configuration?.leave_statuses && Array.isArray(configuration.leave_statuses) ?
                  configuration.leave_statuses.map((status: any) => (
                    <MenuItem key={status.id} value={status.id.toString()}>
                      {status.description || status.name}
                    </MenuItem>
                  )) : null}
              </Select>
            </FormControl>

            <FormControl
              size="small"
              sx={{
                flex: { xs: '1 1 100%', sm: '1 1 auto' },
                minWidth: { xs: '100%', sm: 'auto' },
                order: { xs: 4, sm: 0 }
              }}
            >
              <InputLabel>Leave Type</InputLabel>
              <Select
                value={filters.leave_type_id}
                label="Leave Type"
                onChange={(e) => {
                  setFilters(prev => ({ ...prev, leave_type_id: e.target.value }));
                  setPage(1);
                }}
              >
                <MenuItem value="">All</MenuItem>
                {configuration?.leave_types && Array.isArray(configuration.leave_types) ?
                  configuration.leave_types.map((type: any) => (
                    <MenuItem key={type.id} value={type.id.toString()}>
                      {type.description || type.name}
                    </MenuItem>
                  )) : null}
              </Select>
            </FormControl>

            <TextField
              size="small"
              label="Search by Name"
              placeholder="Enter applicant name..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              sx={{
                flex: { xs: '1 1 100%', sm: '1 1 auto' },
                minWidth: { xs: '100%', sm: 'auto' },
                order: { xs: 4, sm: 0 }
              }}
            />


          </Box>
        </CollapsibleFilterSection>

        {/* All Requests */}
        {loading ? (
            <Box display="flex" justifyContent="center" p={{ xs: 2, sm: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Paper elevation={3} sx={{ p: 3 }}>
              <TableContainer
                sx={{
                  maxHeight: { xs: '60vh', sm: '70vh' },
                  overflow: 'auto'
                }}
              >
              <Table
                stickyHeader
                size="small"
                sx={{
                  '& .MuiTableCell-root': {
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    padding: { xs: '8px 12px', sm: '12px 16px' },
                    borderBottom: '1px solid rgba(224, 224, 224, 1)'
                  },
                  '& .MuiTableHead-root .MuiTableCell-root': {
                    backgroundColor: 'grey.50',
                    fontWeight: 600,
                    fontSize: { xs: '0.75rem', sm: '0.875rem' }
                  }
                }}
              >
                <TableHead>
                  <TableRow>
                    <TableCell>Applicant</TableCell>
                    <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>Type</TableCell>
                    <TableCell>Leave Type</TableCell>
                    <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Duration</TableCell>
                    <TableCell>Days</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Array.isArray(leaveRequests) && leaveRequests.length > 0 ? (
                    leaveRequests.filter(leave => leave && typeof leave === 'object' && leave.id).map((leave) => (
                  <TableRow key={leave.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {leave.applicant_name || 'Unknown'}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {leave.applicant_details || ''}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>
                      <Chip
                        icon={leave.applicant_type === 'student' ? <School /> : <Work />}
                        label={leave.applicant_type === 'student' ? 'Student' : 'Teacher'}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}
                      />
                    </TableCell>
                    <TableCell>{leave.leave_type_name || 'Unknown'}</TableCell>
                    <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                      {leave.start_date ? new Date(leave.start_date).toLocaleDateString() : 'N/A'} - {leave.end_date ? new Date(leave.end_date).toLocaleDateString() : 'N/A'}
                    </TableCell>
                    <TableCell>{leave.total_days || 0}</TableCell>
                    <TableCell>
                      <Chip
                        label={leave.leave_status_name || 'Unknown'}
                        size="small"
                        sx={{
                          backgroundColor: getStatusColor(leave.leave_status_name || 'Unknown', leave.leave_status_color),
                          color: 'white',
                          fontSize: { xs: '0.65rem', sm: '0.75rem' }
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: { xs: 0.25, sm: 0.5 }, flexWrap: 'wrap' }}>
                        <Tooltip title="View">
                          <IconButton size="small" onClick={() => handleOpenDialog(leave, true)} sx={{ minWidth: 36, minHeight: 36 }}>
                            <ViewIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                          </IconButton>
                        </Tooltip>
                        {leave.leave_status_name?.toUpperCase() === 'PENDING' && (
                          <>
                            <Tooltip title="Approve">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => handleApprove(leave.id, 2, 'Approved')}
                                sx={{ minWidth: 36, minHeight: 36 }}
                              >
                                <ApproveIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Reject">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleApprove(leave.id, 3, 'Rejected')}
                                sx={{ minWidth: 36, minHeight: 36 }}
                              >
                                <RejectIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleDelete(leave.id)}
                                sx={{ minWidth: 36, minHeight: 36 }}
                              >
                                <DeleteIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="textSecondary" sx={{ py: 4 }}>
                          No leave requests found
                        </Typography>
                      </TableCell>
                    </TableRow>
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
          )}

        {/* Leave Request Dialog - View Only */}
        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>
            View Leave Request Details
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth disabled={isViewMode}>
                  <InputLabel>Applicant Type</InputLabel>
                  <Select
                    value={leaveForm.applicant_type}
                    label="Applicant Type"
                    onChange={(e) => handleFormChange('applicant_type', e.target.value)}
                  >
                    <MenuItem value="student">Student</MenuItem>
                    <MenuItem value="teacher">Teacher</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              {/* Student Fields */}
              {leaveForm.applicant_type === 'student' && (
                <>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      fullWidth
                      label="Roll Number"
                      value={leaveForm.roll_number}
                      onChange={(e) => handleFormChange('roll_number', e.target.value)}
                      disabled={isViewMode}
                      required
                      error={!leaveForm.roll_number.trim()}
                      helperText={!leaveForm.roll_number.trim() ? 'Roll Number is required' : ''}
                      placeholder="e.g., 001, STU001, etc."
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <ClassDropdown
                      value={leaveForm.class_id}
                      onChange={(value) => handleFormChange('class_id', value)}
                      disabled={isViewMode}
                      required
                      error={!leaveForm.class_id}
                      helperText={!leaveForm.class_id ? 'Class is required' : ''}
                    />
                  </Grid>
                </>
              )}

              {/* Teacher Fields */}
              {leaveForm.applicant_type === 'teacher' && (
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Employee ID"
                    value={leaveForm.employee_id}
                    onChange={(e) => handleFormChange('employee_id', e.target.value)}
                    disabled={isViewMode}
                    required
                    error={!leaveForm.employee_id.trim()}
                    helperText={!leaveForm.employee_id.trim() ? 'Employee ID is required' : ''}
                    placeholder="e.g., EMP001, TCH001, etc."
                  />
                </Grid>
              )}

              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth disabled={isViewMode}>
                  <InputLabel>Leave Type</InputLabel>
                  <Select
                    value={leaveForm.leave_type_id}
                    label="Leave Type"
                    onChange={(e) => handleFormChange('leave_type_id', e.target.value)}
                  >
                    {configuration?.leave_types && Array.isArray(configuration.leave_types) ?
                      configuration.leave_types.map((type: any) => (
                        <MenuItem key={type.id} value={type.id.toString()}>
                          {type.name || 'Unknown Type'}
                        </MenuItem>
                      )) : null}
                  </Select>
                </FormControl>
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <DatePicker
                  label="Start Date"
                  value={leaveForm.start_date || null}
                  onChange={(date) => handleFormChange('start_date', date)}
                  disabled={isViewMode}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      required: true,
                      error: !leaveForm.start_date,
                      helperText: !leaveForm.start_date ? 'Start date is required' : ''
                    }
                  }}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <DatePicker
                  label="End Date"
                  value={leaveForm.end_date || null}
                  onChange={(date) => handleFormChange('end_date', date)}
                  disabled={isViewMode}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      required: true,
                      error: !leaveForm.end_date,
                      helperText: !leaveForm.end_date ? 'End date is required' : ''
                    }
                  }}
                />
              </Grid>

              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Reason"
                  multiline
                  rows={3}
                  value={leaveForm.reason}
                  onChange={(e) => handleFormChange('reason', e.target.value)}
                  disabled={isViewMode}
                  required
                  error={!leaveForm.reason.trim()}
                  helperText={!leaveForm.reason.trim() ? 'Reason is required' : ''}
                />
              </Grid>

              {selectedLeave && selectedLeave.review_comments && (
                <Grid size={12}>
                  <Alert severity="info">
                    <Typography variant="body2">
                      <strong>Review Comments:</strong> {selectedLeave.review_comments}
                    </Typography>
                  </Alert>
                </Grid>
              )}
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog} variant="contained">
              Close
            </Button>
          </DialogActions>
        </Dialog>

        {/* Snackbar for notifications */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
        >
          <Alert 
            onClose={() => setSnackbar(prev => ({ ...prev, open: false }))} 
            severity={snackbar.severity}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </LocalizationProvider>
  );
};

export default LeaveManagementSystem;
