import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import PricingManagementSystem from '../../components/admin/PricingManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import { configurationService } from '../../services/configurationService';

const PricingManagementContent: React.FC = () => {
  const configuration = configurationService.getServiceConfiguration('inventory-management');
  return <PricingManagementSystem configuration={configuration} />;
};

const PricingManagement: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="inventory-management">
        <PricingManagementContent />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default PricingManagement;

