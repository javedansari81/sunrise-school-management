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
  Stack
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as ViewIcon,
  School as SchoolIcon
} from '@mui/icons-material';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { studentLeaveAPI, studentsAPI } from '../../services/api';
import StudentLeaveRequestDialog from './StudentLeaveRequestDialog';

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
  current_class: string;
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

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header Section */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        flexDirection={{ xs: 'column', sm: 'row' }}
        gap={{ xs: 2, sm: 0 }}
        mb={{ xs: 3, sm: 4 }}
      >
        <Typography
          variant="h4"
          fontWeight="bold"
          sx={{
            fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' }
          }}
        >
          My Leave Requests
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{
            fontSize: { xs: '0.875rem', sm: '1rem' },
            padding: { xs: '6px 12px', sm: '8px 16px' },
            alignSelf: { xs: 'flex-end', sm: 'auto' }
          }}
        >
          New Leave Request
        </Button>
      </Box>

      {/* Student Info Card */}
      {studentProfile && (
        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <SchoolIcon color="primary" fontSize="large" />
            <Box>
              <Typography variant="h6" fontWeight="bold">
                {studentProfile.first_name} {studentProfile.last_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Roll No: {studentProfile.roll_number} | Class: {studentProfile.current_class} 
                {studentProfile.section && ` - ${studentProfile.section}`}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Admission No: {studentProfile.admission_number}
              </Typography>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Leave Requests Table */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight="bold" mb={2} color="primary.main">
          Leave Request History ({leaveRequests.length})
        </Typography>
        
        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer sx={{ maxHeight: '70vh', overflow: 'auto' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Leave Type</TableCell>
                  <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Duration</TableCell>
                  <TableCell>Days</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>Submitted</TableCell>
                  <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>Reviewed By</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {leaveRequests.length > 0 ? (
                  leaveRequests.map((leave) => (
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
                        You have not submitted any leave requests yet
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
