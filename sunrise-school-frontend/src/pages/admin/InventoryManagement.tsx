import React from 'react';
import { Box } from '@mui/material';
import AdminLayout from '../../components/Layout/AdminLayout';
import InventoryManagementSystem from '../../components/admin/InventoryManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { configurationService } from '../../services/configurationService';

const InventoryManagementContent: React.FC = () => {
  const configuration = configurationService.getServiceConfiguration('inventory-management');
  return <InventoryManagementSystem configuration={configuration} />;
};

const InventoryManagement: React.FC = () => {
  return (
    <AdminLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <ServiceConfigurationLoader service="inventory-management">
          <InventoryManagementContent />
        </ServiceConfigurationLoader>
      </Box>
    </AdminLayout>
  );
};

export default InventoryManagement;

