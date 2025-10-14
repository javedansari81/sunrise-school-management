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
  Grid,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';

import {
  Visibility as ViewIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { leaveAPI } from '../../services/api';
import { FilterDropdown } from '../common/MetadataDropdown';
import { DEFAULT_PAGE_SIZE } from '../../config/pagination';

// Types
interface LeaveRequest {
  id: number;
  applicant_id: number;
  applicant_type: 'student' | 'teacher';
  applicant_name: string;
  applicant_details: string;
  applicant_roll_number?: number;
  applicant_class_id?: number;
  leave_type_id: number;
  leave_type_name: string;
  leave_status_id: number;
  leave_status_name: string;
  leave_status_color: string;
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  approval_comments?: string;
  reviewer_name?: string;
  created_at: string;
}

interface TeacherClassStudentLeavesProps {
  teacherProfile: any;
}

const TeacherClassStudentLeaves: React.FC<TeacherClassStudentLeavesProps> = ({ teacherProfile }) => {
  const { isLoading: configLoading, isLoaded: configLoaded, error: configError } = useServiceConfiguration('leave-management');
  
  // State
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState<LeaveRequest | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [approvalDialogOpen, setApprovalDialogOpen] = useState(false);
  const [approvalAction, setApprovalAction] = useState<'approve' | 'reject'>('approve');
  const [approvalComments, setApprovalComments] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  
  // Filters
  const [filters, setFilters] = useState<{
    leave_status_id: string | number;
    leave_type_id: string | number;
  }>({
    leave_status_id: 'all',
    leave_type_id: 'all'
  });

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);

  // Load leave requests
  const loadLeaveRequests = useCallback(async () => {
    try {
      setLoading(true);
      
      const params: any = {
        page,
        per_page: DEFAULT_PAGE_SIZE
      };

      if (filters.leave_status_id !== 'all') {
        params.leave_status_id = filters.leave_status_id;
      }

      if (filters.leave_type_id !== 'all') {
        params.leave_type_id = filters.leave_type_id;
      }

      const response = await leaveAPI.getClassStudentLeaves(params);
      
      setLeaveRequests(response.leaves || []);
      setTotalPages(response.total_pages || 0);
      setTotalRecords(response.total || 0);
    } catch (error: any) {
      console.error('Error loading student leave requests:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Error loading student leave requests',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  useEffect(() => {
    if (configLoaded && teacherProfile?.class_teacher_of_id) {
      loadLeaveRequests();
    }
  }, [configLoaded, teacherProfile, loadLeaveRequests]);

  // Handle filter change
  const handleFilterChange = (filterName: string, value: string | number) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
    setPage(1); // Reset to first page when filters change
  };

  // Handle view leave
  const handleViewLeave = (leave: LeaveRequest) => {
    setSelectedLeave(leave);
    setViewDialogOpen(true);
  };

  // Handle approve/reject
  const handleOpenApprovalDialog = (leave: LeaveRequest, action: 'approve' | 'reject') => {
    setSelectedLeave(leave);
    setApprovalAction(action);
    setApprovalComments('');
    setApprovalDialogOpen(true);
  };

  const handleApproveReject = async () => {
    if (!selectedLeave) return;

    try {
      setLoading(true);
      const statusId = approvalAction === 'approve' ? 2 : 3; // 2 = Approved, 3 = Rejected
      
      await leaveAPI.approveLeave(selectedLeave.id, {
        leave_status_id: statusId,
        review_comments: approvalComments
      });

      setSnackbar({
        open: true,
        message: `Leave request ${approvalAction === 'approve' ? 'approved' : 'rejected'} successfully`,
        severity: 'success'
      });

      setApprovalDialogOpen(false);
      loadLeaveRequests();
    } catch (error: any) {
      console.error(`Error ${approvalAction}ing leave:`, error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || `Error ${approvalAction}ing leave request`,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async (leave: LeaveRequest) => {
    if (!window.confirm('Are you sure you want to delete this leave request?')) {
      return;
    }

    try {
      setLoading(true);
      await leaveAPI.deleteLeave(leave.id);
      
      setSnackbar({
        open: true,
        message: 'Leave request deleted successfully',
        severity: 'success'
      });

      loadLeaveRequests();
    } catch (error: any) {
      console.error('Error deleting leave:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Error deleting leave request',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Get status color
  const getStatusColor = (statusId: number): 'default' | 'warning' | 'success' | 'error' => {
    switch (statusId) {
      case 1: return 'warning';  // Pending
      case 2: return 'success';  // Approved
      case 3: return 'error';    // Rejected
      default: return 'default';
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  if (!teacherProfile?.class_teacher_of_id) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          You are not assigned as a class teacher. Only class teachers can view and manage student leave requests.
        </Typography>
      </Box>
    );
  }

  if (configLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (configError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Error loading configuration: {configError}</Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <FilterDropdown
              metadataType="leaveStatuses"
              label="Leave Status"
              value={filters.leave_status_id}
              onChange={(value) => handleFilterChange('leave_status_id', value)}
              allLabel="All Statuses"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <FilterDropdown
              metadataType="leaveTypes"
              label="Leave Type"
              value={filters.leave_type_id}
              onChange={(value) => handleFilterChange('leave_type_id', value)}
              allLabel="All Types"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 12, md: 6 }}>
            <Typography variant="body2" color="text.secondary">
              Showing leave requests from students in your class: <strong>{teacherProfile.class_teacher_of_name}</strong>
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Leave Requests Table */}
      <Paper>
        <TableContainer>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: 'white' }}>
                  <TableCell><strong>Student</strong></TableCell>
                  <TableCell><strong>Leave Type</strong></TableCell>
                  <TableCell><strong>Duration</strong></TableCell>
                  <TableCell><strong>Days</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                  <TableCell><strong>Applied On</strong></TableCell>
                  <TableCell align="center"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {leaveRequests.length > 0 ? (
                  leaveRequests.map((leave) => (
                    <TableRow key={leave.id} hover>
                      <TableCell>{leave.applicant_name}</TableCell>
                      <TableCell>{leave.leave_type_name}</TableCell>
                      <TableCell>
                        {formatDate(leave.start_date)} - {formatDate(leave.end_date)}
                      </TableCell>
                      <TableCell>{leave.total_days}</TableCell>
                      <TableCell>
                        <Chip
                          label={leave.leave_status_name}
                          color={getStatusColor(leave.leave_status_id)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{formatDate(leave.created_at)}</TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => handleViewLeave(leave)}>
                            <ViewIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {leave.leave_status_id === 1 && (
                          <>
                            <Tooltip title="Approve">
                              <IconButton 
                                size="small" 
                                color="success"
                                onClick={() => handleOpenApprovalDialog(leave, 'approve')}
                              >
                                <ApproveIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Reject">
                              <IconButton 
                                size="small" 
                                color="error"
                                onClick={() => handleOpenApprovalDialog(leave, 'reject')}
                              >
                                <RejectIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton 
                                size="small" 
                                color="error"
                                onClick={() => handleDelete(leave)}
                              >
                                <DeleteIcon fontSize="small" />
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
                        No leave requests found from your class students
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </TableContainer>

        {/* Pagination */}
        {totalPages > 1 && (
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </Button>
            <Typography sx={{ px: 2, py: 1 }}>
              Page {page} of {totalPages} ({totalRecords} total)
            </Typography>
            <Button
              variant="outlined"
              size="small"
              disabled={page === totalPages}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </Box>
        )}
      </Paper>

      {/* View Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Leave Request Details</DialogTitle>
        <DialogContent>
          {selectedLeave && (
            <Box sx={{ pt: 1 }}>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Student</Typography>
                  <Typography variant="body1">{selectedLeave.applicant_name}</Typography>
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Class</Typography>
                  <Typography variant="body1">{selectedLeave.applicant_details}</Typography>
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Leave Type</Typography>
                  <Typography variant="body1">{selectedLeave.leave_type_name}</Typography>
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Status</Typography>
                  <Chip
                    label={selectedLeave.leave_status_name}
                    color={getStatusColor(selectedLeave.leave_status_id)}
                    size="small"
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Start Date</Typography>
                  <Typography variant="body1">{formatDate(selectedLeave.start_date)}</Typography>
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">End Date</Typography>
                  <Typography variant="body1">{formatDate(selectedLeave.end_date)}</Typography>
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Total Days</Typography>
                  <Typography variant="body1">{selectedLeave.total_days}</Typography>
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Applied On</Typography>
                  <Typography variant="body1">{formatDate(selectedLeave.created_at)}</Typography>
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="subtitle2" color="text.secondary">Reason</Typography>
                  <Typography variant="body1">{selectedLeave.reason}</Typography>
                </Grid>
                {selectedLeave.approval_comments && (
                  <Grid size={{ xs: 12 }}>
                    <Typography variant="subtitle2" color="text.secondary">Review Comments</Typography>
                    <Typography variant="body1">{selectedLeave.approval_comments}</Typography>
                  </Grid>
                )}
                {selectedLeave.reviewer_name && (
                  <Grid size={{ xs: 12 }}>
                    <Typography variant="subtitle2" color="text.secondary">Reviewed By</Typography>
                    <Typography variant="body1">{selectedLeave.reviewer_name}</Typography>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Approval Dialog */}
      <Dialog open={approvalDialogOpen} onClose={() => setApprovalDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {approvalAction === 'approve' ? 'Approve' : 'Reject'} Leave Request
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Are you sure you want to {approvalAction} this leave request for <strong>{selectedLeave?.applicant_name}</strong>?
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Comments (Optional)"
            value={approvalComments}
            onChange={(e) => setApprovalComments(e.target.value)}
            placeholder={`Add comments for ${approvalAction === 'approve' ? 'approval' : 'rejection'}...`}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color={approvalAction === 'approve' ? 'success' : 'error'}
            onClick={handleApproveReject}
            disabled={loading}
          >
            {approvalAction === 'approve' ? 'Approve' : 'Reject'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default TeacherClassStudentLeaves;

