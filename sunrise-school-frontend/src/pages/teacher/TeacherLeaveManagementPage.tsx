import React from 'react';
import {
  Box,
} from '@mui/material';
import TeacherLayout from '../../components/Layout/TeacherLayout';
import TeacherLeaveManagement from '../../components/teacher/TeacherLeaveManagement';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const TeacherLeaveManagementPage: React.FC = () => {
  return (
    <TeacherLayout>
      <ServiceConfigurationLoader service="leave-management">
        <TeacherLeaveManagement />
      </ServiceConfigurationLoader>
    </TeacherLayout>
  );
};

export default TeacherLeaveManagementPage;
