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
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <ServiceConfigurationLoader service="leave-management">
          <TeacherLeaveManagement />
        </ServiceConfigurationLoader>
      </Box>
    </TeacherLayout>
  );
};

export default TeacherLeaveManagementPage;
