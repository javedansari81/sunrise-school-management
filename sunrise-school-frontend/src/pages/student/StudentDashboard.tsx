import React from 'react';
import {
  Box,
} from '@mui/material';
import StudentLayout from '../../components/Layout/StudentLayout';
import StudentDashboardOverview from '../../components/student/StudentDashboardOverview';

const StudentDashboard: React.FC = () => {
  return (
    <StudentLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <StudentDashboardOverview />
      </Box>
    </StudentLayout>
  );
};

export default StudentDashboard;
