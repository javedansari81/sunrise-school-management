import React from 'react';
import {
  Typography,
  Box,
} from '@mui/material';
import AdminLayout from '../../components/Layout/AdminLayout';
import LeaveManagementSystem from '../../components/admin/LeaveManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const LeaveManagement: React.FC = () => {
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
          Leave Management System
        </Typography>
        <Typography
          variant="body1"
          color="textSecondary"
          sx={{
            mb: { xs: 2, sm: 3 },
            fontSize: { xs: '0.875rem', sm: '1rem' }
          }}
        >
          Manage employee leave requests and approvals
        </Typography>

        <ServiceConfigurationLoader service="leave-management">
          <LeaveManagementSystem />
        </ServiceConfigurationLoader>
      </Box>
    </AdminLayout>
  );
};

export default LeaveManagement;
