import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import TransportManagementSystem from '../../components/admin/TransportManagementSystem';

const TransportManagement: React.FC = () => {
  return (
    <AdminLayout>
      <TransportManagementSystem />
    </AdminLayout>
  );
};

export default TransportManagement;

