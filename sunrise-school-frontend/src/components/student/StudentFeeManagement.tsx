import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  Snackbar,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack
} from '@mui/material';
import {
  AccountBalanceWallet as WalletIcon,
  CalendarMonth as CalendarIcon,
  TrendingUp as TrendingUpIcon,
  Payment as PaymentIcon
} from '@mui/icons-material';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { studentFeeAPI, studentsAPI } from '../../services/api';
import { configurationService } from '../../services/configurationService';

// Types
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
  monthly_fee_amount: number;
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

interface StudentProfile {
  id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  class_name: string;
  section: string;
  roll_number: number;
}

interface FeeData {
  student_id: number;
  admission_number: string;
  student_name: string;
  class_name: string;
  has_fee_records: boolean;
  has_monthly_tracking: boolean;
  summary?: any;
  monthly_history?: StudentMonthlyFeeHistory;
  message?: string;
}

const StudentFeeManagement: React.FC = () => {
  const { isLoaded, isLoading, error } = useServiceConfiguration('fee-management');

  // Get configuration data
  const configuration = configurationService.getServiceConfiguration('fee-management');

  // State
  const [feeData, setFeeData] = useState<FeeData | null>(null);
  const [studentProfile, setStudentProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [sessionYearId, setSessionYearId] = useState<number>(4); // Default to 2025-26
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info'
  });

  // Load student profile and fee data
  useEffect(() => {
    loadStudentProfile();
  }, []);

  useEffect(() => {
    if (studentProfile) {
      loadFeeData();
    }
  }, [sessionYearId, studentProfile]);

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

  const loadFeeData = async () => {
    try {
      setLoading(true);
      const response = await studentFeeAPI.getMyFees(sessionYearId);
      setFeeData(response);
      
      if (!response.has_fee_records) {
        setSnackbar({
          open: true,
          message: response.message || 'No fee records found for current session year',
          severity: 'info'
        });
      }
    } catch (error) {
      console.error('Error loading fee data:', error);
      setSnackbar({
        open: true,
        message: 'Error loading fee information',
        severity: 'error'
      });
      setFeeData(null);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'paid': return '#4caf50';
      case 'pending': return '#ff9800';
      case 'overdue': return '#f44336';
      case 'partial': return '#2196f3';
      default: return '#757575';
    }
  };

  const formatCurrency = (amount: number) => {
    return `₹${amount.toFixed(2)}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const getStatisticsCards = () => {
    if (!feeData?.monthly_history) return [];

    const history = feeData.monthly_history;
    
    return [
      {
        title: 'Total Paid',
        value: formatCurrency(history.total_paid),
        icon: <WalletIcon fontSize="large" />,
        color: '#4caf50',
        subtitle: `${history.collection_percentage.toFixed(1)}% collected`,
      },
      {
        title: 'Months Paid',
        value: history.paid_months.toString(),
        icon: <CalendarIcon fontSize="large" />,
        color: '#2196f3',
        subtitle: `Out of ${history.total_months} months`,
      },
      {
        title: 'Remaining Balance',
        value: formatCurrency(history.total_balance),
        icon: <TrendingUpIcon fontSize="large" />,
        color: '#ff9800',
        subtitle: `${history.pending_months} months pending`,
      },
      {
        title: 'Monthly Fee',
        value: formatCurrency(history.monthly_fee_amount),
        icon: <PaymentIcon fontSize="large" />,
        color: '#9c27b0',
        subtitle: 'Per month',
      },
    ];
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header Section */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        flexDirection={{ xs: 'column', sm: 'row' }}
        gap={2}
        mb={3}
      >
        <Box>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            Fee Management
          </Typography>
          {studentProfile && (
            <Typography variant="body2" color="text.secondary">
              {studentProfile.first_name} {studentProfile.last_name} - Roll: {studentProfile.roll_number}
            </Typography>
          )}
        </Box>

        {/* Session Year Filter */}
        {isLoaded && configuration?.session_years && (
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Session Year</InputLabel>
            <Select
              value={sessionYearId}
              label="Session Year"
              onChange={(e) => setSessionYearId(Number(e.target.value))}
            >
              {configuration.session_years
                .filter((sy: any) => sy.is_active)
                .map((sy: any) => (
                  <MenuItem key={sy.id} value={sy.id}>
                    {sy.description || sy.name}
                  </MenuItem>
                ))}
            </Select>
          </FormControl>
        )}
      </Box>

      {/* Loading State */}
      {(loading || isLoading) && (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Content */}
      {!loading && !isLoading && isLoaded && feeData && (
        <>
          {/* No Fee Records Message */}
          {!feeData.has_fee_records && (
            <Alert severity="info" sx={{ mb: 3 }}>
              {feeData.message || 'No fee records found for the selected session year.'}
            </Alert>
          )}

          {/* Statistics Cards */}
          {feeData.has_monthly_tracking && feeData.monthly_history && (
            <>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {getStatisticsCards().map((card, index) => (
                  <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
                    <Card
                      sx={{
                        height: '100%',
                        background: `linear-gradient(135deg, ${card.color}15 0%, ${card.color}05 100%)`,
                        border: `1px solid ${card.color}30`,
                      }}
                    >
                      <CardContent>
                        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                          <Box sx={{ color: card.color }}>
                            {card.icon}
                          </Box>
                        </Box>
                        <Typography variant="h5" fontWeight="bold" gutterBottom>
                          {card.value}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {card.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {card.subtitle}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              {/* Monthly Payment History Table */}
              <Paper sx={{ width: '100%', overflow: 'hidden' }}>
                <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                  <Typography variant="h6" fontWeight="bold">
                    Monthly Payment History
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Detailed month-wise payment status
                  </Typography>
                </Box>

                <TableContainer sx={{ maxHeight: 600 }}>
                  <Table stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 'bold', backgroundColor: 'white' }}>Month</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', backgroundColor: 'white' }}>Due Date</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 'bold', backgroundColor: 'white' }}>Monthly Fee</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 'bold', backgroundColor: 'white' }}>Paid Amount</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 'bold', backgroundColor: 'white' }}>Balance</TableCell>
                        <TableCell align="center" sx={{ fontWeight: 'bold', backgroundColor: 'white' }}>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {feeData.monthly_history.monthly_history.map((month) => (
                        <TableRow key={`${month.year}-${month.month}`} hover>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {month.month_name} {month.year}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {formatDate(month.due_date)}
                            </Typography>
                            {month.is_overdue && month.days_overdue && (
                              <Typography variant="caption" color="error">
                                {month.days_overdue} days overdue
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell align="right">
                            {formatCurrency(month.monthly_amount)}
                          </TableCell>
                          <TableCell align="right">
                            {formatCurrency(month.paid_amount)}
                          </TableCell>
                          <TableCell align="right">
                            <Typography
                              variant="body2"
                              fontWeight="medium"
                              color={month.balance_amount > 0 ? 'error' : 'success.main'}
                            >
                              {formatCurrency(month.balance_amount)}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={month.status.toUpperCase()}
                              size="small"
                              sx={{
                                backgroundColor: getStatusColor(month.status),
                                color: 'white',
                                fontWeight: 'bold',
                                minWidth: 80
                              }}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            </>
          )}

          {/* No Monthly Tracking Message */}
          {feeData.has_fee_records && !feeData.has_monthly_tracking && (
            <Alert severity="info">
              Monthly fee tracking is not enabled for your account. Please contact the administration for more information.
            </Alert>
          )}
        </>
      )}

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default StudentFeeManagement;

