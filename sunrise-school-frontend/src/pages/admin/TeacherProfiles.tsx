import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import TeacherProfilesSystem from '../../components/admin/TeacherProfilesSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const TeacherProfiles: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="teacher-management">
        <TeacherProfilesSystem />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default TeacherProfiles;
