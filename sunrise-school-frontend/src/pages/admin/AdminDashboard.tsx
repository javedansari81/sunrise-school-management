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
  Collapse,
  IconButton,
} from '@mui/material';
import {
  People,
  School,
  Payment,
  EventNote,
  AccountBalance,
  Visibility,
  DirectionsBus,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import AdminLayout from '../../components/Layout/AdminLayout';
import { leaveAPI, enhancedFeesAPI } from '../../services/api';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

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

interface EnhancedDashboardStats {
  student_management: {
    total_students: number;
    active_students: number;
    inactive_students: number;
    recent_enrollments: number;
    class_breakdown: Array<{
      class_name: string;
      total: number;
      male: number;
      female: number;
    }>;
  };
  fee_management: {
    total_collected: number;
    pending_fees: number;
    collection_rate: number;
    total_records: number;
    paid_records: number;
    monthly_trends: Array<{
      month: string;
      amount: number;
      count: number;
    }>;
  };
  leave_management: {
    total_requests: number;
    pending_approvals: number;
    approved_count: number;
    rejected_count: number;
    leave_type_breakdown: Array<{
      type: string;
      total: number;
      approved: number;
      rejected: number;
      pending: number;
    }>;
  };
  expense_management: {
    total_expenses: number;
    pending_approvals: number;
    category_breakdown: Array<{
      category: string;
      count: number;
      amount: number;
    }>;
    monthly_trends: Array<{
      month: string;
      amount: number;
      count: number;
    }>;
  };
  staff_management: {
    total_staff: number;
    active_staff: number;
    inactive_staff: number;
    department_breakdown: Array<{
      department: string;
      count: number;
    }>;
    qualification_breakdown: Array<{
      qualification: string;
      count: number;
    }>;
  };
  transport_service: {
    total_routes?: number;
    students_using_transport?: number;
    pending_fees?: number;
    collected_fees?: number;
    transport_type_breakdown?: Array<{
      type: string;
      enrollments: number;
      capacity: number;
    }>;
    error?: string;
  };
}

// Color palette for charts
const COLORS = ['#1976d2', '#388e3c', '#f57c00', '#7b1fa2', '#d32f2f', '#0288d1', '#00897b', '#c62828'];

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [enhancedStats, setEnhancedStats] = useState<EnhancedDashboardStats | null>(null);
  const [pendingLeaves, setPendingLeaves] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedCards, setExpandedCards] = useState<{ [key: string]: boolean }>({});

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, enhancedResponse, pendingResponse] = await Promise.all([
        enhancedFeesAPI.getAdminDashboardStats(4), // 2025-26 session year
        enhancedFeesAPI.getAdminDashboardEnhancedStats(4), // Enhanced stats
        leaveAPI.getPendingLeaves()
      ]);

      console.log('Enhanced Stats Response:', enhancedResponse.data);

      setDashboardStats(statsResponse.data);
      setEnhancedStats(enhancedResponse.data);
      setPendingLeaves(Array.isArray(pendingResponse) ? pendingResponse : []);
      setError(null);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      console.error('Error details:', err.response?.data);
      setError('Failed to load dashboard data. Please try again.');
      setDashboardStats(null);
      setEnhancedStats(null);
      setPendingLeaves([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleCardExpansion = (cardKey: string) => {
    setExpandedCards(prev => ({
      ...prev,
      [cardKey]: !prev[cardKey]
    }));
  };

  const getDashboardCards = () => {
    if (!dashboardStats || !enhancedStats) {
      return [
        {
          key: 'students',
          title: 'Student Management',
          value: '0',
          icon: <People fontSize="large" />,
          color: '#1976d2',
          change: 'Loading...',
          clickable: false,
          onClick: undefined,
        },
        {
          key: 'teachers',
          title: 'Staff Management',
          value: '0',
          icon: <School fontSize="large" />,
          color: '#388e3c',
          change: 'Loading...',
          clickable: false,
          onClick: undefined,
        },
        {
          key: 'fees',
          title: 'Fee Management',
          value: '₹0',
          icon: <Payment fontSize="large" />,
          color: '#f57c00',
          change: 'Loading...',
          clickable: false,
          onClick: undefined,
        },
        {
          key: 'leaves',
          title: 'Leave Management',
          value: '0',
          icon: <EventNote fontSize="large" />,
          color: '#7b1fa2',
          change: 'Loading...',
          clickable: false,
          onClick: undefined,
        },
        {
          key: 'expenses',
          title: 'Expense Management',
          value: '₹0',
          icon: <AccountBalance fontSize="large" />,
          color: '#d32f2f',
          change: 'Loading...',
          clickable: false,
          onClick: undefined,
        },
        {
          key: 'transport',
          title: 'Transport Service',
          value: '0',
          icon: <DirectionsBus fontSize="large" />,
          color: '#00897b',
          change: 'Loading...',
          clickable: false,
          onClick: undefined,
        },
      ];
    }

    return [
      {
        key: 'students',
        title: 'Student Management',
        value: (enhancedStats.student_management?.total_students || 0).toString(),
        icon: <People fontSize="large" />,
        color: '#1976d2',
        change: `${enhancedStats.student_management?.active_students || 0} Active • ${enhancedStats.student_management?.recent_enrollments || 0} New`,
        clickable: true,
        onClick: () => navigate('/admin/students'),
        details: enhancedStats.student_management,
      },
      {
        key: 'teachers',
        title: 'Staff Management',
        value: (enhancedStats.staff_management?.total_staff || 0).toString(),
        icon: <School fontSize="large" />,
        color: '#388e3c',
        change: `${enhancedStats.staff_management?.active_staff || 0} Active Staff`,
        clickable: true,
        onClick: () => navigate('/admin/teachers'),
        details: enhancedStats.staff_management,
      },
      {
        key: 'fees',
        title: 'Fee Management',
        value: `₹${(enhancedStats.fee_management?.total_collected || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`,
        icon: <Payment fontSize="large" />,
        color: '#f57c00',
        change: `${(enhancedStats.fee_management?.collection_rate || 0).toFixed(1)}% Collection Rate`,
        clickable: true,
        onClick: () => navigate('/admin/fees'),
        details: enhancedStats.fee_management,
      },
      {
        key: 'leaves',
        title: 'Leave Management',
        value: (enhancedStats.leave_management?.total_requests || 0).toString(),
        icon: <EventNote fontSize="large" />,
        color: '#7b1fa2',
        change: `${enhancedStats.leave_management?.pending_approvals || 0} Pending Approval`,
        clickable: true,
        onClick: () => navigate('/admin/leaves'),
        details: enhancedStats.leave_management,
      },
      {
        key: 'expenses',
        title: 'Expense Management',
        value: `₹${(enhancedStats.expense_management?.total_expenses || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`,
        icon: <AccountBalance fontSize="large" />,
        color: '#d32f2f',
        change: `${enhancedStats.expense_management?.pending_approvals || 0} Pending Approval`,
        clickable: true,
        onClick: () => navigate('/admin/expenses'),
        details: enhancedStats.expense_management,
      },
      {
        key: 'transport',
        title: 'Transport Service',
        value: enhancedStats.transport_service?.error ? 'N/A' : (enhancedStats.transport_service?.students_using_transport || 0).toString(),
        icon: <DirectionsBus fontSize="large" />,
        color: '#00897b',
        change: enhancedStats.transport_service?.error ? 'Data unavailable' : `${enhancedStats.transport_service?.total_routes || 0} Routes Active`,
        clickable: true,
        onClick: () => navigate('/admin/transport'),
        details: enhancedStats.transport_service,
      },
    ];
  };



  // Render detailed statistics for each card
  const renderCardDetails = (card: any) => {
    if (!card.details) return null;

    switch (card.key) {
      case 'students':
        return (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Class Distribution
            </Typography>
            {card.details.class_breakdown && card.details.class_breakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={card.details.class_breakdown}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="class_name" style={{ fontSize: '0.75rem' }} />
                  <YAxis style={{ fontSize: '0.75rem' }} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: '0.75rem' }} />
                  <Bar dataKey="total" fill={card.color} name="Total Students" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Typography variant="body2" color="text.secondary">No data available</Typography>
            )}
            <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip label={`Active: ${card.details.active_students || 0}`} size="small" color="success" />
              <Chip label={`Inactive: ${card.details.inactive_students || 0}`} size="small" color="default" />
            </Box>
          </Box>
        );

      case 'teachers':
        return (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Department Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={card.details.department_breakdown}
                  dataKey="count"
                  nameKey="department"
                  cx="50%"
                  cy="50%"
                  outerRadius={60}
                  label={(entry) => `${entry.department}: ${entry.count}`}
                >
                  {card.details.department_breakdown.map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        );

      case 'fees':
        return (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Collection Trends (Last 12 Months)
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={card.details.monthly_trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" style={{ fontSize: '0.7rem' }} />
                <YAxis style={{ fontSize: '0.75rem' }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '0.75rem' }} />
                <Line type="monotone" dataKey="amount" stroke={card.color} name="Amount Collected" />
              </LineChart>
            </ResponsiveContainer>
            <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip label={`Pending: ₹${card.details.pending_fees.toLocaleString('en-IN')}`} size="small" color="warning" />
              <Chip label={`Paid Records: ${card.details.paid_records}/${card.details.total_records}`} size="small" color="success" />
            </Box>
          </Box>
        );

      case 'leaves':
        return (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Leave Type Breakdown
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={card.details.leave_type_breakdown}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" style={{ fontSize: '0.7rem' }} />
                <YAxis style={{ fontSize: '0.75rem' }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '0.75rem' }} />
                <Bar dataKey="approved" fill="#4caf50" name="Approved" stackId="a" />
                <Bar dataKey="pending" fill="#ff9800" name="Pending" stackId="a" />
                <Bar dataKey="rejected" fill="#f44336" name="Rejected" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
            <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip label={`Approved: ${card.details.approved_count}`} size="small" color="success" />
              <Chip label={`Rejected: ${card.details.rejected_count}`} size="small" color="error" />
            </Box>
          </Box>
        );

      case 'expenses':
        return (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Category Breakdown
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={card.details.category_breakdown.slice(0, 5)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" style={{ fontSize: '0.7rem' }} />
                <YAxis style={{ fontSize: '0.75rem' }} />
                <Tooltip />
                <Bar dataKey="amount" fill={card.color} name="Amount" />
              </BarChart>
            </ResponsiveContainer>
            {card.details.monthly_trends && card.details.monthly_trends.length > 0 && (
              <>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
                  Monthly Spending Trends
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={card.details.monthly_trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" style={{ fontSize: '0.7rem' }} />
                    <YAxis style={{ fontSize: '0.75rem' }} />
                    <Tooltip />
                    <Line type="monotone" dataKey="amount" stroke={card.color} name="Amount" />
                  </LineChart>
                </ResponsiveContainer>
              </>
            )}
          </Box>
        );

      case 'transport':
        // Check if there's an error in transport service data
        if (card.details.error) {
          return (
            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
              <Typography variant="body2" color="error">
                Transport service data unavailable. Please check the database configuration.
              </Typography>
            </Box>
          );
        }
        return (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Transport Type Utilization
            </Typography>
            {card.details.transport_type_breakdown && card.details.transport_type_breakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={card.details.transport_type_breakdown}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" style={{ fontSize: '0.7rem' }} />
                  <YAxis style={{ fontSize: '0.75rem' }} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: '0.75rem' }} />
                  <Bar dataKey="enrollments" fill={card.color} name="Enrollments" />
                  <Bar dataKey="capacity" fill="#90caf9" name="Capacity" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Typography variant="body2" color="text.secondary">No transport data available</Typography>
            )}
            <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip label={`Collected: ₹${(card.details.collected_fees || 0).toLocaleString('en-IN')}`} size="small" color="success" />
              <Chip label={`Pending: ₹${(card.details.pending_fees || 0).toLocaleString('en-IN')}`} size="small" color="warning" />
            </Box>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <AdminLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
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
                lg: 'repeat(3, 1fr)',
              },
              gap: { xs: 2, sm: 2, md: 3 },
              mb: { xs: 3, sm: 4 },
              alignItems: 'start', // Prevent cards from stretching to match tallest card
            }}
          >
          {getDashboardCards().map((card) => (
            <Card
              key={card.key}
              sx={{
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  boxShadow: { xs: 2, sm: 4 },
                },
              }}
            >
              <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                <Box
                  display="flex"
                  alignItems="center"
                  justifyContent="space-between"
                  mb={{ xs: 1.5, sm: 2 }}
                  sx={{ cursor: card.clickable ? 'pointer' : 'default' }}
                  onClick={card.onClick}
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
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleCardExpansion(card.key);
                    }}
                  >
                    {expandedCards[card.key] ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Box>
                <Box sx={{ cursor: card.clickable ? 'pointer' : 'default' }} onClick={card.onClick}>
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
                </Box>

                {/* Expandable Details Section */}
                <Collapse in={expandedCards[card.key]} timeout="auto" unmountOnExit>
                  {renderCardDetails(card)}
                </Collapse>
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
