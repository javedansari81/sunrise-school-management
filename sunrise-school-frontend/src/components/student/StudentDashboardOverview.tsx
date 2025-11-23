import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  LinearProgress,
} from '@mui/material';
import {
  EventNote,
  Schedule,
  CheckCircle,
  Cancel,
  Pending,
  Person,
  AccountBalanceWallet,
  School,
  Badge,
  CalendarToday,
  DirectionsBus,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { studentLeaveAPI, studentsAPI, studentFeeAPI } from '../../services/api';

interface LeaveRequest {
  id: number;
  leave_type_name: string;
  start_date: string;
  end_date: string;
  total_days: number;
  leave_status_name: string;
  leave_status_id: number;
  reason: string;
  created_at: string;
}

interface DashboardStats {
  academic_info: {
    admission_number: string;
    first_name: string;
    last_name: string;
    class_name: string;
    class_code: string;
    section: string | null;
    roll_number: string | null;
    session_year: string;
    gender: string;
    date_of_birth: string;
    admission_date: string;
  };
  leave_stats: {
    total: number;
    pending: number;
    approved: number;
    rejected: number;
  };
  fee_summary: {
    has_fee_records: boolean;
    total_fee: number;
    total_paid: number;
    remaining_balance: number;
    last_payment_date: string | null;
    payment_percentage: number;
  };
  transport_info: {
    transport_type_name: string;
    pickup_location: string;
    drop_location: string;
    monthly_fee: number;
    distance_km: number;
  } | null;
}

const StudentDashboardOverview: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recentLeaves, setRecentLeaves] = useState<LeaveRequest[]>([]);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load dashboard stats and recent leave requests
      const [statsResponse, leavesResponse] = await Promise.all([
        studentsAPI.getMyDashboardStats(),
        studentLeaveAPI.getMyLeaveRequests()
      ]);

      setDashboardStats(statsResponse.data);

      // Process leave requests
      const leaves = Array.isArray(leavesResponse) ? leavesResponse : [];
      setRecentLeaves(leaves.slice(0, 5)); // Show only recent 5

      setError(null);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (statusId: number) => {
    switch (statusId) {
      case 1: return <Pending color="warning" />;
      case 2: return <CheckCircle color="success" />;
      case 3: return <Cancel color="error" />;
      default: return <Schedule />;
    }
  };

  const getStatusColor = (statusId: number) => {
    switch (statusId) {
      case 1: return 'warning';
      case 2: return 'success';
      case 3: return 'error';
      default: return 'default';
    }
  };

  const getDashboardCards = (): Array<{
    title: string;
    value: string;
    icon: React.ReactElement;
    color: string;
    subtitle: string;
    clickable?: boolean;
    onClick?: () => void;
  }> => {
    if (!dashboardStats) return [];

    const cards = [
      {
        title: 'Total Leave Requests',
        value: dashboardStats.leave_stats.total.toString(),
        icon: <EventNote fontSize="large" />,
        color: '#1976d2',
        subtitle: 'All time requests',
      },
      {
        title: 'Pending Approval',
        value: dashboardStats.leave_stats.pending.toString(),
        icon: <Pending fontSize="large" />,
        color: '#f57c00',
        subtitle: 'Awaiting review',
      },
      {
        title: 'Approved Leaves',
        value: dashboardStats.leave_stats.approved.toString(),
        icon: <CheckCircle fontSize="large" />,
        color: '#388e3c',
        subtitle: 'Successfully approved',
      },
    ];

    // Add fee card if fee data is available
    if (dashboardStats.fee_summary.has_fee_records) {
      cards.push({
        title: 'Fee Balance',
        value: `₹${dashboardStats.fee_summary.remaining_balance.toFixed(0)}`,
        icon: <AccountBalanceWallet fontSize="large" />,
        color: '#9c27b0',
        subtitle: `Paid: ₹${dashboardStats.fee_summary.total_paid.toFixed(0)}`,
      });
    }

    return cards;
  };

  const getFeeProgressColor = (percentage: number) => {
    if (percentage >= 75) return 'success';
    if (percentage >= 25) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Welcome Message */}
      {dashboardStats && (
        <Box mb={3}>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            Welcome back, {dashboardStats.academic_info.first_name} {dashboardStats.academic_info.last_name}!
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Class {dashboardStats.academic_info.class_name}
            {dashboardStats.academic_info.section && `-${dashboardStats.academic_info.section}`}
            {dashboardStats.academic_info.roll_number && ` • Roll No: ${dashboardStats.academic_info.roll_number}`}
          </Typography>
        </Box>
      )}

      {/* Academic Information Section */}
      {dashboardStats && (
        <Paper sx={{ p: { xs: 2, md: 3 }, mb: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={3}>
            Academic Information
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 2,
            }}
          >
            <Box display="flex" alignItems="center" gap={1}>
              <Badge color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Admission Number
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.academic_info.admission_number}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <School color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Class & Section
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.academic_info.class_name}
                  {dashboardStats.academic_info.section && `-${dashboardStats.academic_info.section}`}
                </Typography>
              </Box>
            </Box>
            {dashboardStats.academic_info.roll_number && (
              <Box display="flex" alignItems="center" gap={1}>
                <Person color="primary" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Roll Number
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {dashboardStats.academic_info.roll_number}
                  </Typography>
                </Box>
              </Box>
            )}
            <Box display="flex" alignItems="center" gap={1}>
              <CalendarToday color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Session Year
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.academic_info.session_year}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <CalendarToday color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Date of Birth
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {new Date(dashboardStats.academic_info.date_of_birth).toLocaleDateString()}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <CalendarToday color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Admission Date
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {new Date(dashboardStats.academic_info.admission_date).toLocaleDateString()}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Fee Summary Section with Progress Bar */}
      {dashboardStats && dashboardStats.fee_summary.has_fee_records && (
        <Paper sx={{ p: { xs: 2, md: 3 }, mb: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={3}>
            Fee Summary
          </Typography>
          <Box>
            <Box mb={3}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary">
                  Payment Progress
                </Typography>
                <Typography variant="body2" fontWeight="bold" color="primary">
                  {dashboardStats.fee_summary.payment_percentage.toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={Math.min(dashboardStats.fee_summary.payment_percentage, 100)}
                color={getFeeProgressColor(dashboardStats.fee_summary.payment_percentage)}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: {
                  xs: '1fr',
                  sm: 'repeat(3, 1fr)',
                },
                gap: 3,
                mb: 2,
              }}
            >
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Total Fee Amount
                </Typography>
                <Typography variant="h6" fontWeight="bold" color="primary">
                  ₹{dashboardStats.fee_summary.total_fee.toFixed(2)}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Paid Amount
                </Typography>
                <Typography variant="h6" fontWeight="bold" color="success.main">
                  ₹{dashboardStats.fee_summary.total_paid.toFixed(2)}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Remaining Balance
                </Typography>
                <Typography variant="h6" fontWeight="bold" color="error.main">
                  ₹{dashboardStats.fee_summary.remaining_balance.toFixed(2)}
                </Typography>
              </Box>
            </Box>
            {dashboardStats.fee_summary.last_payment_date && (
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Last Payment: {new Date(dashboardStats.fee_summary.last_payment_date).toLocaleDateString()}
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>
      )}

      {/* Transport Information Section */}
      {dashboardStats && dashboardStats.transport_info && (
        <Paper sx={{ p: { xs: 2, md: 3 }, mb: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={3}>
            Transport Information
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 2,
            }}
          >
            <Box display="flex" alignItems="center" gap={1}>
              <DirectionsBus color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Transport Type
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.transport_info.transport_type_name}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <DirectionsBus color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Distance
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.transport_info.distance_km > 0
                    ? `${dashboardStats.transport_info.distance_km} km`
                    : 'N/A'}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <AccountBalanceWallet color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Monthly Fee
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  ₹{dashboardStats.transport_info.monthly_fee.toFixed(2)}
                </Typography>
              </Box>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Pickup Location
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {dashboardStats.transport_info.pickup_location}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Drop Location
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {dashboardStats.transport_info.drop_location}
              </Typography>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Dashboard Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            lg: 'repeat(4, 1fr)',
          },
          gap: 2,
          mb: 4,
        }}
      >
        {getDashboardCards().map((card, index) => (
          <Card
            key={index}
            sx={{
              background: `linear-gradient(135deg, ${card.color} 0%, ${card.color}dd 100%)`,
              color: 'white',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 6,
              },
            }}
            onClick={card.onClick}
          >
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                <Box>
                  <Typography variant="h4" fontWeight="bold" gutterBottom>
                    {card.value}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    {card.title}
                  </Typography>
                </Box>
                <Box sx={{ opacity: 0.8 }}>
                  {card.icon}
                </Box>
              </Box>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                {card.subtitle}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Recent Leave Requests */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            md: '2fr 1fr',
          },
          gap: 2,
        }}
      >
        <Box>
          <Paper sx={{ p: { xs: 2, md: 3 } }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" fontWeight="bold">
                Recent Leave Requests
              </Typography>
              <Button
                variant="contained"
                onClick={() => navigate('/student/leaves')}
                size="small"
              >
                View All
              </Button>
            </Box>
            
            {recentLeaves.length === 0 ? (
              <Typography color="text.secondary" textAlign="center" py={4}>
                No leave requests found. Click "View All" to create your first request.
              </Typography>
            ) : (
              <List>
                {recentLeaves.map((leave, index) => (
                  <React.Fragment key={leave.id}>
                    <ListItem>
                      <ListItemIcon>
                        {getStatusIcon(leave.leave_status_id)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body1" fontWeight="medium">
                              {leave.leave_type_name}
                            </Typography>
                            <Chip
                              label={leave.leave_status_name}
                              size="small"
                              color={getStatusColor(leave.leave_status_id) as any}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {new Date(leave.start_date).toLocaleDateString()} - {new Date(leave.end_date).toLocaleDateString()} ({leave.total_days} days)
                            </Typography>
                            <Typography variant="body2" color="text.secondary" noWrap>
                              {leave.reason}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < recentLeaves.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Box>

        <Paper sx={{ p: { xs: 2, md: 3 } }}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Quick Actions
          </Typography>
          <Box display="flex" flexDirection="column" gap={2}>
            <Button
              variant="contained"
              startIcon={<EventNote />}
              onClick={() => navigate('/student/leaves')}
              fullWidth
            >
              Manage Leave Requests
            </Button>
            {dashboardStats?.fee_summary.has_fee_records && (
              <Button
                variant="contained"
                startIcon={<AccountBalanceWallet />}
                onClick={() => navigate('/student/fees')}
                fullWidth
                sx={{ backgroundColor: '#9c27b0', '&:hover': { backgroundColor: '#7b1fa2' } }}
              >
                View Fee Details
              </Button>
            )}
            <Button
              variant="outlined"
              startIcon={<Person />}
              onClick={() => navigate('/profile')}
              fullWidth
            >
              View Profile
            </Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default StudentDashboardOverview;
