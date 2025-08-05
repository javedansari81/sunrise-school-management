import React from 'react';
import {
  Box,
} from '@mui/material';
import StudentLayout from '../../components/Layout/StudentLayout';
import StudentLeaveManagement from '../../components/student/StudentLeaveManagement';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const StudentDashboard: React.FC = () => {
  return (
    <StudentLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <ServiceConfigurationLoader service="leave-management">
          <StudentLeaveManagement />
        </ServiceConfigurationLoader>
      </Box>
    </StudentLayout>
  );
};

export default StudentDashboard;
