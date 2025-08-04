import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import UserProfile from '../components/UserProfile';
import StudentProfile from '../components/StudentProfile';
import TeacherProfile from '../components/TeacherProfile';
import { useAuth } from '../contexts/AuthContext';

const Profile: React.FC = () => {
  const { user } = useAuth();

  const isStudent = user?.user_type?.toLowerCase() === 'student';
  const isTeacher = user?.user_type?.toLowerCase() === 'teacher';

  const getProfileDescription = () => {
    if (isStudent) return 'View and update your student profile information.';
    if (isTeacher) return 'View and update your teacher profile information.';
    return 'Manage your personal information and account settings.';
  };

  const renderProfile = () => {
    if (isStudent) return <StudentProfile />;
    if (isTeacher) return <TeacherProfile />;
    return <UserProfile />;
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

      {renderProfile()}
    </Container>
  );
};

export default Profile;
