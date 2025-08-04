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
    { label: 'Teacher Profiles', icon: <PersonAdd />, path: '/admin/teachers' },
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
      <Paper elevation={1} sx={{ mb: { xs: 2, md: 3 } }}>
        <Container maxWidth="lg" sx={{ px: { xs: 1, sm: 2, md: 3 } }}>
          {/* Top Header Bar */}
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            sx={{
              p: { xs: 1, sm: 2 },
              flexWrap: 'wrap',
              gap: { xs: 1, sm: 0 }
            }}
          >
            <Typography
              variant="h4"
              fontWeight="bold"
              color="primary"
              sx={{
                fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' },
                lineHeight: 1.2
              }}
            >
              Admin Dashboard
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <IconButton
                color="primary"
                size="small"
                sx={{
                  display: { xs: 'flex', sm: 'flex' },
                  p: { xs: 1, sm: 1.5 }
                }}
              >
                <Notifications fontSize="small" />
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
              allowScrollButtonsMobile
              sx={{
                '& .MuiTab-root': {
                  minHeight: { xs: 48, sm: 56, md: 64 },
                  textTransform: 'none',
                  fontSize: { xs: '0.75rem', sm: '0.875rem', md: '1rem' },
                  fontWeight: 500,
                  minWidth: { xs: 80, sm: 120, md: 160 },
                  px: { xs: 1, sm: 2 },
                },
                '& .Mui-selected': {
                  backgroundColor: 'rgba(25, 118, 210, 0.08)',
                  color: 'primary.main',
                  fontWeight: 600,
                },
                '& .MuiTabs-scrollButtons': {
                  '&.Mui-disabled': {
                    opacity: 0.3,
                  },
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
                    '& .MuiSvgIcon-root': {
                      fontSize: { xs: '1rem', sm: '1.25rem', md: '1.5rem' },
                    },
                    flexDirection: { xs: 'column', sm: 'row' },
                    gap: { xs: 0.5, sm: 1 },
                  }}
                />
              ))}
            </Tabs>
          </Box>
        </Container>
      </Paper>

      {/* Page Content */}
      <Container
        maxWidth="lg"
        sx={{
          px: { xs: 1, sm: 2, md: 3 },
          pb: { xs: 2, sm: 3, md: 4 }
        }}
      >
        {children}
      </Container>
    </Box>
  );
};

export default AdminLayout;
