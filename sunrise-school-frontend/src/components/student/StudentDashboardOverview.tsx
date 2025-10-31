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
} from '@mui/material';
import {
  EventNote,
  Schedule,
  CheckCircle,
  Cancel,
  Pending,
  Person,
  AccountBalanceWallet,
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

interface StudentProfile {
  id: number;
  first_name: string;
  last_name: string;
  roll_number: string;
  class_name: string;
  email: string;
}

const StudentDashboardOverview: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recentLeaves, setRecentLeaves] = useState<LeaveRequest[]>([]);
  const [studentProfile, setStudentProfile] = useState<StudentProfile | null>(null);
  const [leaveStats, setLeaveStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
  });
  const [feeStats, setFeeStats] = useState<{
    totalPaid: number;
    remainingBalance: number;
    hasFeeRecords: boolean;
  } | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load student profile, recent leave requests, and fee data
      const [profileResponse, leavesResponse, feeResponse] = await Promise.all([
        studentsAPI.getMyProfile(),
        studentLeaveAPI.getMyLeaveRequests(),
        studentFeeAPI.getMyFees(4).catch(() => null) // Don't fail if fee data unavailable
      ]);

      setStudentProfile(profileResponse.data);

      // Process leave requests
      const leaves = Array.isArray(leavesResponse) ? leavesResponse : [];
      setRecentLeaves(leaves.slice(0, 5)); // Show only recent 5

      // Calculate leave stats
      const stats = leaves.reduce((acc, leave) => {
        acc.total++;
        if (leave.leave_status_id === 1) acc.pending++;
        else if (leave.leave_status_id === 2) acc.approved++;
        else if (leave.leave_status_id === 3) acc.rejected++;
        return acc;
      }, { total: 0, pending: 0, approved: 0, rejected: 0 });

      setLeaveStats(stats);

      // Process fee data
      if (feeResponse && feeResponse.has_fee_records && feeResponse.monthly_history) {
        setFeeStats({
          totalPaid: feeResponse.monthly_history.total_paid || 0,
          remainingBalance: feeResponse.monthly_history.total_balance || 0,
          hasFeeRecords: true
        });
      } else {
        setFeeStats({
          totalPaid: 0,
          remainingBalance: 0,
          hasFeeRecords: false
        });
      }

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
    const cards = [
      {
        title: 'Total Leave Requests',
        value: leaveStats.total.toString(),
        icon: <EventNote fontSize="large" />,
        color: '#1976d2',
        subtitle: 'All time requests',
      },
      {
        title: 'Pending Approval',
        value: leaveStats.pending.toString(),
        icon: <Pending fontSize="large" />,
        color: '#f57c00',
        subtitle: 'Awaiting review',
      },
      {
        title: 'Approved Leaves',
        value: leaveStats.approved.toString(),
        icon: <CheckCircle fontSize="large" />,
        color: '#388e3c',
        subtitle: 'Successfully approved',
      },
    ];

    // Add fee card if fee data is available
    if (feeStats?.hasFeeRecords) {
      cards.push({
        title: 'Fee Balance',
        value: `₹${feeStats.remainingBalance.toFixed(0)}`,
        icon: <AccountBalanceWallet fontSize="large" />,
        color: '#9c27b0',
        subtitle: `Paid: ₹${feeStats.totalPaid.toFixed(0)}`,
      });
    }

    return cards;
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

      {/* Dashboard Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(4, 1fr)',
          },
          gap: 3,
          mb: 4,
        }}
      >
        {getDashboardCards().map((card, index) => (
          <Card
            key={index}
            sx={{
              height: '100%',
              cursor: card.clickable ? 'pointer' : 'default',
              '&:hover': card.clickable ? {
                transform: 'translateY(-2px)',
                boxShadow: 3,
              } : {},
              transition: 'all 0.2s ease-in-out',
            }}
            onClick={card.onClick}
          >
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Box
                  sx={{
                    backgroundColor: card.color,
                    color: 'white',
                    borderRadius: '50%',
                    p: 1,
                    mr: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {card.icon}
                </Box>
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {card.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.subtitle}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body1" fontWeight="medium">
                {card.title}
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
          gap: 3,
        }}
      >
        <Box>
          <Paper sx={{ p: 3 }}>
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

        <Paper sx={{ p: 3 }}>
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
            {feeStats?.hasFeeRecords && (
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
