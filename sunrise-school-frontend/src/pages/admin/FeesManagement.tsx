import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import FeeManagementComponent from '../../components/fees/FeeManagementComponent';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const FeesManagement: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="fee-management">
        <FeeManagementComponent />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default FeesManagement;
