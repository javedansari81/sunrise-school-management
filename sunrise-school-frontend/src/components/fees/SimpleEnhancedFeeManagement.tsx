import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Snackbar,
  Card,
  CardContent,
  LinearProgress,
  Tooltip,
  Stack,
  Grid,
} from '@mui/material';
import {
  Search,
  Visibility,
  History,
  Settings,
  CheckCircle,
  Schedule,
  Error,
  Close as CloseIcon,
} from '@mui/icons-material';
import {
  SessionYearDropdown,
  ClassDropdown
} from '../common/MetadataDropdown';
import { useAuth } from '../../contexts/AuthContext';
import { enhancedFeesAPI } from '../../services/api';

interface EnhancedStudentFeeSummary {
  student_id: number;
  admission_number: string;
  student_name: string;
  class_name: string;
  session_year: string;
  annual_fee?: number;
  total_paid?: number;
  total_balance?: number;
  total_months_tracked: number;
  paid_months: number;
  pending_months: number;
  overdue_months: number;
  collection_percentage: number;
  has_monthly_tracking: boolean;
}

interface MonthlyFeeStatus {
  month: number;
  year: number;
  month_name: string;
  monthly_amount: number;
  paid_amount: number;
  balance_amount: number;
  due_date: string;
  status: string;
  status_color: string;
  is_overdue: boolean;
  days_overdue?: number;
  late_fee: number;
  discount_amount: number;
}

interface StudentMonthlyFeeHistory {
  student_id: number;
  student_name: string;
  class_name: string;
  session_year: string;
  total_annual_fee: number;
  monthly_history: MonthlyFeeStatus[];
  total_months: number;
  paid_months: number;
  pending_months: number;
  overdue_months: number;
  total_paid: number;
  total_balance: number;
  collection_percentage: number;
}

