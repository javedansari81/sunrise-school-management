import React from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Card,
  CardContent,
  IconButton,
  Button,
} from '@mui/material';
import {
  People,
  School,
  Payment,
  EventNote,
  AccountBalance,
  TrendingUp,
  Notifications,
  Settings,
  ExitToApp,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    navigate('/admin/login');
  };

  const dashboardCards = [
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
      value: '8',
      icon: <EventNote fontSize="large" />,
      color: '#7b1fa2',
      change: '3 pending approval',
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

  const quickActions = [
    { title: 'Fees Management', path: '/admin/fees', color: '#1976d2' },
    { title: 'Leave Management', path: '/admin/leaves', color: '#388e3c' },
    { title: 'Expense Management', path: '/admin/expenses', color: '#f57c00' },
    { title: 'Student Profiles', path: '/admin/students', color: '#7b1fa2' },
  ];

  return (
    <Box sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      {/* Header */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Container maxWidth="lg">
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h4" fontWeight="bold" color="primary">
              Admin Dashboard
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <IconButton color="primary">
                <Notifications />
              </IconButton>
              <IconButton color="primary">
                <Settings />
              </IconButton>
              <Button
                variant="outlined"
                startIcon={<ExitToApp />}
                onClick={handleLogout}
              >
                Logout
              </Button>
            </Box>
          </Box>
        </Container>
      </Paper>

      <Container maxWidth="lg">
        {/* Welcome Section */}
        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            Welcome back, Administrator!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's what's happening at Sunrise National Public School today.
          </Typography>
        </Box>

        {/* Dashboard Cards */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
          {dashboardCards.map((card, index) => (
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

        {/* Quick Actions */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            Quick Actions
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {quickActions.map((action, index) => (
              <Box key={index} sx={{ flex: '1 1 200px', minWidth: 200 }}>
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  sx={{
                    backgroundColor: action.color,
                    py: 2,
                    '&:hover': {
                      backgroundColor: action.color,
                      opacity: 0.9,
                    },
                  }}
                  onClick={() => navigate(action.path)}
                >
                  {action.title}
                </Button>
              </Box>
            ))}
          </Box>
        </Paper>

        {/* Recent Activities */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            Recent Activities
          </Typography>
          <Box>
            <Typography variant="body2" color="text.secondary">
              • New student admission: John Smith (Class 5)
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Fee payment received: ₹15,000 from Sarah Johnson
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Leave request approved for Mike Davis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Expense approved: Office supplies - ₹5,000
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default AdminDashboard;
