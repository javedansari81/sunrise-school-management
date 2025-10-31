import React from 'react';
import {
  Box,
} from '@mui/material';
import TeacherLayout from '../../components/Layout/TeacherLayout';
import TeacherDashboardOverview from '../../components/teacher/TeacherDashboardOverview';

const TeacherDashboard: React.FC = () => {
  return (
    <TeacherLayout>
      <TeacherDashboardOverview />
    </TeacherLayout>
  );
};

export default TeacherDashboard;
