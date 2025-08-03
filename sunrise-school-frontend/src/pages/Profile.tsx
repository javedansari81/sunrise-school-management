import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import UserProfile from '../components/UserProfile';
import StudentProfile from '../components/StudentProfile';
import { useAuth } from '../contexts/AuthContext';

const Profile: React.FC = () => {
  const { user } = useAuth();

  const isStudent = user?.user_type?.toLowerCase() === 'student';

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {isStudent
            ? 'View and update your student profile information.'
            : 'Manage your personal information and account settings.'
          }
        </Typography>
      </Box>

      {isStudent ? <StudentProfile /> : <UserProfile />}
    </Container>
  );
};

export default Profile;
