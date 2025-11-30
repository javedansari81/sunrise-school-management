import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import LeaveManagementSystem from '../../components/admin/LeaveManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const LeaveManagement: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="leave-management">
        <LeaveManagementSystem />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default LeaveManagement;