const SimpleEnhancedFeeManagement: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [students, setStudents] = useState<EnhancedStudentFeeSummary[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<StudentMonthlyFeeHistory | null>(null);
  const [filters, setFilters] = useState({
    session_year_id: '',
    class_id: 'all',
    search: '',
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [enableTrackingDialog, setEnableTrackingDialog] = useState(false);
  const [selectedStudentIds, setSelectedStudentIds] = useState<number[]>([]);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'warning' | 'info'
  });

  // Fetch enhanced student summary
  const fetchStudentsSummary = async () => {
    if (!filters.session_year_id) return;

    if (!isAuthenticated) {
      setSnackbar({
        open: true,
        message: 'Please login to access fee management',
        severity: 'error'
      });
      return;
    }

    setLoading(true);
    try {
      const params: any = {
        session_year_id: filters.session_year_id,
        page: 1,
        per_page: 50
      };

      if (filters.class_id && filters.class_id !== 'all') {
        params.class_id = filters.class_id;
      }

      if (filters.search) {
        params.search = filters.search;
      }

      console.log('🌐 API Params:', params);
      console.log('🔑 User authenticated:', isAuthenticated);
      console.log('👤 Current user:', user);
      console.log('🎯 Making API call to enhanced-students-summary...');

      const response = await enhancedFeesAPI.getEnhancedStudentsSummary(params);
      console.log('✅ API Response received:', {
        status: response.status,
        data: response.data,
        studentsCount: response.data?.students?.length || 0
      });

      const students = response.data.students || [];
      console.log('📊 Students data:', students);
      setStudents(students);
    } catch (error: any) {
      console.error('❌ API Error:', error);
      console.error('❌ Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      });

      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch students data';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Fetch student monthly history
  const fetchStudentMonthlyHistory = async (studentId: number) => {
    if (!filters.session_year_id) {
      setSnackbar({
        open: true,
        message: 'Please select a session year first',
        severity: 'warning'
      });
      return;
    }

    setLoading(true);
    try {
      const response = await enhancedFeesAPI.getEnhancedMonthlyHistory(
        studentId,
        parseInt(filters.session_year_id)
      );

      if (!response.data || !response.data.monthly_history || response.data.monthly_history.length === 0) {
        setSnackbar({
          open: true,
          message: 'No monthly tracking records found for this student',
          severity: 'info'
        });
        return;
      }

      setSelectedStudent(response.data);
      setDialogOpen(true);
    } catch (error: any) {
      console.error('Error fetching monthly history:', error);

      // Handle specific error cases
      if (error.response?.status === 404) {
        setSnackbar({
          open: true,
          message: 'Monthly fee history not found for this student. Please enable monthly tracking first.',
          severity: 'warning'
        });
      } else if (error.response?.status === 403) {
        setSnackbar({
          open: true,
          message: 'You do not have permission to view this student\'s fee history',
          severity: 'error'
        });
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch monthly history';
        setSnackbar({
          open: true,
          message: errorMessage,
          severity: 'error'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  // Enable monthly tracking for selected students
  const enableMonthlyTracking = async () => {
    if (selectedStudentIds.length === 0) return;

    setLoading(true);
    try {
      const feeRecordIds = students
        .filter(s => selectedStudentIds.includes(s.student_id))
        .map(s => s.student_id); // Using student_id as placeholder

      const requestData = {
        fee_record_ids: feeRecordIds,
        start_month: 4,
        start_year: new Date().getFullYear()
      };

      const response = await enhancedFeesAPI.enableMonthlyTracking(requestData);

      setSnackbar({
        open: true,
        message: response.data.message || 'Monthly tracking enabled successfully',
        severity: 'success'
      });
      setEnableTrackingDialog(false);
      setSelectedStudentIds([]);
      fetchStudentsSummary();
    } catch (error: any) {
      console.error('Error enabling monthly tracking:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to enable monthly tracking';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudentsSummary();
  }, [filters.session_year_id, filters.class_id]);

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          Please login to access the fee management system.
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

  return (
    <Box sx={{ p: 3 }}>
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <SessionYearDropdown
            value={filters.session_year_id}
            onChange={(value) => setFilters(prev => ({ ...prev, session_year_id: value as string }))}
            required
          />
          <ClassDropdown
            value={filters.class_id}
            onChange={(value) => setFilters(prev => ({ ...prev, class_id: value as string }))}
            includeAll={true}
            allLabel="ALL"
          />
          <TextField
            placeholder="Search students..."
            value={filters.search}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            InputProps={{
              startAdornment: <Search />,
            }}
            sx={{ minWidth: 200 }}
          />
          <Button
            variant="contained"
            onClick={fetchStudentsSummary}
            disabled={!filters.session_year_id}
          >
            Search
          </Button>
          {selectedStudentIds.length > 0 && (
            <Button
              variant="outlined"
              startIcon={<Settings />}
              onClick={() => setEnableTrackingDialog(true)}
            >
              Enable Monthly Tracking ({selectedStudentIds.length})
            </Button>
          )}
        </Stack>
      </Paper>

      {/* Students Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <input
                    type="checkbox"
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedStudentIds(students.map(s => s.student_id));
                      } else {
                        setSelectedStudentIds([]);
                      }
                    }}
                    checked={selectedStudentIds.length === students.length && students.length > 0}
                  />
                </TableCell>
                <TableCell>Student</TableCell>
                <TableCell>Class</TableCell>
                <TableCell>Annual Fee</TableCell>
                <TableCell>Collection %</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Monthly Tracking</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : students.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography color="textSecondary">
                      No students found. Please select a session year and try again.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                students.map((student) => (
                  <TableRow key={student.student_id}>
                    <TableCell padding="checkbox">
                      <input
                        type="checkbox"
                        checked={selectedStudentIds.includes(student.student_id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedStudentIds(prev => [...prev, student.student_id]);
                          } else {
                            setSelectedStudentIds(prev => prev.filter(id => id !== student.student_id));
                          }
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {student.student_name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {student.admission_number}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{student.class_name}</TableCell>
                    <TableCell>
                      ₹{student.annual_fee?.toLocaleString() || 0}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={student.collection_percentage}
                          sx={{ width: 60, height: 6 }}
                        />
                        <Typography variant="caption">
                          {student.collection_percentage.toFixed(1)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {student.has_monthly_tracking ? (
                        <Stack direction="row" spacing={1}>
                          <Chip
                            size="small"
                            icon={<CheckCircle />}
                            label={`${student.paid_months}P`}
                            color="success"
                            variant="outlined"
                          />
                          <Chip
                            size="small"
                            icon={<Schedule />}
                            label={`${student.pending_months}Pe`}
                            color="info"
                            variant="outlined"
                          />
                          <Chip
                            size="small"
                            icon={<Error />}
                            label={`${student.overdue_months}O`}
                            color="error"
                            variant="outlined"
                          />
                        </Stack>
                      ) : (
                        <Chip
                          size="small"
                          label={student.total_balance && student.total_balance > 0 ? 'Pending' : 'Paid'}
                          color={student.total_balance && student.total_balance > 0 ? 'warning' : 'success'}
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={student.has_monthly_tracking ? 'Enabled' : 'Disabled'}
                        color={student.has_monthly_tracking ? 'success' : 'default'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1}>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => fetchStudentMonthlyHistory(student.student_id)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Payment History">
                          <IconButton size="small">
                            <History />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Enable Monthly Tracking Dialog */}
      <Dialog
        open={enableTrackingDialog}
        onClose={() => setEnableTrackingDialog(false)}
      >
        <DialogTitle>Enable Monthly Tracking</DialogTitle>
        <DialogContent>
          <Typography>
            Enable monthly fee tracking for {selectedStudentIds.length} selected students?
            This will create month-wise fee records for better payment tracking.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEnableTrackingDialog(false)}>Cancel</Button>
          <Button
            onClick={enableMonthlyTracking}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : 'Enable Tracking'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Monthly History Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Monthly Fee History - {selectedStudent?.student_name}
            </Typography>
            <IconButton onClick={() => setDialogOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedStudent && (
            <Box>
              {/* Student Summary */}
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Typography variant="body2" color="textSecondary">Student</Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {selectedStudent.student_name}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {selectedStudent.class_name} • {selectedStudent.session_year}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Typography variant="body2" color="textSecondary">Annual Fee</Typography>
                    <Typography variant="h6" color="primary">
                      ₹{selectedStudent.total_annual_fee?.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Typography variant="body2" color="textSecondary">Total Paid</Typography>
                    <Typography variant="h6" color="success.main">
                      ₹{selectedStudent.total_paid?.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Typography variant="body2" color="textSecondary">Collection %</Typography>
                    <Typography variant="h6" color="info.main">
                      {selectedStudent.collection_percentage?.toFixed(1)}%
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>

              {/* Monthly Status Summary */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Card sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h6" color="success.main">
                      {selectedStudent.paid_months}
                    </Typography>
                    <Typography variant="caption">Paid</Typography>
                  </Card>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Card sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h6" color="warning.main">
                      {selectedStudent.pending_months}
                    </Typography>
                    <Typography variant="caption">Pending</Typography>
                  </Card>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Card sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h6" color="error.main">
                      {selectedStudent.overdue_months}
                    </Typography>
                    <Typography variant="caption">Overdue</Typography>
                  </Card>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Card sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h6" color="primary.main">
                      {selectedStudent.total_months}
                    </Typography>
                    <Typography variant="caption">Total</Typography>
                  </Card>
                </Grid>
              </Grid>

              {/* Monthly History Table */}
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Month</TableCell>
                      <TableCell>Due Date</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell align="right">Paid</TableCell>
                      <TableCell align="right">Balance</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Late Fee</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {selectedStudent.monthly_history?.map((month, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {month.month_name} {month.year}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(month.due_date).toLocaleDateString()}
                          </Typography>
                          {month.is_overdue && month.days_overdue && (
                            <Typography variant="caption" color="error">
                              {month.days_overdue} days overdue
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell align="right">
                          ₹{month.monthly_amount.toLocaleString()}
                        </TableCell>
                        <TableCell align="right">
                          <Typography
                            color={month.paid_amount > 0 ? 'success.main' : 'textSecondary'}
                          >
                            ₹{month.paid_amount.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography
                            color={month.balance_amount > 0 ? 'error.main' : 'success.main'}
                          >
                            ₹{month.balance_amount.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={month.status}
                            sx={{
                              bgcolor: month.status_color,
                              color: 'white',
                              fontWeight: 'bold'
                            }}
                          />
                        </TableCell>
                        <TableCell align="right">
                          {month.late_fee > 0 && (
                            <Typography variant="body2" color="error">
                              ₹{month.late_fee.toLocaleString()}
                            </Typography>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
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
  );
};

export default SimpleEnhancedFeeManagement;
