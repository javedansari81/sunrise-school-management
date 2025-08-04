import React from 'react';
import {
  Box,
} from '@mui/material';
import AdminLayout from '../../components/Layout/AdminLayout';
import TeacherProfilesSystem from '../../components/admin/TeacherProfilesSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

const TeacherProfiles: React.FC = () => {
  return (
    <AdminLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <ServiceConfigurationLoader service="teacher-management">
          <TeacherProfilesSystem />
        </ServiceConfigurationLoader>
      </Box>
    </AdminLayout>
  );
};

export default TeacherProfiles;
