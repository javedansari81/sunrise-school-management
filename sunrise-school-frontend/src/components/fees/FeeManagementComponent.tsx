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
  LinearProgress,
  Tooltip,
  Stack,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  ListItemText,
  Checkbox,
  FormHelperText,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Search,
  Visibility,
  History,
  Settings,
  CheckCircle,
  Schedule,
  Close as CloseIcon,
  Payment,
  AccountBalance,
  Warning,
  Add as AddIcon,
  School as SchoolIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import {
  SessionYearDropdown,
  ClassDropdown
} from '../common/MetadataDropdown';
import { useAuth } from '../../contexts/AuthContext';
import { dialogStyles } from '../../styles/dialogTheme';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { enhancedFeesAPI } from '../../services/api';
import { configurationService } from '../../services/configurationService';
import {
  ID_TO_SESSION_YEAR_MAP,
  getCurrentSessionYearId,
  DEFAULT_SESSION_YEAR_ID,
  DEFAULT_SESSION_YEAR
} from '../../utils/sessionYearUtils';

interface EnhancedStudentFeeSummary {
  student_id: number;
  admission_number: string;
  student_name: string;
  class_name: string;
  session_year: string;
  fee_record_id?: number;  // Added missing property
  annual_fee?: number;
  total_paid?: number;
  total_balance?: number;
  total_months_tracked: number;
  paid_months: number;
  pending_months: number;
  overdue_months: number;
  monthly_total?: number;
  monthly_paid?: number;
  monthly_balance?: number;
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

interface AvailableMonth {
  month: number;
  year: number;
  month_name: string;
  monthly_amount: number;
  balance_amount: number;
  due_date: string;
  is_overdue: boolean;
  days_overdue?: number;
}

interface AvailableMonthsData {
  student: {
    id: number;
    name: string;
    admission_number: string;
    class: string;
  };
  session_year: string;
  monthly_fee: number;
  total_annual_fee: number;
  available_months: AvailableMonth[];
  paid_months: AvailableMonth[];
  summary: {
    total_months: number;
    available_months: number;
    paid_months: number;
    total_pending_amount: number;
  };
}

const FeeManagementComponent: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const { isLoaded: configLoaded } = useServiceConfiguration('fee-management');

  // Get payment methods from configuration
  const getPaymentMethods = () => {
    if (!configLoaded) return [];
    const config = configurationService.getServiceConfiguration('fee-management');
    return config?.payment_methods || [];
  };

  const [loading, setLoading] = useState(false);
  const [dialogLoading, setDialogLoading] = useState(false);
  const [paymentHistoryLoading, setPaymentHistoryLoading] = useState(false);
  const [students, setStudents] = useState<EnhancedStudentFeeSummary[]>([]);
  const [allStudents, setAllStudents] = useState<EnhancedStudentFeeSummary[]>([]); // Store all students for filtering
  const [selectedStudent, setSelectedStudent] = useState<StudentMonthlyFeeHistory | null>(null);
  const [paymentHistory, setPaymentHistory] = useState<any>(null);
  const [filters, setFilters] = useState({
    session_year_id: DEFAULT_SESSION_YEAR_ID, // Default to 2025-26
    class_id: 'all',
    search: '',
  });
  const [tabValue, setTabValue] = useState(0); // 0: All, 1: Pending, 2: Paid, 3: Statistics
  const [dialogOpen, setDialogOpen] = useState(false);
  const [paymentHistoryDialogOpen, setPaymentHistoryDialogOpen] = useState(false);
  const [enableTrackingDialog, setEnableTrackingDialog] = useState(false);
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [monthlyTrackingWarningDialog, setMonthlyTrackingWarningDialog] = useState(false);
  const [selectedStudentForWarning, setSelectedStudentForWarning] = useState<EnhancedStudentFeeSummary | null>(null);
  const [selectedStudentIds, setSelectedStudentIds] = useState<number[]>([]);
  const [availableMonthsData, setAvailableMonthsData] = useState<AvailableMonthsData | null>(null);
  const [paymentForm, setPaymentForm] = useState({
    amount: '',
    selectedMonths: [] as number[],
    paymentMethodId: 1,
    transactionId: '',
    remarks: ''
  });
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [loadingStates, setLoadingStates] = useState<{
    payment: { [studentId: number]: boolean };
    paymentHistory: { [studentId: number]: boolean };
    monthlyHistory: { [studentId: number]: boolean };
  }>({
    payment: {},
    paymentHistory: {},
    monthlyHistory: {}
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'warning' | 'info'
  });

  // Utility function to get class display name
  const getClassDisplayName = (className: string): string => {
    if (!className) return className;

    // Try to get from configuration service
    const classes = configurationService.getClasses();
    const classItem = classes.find(cls => cls.name === className);
    if (classItem && classItem.description) {
      return classItem.description;
    }

    return className;
  };

  // Filter students based on tab selection
  const filterStudentsByTab = (students: EnhancedStudentFeeSummary[], tab: number) => {
    switch (tab) {
      case 0: // All Students
        return students;
      case 1: // Pending Payments
        return students.filter(s =>
          s.has_monthly_tracking &&
          (s.pending_months > 0 || s.overdue_months > 0)
        );
      case 2: // Paid in Full
        return students.filter(s =>
          s.has_monthly_tracking &&
          s.pending_months === 0 &&
          s.overdue_months === 0 &&
          s.paid_months > 0
        );
      case 3: // Statistics (show all for now)
        return students;
      default:
        return students;
    }
  };

  // Apply filters and tab selection
  useEffect(() => {
    const filtered = filterStudentsByTab(allStudents, tabValue);
    setStudents(filtered);
  }, [tabValue, allStudents]);

