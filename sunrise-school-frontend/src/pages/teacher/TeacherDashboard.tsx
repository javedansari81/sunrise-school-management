import React from 'react';
import {
  Box,
} from '@mui/material';
import TeacherLayout from '../../components/Layout/TeacherLayout';
import TeacherDashboardOverview from '../../components/teacher/TeacherDashboardOverview';

const TeacherDashboard: React.FC = () => {
  return (
    <TeacherLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <TeacherDashboardOverview />
      </Box>
    </TeacherLayout>
  );
};

export default TeacherDashboard;
