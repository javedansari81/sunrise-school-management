import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  Button,
  Alert,
  CircularProgress,
  Paper,
  Avatar,
} from '@mui/material';
import {
  EventNote,
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
  AccessTime,
  TrendingUp,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { leaveAPI, teachersAPI } from '../../services/api';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';

// Chart colors
const CHART_COLORS = {
  pending: '#f57c00',
  approved: '#388e3c',
  rejected: '#d32f2f',
  primary: '#1976d2',
};

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

      const [statsResponse, leavesResponse] = await Promise.all([
        teachersAPI.getMyDashboardStats(),
        leaveAPI.getMyLeaveRequests()
      ]);

      setDashboardStats(statsResponse.data);

      const leaves = Array.isArray(leavesResponse) ? leavesResponse : [];
      setRecentLeaves(leaves.slice(0, 5));

      setError(null);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (statusId: number): string => {
    switch (statusId) {
      case 1: return CHART_COLORS.pending;
      case 2: return CHART_COLORS.approved;
      case 3: return CHART_COLORS.rejected;
      default: return '#9e9e9e';
    }
  };

  const getStatusIcon = (statusId: number) => {
    switch (statusId) {
      case 1: return <Pending sx={{ color: CHART_COLORS.pending }} />;
      case 2: return <CheckCircle sx={{ color: CHART_COLORS.approved }} />;
      case 3: return <Cancel sx={{ color: CHART_COLORS.rejected }} />;
      default: return <AccessTime sx={{ color: '#9e9e9e' }} />;
    }
  };

  // Prepare chart data for leave status distribution
  const getLeaveChartData = () => {
    if (!dashboardStats) return [];
    const { leave_stats } = dashboardStats;
    return [
      { name: 'Pending', value: leave_stats.pending, color: CHART_COLORS.pending },
      { name: 'Approved', value: leave_stats.approved, color: CHART_COLORS.approved },
      { name: 'Rejected', value: leave_stats.rejected, color: CHART_COLORS.rejected },
    ].filter(item => item.value > 0);
  };

  const getDashboardCards = () => {
    if (!dashboardStats) return [];
    const { leave_stats } = dashboardStats;

    return [
      { title: 'Total', value: leave_stats.total, icon: <EventNote />, color: CHART_COLORS.primary },
      { title: 'Pending', value: leave_stats.pending, icon: <Pending />, color: CHART_COLORS.pending },
      { title: 'Approved', value: leave_stats.approved, icon: <CheckCircle />, color: CHART_COLORS.approved },
      { title: 'Rejected', value: leave_stats.rejected, icon: <Cancel />, color: CHART_COLORS.rejected },
    ];
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const leaveChartData = getLeaveChartData();

  return (
    <Box sx={{ width: '100%' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Welcome Header */}
      {dashboardStats && (
        <Paper
          sx={{
            p: 3,
            mb: 3,
            background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
            color: 'white',
            borderRadius: 2,
          }}
        >
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar
              sx={{
                width: 56,
                height: 56,
                bgcolor: 'rgba(255,255,255,0.2)',
                fontSize: '1.5rem',
              }}
            >
              {dashboardStats.professional_info.first_name[0]}{dashboardStats.professional_info.last_name[0]}
            </Avatar>
            <Box>
              <Typography variant="h5" fontWeight="bold">
                Welcome, {dashboardStats.professional_info.first_name}!
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {dashboardStats.professional_info.position} • {dashboardStats.professional_info.department}
              </Typography>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Stats Cards & Leave Chart */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
          gap: 3,
          mb: 3,
        }}
      >
        {/* Leave Stats Cards */}
        <Paper sx={{ p: 2.5, borderRadius: 2 }}>
          <Typography variant="subtitle1" fontWeight="bold" mb={2} display="flex" alignItems="center" gap={1}>
            <TrendingUp fontSize="small" color="primary" />
            Leave Overview
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: 2,
            }}
          >
            {getDashboardCards().map((card, index) => (
              <Card
                key={index}
                elevation={0}
                sx={{
                  p: 2,
                  bgcolor: `${card.color}10`,
                  border: `1px solid ${card.color}30`,
                  borderRadius: 2,
                  transition: 'transform 0.2s',
                  '&:hover': { transform: 'scale(1.02)' },
                }}
              >
                <Box display="flex" alignItems="center" gap={1.5}>
                  <Avatar sx={{ bgcolor: card.color, width: 40, height: 40 }}>
                    {card.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color={card.color}>
                      {card.value}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {card.title}
                    </Typography>
                  </Box>
                </Box>
              </Card>
            ))}
          </Box>
        </Paper>

        {/* Leave Distribution Chart */}
        <Paper sx={{ p: 2.5, borderRadius: 2 }}>
          <Typography variant="subtitle1" fontWeight="bold" mb={1} display="flex" alignItems="center" gap={1}>
            <EventNote fontSize="small" color="primary" />
            Leave Distribution
          </Typography>
          {leaveChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={leaveChartData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                >
                  {leaveChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number, name: string) => [`${value} requests`, name]}
                  contentStyle={{ borderRadius: 8, fontSize: '0.875rem' }}
                />
                <Legend
                  iconType="circle"
                  iconSize={10}
                  wrapperStyle={{ fontSize: '0.8rem' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <Box display="flex" justifyContent="center" alignItems="center" height={200}>
              <Typography color="text.secondary">No leave data to display</Typography>
            </Box>
          )}
        </Paper>
      </Box>

      {/* Professional Info & Quick Actions Row */}
      {dashboardStats && (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
            gap: 3,
            mb: 3,
          }}
        >
          {/* Professional Info - Compact Grid */}
          <Paper sx={{ p: 2.5, borderRadius: 2 }}>
            <Typography variant="subtitle1" fontWeight="bold" mb={2} display="flex" alignItems="center" gap={1}>
              <Person fontSize="small" color="primary" />
              Professional Info
            </Typography>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
                gap: 2,
              }}
            >
              {[
                { icon: <Badge fontSize="small" />, label: 'ID', value: dashboardStats.professional_info.employee_id },
                { icon: <Work fontSize="small" />, label: 'Dept', value: dashboardStats.professional_info.department || 'N/A' },
                { icon: <School fontSize="small" />, label: 'Qual', value: dashboardStats.professional_info.qualification || 'N/A' },
                { icon: <CalendarToday fontSize="small" />, label: 'Joined', value: dashboardStats.professional_info.joining_date ? new Date(dashboardStats.professional_info.joining_date).toLocaleDateString() : 'N/A' },
                { icon: <AccessTime fontSize="small" />, label: 'Exp', value: `${dashboardStats.professional_info.experience_years} yrs` },
                ...(dashboardStats.professional_info.class_teacher_of ? [{ icon: <School fontSize="small" />, label: 'Class', value: dashboardStats.professional_info.class_teacher_of }] : []),
              ].map((item, index) => (
                <Box key={index} display="flex" alignItems="center" gap={1}>
                  <Box sx={{ color: 'primary.main' }}>{item.icon}</Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">{item.label}</Typography>
                    <Typography variant="body2" fontWeight="medium">{item.value}</Typography>
                  </Box>
                </Box>
              ))}
            </Box>
            {/* Contact Info */}
            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider', display: 'flex', gap: 3, flexWrap: 'wrap' }}>
              <Box display="flex" alignItems="center" gap={1}>
                <Email fontSize="small" color="primary" />
                <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>{dashboardStats.professional_info.email}</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <Phone fontSize="small" color="primary" />
                <Typography variant="body2">{dashboardStats.professional_info.phone}</Typography>
              </Box>
            </Box>
          </Paper>

          {/* Quick Actions */}
          <Paper sx={{ p: 2.5, borderRadius: 2 }}>
            <Typography variant="subtitle1" fontWeight="bold" mb={2}>
              Quick Actions
            </Typography>
            <Box display="flex" flexDirection="column" gap={1.5}>
              <Button
                variant="contained"
                startIcon={<EventNote />}
                onClick={() => navigate('/teacher/leaves')}
                fullWidth
                sx={{ py: 1.2 }}
              >
                Manage Leaves
              </Button>
              <Button
                variant="outlined"
                startIcon={<Person />}
                onClick={() => navigate('/profile')}
                fullWidth
                sx={{ py: 1.2 }}
              >
                View Profile
              </Button>
            </Box>
          </Paper>
        </Box>
      )}

      {/* Recent Leave Requests - Timeline Style */}
      <Paper sx={{ p: 2.5, borderRadius: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="subtitle1" fontWeight="bold" display="flex" alignItems="center" gap={1}>
            <AccessTime fontSize="small" color="primary" />
            Recent Leave Requests
          </Typography>
          <Button
            variant="text"
            size="small"
            onClick={() => navigate('/teacher/leaves')}
            sx={{ textTransform: 'none' }}
          >
            View All →
          </Button>
        </Box>

        {recentLeaves.length === 0 ? (
          <Box textAlign="center" py={4}>
            <EventNote sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography color="text.secondary">No leave requests yet</Typography>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            {recentLeaves.map((leave) => (
              <Card
                key={leave.id}
                elevation={0}
                sx={{
                  p: 2,
                  bgcolor: 'grey.50',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 2,
                  borderLeft: `4px solid ${getStatusColor(leave.leave_status_id)}`,
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateX(4px)',
                    boxShadow: 1,
                  },
                }}
              >
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={1}>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getStatusIcon(leave.leave_status_id)}
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {leave.leave_type_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(leave.start_date).toLocaleDateString()} - {new Date(leave.end_date).toLocaleDateString()} • {leave.total_days} day{leave.total_days > 1 ? 's' : ''}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography
                    variant="caption"
                    sx={{
                      px: 1.5,
                      py: 0.5,
                      borderRadius: 1,
                      bgcolor: `${getStatusColor(leave.leave_status_id)}15`,
                      color: getStatusColor(leave.leave_status_id),
                      fontWeight: 'bold',
                    }}
                  >
                    {leave.leave_status_name}
                  </Typography>
                </Box>
              </Card>
            ))}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default TeacherDashboardOverview;
