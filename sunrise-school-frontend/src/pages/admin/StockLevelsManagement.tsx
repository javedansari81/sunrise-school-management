import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import StockLevelsManagementSystem from '../../components/admin/StockLevelsManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import { configurationService } from '../../services/configurationService';

const StockLevelsManagementContent: React.FC = () => {
  const configuration = configurationService.getServiceConfiguration('inventory-management');
  return <StockLevelsManagementSystem configuration={configuration} />;
};

const StockLevelsManagement: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="inventory-management">
        <StockLevelsManagementContent />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default StockLevelsManagement;

