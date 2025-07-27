import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import UserProfile from '../components/UserProfile';

const Profile: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your personal information and account settings.
        </Typography>
      </Box>
      
      <UserProfile />
    </Container>
  );
};

export default Profile;
