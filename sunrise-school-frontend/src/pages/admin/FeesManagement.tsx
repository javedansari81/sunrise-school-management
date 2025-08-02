import React from 'react';
import {
  Box,
  Typography,
} from '@mui/material';
import AdminLayout from '../../components/Layout/AdminLayout';
import SimpleEnhancedFeeManagement from '../../components/fees/SimpleEnhancedFeeManagement';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const FeesManagement: React.FC = () => {
  return (
    <AdminLayout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Fee Management System
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
          Manage student fees with monthly tracking and payment history
        </Typography>

        <ServiceConfigurationLoader service="fee-management">
          <SimpleEnhancedFeeManagement />
        </ServiceConfigurationLoader>
      </Box>
    </AdminLayout>
  );
};

export default FeesManagement;
