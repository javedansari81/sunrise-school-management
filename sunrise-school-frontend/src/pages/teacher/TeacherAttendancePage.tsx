/**
 * Teacher Attendance Page
 * Wrapper component that provides layout and configuration context
 */

import React from 'react';
import TeacherLayout from '../../components/Layout/TeacherLayout';
import TeacherAttendance from '../../components/teacher/TeacherAttendance';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const TeacherAttendancePage: React.FC = () => {
  return (
    <TeacherLayout>
      <ServiceConfigurationLoader service="attendance-management">
        <TeacherAttendance />
      </ServiceConfigurationLoader>
    </TeacherLayout>
  );
};

export default TeacherAttendancePage;

