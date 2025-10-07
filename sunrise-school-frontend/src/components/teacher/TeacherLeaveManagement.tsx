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
  Chip,
  CircularProgress,
  Snackbar,
  Alert,
  TextField,
  Grid,
  Card,
  CardContent,
  Stack,
  InputAdornment,
  IconButton,
  Tooltip
} from '@mui/material';

import {
  Add as AddIcon,
  Visibility as ViewIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  EventNote,
  Schedule,
  CheckCircle,
  Cancel,
  Pending
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useServiceConfiguration, useConfiguration } from '../../contexts/ConfigurationContext';
import { leaveAPI, teachersAPI } from '../../services/api';
import { FilterDropdown } from '../common/MetadataDropdown';
import TeacherLeaveRequestDialog from './TeacherLeaveRequestDialog';

// Types
interface LeaveRequest {
  id: number;
  applicant_id: number;
  applicant_type: 'student' | 'teacher';
  applicant_name: string;
  applicant_details: string;
  applicant_employee_id?: string;  // Employee ID for teachers
  applicant_roll_number?: number;  // Roll number for students
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

interface TeacherProfile {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  department: string;
  position: string;
}

const TeacherLeaveManagement: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const { isLoading: configLoading, isLoaded: configLoaded, error: configError } = useServiceConfiguration('leave-management');
  const { getServiceConfiguration } = useConfiguration();

  // Get the service configuration
  const configuration = getServiceConfiguration('leave-management');
  
  // State
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [teacherProfile, setTeacherProfile] = useState<TeacherProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState<LeaveRequest | null>(null);
  const [isViewMode, setIsViewMode] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [searchTerm, setSearchTerm] = useState('');
  
  // Filters
  const [filters, setFilters] = useState<{
    leave_status_id: string | number;
    leave_type_id: string | number;
  }>({
    leave_status_id: 'all',
    leave_type_id: 'all'
  });

