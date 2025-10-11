import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import SimpleEnhancedFeeManagement from '../../components/fees/SimpleEnhancedFeeManagement';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const FeesManagement: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="fee-management">
        <SimpleEnhancedFeeManagement />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default FeesManagement;
