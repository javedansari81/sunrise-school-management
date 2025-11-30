import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import InventoryManagementSystem from '../../components/admin/InventoryManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import { configurationService } from '../../services/configurationService';

const InventoryManagementContent: React.FC = () => {
  const configuration = configurationService.getServiceConfiguration('inventory-management');
  return <InventoryManagementSystem configuration={configuration} />;
};

const InventoryManagement: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="inventory-management">
        <InventoryManagementContent />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default InventoryManagement;

