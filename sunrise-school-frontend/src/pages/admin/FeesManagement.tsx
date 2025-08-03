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
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <Typography
          variant="h4"
          gutterBottom
          sx={{
            fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' },
            mb: { xs: 1, sm: 2 }
          }}
        >
          Fee Management System
        </Typography>
        <Typography
          variant="body1"
          color="textSecondary"
          sx={{
            mb: { xs: 2, sm: 3 },
            fontSize: { xs: '0.875rem', sm: '1rem' }
          }}
        >
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
