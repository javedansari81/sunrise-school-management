import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  People,
  School,
  Payment,
  EventNote,
  AccountBalance,
  TrendingUp,
  Visibility,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import AdminLayout from '../../components/Layout/AdminLayout';
import { leaveAPI } from '../../services/api';

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [leaveStats, setLeaveStats] = useState<any>(null);
  const [pendingLeaves, setPendingLeaves] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, pendingResponse] = await Promise.all([
        leaveAPI.getLeaveStatistics(),
        leaveAPI.getPendingLeaves()
      ]);

      setLeaveStats(statsResponse);
      setPendingLeaves(Array.isArray(pendingResponse) ? pendingResponse : []);
      setError(null);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
      setLeaveStats(null);
      setPendingLeaves([]);
    } finally {
      setLoading(false);
    }
  };

  const getDashboardCards = () => [
    {
      title: 'Total Students',
      value: '245',
      icon: <People fontSize="large" />,
      color: '#1976d2',
      change: '+12 this month',
    },
    {
      title: 'Total Teachers',
      value: '18',
      icon: <School fontSize="large" />,
      color: '#388e3c',
      change: '+2 this month',
    },
    {
      title: 'Pending Fees',
      value: '₹1,25,000',
      icon: <Payment fontSize="large" />,
      color: '#f57c00',
      change: '-₹15,000 this week',
    },
    {
      title: 'Leave Requests',
      value: leaveStats?.summary?.total_requests?.toString() || '0',
      icon: <EventNote fontSize="large" />,
      color: '#7b1fa2',
      change: `${leaveStats?.summary?.pending_requests || 0} pending approval`,
      clickable: true,
      onClick: () => navigate('/admin/leaves'),
    },
    {
      title: 'Monthly Expenses',
      value: '₹85,000',
      icon: <AccountBalance fontSize="large" />,
      color: '#d32f2f',
      change: '+₹5,000 from last month',
    },
    {
      title: 'Revenue Growth',
      value: '12.5%',
      icon: <TrendingUp fontSize="large" />,
      color: '#0288d1',
      change: '+2.3% from last quarter',
    },
  ];



  return (
    <AdminLayout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard Overview
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
          School operations summary and key metrics
        </Typography>

        {/* Dashboard Cards */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
          {getDashboardCards().map((card, index) => (
            <Box key={index} sx={{ flex: '1 1 300px', minWidth: 300 }}>
              <Card
                sx={{
                  height: '100%',
                  transition: 'transform 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                    <Box
                      sx={{
                        backgroundColor: card.color,
                        color: 'white',
                        borderRadius: '50%',
                        p: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {card.icon}
                    </Box>
                  </Box>
                  <Typography variant="h4" fontWeight="bold" gutterBottom>
                    {card.value}
                  </Typography>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    {card.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.change}
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          ))}
        </Box>

        {/* Pending Leave Requests Section */}
        {!loading && pendingLeaves.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">
                  Pending Leave Requests ({pendingLeaves.length})
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Visibility />}
                  onClick={() => navigate('/admin/leaves')}
                >
                  View All
                </Button>
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {pendingLeaves.slice(0, 5).map((leave) => (
                  <Box
                    key={leave.id}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 2,
                      border: '1px solid #e0e0e0',
                      borderRadius: 1,
                      '&:hover': {
                        backgroundColor: '#f5f5f5',
                      },
                    }}
                  >
                    <Box>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {leave.applicant_name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {leave.applicant_details} • {leave.leave_type_name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {leave.start_date} to {leave.end_date} ({leave.total_days} days)
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={leave.leave_status_name}
                        color="warning"
                        size="small"
                      />
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => navigate('/admin/leaves')}
                      >
                        Review
                      </Button>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>
    </AdminLayout>
  );
};

export default AdminDashboard;
