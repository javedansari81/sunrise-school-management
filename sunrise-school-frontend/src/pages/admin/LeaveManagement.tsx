import React from 'react';
import {
  Box,
} from '@mui/material';
import AdminLayout from '../../components/Layout/AdminLayout';
import LeaveManagementSystem from '../../components/admin/LeaveManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const LeaveManagement: React.FC = () => {
  return (
    <AdminLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <ServiceConfigurationLoader service="leave-management">
          <LeaveManagementSystem />
        </ServiceConfigurationLoader>
      </Box>
    </AdminLayout>
  );
};

export default LeaveManagement;
