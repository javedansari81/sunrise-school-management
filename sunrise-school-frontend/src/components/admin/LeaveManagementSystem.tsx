import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
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
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Delete as DeleteIcon,
  School,
  Work,
  FilterList
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useServiceConfiguration, useConfiguration } from '../../contexts/ConfigurationContext';
import { useAuth } from '../../contexts/AuthContext';
import { leaveAPI } from '../../services/api';

// Types
interface LeaveRequest {
  id: number;
  applicant_id: number;
  applicant_type: 'student' | 'teacher';
  applicant_name: string;
  applicant_details: string;
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

interface Configuration {
  leave_types: Array<{
    id: number;
    name: string;
    description: string;
    max_days_per_year: number;
    requires_medical_certificate: boolean;
    is_active: boolean;
  }>;
  leave_statuses: Array<{
    id: number;
    name: string;
    description: string;
    color_code: string;
    is_final: boolean;
    is_active: boolean;
  }>;
  classes: Array<{
    id: number;
    name: string;
    display_name: string;
    is_active: boolean;
  }>;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`leave-tabpanel-${index}`}
      aria-labelledby={`leave-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const LeaveManagementSystem: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const { isLoading: configLoading, isLoaded: configLoaded, error: configError } = useServiceConfiguration('leave-management');
  const { getServiceConfiguration } = useConfiguration();

  // Get the service configuration
  const configuration = getServiceConfiguration('leave-management');
  const [tabValue, setTabValue] = useState(0);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState<LeaveRequest | null>(null);
  const [isViewMode, setIsViewMode] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [statistics, setStatistics] = useState<any>({});


  
  // Form state
  const [leaveForm, setLeaveForm] = useState({
    applicant_id: '',
    applicant_type: 'student' as 'student' | 'teacher',
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
    class_name: '',
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

      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      console.log('🌐 Loading leave requests with params:', Object.fromEntries(queryParams));
      console.log('🔑 User authenticated:', isAuthenticated);
      console.log('👤 Current user:', user);

      const data = await leaveAPI.getLeaves(queryParams);
      console.log('✅ Leave requests loaded:', data);
      setLeaveRequests(Array.isArray(data.leaves) ? data.leaves : []);
    } catch (error: any) {
      console.error('Error loading leave requests:', error);
      setLeaveRequests([]); // Ensure we set an empty array on error
      const errorMessage = error.code === 'ERR_NETWORK'
        ? 'Backend server is not running. Please start the backend server.'
        : error.response?.data?.detail || error.message || 'Error loading leave requests';
      setSnackbar({ open: true, message: errorMessage, severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, [filters, isAuthenticated, user]);

  const loadStatistics = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      console.log('🌐 Loading leave statistics...');
      const stats = await leaveAPI.getLeaveStatistics();
      console.log('✅ Leave statistics loaded:', stats);
      setStatistics(stats);
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  }, [isAuthenticated]);

  // Load leave requests and statistics
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
      loadStatistics();
    } else if (configError) {
      console.error('❌ Configuration error in leave management:', configError);
      setSnackbar({
        open: true,
        message: `Configuration error: ${configError}`,
        severity: 'error'
      });
    }
  }, [configLoading, configLoaded, configError, isAuthenticated, filters, loadLeaveRequests, loadStatistics]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenDialog = (leave?: LeaveRequest, viewMode = false) => {
    if (leave) {
      setSelectedLeave(leave);
      setLeaveForm({
        applicant_id: leave.applicant_id.toString(),
        applicant_type: leave.applicant_type,
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
    } else {
      setSelectedLeave(null);
      setLeaveForm({
        applicant_id: '',
        applicant_type: 'student',
        leave_type_id: '',
        start_date: null,
        end_date: null,
        reason: '',
        parent_consent: false,
        emergency_contact_name: '',
        emergency_contact_phone: '',
        substitute_teacher_id: '',
        substitute_arranged: false
      });
    }
    setIsViewMode(viewMode);
    setDialogOpen(true);
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

  const handleSubmit = async () => {
    // Form validation
    if (!leaveForm.applicant_id || !leaveForm.leave_type_id || !leaveForm.start_date || !leaveForm.end_date || !leaveForm.reason.trim()) {
      setSnackbar({
        open: true,
        message: 'Please fill in all required fields',
        severity: 'error'
      });
      return;
    }

    try {
      setLoading(true);
      const submitData = {
        ...leaveForm,
        start_date: leaveForm.start_date?.toISOString().split('T')[0],
        end_date: leaveForm.end_date?.toISOString().split('T')[0],
        applicant_id: parseInt(leaveForm.applicant_id),
        leave_type_id: parseInt(leaveForm.leave_type_id),
        total_days: leaveForm.start_date && leaveForm.end_date
          ? Math.ceil((leaveForm.end_date.getTime() - leaveForm.start_date.getTime()) / (1000 * 60 * 60 * 24)) + 1
          : 1
      };

      if (selectedLeave) {
        await leaveAPI.updateLeave(selectedLeave.id, submitData);
        setSnackbar({
          open: true,
          message: 'Leave request updated successfully',
          severity: 'success'
        });
      } else {
        await leaveAPI.createLeave(submitData);
        setSnackbar({
          open: true,
          message: 'Leave request created successfully',
          severity: 'success'
        });
      }

      handleCloseDialog();
      loadLeaveRequests();
    } catch (error: any) {
      console.error('Error submitting leave request:', error);
      const errorMessage = typeof error.response?.data?.detail === 'string'
        ? error.response.data.detail
        : error.message || 'Error submitting leave request';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

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
        <Paper sx={{ width: '100%', mb: { xs: 2, sm: 3 } }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="leave management tabs"
            variant="scrollable"
            scrollButtons="auto"
            allowScrollButtonsMobile
            sx={{
              '& .MuiTab-root': {
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                minHeight: { xs: 40, sm: 48 },
                minWidth: { xs: 80, sm: 120 },
                textTransform: 'none',
                fontWeight: 500,
              },
              '& .Mui-selected': {
                fontWeight: 600,
              }
            }}
          >
            <Tab label="All Requests" />
            <Tab label="Pending Approval" />
            <Tab label="My Requests" />
            <Tab label="Statistics" />
          </Tabs>
        </Paper>

        <TabPanel value={tabValue} index={0}>
          {/* All Requests Tab - Mobile Responsive */}
          <Box sx={{
            mb: { xs: 2, sm: 3 },
            display: 'flex',
            gap: { xs: 1.5, sm: 2 },
            alignItems: { xs: 'stretch', sm: 'center' },
            flexWrap: 'wrap',
            flexDirection: { xs: 'column', sm: 'row' }
          }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
              sx={{
                fontSize: { xs: '0.875rem', sm: '1rem' },
                padding: { xs: '6px 12px', sm: '8px 16px' },
                order: { xs: 1, sm: 0 }
              }}
            >
              New Leave Request
            </Button>

            <FormControl
              size="small"
              sx={{
                minWidth: { xs: '100%', sm: 120 },
                order: { xs: 2, sm: 0 }
              }}
            >
              <InputLabel>Applicant Type</InputLabel>
              <Select
                value={filters.applicant_type}
                label="Applicant Type"
                onChange={(e) => setFilters(prev => ({ ...prev, applicant_type: e.target.value }))}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="student">Students</MenuItem>
                <MenuItem value="teacher">Teachers</MenuItem>
              </Select>
            </FormControl>

            <FormControl
              size="small"
              sx={{
                minWidth: { xs: '100%', sm: 120 },
                order: { xs: 3, sm: 0 }
              }}
            >
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.leave_status_id}
                label="Status"
                onChange={(e) => setFilters(prev => ({ ...prev, leave_status_id: e.target.value }))}
              >
                <MenuItem value="">All</MenuItem>
                {configuration?.leave_statuses && Array.isArray(configuration.leave_statuses) ?
                  configuration.leave_statuses.map((status: any) => (
                    <MenuItem key={status.id} value={status.id.toString()}>
                      {status.name}
                    </MenuItem>
                  )) : null}
              </Select>
            </FormControl>

            <Button
              variant="outlined"
              startIcon={<FilterList />}
              onClick={loadLeaveRequests}
              sx={{
                fontSize: { xs: '0.875rem', sm: '1rem' },
                padding: { xs: '6px 12px', sm: '8px 16px' },
                order: { xs: 4, sm: 0 },
                minWidth: { xs: '100%', sm: 'auto' }
              }}
            >
              Apply Filters
            </Button>
          </Box>

          {loading ? (
            <Box display="flex" justifyContent="center" p={{ xs: 2, sm: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer
              component={Paper}
              sx={{
                maxHeight: { xs: '60vh', sm: '70vh' },
                overflow: 'auto'
              }}
            >
              <Table
                size="small"
                sx={{
                  '& .MuiTableCell-root': {
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    padding: { xs: '8px', sm: '16px' }
                  }
                }}
              >
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Applicant</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', display: { xs: 'none', sm: 'table-cell' } }}>Type</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Leave Type</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', display: { xs: 'none', md: 'table-cell' } }}>Duration</TableCell>
                    <TableCell>Days</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
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
                    <TableCell>
                      <Chip
                        icon={leave.applicant_type === 'student' ? <School /> : <Work />}
                        label={leave.applicant_type === 'student' ? 'Student' : 'Teacher'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{leave.leave_type_name || 'Unknown'}</TableCell>
                    <TableCell>
                      {leave.start_date ? new Date(leave.start_date).toLocaleDateString() : 'N/A'} - {leave.end_date ? new Date(leave.end_date).toLocaleDateString() : 'N/A'}
                    </TableCell>
                    <TableCell>{leave.total_days || 0}</TableCell>
                    <TableCell>
                      <Chip
                        label={leave.leave_status_name || 'Unknown'}
                        size="small"
                        sx={{
                          backgroundColor: getStatusColor(leave.leave_status_name || 'Unknown', leave.leave_status_color),
                          color: 'white'
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View">
                        <IconButton size="small" onClick={() => handleOpenDialog(leave, true)}>
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      {leave.leave_status_name === 'Pending' && (
                        <>
                          <Tooltip title="Edit">
                            <IconButton size="small" onClick={() => handleOpenDialog(leave, false)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Approve">
                            <IconButton 
                              size="small" 
                              color="success"
                              onClick={() => handleApprove(leave.id, 2, 'Approved')}
                            >
                              <ApproveIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reject">
                            <IconButton 
                              size="small" 
                              color="error"
                              onClick={() => handleApprove(leave.id, 3, 'Rejected')}
                            >
                              <RejectIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton 
                              size="small" 
                              color="error"
                              onClick={() => handleDelete(leave.id)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
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
          )}
        </TabPanel>

        {/* Leave Request Dialog */}
        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>
            {isViewMode ? 'View Leave Request' : selectedLeave ? 'Edit Leave Request' : 'New Leave Request'}
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

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Applicant ID"
                  type="number"
                  value={leaveForm.applicant_id}
                  onChange={(e) => handleFormChange('applicant_id', e.target.value)}
                  disabled={isViewMode}
                  required
                  error={!leaveForm.applicant_id}
                  helperText={!leaveForm.applicant_id ? 'Applicant ID is required' : ''}
                />
              </Grid>

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

              <Grid size={12}>
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
            <Button onClick={handleCloseDialog}>
              {isViewMode ? 'Close' : 'Cancel'}
            </Button>
            {!isViewMode && (
              <Button onClick={handleSubmit} variant="contained">
                {selectedLeave ? 'Update' : 'Create'}
              </Button>
            )}
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
