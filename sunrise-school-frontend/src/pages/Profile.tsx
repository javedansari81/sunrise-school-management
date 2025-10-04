import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  TextField,
  Button,
  Alert
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const Profile: React.FC = () => {
  const { user } = useAuth();

  const getProfileDescription = () => {
    if (user?.user_type?.toLowerCase() === 'student') {
      return 'View and update your student profile information.';
    }
    if (user?.user_type?.toLowerCase() === 'teacher') {
      return 'View and update your teacher profile information.';
    }
    return 'Manage your personal information and account settings.';
  };

  const getUserTypeDisplay = () => {
    if (!user?.user_type) return 'User';
    return user.user_type.charAt(0).toUpperCase() + user.user_type.slice(1).toLowerCase();
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {getProfileDescription()}
        </Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Profile Information
        </Typography>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Email"
              value={user?.email || ''}
              disabled
              variant="outlined"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="User Type"
              value={getUserTypeDisplay()}
              disabled
              variant="outlined"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Phone Number"
              value={(user as any)?.phone_number || 'Not provided'}
              disabled
              variant="outlined"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="User ID"
              value={user?.id || ''}
              disabled
              variant="outlined"
            />
          </Grid>
        </Grid>

        <Box sx={{ mt: 3 }}>
          <Alert severity="info">
            Profile editing functionality will be available in a future update.
            Contact the administrator if you need to update your information.
          </Alert>
        </Box>

        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          <Button variant="outlined" disabled>
            Edit Profile
          </Button>
          <Button variant="outlined" disabled>
            Change Password
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Profile;
