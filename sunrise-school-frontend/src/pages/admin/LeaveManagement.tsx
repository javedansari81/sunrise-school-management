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
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Leave Management System
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
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
