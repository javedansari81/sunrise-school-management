import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
} from '@mui/material';
import {
  People,
  School,
  Payment,
  EventNote,
  AccountBalance,
  TrendingUp,
} from '@mui/icons-material';
import AdminLayout from '../../components/Layout/AdminLayout';

const AdminDashboard: React.FC = () => {
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
      </Box>
    </AdminLayout>
  );
};

export default AdminDashboard;