  // Load teacher profile
  const loadTeacherProfile = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      const response = await teachersAPI.getMyProfile();
      setTeacherProfile(response.data);
    } catch (error: any) {
      console.error('Error loading teacher profile:', error);
      setSnackbar({
        open: true,
        message: 'Error loading teacher profile',
        severity: 'error'
      });
    }
  }, [isAuthenticated]);

  // Load teacher's leave requests
  const loadLeaveRequests = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      setLoading(true);
      const data = await leaveAPI.getMyLeaveRequests();
      setLeaveRequests(Array.isArray(data) ? data : []);
    } catch (error: any) {
      console.error('Error loading leave requests:', error);
      setLeaveRequests([]);

      let errorMessage = 'Error loading leave requests';
      if (error.response?.status === 401 || error.response?.status === 403) {
        errorMessage = 'Authentication required. Please log in again.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }

      setSnackbar({ open: true, message: errorMessage, severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  // Effects
  useEffect(() => {
    loadTeacherProfile();
  }, [loadTeacherProfile]);

  useEffect(() => {
    loadLeaveRequests();
  }, [loadLeaveRequests]);

  // Filter leave requests based on search and filters
  const filteredLeaveRequests = leaveRequests.filter(leave => {
    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch =
        leave.leave_type_name.toLowerCase().includes(searchLower) ||
        leave.reason.toLowerCase().includes(searchLower) ||
        leave.leave_status_name.toLowerCase().includes(searchLower);

      if (!matchesSearch) return false;
    }

    // Status filter - only apply if a specific status is selected (not 'all')
    if (filters.leave_status_id !== 'all' && filters.leave_status_id !== '') {
      // Convert both to numbers for comparison
      const filterStatusId = typeof filters.leave_status_id === 'number'
        ? filters.leave_status_id
        : parseInt(filters.leave_status_id, 10);

      if (leave.leave_status_id !== filterStatusId) {
        return false;
      }
    }

    // Type filter - only apply if a specific type is selected (not 'all')
    if (filters.leave_type_id !== 'all' && filters.leave_type_id !== '') {
      // Convert both to numbers for comparison
      const filterTypeId = typeof filters.leave_type_id === 'number'
        ? filters.leave_type_id
        : parseInt(filters.leave_type_id, 10);

      if (leave.leave_type_id !== filterTypeId) {
        return false;
      }
    }

    return true;
  });

  // Get status icon
  const getStatusIcon = (statusName: string) => {
    switch (statusName.toLowerCase()) {
      case 'approved':
        return <CheckCircle sx={{ fontSize: 16 }} />;
      case 'rejected':
        return <Cancel sx={{ fontSize: 16 }} />;
      case 'pending':
      default:
        return <Pending sx={{ fontSize: 16 }} />;
    }
  };

  // Get status color
  const getStatusColor = (statusName: string): 'success' | 'error' | 'warning' | 'default' => {
    switch (statusName.toLowerCase()) {
      case 'approved':
        return 'success';
      case 'rejected':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Handle view leave request
  const handleViewLeave = (leave: LeaveRequest) => {
    setSelectedLeave(leave);
    setIsViewMode(true);
    setDialogOpen(true);
  };

  // Handle new leave request
  const handleNewLeaveRequest = () => {
    setSelectedLeave(null);
    setIsViewMode(false);
    setDialogOpen(true);
  };

  // Handle close dialog
  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedLeave(null);
    setIsViewMode(false);
  };

  // Handle filter change
  const handleFilterChange = (field: string, value: string | number) => {
    console.log(`Filter changed - ${field}:`, value, typeof value);
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Get status statistics
  const getStatusStats = () => {
    const stats = {
      total: leaveRequests.length,
      pending: leaveRequests.filter(leave => leave.leave_status_name.toLowerCase() === 'pending').length,
      approved: leaveRequests.filter(leave => leave.leave_status_name.toLowerCase() === 'approved').length,
      rejected: leaveRequests.filter(leave => leave.leave_status_name.toLowerCase() === 'rejected').length,
    };
    return stats;
  };

  const statusStats = getStatusStats();

  if (configLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (configError) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error loading configuration: {configError}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
      {/* Header Section */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
          My Leave Requests
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {teacherProfile && `${teacherProfile.first_name} ${teacherProfile.last_name} (${teacherProfile.employee_id})`}
        </Typography>
      </Box>

      {/* Status Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 6, sm: 3 }}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h6" color="primary">
              {statusStats.total}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Total Requests
            </Typography>
          </Card>
        </Grid>
        <Grid size={{ xs: 6, sm: 3 }}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h6" color="warning.main">
              {statusStats.pending}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Pending
            </Typography>
          </Card>
        </Grid>
        <Grid size={{ xs: 6, sm: 3 }}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h6" color="success.main">
              {statusStats.approved}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Approved
            </Typography>
          </Card>
        </Grid>
        <Grid size={{ xs: 6, sm: 3 }}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h6" color="error.main">
              {statusStats.rejected}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Rejected
            </Typography>
          </Card>
        </Grid>
      </Grid>

      {/* Action Button and Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack spacing={2}>
          {/* Add New Request Button */}
          <Box display="flex" justifyContent="flex-start">
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleNewLeaveRequest}
              sx={{ mb: 2 }}
            >
              New Leave Request
            </Button>
          </Box>

          {/* Filters Row */}
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, sm: 6, md: 4 }}>
              <TextField
                fullWidth
                placeholder="Search by type, reason, or status..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                size="small"
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 3, md: 2 }}>
              <FilterDropdown
                metadataType="leaveStatuses"
                label="Status"
                value={filters.leave_status_id}
                onChange={(value) => handleFilterChange('leave_status_id', value)}
                size="small"
                fullWidth
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 3, md: 2 }}>
              <FilterDropdown
                metadataType="leaveTypes"
                label="Leave Type"
                value={filters.leave_type_id}
                onChange={(value) => handleFilterChange('leave_type_id', value)}
                size="small"
                fullWidth
              />
            </Grid>
          </Grid>
        </Stack>
      </Paper>

      {/* Leave Requests Table */}
      <Paper sx={{ width: '100%' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Leave Type</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Days</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Applied Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress size={24} />
                  </TableCell>
                </TableRow>
              ) : filteredLeaveRequests.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="textSecondary">
                      No leave requests found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredLeaveRequests.map((leave) => (
                  <TableRow key={leave.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>
                        {leave.leave_type_name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(leave.start_date).toLocaleDateString()} - {new Date(leave.end_date).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {leave.total_days} day{leave.total_days !== 1 ? 's' : ''}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(leave.leave_status_name)}
                        label={leave.leave_status_name}
                        color={getStatusColor(leave.leave_status_name)}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(leave.created_at).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => handleViewLeave(leave)}
                          color="primary"
                        >
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Leave Request Dialog */}
      <TeacherLeaveRequestDialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        onSuccess={() => {
          loadLeaveRequests();
          setSnackbar({
            open: true,
            message: 'Leave request submitted successfully',
            severity: 'success'
          });
        }}
        selectedLeave={selectedLeave}
        isViewMode={isViewMode}
        teacherProfile={teacherProfile}
      />
    </Box>
  );
};

export default TeacherLeaveManagement;
