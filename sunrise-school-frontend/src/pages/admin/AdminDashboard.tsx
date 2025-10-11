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
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <Typography
          variant="h4"
          gutterBottom
          sx={{
            fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' },
            mb: { xs: 1, sm: 2 }
          }}
        >
          Dashboard Overview
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              sm: 'repeat(2, 1fr)',
              md: 'repeat(3, 1fr)',
              lg: 'repeat(3, 1fr)',
              xl: 'repeat(4, 1fr)'
            },
            gap: { xs: 2, sm: 2, md: 3 },
            mb: { xs: 3, sm: 4 }
          }}
        >
          {getDashboardCards().map((card, index) => (
            <Card
              key={index}
              sx={{
                height: '100%',
                transition: 'transform 0.2s ease-in-out',
                cursor: card.clickable ? 'pointer' : 'default',
                '&:hover': {
                  transform: card.clickable ? 'translateY(-4px)' : 'translateY(-2px)',
                  boxShadow: { xs: 2, sm: 4 },
                },
                minHeight: { xs: '140px', sm: '160px', md: '180px' }
              }}
              onClick={card.onClick}
            >
              <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                <Box
                  display="flex"
                  alignItems="center"
                  justifyContent="space-between"
                  mb={{ xs: 1.5, sm: 2 }}
                >
                  <Box
                    sx={{
                      backgroundColor: card.color,
                      color: 'white',
                      borderRadius: '50%',
                      p: { xs: 1, sm: 1.5 },
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      '& .MuiSvgIcon-root': {
                        fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' }
                      }
                    }}
                  >
                    {card.icon}
                  </Box>
                </Box>
                <Typography
                  variant="h4"
                  fontWeight="bold"
                  gutterBottom
                  sx={{
                    fontSize: { xs: '1.5rem', sm: '1.75rem', md: '2rem' },
                    lineHeight: 1.2,
                    mb: { xs: 0.5, sm: 1 }
                  }}
                >
                  {card.value}
                </Typography>
                <Typography
                  variant="h6"
                  color="text.secondary"
                  gutterBottom
                  sx={{
                    fontSize: { xs: '0.875rem', sm: '1rem', md: '1.125rem' },
                    fontWeight: 500,
                    mb: { xs: 0.5, sm: 1 }
                  }}
                >
                  {card.title}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    lineHeight: 1.3
                  }}
                >
                  {card.change}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Pending Leave Requests Section - Mobile Responsive */}
        {!loading && pendingLeaves.length > 0 && (
          <Card sx={{ mb: { xs: 2, sm: 3 } }}>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: { xs: 'flex-start', sm: 'center' },
                  flexDirection: { xs: 'column', sm: 'row' },
                  gap: { xs: 1, sm: 0 },
                  mb: { xs: 2, sm: 2 }
                }}
              >
                <Typography
                  variant="h6"
                  fontWeight="bold"
                  sx={{
                    fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
                  }}
                >
                  Pending Leave Requests ({pendingLeaves.length})
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Visibility />}
                  onClick={() => navigate('/admin/leaves')}
                  sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    padding: { xs: '4px 8px', sm: '6px 12px' },
                    alignSelf: { xs: 'flex-end', sm: 'auto' }
                  }}
                >
                  View All
                </Button>
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: { xs: 1.5, sm: 2 } }}>
                {pendingLeaves.slice(0, 5).map((leave) => (
                  <Box
                    key={leave.id}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: { xs: 'flex-start', sm: 'center' },
                      flexDirection: { xs: 'column', sm: 'row' },
                      gap: { xs: 1.5, sm: 1 },
                      p: { xs: 1.5, sm: 2 },
                      border: '1px solid #e0e0e0',
                      borderRadius: { xs: 1, sm: 1.5 },
                      '&:hover': {
                        backgroundColor: '#f5f5f5',
                      },
                    }}
                  >
                    <Box sx={{ flex: 1 }}>
                      <Typography
                        variant="subtitle1"
                        fontWeight="bold"
                        sx={{
                          fontSize: { xs: '0.875rem', sm: '1rem' },
                          mb: { xs: 0.5, sm: 0 }
                        }}
                      >
                        {leave.applicant_name}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="textSecondary"
                        sx={{
                          fontSize: { xs: '0.75rem', sm: '0.875rem' },
                          mb: { xs: 0.25, sm: 0 }
                        }}
                      >
                        {leave.applicant_details} • {leave.leave_type_name}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="textSecondary"
                        sx={{
                          fontSize: { xs: '0.75rem', sm: '0.875rem' }
                        }}
                      >
                        {leave.start_date} to {leave.end_date} ({leave.total_days} days)
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: { xs: 1, sm: 1.5 },
                        flexDirection: { xs: 'row', sm: 'row' },
                        alignSelf: { xs: 'flex-end', sm: 'center' }
                      }}
                    >
                      <Chip
                        label={leave.leave_status_name}
                        color="warning"
                        size="small"
                        sx={{
                          fontSize: { xs: '0.6rem', sm: '0.75rem' },
                          height: { xs: '24px', sm: '32px' }
                        }}
                      />
                      <Button
                        variant="outlined"
                        onClick={() => navigate('/admin/leaves')}
                        sx={{
                          fontSize: { xs: '0.7rem', sm: '0.8rem' },
                          padding: { xs: '4px 8px', sm: '6px 12px' }
                        }}
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
