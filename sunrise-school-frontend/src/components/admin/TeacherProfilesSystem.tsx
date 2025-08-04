import React from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Add as AddIcon
} from '@mui/icons-material';

import { useAuth } from '../../contexts/AuthContext';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';

const TeacherProfilesSystem: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const {
    isLoaded: configLoaded,
    isLoading: configLoading,
    error: configError
  } = useServiceConfiguration('teacher-management');

  if (configLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Loading teacher management configuration...
        </Typography>
      </Box>
    );
  }

  if (configError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Configuration Error: {configError}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header Section with Title and New Teacher Button */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        flexDirection={{ xs: 'column', sm: 'row' }}
        gap={{ xs: 2, sm: 0 }}
        mb={{ xs: 3, sm: 4 }}
      >
        <Typography
          variant="h4"
          fontWeight="bold"
          sx={{
            fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' }
          }}
        >
          Teacher Profiles
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {/* Handle new teacher */}}
          sx={{
            fontSize: { xs: '0.875rem', sm: '1rem' },
            padding: { xs: '6px 12px', sm: '8px 16px' },
            alignSelf: { xs: 'flex-end', sm: 'auto' }
          }}
        >
          New Teacher
        </Button>
      </Box>

      {/* Content Section */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Teacher Management System
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Teacher profiles management functionality is being loaded...
        </Typography>
        <Typography variant="body2" sx={{ mt: 2 }}>
          Configuration Status: {configLoaded ? 'Loaded' : 'Loading...'}
        </Typography>
        <Typography variant="body2">
          Authentication Status: {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
        </Typography>
      </Paper>
    </Box>
  );
};

export default TeacherProfilesSystem;