  // Real-time search with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      if (filters.session_year_id) {
        fetchStudentsSummary();
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [filters.search, filters.class_id]);

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
      console.log('📊 Students with tracking info:', students.map((s: EnhancedStudentFeeSummary) => ({
        id: s.student_id,
        name: s.student_name,
        has_monthly_tracking: s.has_monthly_tracking,
        fee_record_id: s.fee_record_id
      })));
      setAllStudents(students); // Store all students
      setStudents(students); // Display all initially
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

    // Check if monthly tracking is enabled
    const student = students.find(s => s.student_id === studentId);
    if (student && !checkMonthlyTrackingEnabled(student)) {
      return;
    }

    // Set loading state for this specific student
    setLoadingStates(prev => ({
      ...prev,
      monthlyHistory: { ...prev.monthlyHistory, [studentId]: true }
    }));
    setDialogLoading(true);
    try {
      // Add cache busting to ensure fresh data
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
      setDialogLoading(false);
      // Clear loading state for this specific student
      setLoadingStates(prev => ({
        ...prev,
        monthlyHistory: { ...prev.monthlyHistory, [studentId]: false }
      }));
    }
  };

  // Check if monthly tracking is enabled for a student
  const checkMonthlyTrackingEnabled = (student: EnhancedStudentFeeSummary): boolean => {
    if (!student.has_monthly_tracking) {
      setSelectedStudentForWarning(student);
      setMonthlyTrackingWarningDialog(true);
      return false;
    }
    return true;
  };

  // Handle enabling monthly tracking from warning dialog
  const handleEnableTrackingFromWarning = () => {
    if (selectedStudentForWarning) {
      setMonthlyTrackingWarningDialog(false);
      setSelectedStudentIds([selectedStudentForWarning.student_id]);
      setEnableTrackingDialog(true);
    }
  };

  // Fetch payment history for a student
  const fetchPaymentHistory = async (studentId: number) => {
    if (!filters.session_year_id) {
      setSnackbar({
        open: true,
        message: 'Please select a session year first',
        severity: 'warning'
      });
      return;
    }

    // Check if monthly tracking is enabled
    const student = students.find(s => s.student_id === studentId);
    if (student && !checkMonthlyTrackingEnabled(student)) {
      return;
    }

    // Set loading state for this specific student
    setLoadingStates(prev => ({
      ...prev,
      paymentHistory: { ...prev.paymentHistory, [studentId]: true }
    }));
    setPaymentHistoryLoading(true);
    try {
      // Convert session_year_id to session year string
      const sessionYear = ID_TO_SESSION_YEAR_MAP[filters.session_year_id] || DEFAULT_SESSION_YEAR;

      const response = await enhancedFeesAPI.getPaymentHistory(studentId, sessionYear);

      if (!response.data) {
        setSnackbar({
          open: true,
          message: 'No payment history found for this student',
          severity: 'info'
        });
        return;
      }

      setPaymentHistory(response.data);
      setPaymentHistoryDialogOpen(true);
    } catch (error: any) {
      console.error('Error fetching payment history:', error);

      if (error.response?.status === 404) {
        setSnackbar({
          open: true,
          message: 'Payment history not found for this student',
          severity: 'warning'
        });
      } else if (error.response?.status === 403) {
        setSnackbar({
          open: true,
          message: 'You do not have permission to view this student\'s payment history',
          severity: 'error'
        });
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch payment history';
        setSnackbar({
          open: true,
          message: errorMessage,
          severity: 'error'
        });
      }
    } finally {
      setPaymentHistoryLoading(false);
      // Clear loading state for this specific student
      setLoadingStates(prev => ({
        ...prev,
        paymentHistory: { ...prev.paymentHistory, [studentId]: false }
      }));
    }
  };

  // Fetch available months for payment
  const fetchAvailableMonths = async (studentId: number) => {
    if (!filters.session_year_id) {
      setSnackbar({
        open: true,
        message: 'Please select a session year first',
        severity: 'warning'
      });
      return;
    }

    // Check if monthly tracking is enabled
    const student = students.find(s => s.student_id === studentId);
    if (student && !checkMonthlyTrackingEnabled(student)) {
      return;
    }

    // Set loading state for this specific student
    setLoadingStates(prev => ({
      ...prev,
      payment: { ...prev.payment, [studentId]: true }
    }));
    setPaymentLoading(true);
    try {
      // Convert session_year_id to session year string
      const sessionYear = ID_TO_SESSION_YEAR_MAP[filters.session_year_id] || DEFAULT_SESSION_YEAR;
      const response = await enhancedFeesAPI.getAvailableMonths(studentId, sessionYear);

      if (!response.data || !response.data.available_months) {
        setSnackbar({
          open: true,
          message: 'No available months found for payment',
          severity: 'info'
        });
        return;
      }

      setAvailableMonthsData(response.data);
      setPaymentForm({
        amount: '',
        selectedMonths: [],
        paymentMethodId: 1,
        transactionId: '',
        remarks: ''
      });
      setPaymentDialogOpen(true);
    } catch (error: any) {
      console.error('Error fetching available months:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch available months';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setPaymentLoading(false);
      // Clear loading state for this specific student
      setLoadingStates(prev => ({
        ...prev,
        payment: { ...prev.payment, [studentId]: false }
      }));
    }
  };

  // Make enhanced payment
  const makePayment = async () => {
    if (!availableMonthsData || paymentForm.selectedMonths.length === 0 || !paymentForm.amount) {
      setSnackbar({
        open: true,
        message: 'Please select months and enter payment amount',
        severity: 'warning'
      });
      return;
    }

    // Check if transaction ID is required for selected payment method
    const selectedMethod = getPaymentMethods().find(m => m.id === paymentForm.paymentMethodId);
    if (selectedMethod?.requires_reference && !paymentForm.transactionId.trim()) {
      setSnackbar({
        open: true,
        message: `Transaction ID is required for ${selectedMethod.description}`,
        severity: 'warning'
      });
      return;
    }

    setPaymentLoading(true);
    try {
      const sessionYear = ID_TO_SESSION_YEAR_MAP[filters.session_year_id] || DEFAULT_SESSION_YEAR;

      const paymentData = {
        amount: parseFloat(paymentForm.amount),
        payment_method_id: paymentForm.paymentMethodId,
        selected_months: paymentForm.selectedMonths,
        session_year: sessionYear,
        transaction_id: paymentForm.transactionId || `TXN${Date.now()}`,
        remarks: paymentForm.remarks || 'Monthly fee payment'
      };

      const response = await enhancedFeesAPI.makeEnhancedPayment(availableMonthsData.student.id, paymentData);

      setSnackbar({
        open: true,
        message: response.data.message || 'Payment processed successfully',
        severity: 'success'
      });
      setPaymentDialogOpen(false);
      fetchStudentsSummary(); // Refresh the data
    } catch (error: any) {
      console.error('Error making payment:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to process payment';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setPaymentLoading(false);
      // Clear loading state for this specific student
      if (availableMonthsData) {
        setLoadingStates(prev => ({
          ...prev,
          payment: { ...prev.payment, [availableMonthsData.student.id]: false }
        }));
      }
    }
  };

  // Enable monthly tracking for selected students
  const enableMonthlyTracking = async () => {
    if (selectedStudentIds.length === 0) return;

    setLoading(true);
    try {
      // Pass student_ids directly (the API now handles fee record creation)
      const requestData = {
        fee_record_ids: selectedStudentIds, // These are actually student_ids
        start_month: 4,
        start_year: new Date().getFullYear()
      };

      console.log('🚀 Enabling monthly tracking for students:', {
        selectedStudentIds,
        requestData
      });

      const response = await enhancedFeesAPI.enableMonthlyTracking(requestData);

      console.log('✅ Monthly tracking response:', response.data);

      // Show detailed success message
      const { message, fee_records_created, results } = response.data;
      const failedStudents = results.filter((r: any) => !r.success);

      let successMessage = message;
      if (fee_records_created > 0) {
        successMessage += ` (${fee_records_created} fee records created automatically)`;
      }

      setSnackbar({
        open: true,
        message: successMessage,
        severity: failedStudents.length > 0 ? 'warning' : 'success'
      });

      // Log any failures
      if (failedStudents.length > 0) {
        console.warn('Some students failed:', failedStudents);
      }

      setEnableTrackingDialog(false);
      setSelectedStudentIds([]);
      fetchStudentsSummary(); // Refresh to show updated status
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

  // Set default session year when configuration is loaded
  useEffect(() => {
    if (configLoaded && !filters.session_year_id) {
      // Get current session year from configuration
      const currentSessionYear = configurationService.getCurrentSessionYear();
      if (currentSessionYear) {
        setFilters(prev => ({ ...prev, session_year_id: currentSessionYear.id.toString() }));
      } else {
        // Fallback: Use calculated current session year ID
        const defaultSessionYearId = getCurrentSessionYearId() || DEFAULT_SESSION_YEAR_ID;
        setFilters(prev => ({ ...prev, session_year_id: defaultSessionYearId }));
      }
    }
  }, [configLoaded, filters.session_year_id]);

  useEffect(() => {
    fetchStudentsSummary();
  }, [filters.session_year_id, filters.class_id]); // eslint-disable-line react-hooks/exhaustive-deps

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
    <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
      {/* Action Button - Positioned above filters */}
      <Box
        display="flex"
        justifyContent="flex-end"
        alignItems="center"
        mb={{ xs: 2, sm: 3 }}
      >
        {selectedStudentIds.length > 0 && (
          <Button
            variant="outlined"
            startIcon={<Settings />}
            onClick={() => {
              console.log('🔍 Enable Monthly Tracking Button Clicked:', {
                selectedStudentIds: selectedStudentIds,
                totalStudents: students.length,
              });
              setEnableTrackingDialog(true);
            }}
            sx={{
              fontSize: { xs: '0.875rem', sm: '1rem' },
              padding: { xs: '6px 12px', sm: '8px 16px' },
            }}
          >
            Enable Monthly Tracking ({selectedStudentIds.length})
          </Button>
        )}
      </Box>

      {/* Filters - Mobile Responsive */}
      <Paper sx={{ p: { xs: 1.5, sm: 2 }, mb: { xs: 2, sm: 3 } }}>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={{ xs: 1.5, sm: 2 }}
          alignItems={{ xs: 'stretch', sm: 'center' }}
        >
          <SessionYearDropdown
            value={filters.session_year_id}
            onChange={(value) => {
              setFilters(prev => ({ ...prev, session_year_id: value as string }));
              // Auto-fetch when session year changes
              setTimeout(() => fetchStudentsSummary(), 100);
            }}
            required
          />
          <ClassDropdown
            value={filters.class_id}
            onChange={(value) => setFilters(prev => ({ ...prev, class_id: value as string }))}
            includeAll={true}
            allLabel="ALL"
          />
          <TextField
            placeholder="Search by name or admission number..."
            value={filters.search}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            slotProps={{
              input: {
                startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />,
              }
            }}
            sx={{
              minWidth: { xs: '100%', sm: 250 },
              '& .MuiInputBase-input': {
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }
            }}
          />
        </Stack>
      </Paper>

      {/* Tabs for filtering */}
      <Paper sx={{ mb: { xs: 2, sm: 3 } }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 500,
              fontSize: { xs: '0.875rem', sm: '1rem' },
              minHeight: { xs: 48, sm: 56 },
            }
          }}
        >
          <Tab
            label="All Students"
            icon={<SchoolIcon />}
            iconPosition="start"
          />
          <Tab
            label="Pending Payments"
            icon={<Schedule />}
            iconPosition="start"
          />
          <Tab
            label="Paid in Full"
            icon={<CheckCircle />}
            iconPosition="start"
          />
          <Tab
            label="Statistics"
            icon={<AssessmentIcon />}
            iconPosition="start"
          />
        </Tabs>
      </Paper>



      {/* Statistics Tab Content */}
      {tabValue === 3 ? (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            Fee Collection Statistics
          </Typography>
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ p: 2.5, textAlign: 'center', border: '1px solid #e0e0e0' }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Total Students
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="primary.main">
                  {allStudents.length}
                </Typography>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ p: 2.5, textAlign: 'center', border: '1px solid #e0e0e0' }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  With Tracking Enabled
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {allStudents.filter(s => s.has_monthly_tracking).length}
                </Typography>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ p: 2.5, textAlign: 'center', border: '1px solid #e0e0e0' }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Pending Payments
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="warning.main">
                  {filterStudentsByTab(allStudents, 1).length}
                </Typography>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ p: 2.5, textAlign: 'center', border: '1px solid #e0e0e0' }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Paid in Full
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {filterStudentsByTab(allStudents, 2).length}
                </Typography>
              </Card>
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Card sx={{ p: 3, border: '1px solid #e0e0e0' }}>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Collection Overview
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Average Collection Rate
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={
                        allStudents.length > 0
                          ? allStudents.reduce((sum, s) => sum + s.collection_percentage, 0) / allStudents.length
                          : 0
                      }
                      sx={{
                        flexGrow: 1,
                        height: 12,
                        borderRadius: 2,
                        bgcolor: 'grey.200',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: 'primary.main',
                          borderRadius: 2
                        }
                      }}
                    />
                    <Typography variant="h6" fontWeight="bold" color="primary.main">
                      {allStudents.length > 0
                        ? (allStudents.reduce((sum, s) => sum + s.collection_percentage, 0) / allStudents.length).toFixed(1)
                        : 0}%
                    </Typography>
                  </Box>
                </Box>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      ) : (
        /* Students Table - Mobile Responsive */
        <Paper sx={{ overflow: 'hidden' }}>
        <TableContainer sx={{
          maxHeight: { xs: '70vh', sm: '80vh' },
          '& .MuiTable-root': {
            minWidth: { xs: 'auto', sm: 650 }
          }
        }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{
                bgcolor: 'white',
                borderBottom: '2px solid',
                borderColor: 'divider',
                '& .MuiTableCell-head': {
                  color: 'text.primary',
                  fontWeight: 'bold',
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  py: 2
                }
              }}>
                <TableCell
                  padding="checkbox"
                  sx={{
                    minWidth: { xs: 'auto', sm: 48 }
                  }}
                >
                  <Checkbox
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedStudentIds(students.map(s => s.student_id));
                      } else {
                        setSelectedStudentIds([]);
                      }
                    }}
                    checked={selectedStudentIds.length === students.length && students.length > 0}
                    sx={{
                      padding: { xs: 0.75, sm: 0.5 },
                      '& .MuiSvgIcon-root': {
                        fontSize: { xs: '1.5rem', sm: '1.25rem' }
                      }
                    }}
                  />
                </TableCell>
                <TableCell>Student</TableCell>
                <TableCell>Class</TableCell>
                <TableCell>Annual Fee</TableCell>
                <TableCell>Collection %</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Tracking</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 8 }}>
                    <CircularProgress size={48} />
                    <Typography variant="body1" sx={{ mt: 2, color: 'text.secondary' }}>
                      Loading students...
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : students.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Box sx={{ py: 8, textAlign: 'center' }}>
                      <SchoolIcon sx={{ fontSize: 64, color: 'grey.300', mb: 2 }} />
                      <Typography variant="h6" color="textSecondary" gutterBottom>
                        No Students Found
                      </Typography>
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                        {filters.search
                          ? 'Try adjusting your search criteria'
                          : 'Select a session year and class to view fee records'
                        }
                      </Typography>
                      {filters.search && (
                        <Button
                          variant="outlined"
                          onClick={() => setFilters(prev => ({ ...prev, search: '' }))}
                        >
                          Clear Search
                        </Button>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                students.map((student) => (
                  <TableRow
                    key={student.student_id}
                    sx={{
                      '&:hover': { bgcolor: 'action.hover' },
                      transition: 'background-color 0.2s'
                    }}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedStudentIds.includes(student.student_id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedStudentIds(prev => [...prev, student.student_id]);
                          } else {
                            setSelectedStudentIds(prev => prev.filter(id => id !== student.student_id));
                          }
                        }}
                        sx={{
                          padding: { xs: 0.75, sm: 0.5 },
                          '& .MuiSvgIcon-root': {
                            fontSize: { xs: '1.5rem', sm: '1.25rem' }
                          }
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold" color="primary.main">
                          {student.student_name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Roll: {student.admission_number}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {getClassDisplayName(student.class_name)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        ₹{student.annual_fee?.toLocaleString() || 0}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ minWidth: 100 }}>
                        <LinearProgress
                          variant="determinate"
                          value={student.collection_percentage}
                          sx={{
                            height: 8,
                            borderRadius: 1,
                            bgcolor: 'grey.200',
                            mb: 0.5,
                            '& .MuiLinearProgress-bar': {
                              bgcolor: student.collection_percentage < 50 ? 'error.main' :
                                       student.collection_percentage < 80 ? 'warning.main' : 'success.main',
                              borderRadius: 1
                            }
                          }}
                        />
                        <Typography variant="caption" fontWeight="bold">
                          {student.collection_percentage.toFixed(0)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {student.has_monthly_tracking ? (
                        <Tooltip title={`${student.paid_months} Paid, ${student.pending_months} Pending, ${student.overdue_months} Overdue`}>
                          <Stack direction="row" spacing={0.5}>
                            <Chip
                              size="small"
                              label={`${student.paid_months}P`}
                              color="success"
                              sx={{
                                minWidth: 45,
                                height: 24,
                                fontSize: '0.75rem',
                                fontWeight: 'bold'
                              }}
                            />
                            <Chip
                              size="small"
                              label={`${student.pending_months}Pe`}
                              color="info"
                              sx={{
                                minWidth: 45,
                                height: 24,
                                fontSize: '0.75rem',
                                fontWeight: 'bold'
                              }}
                            />
                            <Chip
                              size="small"
                              label={`${student.overdue_months}O`}
                              color="error"
                              sx={{
                                minWidth: 45,
                                height: 24,
                                fontSize: '0.75rem',
                                fontWeight: 'bold'
                              }}
                            />
                          </Stack>
                        </Tooltip>
                      ) : (
                        <Chip
                          size="small"
                          label={
                            (student.total_paid && student.total_paid > 0 &&
                             (!student.total_balance || student.total_balance === 0) &&
                             student.annual_fee && student.annual_fee > 0)
                              ? 'Paid'
                              : 'Pending'
                          }
                          color={
                            (student.total_paid && student.total_paid > 0 &&
                             (!student.total_balance || student.total_balance === 0) &&
                             student.annual_fee && student.annual_fee > 0)
                              ? 'success'
                              : 'warning'
                          }
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
                        <Tooltip title="Make Payment">
                          <span>
                            <IconButton
                              size="small"
                              onClick={() => fetchAvailableMonths(student.student_id)}
                              disabled={!student.has_monthly_tracking || loadingStates.payment[student.student_id] || paymentLoading}
                              color="primary"
                              sx={{
                                opacity: (!student.has_monthly_tracking || loadingStates.payment[student.student_id]) ? 0.4 : 1,
                                '&.Mui-disabled': {
                                  opacity: loadingStates.payment[student.student_id] ? 0.6 : 0.3
                                }
                              }}
                            >
                              {loadingStates.payment[student.student_id] ? (
                                <CircularProgress size={16} />
                              ) : (
                                <Payment />
                              )}
                            </IconButton>
                          </span>
                        </Tooltip>
                        <Tooltip title="View Monthly Details">
                          <span>
                            <IconButton
                              size="small"
                              onClick={() => fetchStudentMonthlyHistory(student.student_id)}
                              disabled={!student.has_monthly_tracking || loadingStates.monthlyHistory[student.student_id]}
                              color="default"
                              sx={{
                                opacity: (!student.has_monthly_tracking || loadingStates.monthlyHistory[student.student_id]) ? 0.4 : 1,
                                '&.Mui-disabled': {
                                  opacity: loadingStates.monthlyHistory[student.student_id] ? 0.6 : 0.3
                                }
                              }}
                            >
                              {loadingStates.monthlyHistory[student.student_id] ? (
                                <CircularProgress size={16} />
                              ) : (
                                <Visibility />
                              )}
                            </IconButton>
                          </span>
                        </Tooltip>
                        <Tooltip title="Payment History">
                          <span>
                            <IconButton
                              size="small"
                              onClick={() => fetchPaymentHistory(student.student_id)}
                              disabled={!student.has_monthly_tracking || loadingStates.paymentHistory[student.student_id] || paymentHistoryLoading}
                              color="default"
                              sx={{
                                opacity: (!student.has_monthly_tracking || loadingStates.paymentHistory[student.student_id]) ? 0.4 : 1,
                                '&.Mui-disabled': {
                                  opacity: loadingStates.paymentHistory[student.student_id] ? 0.6 : 0.3
                                }
                              }}
                            >
                              {loadingStates.paymentHistory[student.student_id] ? (
                                <CircularProgress size={16} />
                              ) : (
                                <History />
                              )}
                            </IconButton>
                          </span>
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
      )}

      {/* Enable Monthly Tracking Dialog */}
      <Dialog
        open={enableTrackingDialog}
        onClose={() => setEnableTrackingDialog(false)}
        maxWidth="sm"
        fullWidth
        slotProps={{
          paper: {
            sx: dialogStyles.paper
          }
        }}
      >
        <DialogTitle sx={dialogStyles.title}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Settings sx={{ fontSize: 28 }} />
            <Typography sx={dialogStyles.titleText}>Enable Monthly Tracking</Typography>
          </Box>
          <IconButton
            onClick={() => setEnableTrackingDialog(false)}
            sx={dialogStyles.closeButton}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={dialogStyles.content}>
          <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
            Enable monthly fee tracking for <strong>{selectedStudentIds.length}</strong> selected students?
            This will create month-wise fee records for better payment tracking.
          </Typography>
        </DialogContent>
        <DialogActions sx={dialogStyles.actions}>
          <Button
            onClick={() => setEnableTrackingDialog(false)}
            variant="outlined"
            sx={dialogStyles.secondaryButton}
          >
            Cancel
          </Button>
          <Button
            onClick={enableMonthlyTracking}
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <Settings />}
            sx={dialogStyles.primaryButton}
          >
            {loading ? 'Enabling...' : 'Enable Tracking'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Monthly History Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
        slotProps={{
          paper: {
            sx: dialogStyles.paper
          }
        }}
      >
        <DialogTitle sx={dialogStyles.title}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <History sx={{ fontSize: 28 }} />
            <Box>
              <Typography sx={dialogStyles.titleText}>
                Monthly Fee History
              </Typography>
              <Typography
                variant="subtitle2"
                sx={{
                  opacity: 0.9,
                  fontSize: { xs: '0.875rem', sm: '1rem' }
                }}
              >
                {selectedStudent?.student_name} • {getClassDisplayName(selectedStudent?.class_name || '')}
              </Typography>
            </Box>
          </Box>
          <IconButton
            onClick={() => setDialogOpen(false)}
            sx={dialogStyles.closeButton}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ ...dialogStyles.content, p: 0 }}>
          {dialogLoading ? (
            <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="300px">
              <CircularProgress size={48} />
              <Typography variant="body1" sx={{ mt: 2, color: 'text.secondary' }}>
                Loading student fee history...
              </Typography>
            </Box>
          ) : selectedStudent && (
            <Box>
              {/* Monthly History Table */}
              <Box sx={{ p: { xs: 2, sm: 3 } }}>
                <Typography
                  variant="h6"
                  gutterBottom
                  sx={{
                    mb: 2,
                    fontWeight: 'bold',
                    fontSize: { xs: '1rem', sm: '1.25rem' }
                  }}
                >
                  Monthly Payment History
                </Typography>
                <TableContainer component={Paper} sx={{
                  borderRadius: 2,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  border: '1px solid #e0e0e0'
                }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ bgcolor: 'grey.100' }}>
                        <TableCell sx={{ fontWeight: 'bold', fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>Month</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 'bold', fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>Amount</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 'bold', fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>Paid</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 'bold', fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>Balance</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>Status</TableCell>
                      </TableRow>
                    </TableHead>
                  <TableBody>
                    {selectedStudent.monthly_history?.map((month, index) => (
                      <TableRow
                        key={index}
                        sx={{
                          '&:nth-of-type(odd)': { bgcolor: 'grey.25' },
                          '&:hover': { bgcolor: 'grey.100' },
                          transition: 'background-color 0.2s'
                        }}
                      >
                        <TableCell>
                          <Typography
                            variant="body2"
                            fontWeight="bold"
                            color="primary.main"
                            sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                          >
                            {month.month_name} {month.year}
                          </Typography>
                          {month.is_overdue && month.days_overdue && (
                            <Typography variant="caption" color="error" sx={{ display: 'block', mt: 0.5 }}>
                              {month.days_overdue} days overdue
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell align="right">
                          <Typography
                            variant="body2"
                            fontWeight="medium"
                            sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                          >
                            ₹{month.monthly_amount.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography
                            variant="body2"
                            fontWeight="medium"
                            color={month.paid_amount > 0 ? 'success.main' : 'textSecondary'}
                            sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                          >
                            ₹{month.paid_amount.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography
                            variant="body2"
                            fontWeight="medium"
                            color={month.balance_amount > 0 ? 'error.main' : 'success.main'}
                            sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                          >
                            ₹{month.balance_amount.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip
                              size="small"
                              label={month.status}
                              sx={{
                                bgcolor: month.status_color,
                                color: 'white',
                                fontWeight: 'bold',
                                borderRadius: 1.5,
                                fontSize: { xs: '0.65rem', sm: '0.75rem' },
                                height: { xs: 20, sm: 24 }
                              }}
                            />
                            {month.paid_amount > month.monthly_amount && (
                              <Tooltip title={`Issue: Paid amount (₹${month.paid_amount}) exceeds monthly amount (₹${month.monthly_amount})`}>
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => {
                                    alert(`⚠️ Payment Issue Detected!\n\nMonth: ${month.month_name} ${month.year}\nMonthly Amount: ₹${month.monthly_amount}\nPaid Amount: ₹${month.paid_amount}\nOverpayment: ₹${month.paid_amount - month.monthly_amount}\n\nThis issue has been automatically fixed in the backend. Please refresh the data.`);
                                  }}
                                >
                                  <Warning fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={dialogStyles.actions}>
          <Button
            onClick={() => setDialogOpen(false)}
            variant="contained"
            sx={dialogStyles.primaryButton}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Payment History Dialog */}
      <Dialog
        open={paymentHistoryDialogOpen}
        onClose={() => setPaymentHistoryDialogOpen(false)}
        maxWidth="md"
        fullWidth
        slotProps={{
          paper: {
            sx: dialogStyles.paper
          }
        }}
      >
        <DialogTitle sx={dialogStyles.title}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Payment sx={{ fontSize: 28 }} />
            <Box>
              <Typography sx={dialogStyles.titleText}>
                Payment History
              </Typography>
              <Typography
                variant="subtitle2"
                sx={{
                  opacity: 0.9,
                  fontSize: { xs: '0.875rem', sm: '1rem' }
                }}
              >
                {paymentHistory?.student_name} • {getClassDisplayName(paymentHistory?.class || '')} • {paymentHistory?.session_year}
              </Typography>
            </Box>
          </Box>
          <IconButton
            onClick={() => setPaymentHistoryDialogOpen(false)}
            sx={dialogStyles.closeButton}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ ...dialogStyles.content, p: 0 }}>
          {paymentHistoryLoading ? (
            <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="300px">
              <CircularProgress size={48} />
              <Typography variant="body1" sx={{ mt: 2, color: 'text.secondary' }}>
                Loading payment history...
              </Typography>
            </Box>
          ) : paymentHistory && (
            <Box>
              {/* Payment Summary Cards */}
              <Box sx={{ p: 3, bgcolor: 'grey.50', borderBottom: '1px solid #e0e0e0' }}>
                <Grid container spacing={3}>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Card sx={{
                      p: 2.5,
                      textAlign: 'center',
                      border: '1px solid #e0e0e0',
                      borderRadius: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      '&:hover': { boxShadow: '0 4px 16px rgba(0,0,0,0.15)' }
                    }}>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Total Amount
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="primary.main">
                        ₹{paymentHistory.summary?.total_amount?.toLocaleString() || 0}
                      </Typography>
                    </Card>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Card sx={{
                      p: 2.5,
                      textAlign: 'center',
                      border: '1px solid #e0e0e0',
                      borderRadius: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      '&:hover': { boxShadow: '0 4px 16px rgba(0,0,0,0.15)' }
                    }}>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Total Paid Amount
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="success.main">
                        ₹{paymentHistory.summary?.total_paid?.toLocaleString() || 0}
                      </Typography>
                    </Card>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Card sx={{
                      p: 2.5,
                      textAlign: 'center',
                      border: '1px solid #e0e0e0',
                      borderRadius: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      '&:hover': { boxShadow: '0 4px 16px rgba(0,0,0,0.15)' }
                    }}>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Balance
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="error.main">
                        ₹{((paymentHistory.summary?.total_amount || 0) - (paymentHistory.summary?.total_paid || 0)).toLocaleString()}
                      </Typography>
                    </Card>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Card sx={{
                      p: 2.5,
                      textAlign: 'center',
                      border: '1px solid #e0e0e0',
                      borderRadius: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      '&:hover': { boxShadow: '0 4px 16px rgba(0,0,0,0.15)' }
                    }}>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        No of Payments
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="info.main">
                        {paymentHistory.summary?.total_payments || 0}
                      </Typography>
                    </Card>
                  </Grid>
                </Grid>
              </Box>

              {/* Payment History Table */}
              <Box sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ mb: 2, fontWeight: 'bold' }}>
                  All Payments
                </Typography>
                <TableContainer component={Paper} sx={{
                  borderRadius: 2,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  border: '1px solid #e0e0e0'
                }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ bgcolor: 'grey.100' }}>
                        <TableCell sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>Payment Date</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>Paid Amount</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>Payment Method</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>Transaction ID</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {(() => {
                        // Flatten all payments from all records
                        const allPayments: any[] = [];
                        paymentHistory.payment_history?.forEach((record: any) => {
                          record.payments?.forEach((payment: any) => {
                            allPayments.push(payment);
                          });
                        });

                        // Sort payments by date (newest first)
                        allPayments.sort((a, b) => new Date(b.payment_date).getTime() - new Date(a.payment_date).getTime());

                        return allPayments.map((payment: any, index: number) => (
                          <TableRow
                            key={index}
                            sx={{
                              '&:nth-of-type(odd)': { bgcolor: 'grey.25' },
                              '&:hover': { bgcolor: 'grey.100' },
                              transition: 'background-color 0.2s'
                            }}
                          >
                            <TableCell>
                              <Typography variant="body2" fontWeight="medium">
                                {new Date(payment.payment_date).toLocaleDateString()}
                              </Typography>
                            </TableCell>
                            <TableCell align="right">
                              <Typography
                                variant="body2"
                                fontWeight="bold"
                                color="success.main"
                              >
                                ₹{payment.amount?.toLocaleString() || 0}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                size="small"
                                label={payment.payment_method || 'Unknown'}
                                color="primary"
                                variant="outlined"
                                sx={{
                                  borderRadius: 1.5,
                                  fontSize: '0.75rem',
                                  fontWeight: 'medium'
                                }}
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" color="textSecondary">
                                {payment.transaction_id || 'N/A'}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ));
                      })()}
                      {(!paymentHistory.payment_history || paymentHistory.payment_history.length === 0) && (
                        <TableRow>
                          <TableCell colSpan={4} align="center">
                            <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                              No payments found
                            </Typography>
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={dialogStyles.actions}>
          <Button
            onClick={() => setPaymentHistoryDialogOpen(false)}
            variant="contained"
            sx={dialogStyles.primaryButton}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Enhanced Payment Dialog */}
      <Dialog
        open={paymentDialogOpen}
        onClose={() => setPaymentDialogOpen(false)}
        maxWidth="md"
        fullWidth
        slotProps={{
          paper: {
            sx: dialogStyles.paper
          }
        }}
      >
        <DialogTitle sx={dialogStyles.title}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AccountBalance sx={{ fontSize: 28 }} />
            <Box>
              <Typography sx={dialogStyles.titleText}>
                Make Payment
              </Typography>
              <Typography
                variant="subtitle2"
                sx={{
                  opacity: 0.9,
                  fontSize: { xs: '0.875rem', sm: '1rem' }
                }}
              >
                {availableMonthsData?.student.name} • {getClassDisplayName(availableMonthsData?.student.class || '')}
              </Typography>
            </Box>
          </Box>
          <IconButton
            onClick={() => setPaymentDialogOpen(false)}
            sx={dialogStyles.closeButton}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={dialogStyles.content}>
          {paymentLoading ? (
            <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="200px">
              <CircularProgress size={48} />
              <Typography variant="body1" sx={{ mt: 2, color: 'text.secondary' }}>
                Loading payment options...
              </Typography>
            </Box>
          ) : availableMonthsData && (
            <Box>
              {/* Payment Summary */}
              <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                <Grid container spacing={2}>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Typography variant="caption" color="textSecondary">Monthly Fee</Typography>
                    <Typography variant="h6" fontWeight="bold" color="primary.main">
                      ₹{availableMonthsData.monthly_fee.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Typography variant="caption" color="textSecondary">Available Months</Typography>
                    <Typography variant="h6" fontWeight="bold" color="info.main">
                      {availableMonthsData.summary.available_months}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Typography variant="caption" color="textSecondary">Total Pending</Typography>
                    <Typography variant="h6" fontWeight="bold" color="error.main">
                      ₹{availableMonthsData.summary.total_pending_amount.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Typography variant="caption" color="textSecondary">Session Year</Typography>
                    <Typography variant="h6" fontWeight="bold" color="secondary.main">
                      {availableMonthsData.session_year}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>

              {/* Available Months Selection */}
              <Box sx={{ mb: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>Select Months to Pay</InputLabel>
                  <Select
                    multiple
                    value={paymentForm.selectedMonths}
                    onChange={(event) => {
                      const value = event.target.value;
                      setPaymentForm(prev => ({
                        ...prev,
                        selectedMonths: typeof value === 'string' ? value.split(',').map(Number) : value
                      }));
                    }}
                    input={<OutlinedInput label="Select Months to Pay" />}
                    renderValue={(selected) => {
                      const selectedMonths = availableMonthsData.available_months.filter(month =>
                        selected.includes(month.month)
                      );
                      return selectedMonths.map(month =>
                        `${month.month_name} ${month.year}`
                      ).join(', ');
                    }}
                    MenuProps={{
                      PaperProps: {
                        style: {
                          maxHeight: 224,
                          width: 250,
                        },
                      },
                    }}
                  >
                    {availableMonthsData.available_months.map((month) => (
                      <MenuItem key={month.month} value={month.month}>
                        <Checkbox checked={paymentForm.selectedMonths.includes(month.month)} />
                        <ListItemText
                          primary={`${month.month_name} ${month.year}`}
                          secondary={`₹${month.balance_amount.toLocaleString()}`}
                        />
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                {paymentForm.selectedMonths.length > 0 && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      💡 <strong>Smart Distribution:</strong> Payments are automatically distributed
                      across months. Example: ₹1000 for ₹840/month = ₹840 (Month 1) + ₹160 (Month 2)
                    </Typography>
                  </Alert>
                )}
              </Box>

              {/* Payment Form */}
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Payment Amount"
                    type="number"
                    value={paymentForm.amount}
                    onChange={(e) => setPaymentForm(prev => ({ ...prev, amount: e.target.value }))}
                    slotProps={{
                      input: {
                        startAdornment: <Typography sx={{ mr: 1 }}>₹</Typography>,
                      }
                    }}
                    helperText="Amount will be automatically distributed across selected months"
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <FormControl fullWidth>
                    <InputLabel>Payment Method</InputLabel>
                    <Select
                      value={paymentForm.paymentMethodId}
                      onChange={(e) => setPaymentForm(prev => ({ ...prev, paymentMethodId: e.target.value as number }))}
                      label="Payment Method"
                      disabled={!configLoaded}
                    >
                      {getPaymentMethods().length > 0 ? (
                        getPaymentMethods().map((method: any) => (
                          <MenuItem key={method.id} value={method.id}>
                            {method.description}
                          </MenuItem>
                        ))
                      ) : (
                        <MenuItem value={1}>Cash Payment</MenuItem>
                      )}
                    </Select>
                    <FormHelperText>
                      {configLoaded ? 'Select payment method' : 'Loading payment methods...'}
                    </FormHelperText>
                  </FormControl>
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Transaction ID"
                    value={paymentForm.transactionId}
                    onChange={(e) => setPaymentForm(prev => ({ ...prev, transactionId: e.target.value }))}
                    helperText={(() => {
                      const selectedMethod = getPaymentMethods().find(m => m.id === paymentForm.paymentMethodId);
                      return selectedMethod?.requires_reference
                        ? "Required: Enter transaction/reference ID"
                        : "Optional: Transaction reference ID";
                    })()}
                    required={(() => {
                      const selectedMethod = getPaymentMethods().find(m => m.id === paymentForm.paymentMethodId);
                      return selectedMethod?.requires_reference || false;
                    })()}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Remarks"
                    multiline
                    rows={2}
                    value={paymentForm.remarks}
                    onChange={(e) => setPaymentForm(prev => ({ ...prev, remarks: e.target.value }))}
                    helperText="Optional: Additional notes about the payment"
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={dialogStyles.actions}>
          <Button
            onClick={() => setPaymentDialogOpen(false)}
            variant="outlined"
            sx={dialogStyles.secondaryButton}
          >
            Cancel
          </Button>
          <Button
            onClick={makePayment}
            variant="contained"
            disabled={(() => {
              const selectedMethod = getPaymentMethods().find(m => m.id === paymentForm.paymentMethodId);
              const isTransactionIdRequired = selectedMethod?.requires_reference && !paymentForm.transactionId.trim();
              return paymentLoading || !paymentForm.amount || paymentForm.selectedMonths.length === 0 || isTransactionIdRequired;
            })()}
            startIcon={paymentLoading ? <CircularProgress size={20} /> : <AccountBalance />}
            sx={dialogStyles.primaryButton}
          >
            {paymentLoading ? 'Processing...' : 'Make Payment'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Monthly Tracking Warning Dialog */}
      <Dialog
        open={monthlyTrackingWarningDialog}
        onClose={() => setMonthlyTrackingWarningDialog(false)}
        maxWidth="sm"
        fullWidth
        slotProps={{
          paper: {
            sx: dialogStyles.paper
          }
        }}
      >
        <DialogTitle sx={dialogStyles.title}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Warning color="warning" />
            <Typography variant="h6">Monthly Tracking Required</Typography>
          </Box>
        </DialogTitle>
        <DialogContent sx={dialogStyles.content}>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Monthly tracking is currently disabled for this student.
          </Alert>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Please enable monthly tracking for <strong>{selectedStudentForWarning?.student_name}</strong> ({selectedStudentForWarning?.admission_number}) before making payments or viewing fee details.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Monthly tracking allows you to:
          </Typography>
          <Box component="ul" sx={{ mt: 1, pl: 2 }}>
            <Typography component="li" variant="body2" color="text.secondary">
              Track month-by-month fee payments
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              View detailed payment history
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Make payments for specific months
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Monitor overdue and pending fees
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions sx={dialogStyles.actions}>
          <Button
            onClick={() => setMonthlyTrackingWarningDialog(false)}
            variant="outlined"
            sx={dialogStyles.secondaryButton}
          >
            Close
          </Button>
          <Button
            onClick={handleEnableTrackingFromWarning}
            variant="contained"
            startIcon={<Settings />}
            sx={dialogStyles.primaryButton}
          >
            Enable Monthly Tracking
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
  );
};

export default FeeManagementComponent;
