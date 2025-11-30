import React from 'react';
import StudentLayout from '../../components/Layout/StudentLayout';
import StudentAttendanceView from '../../components/student/StudentAttendanceView';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const StudentAttendancePage: React.FC = () => {
  return (
    <StudentLayout>
      <ServiceConfigurationLoader service="attendance-management">
        <StudentAttendanceView />
      </ServiceConfigurationLoader>
    </StudentLayout>
  );
};

export default StudentAttendancePage;

