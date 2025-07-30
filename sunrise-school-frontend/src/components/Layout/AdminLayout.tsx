import React from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  IconButton,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Notifications,
  Dashboard as DashboardIcon,
  AttachMoney,
  BeachAccess,
  Receipt,
  PersonAdd,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const adminTabs = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/admin/dashboard' },
    { label: 'Fees Management', icon: <AttachMoney />, path: '/admin/fees' },
    { label: 'Leave Management', icon: <BeachAccess />, path: '/admin/leaves' },
    { label: 'Expense Management', icon: <Receipt />, path: '/admin/expenses' },
    { label: 'Student Profiles', icon: <PersonAdd />, path: '/admin/students' },
  ];

  // Get current tab index based on location
  const getCurrentTabIndex = () => {
    const currentPath = location.pathname;
    const tabIndex = adminTabs.findIndex(tab => tab.path === currentPath);
    return tabIndex >= 0 ? tabIndex : 0;
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    navigate(adminTabs[newValue].path);
  };

  return (
    <Box sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      {/* Header with Navigation Tabs */}
      <Paper elevation={1} sx={{ mb: 3 }}>
        <Container maxWidth="lg">
          {/* Top Header Bar */}
          <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ p: 2 }}>
            <Typography variant="h4" fontWeight="bold" color="primary">
              Admin Dashboard
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <IconButton color="primary">
                <Notifications />
              </IconButton>
            </Box>
          </Box>
          
          {/* Navigation Tabs */}
          <Box sx={{ borderTop: 1, borderColor: 'divider' }}>
            <Tabs
              value={getCurrentTabIndex()}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                '& .MuiTab-root': {
                  minHeight: 64,
                  textTransform: 'none',
                  fontSize: '1rem',
                  fontWeight: 500,
                },
                '& .Mui-selected': {
                  backgroundColor: 'rgba(25, 118, 210, 0.08)',
                  color: 'primary.main',
                  fontWeight: 600,
                },
              }}
            >
              {adminTabs.map((tab, index) => (
                <Tab
                  key={index}
                  icon={tab.icon}
                  label={tab.label}
                  iconPosition="start"
                  sx={{
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.04)',
                    },
                  }}
                />
              ))}
            </Tabs>
          </Box>
        </Container>
      </Paper>

      {/* Page Content */}
      <Container maxWidth="lg">
        {children}
      </Container>
    </Box>
  );
};

export default AdminLayout;
