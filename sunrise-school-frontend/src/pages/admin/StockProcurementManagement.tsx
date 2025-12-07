import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import StockProcurementManagementSystem from '../../components/admin/StockProcurementManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import { configurationService } from '../../services/configurationService';

const StockProcurementManagementContent: React.FC = () => {
  const configuration = configurationService.getServiceConfiguration('inventory-management');
  return <StockProcurementManagementSystem configuration={configuration} />;
};

const StockProcurementManagement: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="inventory-management">
        <StockProcurementManagementContent />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default StockProcurementManagement;

