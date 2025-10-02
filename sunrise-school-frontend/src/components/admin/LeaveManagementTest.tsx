import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';

const LeaveManagementTest: React.FC = () => {
  const { isLoaded, isLoading: configLoading, error: configError } = useServiceConfiguration('leave-management');
  const [leaveRequests, setLeaveRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  useEffect(() => {
    if (!configLoading && isLoaded) {
      loadTestData();
    }
  }, [configLoading, isLoaded]);

  const loadTestData = () => {
    try {
      setLoading(true);
      // Simulate some test data
      const testData = [
        {
          id: 1,
          applicant_name: 'John Doe',
          applicant_type: 'student',
          leave_type_name: 'Sick Leave',
          start_date: '2024-02-15',
          end_date: '2024-02-17',
          total_days: 3,
          leave_status_name: 'Pending',
          reason: 'Fever and cold'
        },
        {
          id: 2,
          applicant_name: 'Jane Smith',
          applicant_type: 'teacher',
          leave_type_name: 'Casual Leave',
          start_date: '2024-02-20',
          end_date: '2024-02-22',
          total_days: 3,
          leave_status_name: 'Approved',
          reason: 'Personal work'
        }
      ];
      
      setLeaveRequests(testData);
      setError(null);
    } catch (err: any) {
      console.error('Error loading test data:', err);
      setError('Failed to load test data');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Show loading if configuration is still loading
  if (configLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading configuration...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Leave Management Test Component
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Configuration Status
        </Typography>
        <Typography variant="body2">
          Configuration Loaded: {isLoaded ? 'Yes' : 'No'}
        </Typography>
        {configError && (
          <Typography variant="body2" color="error">
            Error: {configError}
          </Typography>
        )}
        {isLoaded && (
          <Typography variant="body2">
            Leave management configuration loaded successfully
          </Typography>
        )}
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Leave Requests Test
          </Typography>
          <Button 
            variant="contained" 
            onClick={loadTestData}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Reload Test Data'}
          </Button>
        </Box>

        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Applicant</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Leave Type</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Days</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Reason</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Array.isArray(leaveRequests) && leaveRequests.length > 0 ? (
                  leaveRequests.map((leave) => (
                    <TableRow key={leave.id}>
                      <TableCell>{String(leave.id)}</TableCell>
                      <TableCell>{String(leave.applicant_name || 'Unknown')}</TableCell>
                      <TableCell>{String(leave.applicant_type || 'Unknown')}</TableCell>
                      <TableCell>{String(leave.leave_type_name || 'Unknown')}</TableCell>
                      <TableCell>
                        {String(leave.start_date || 'N/A')} - {String(leave.end_date || 'N/A')}
                      </TableCell>
                      <TableCell>{String(leave.total_days || 0)}</TableCell>
                      <TableCell>{String(leave.leave_status_name || 'Unknown')}</TableCell>
                      <TableCell>{String(leave.reason || 'No reason provided')}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
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
      </Paper>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbar.message}
      />
    </Box>
  );
};

export default LeaveManagementTest;
