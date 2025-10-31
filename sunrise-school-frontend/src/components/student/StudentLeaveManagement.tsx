import React, { useState, useEffect } from 'react';
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
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Snackbar,
  Stack,
  TextField,
  InputAdornment,
  Grid
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as ViewIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { studentLeaveAPI, studentsAPI } from '../../services/api';
import StudentLeaveRequestDialog from './StudentLeaveRequestDialog';
import { FilterDropdown } from '../common/MetadataDropdown';

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

interface StudentProfile {
  id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  class_name: string;
  section: string;
  roll_number: number;
}

const StudentLeaveManagement: React.FC = () => {
  const { isLoaded, isLoading, error } = useServiceConfiguration('leave-management');

  // State
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [studentProfile, setStudentProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState<LeaveRequest | null>(null);
  const [isViewMode, setIsViewMode] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  // Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<{
    leave_status_id: string | number;
    leave_type_id: string | number;
  }>({
    leave_status_id: 'all',
    leave_type_id: 'all'
  });

  // Load student profile and leave requests
  useEffect(() => {
    loadStudentProfile();
    loadLeaveRequests();
  }, []);

  const loadStudentProfile = async () => {
    try {
      const response = await studentsAPI.getMyProfile();
      setStudentProfile(response.data);
    } catch (error) {
      console.error('Error loading student profile:', error);
      setSnackbar({
        open: true,
        message: 'Error loading student profile',
        severity: 'error'
      });
    }
  };

  const loadLeaveRequests = async () => {
    try {
      setLoading(true);
      const response = await studentLeaveAPI.getMyLeaveRequests();
      setLeaveRequests(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error loading leave requests:', error);
      setSnackbar({
        open: true,
        message: 'Error loading leave requests',
        severity: 'error'
      });
      setLeaveRequests([]);
    } finally {
      setLoading(false);
    }
  };

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
      const filterStatusId = typeof filters.leave_status_id === 'number'
        ? filters.leave_status_id
        : parseInt(filters.leave_status_id, 10);

      if (leave.leave_status_id !== filterStatusId) {
        return false;
      }
    }

    // Type filter - only apply if a specific type is selected (not 'all')
    if (filters.leave_type_id !== 'all' && filters.leave_type_id !== '') {
      const filterTypeId = typeof filters.leave_type_id === 'number'
        ? filters.leave_type_id
        : parseInt(filters.leave_type_id, 10);

      if (leave.leave_type_id !== filterTypeId) {
        return false;
      }
    }

    return true;
  });

  const handleOpenDialog = (leave?: LeaveRequest, viewMode = false) => {
    setSelectedLeave(leave || null);
    setIsViewMode(viewMode);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedLeave(null);
    setIsViewMode(false);
  };

  const getStatusColor = (statusName: string, statusColor?: string) => {
    if (statusColor) return statusColor;
    
    switch (statusName?.toLowerCase()) {
      case 'pending': return '#ff9800';
      case 'approved': return '#4caf50';
      case 'rejected': return '#f44336';
      default: return '#757575';
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Handle filter change
  const handleFilterChange = (field: string, value: string | number) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Filters Section */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          {/* Search Field */}
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

          {/* Status Filter */}
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

          {/* Leave Type Filter */}
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

          {/* New Leave Request Button */}
          <Grid size={{ xs: 12, sm: 12, md: 4 }} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
              sx={{ width: { xs: '100%', md: 'auto' } }}
            >
              New Leave Request
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Leave Requests Table */}
      <Paper elevation={3} sx={{ p: 3 }}>
        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer sx={{ maxHeight: '70vh', overflow: 'auto' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ backgroundColor: 'white' }}>Leave Type</TableCell>
                  <TableCell sx={{ display: { xs: 'none', md: 'table-cell' }, backgroundColor: 'white' }}>Duration</TableCell>
                  <TableCell sx={{ backgroundColor: 'white' }}>Days</TableCell>
                  <TableCell sx={{ backgroundColor: 'white' }}>Status</TableCell>
                  <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' }, backgroundColor: 'white' }}>Submitted</TableCell>
                  <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' }, backgroundColor: 'white' }}>Reviewed By</TableCell>
                  <TableCell align="center" sx={{ backgroundColor: 'white' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredLeaveRequests.length > 0 ? (
                  filteredLeaveRequests.map((leave) => (
                    <TableRow key={leave.id}>
                      <TableCell>
                        <Stack spacing={0.5}>
                          <Typography variant="body2" fontWeight={600} noWrap>
                            {leave.leave_type_name || 'Unknown'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" noWrap>
                            {leave.reason ? (leave.reason.length > 50 ? `${leave.reason.substring(0, 50)}...` : leave.reason) : 'No reason provided'}
                          </Typography>
                        </Stack>
                      </TableCell>
                      <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                        <Stack spacing={0.5}>
                          <Typography variant="body2" noWrap>
                            {leave.start_date ? new Date(leave.start_date).toLocaleDateString() : 'N/A'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" noWrap>
                            to {leave.end_date ? new Date(leave.end_date).toLocaleDateString() : 'N/A'}
                          </Typography>
                        </Stack>
                      </TableCell>
                      <TableCell>{leave.total_days || 0}</TableCell>
                      <TableCell>
                        <Chip
                          label={leave.leave_status_name || 'Unknown'}
                          size="small"
                          sx={{
                            backgroundColor: getStatusColor(leave.leave_status_name || 'Unknown', leave.leave_status_color),
                            color: 'white',
                            fontWeight: 'bold'
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>
                        <Typography variant="caption" color="textSecondary">
                          {leave.created_at ? new Date(leave.created_at).toLocaleDateString() : 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>
                        <Typography variant="caption" color="textSecondary">
                          {leave.reviewer_name || (leave.leave_status_name === 'Pending' ? 'Pending' : 'N/A')}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenDialog(leave, true)}
                            sx={{ color: 'primary.main' }}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography variant="body2" color="textSecondary" sx={{ py: 4 }}>
                        {searchTerm || filters.leave_status_id !== 'all' || filters.leave_type_id !== 'all'
                          ? 'No leave requests found matching the selected filters'
                          : 'You have not submitted any leave requests yet'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Leave Request Dialog */}
      <StudentLeaveRequestDialog
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
        studentProfile={studentProfile}
      />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default StudentLeaveManagement;
