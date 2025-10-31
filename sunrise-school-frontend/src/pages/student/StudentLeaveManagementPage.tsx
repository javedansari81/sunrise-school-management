import React from 'react';
import StudentLayout from '../../components/Layout/StudentLayout';
import StudentLeaveManagement from '../../components/student/StudentLeaveManagement';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const StudentLeaveManagementPage: React.FC = () => {
  return (
    <StudentLayout>
      <ServiceConfigurationLoader service="leave-management">
        <StudentLeaveManagement />
      </ServiceConfigurationLoader>
    </StudentLayout>
  );
};

export default StudentLeaveManagementPage;
