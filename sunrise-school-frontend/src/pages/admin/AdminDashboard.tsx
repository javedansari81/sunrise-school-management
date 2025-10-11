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
import { leaveAPI, enhancedFeesAPI } from '../../services/api';

interface DashboardStats {
  students: {
    total: number;
    added_this_month: number;
    change_text: string;
  };
  teachers: {
    total: number;
    added_this_month: number;
    change_text: string;
  };
  fees: {
    pending_amount: number;
    collected_this_week: number;
    change_text: string;
    total_collected: number;
    collection_rate: number;
  };
  leave_requests: {
    total: number;
    pending: number;
    change_text: string;
  };
  expenses: {
    current_month: number;
    last_month: number;
    change: number;
    change_text: string;
  };
  revenue_growth: {
    percentage: number;
    current_quarter: number;
    last_quarter: number;
    change_text: string;
  };
}

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
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
        enhancedFeesAPI.getAdminDashboardStats(4), // 2025-26 session year
        leaveAPI.getPendingLeaves()
      ]);

      setDashboardStats(statsResponse.data);
      setPendingLeaves(Array.isArray(pendingResponse) ? pendingResponse : []);
      setError(null);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
      setDashboardStats(null);
      setPendingLeaves([]);
    } finally {
      setLoading(false);
    }
  };

  const getDashboardCards = () => {
    if (!dashboardStats) {
      return [
        {
          title: 'Total Students',
          value: '0',
          icon: <People fontSize="large" />,
          color: '#1976d2',
          change: 'Loading...',
        },
        {
          title: 'Total Teachers',
          value: '0',
          icon: <School fontSize="large" />,
          color: '#388e3c',
          change: 'Loading...',
        },
        {
          title: 'Pending Fees',
          value: '₹0',
          icon: <Payment fontSize="large" />,
          color: '#f57c00',
          change: 'Loading...',
        },
        {
          title: 'Leave Requests',
          value: '0',
          icon: <EventNote fontSize="large" />,
          color: '#7b1fa2',
          change: 'Loading...',
        },
        {
          title: 'Monthly Expenses',
          value: '₹0',
          icon: <AccountBalance fontSize="large" />,
          color: '#d32f2f',
          change: 'Loading...',
        },
        {
          title: 'Revenue Growth',
          value: '0%',
          icon: <TrendingUp fontSize="large" />,
          color: '#0288d1',
          change: 'Loading...',
        },
      ];
    }

    return [
      {
        title: 'Total Students',
        value: dashboardStats.students.total.toString(),
        icon: <People fontSize="large" />,
        color: '#1976d2',
        change: dashboardStats.students.change_text,
      },
      {
        title: 'Total Teachers',
        value: dashboardStats.teachers.total.toString(),
        icon: <School fontSize="large" />,
        color: '#388e3c',
        change: dashboardStats.teachers.change_text,
      },
      {
        title: 'Pending Fees',
        value: `₹${dashboardStats.fees.pending_amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`,
        icon: <Payment fontSize="large" />,
        color: '#f57c00',
        change: dashboardStats.fees.change_text,
      },
      {
        title: 'Leave Requests',
        value: dashboardStats.leave_requests.total.toString(),
        icon: <EventNote fontSize="large" />,
        color: '#7b1fa2',
        change: dashboardStats.leave_requests.change_text,
        clickable: true,
        onClick: () => navigate('/admin/leaves'),
      },
      {
        title: 'Monthly Expenses',
        value: `₹${dashboardStats.expenses.current_month.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`,
        icon: <AccountBalance fontSize="large" />,
        color: '#d32f2f',
        change: dashboardStats.expenses.change_text,
      },
      {
        title: 'Revenue Growth',
        value: `${dashboardStats.revenue_growth.percentage}%`,
        icon: <TrendingUp fontSize="large" />,
        color: '#0288d1',
        change: dashboardStats.revenue_growth.change_text,
      },
    ];
  };



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

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
            <CircularProgress size={60} />
          </Box>
        )}

        {/* Dashboard Cards */}
        {!loading && (
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
        )}

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
