import React from 'react';
import { Box } from '@mui/material';
import AdminLayout from '../../components/Layout/AdminLayout';
import TransportManagementSystem from '../../components/admin/TransportManagementSystem';

const TransportManagement: React.FC = () => {
  return (
    <AdminLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <TransportManagementSystem />
      </Box>
    </AdminLayout>
  );
};

export default TransportManagement;

