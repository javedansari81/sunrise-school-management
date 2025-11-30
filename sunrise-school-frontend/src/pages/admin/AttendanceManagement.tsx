import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import AttendanceManagementSystem from '../../components/admin/AttendanceManagementSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const AttendanceManagement: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="attendance-management">
        <AttendanceManagementSystem />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default AttendanceManagement;

