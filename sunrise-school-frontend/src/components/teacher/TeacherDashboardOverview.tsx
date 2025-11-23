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
  Work,
  Email,
  Phone,
  CalendarToday,
  School,
  Badge,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { leaveAPI, teachersAPI } from '../../services/api';

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
  professional_info: {
    employee_id: string;
    first_name: string;
    last_name: string;
    department: string;
    position: string;
    qualification: string;
    employment_status: string;
    joining_date: string;
    tenure: string;
    experience_years: number;
    class_teacher_of: string | null;
    email: string;
    phone: string;
  };
  leave_stats: {
    total: number;
    pending: number;
    approved: number;
    rejected: number;
  };
  upcoming_leaves: Array<{
    id: number;
    start_date: string;
    end_date: string;
    total_days: number;
    reason: string;
    leave_type_name: string;
  }>;
}

const TeacherDashboardOverview: React.FC = () => {
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
        teachersAPI.getMyDashboardStats(),
        leaveAPI.getMyLeaveRequests()
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

  const getDashboardCards = () => {
    if (!dashboardStats) return [];

    return [
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
      {
        title: 'Rejected Leaves',
        value: dashboardStats.leave_stats.rejected.toString(),
        icon: <Cancel fontSize="large" />,
        color: '#d32f2f',
        subtitle: 'Not approved',
      },
    ];
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
            Welcome back, {dashboardStats.professional_info.first_name} {dashboardStats.professional_info.last_name}!
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {dashboardStats.professional_info.position} • {dashboardStats.professional_info.department}
          </Typography>
        </Box>
      )}

      {/* Dashboard Statistics Cards */}
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

      {/* Professional Information Section */}
      {dashboardStats && (
        <Paper sx={{ p: { xs: 2, md: 3 }, mb: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={3}>
            Professional Information
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
                  Employee ID
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.professional_info.employee_id}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <Work color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Department
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.professional_info.department || 'N/A'}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <Person color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Position
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.professional_info.position || 'N/A'}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <School color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Qualification
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.professional_info.qualification || 'N/A'}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <CalendarToday color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Joining Date
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.professional_info.joining_date
                    ? new Date(dashboardStats.professional_info.joining_date).toLocaleDateString()
                    : 'N/A'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Tenure: {dashboardStats.professional_info.tenure}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <EventNote color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Experience
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.professional_info.experience_years} years
                </Typography>
              </Box>
            </Box>
            {dashboardStats.professional_info.class_teacher_of && (
              <Box display="flex" alignItems="center" gap={1}>
                <School color="primary" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Class Teacher Of
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {dashboardStats.professional_info.class_teacher_of}
                  </Typography>
                </Box>
              </Box>
            )}
            <Box display="flex" alignItems="center" gap={1}>
              <Email color="primary" />
              <Box sx={{ minWidth: 0 }}>
                <Typography variant="caption" color="text.secondary">
                  Email
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight="medium"
                  sx={{
                    wordBreak: 'break-word',
                    fontSize: { xs: '0.875rem', sm: '1rem' }
                  }}
                >
                  {dashboardStats.professional_info.email}
                </Typography>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <Phone color="primary" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Phone
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {dashboardStats.professional_info.phone}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Recent Leave Requests and Quick Actions */}
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
                onClick={() => navigate('/teacher/leaves')}
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
              onClick={() => navigate('/teacher/leaves')}
              fullWidth
            >
              Manage Leave Requests
            </Button>
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

export default TeacherDashboardOverview;
