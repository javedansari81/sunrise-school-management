import React from 'react';
import {
  Box,
} from '@mui/material';
import StudentLayout from '../../components/Layout/StudentLayout';
import StudentFeeManagement from '../../components/student/StudentFeeManagement';

const StudentFeeManagementPage: React.FC = () => {
  return (
    <StudentLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <StudentFeeManagement />
      </Box>
    </StudentLayout>
  );
};

export default StudentFeeManagementPage;

