import React from 'react';
import { Box } from '@mui/material';
import AdminLayout from '../../components/Layout/AdminLayout';
import AttendanceManagementSystem from '../../components/admin/AttendanceManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const AttendanceManagement: React.FC = () => {
  return (
    <AdminLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <ServiceConfigurationLoader service="attendance-management">
          <AttendanceManagementSystem />
        </ServiceConfigurationLoader>
      </Box>
    </AdminLayout>
  );
};

export default AttendanceManagement;

