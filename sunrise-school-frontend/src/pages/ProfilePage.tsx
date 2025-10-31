import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import TeacherLayout from '../components/Layout/TeacherLayout';
import StudentLayout from '../components/Layout/StudentLayout';
import Profile from './Profile';

/**
 * ProfilePage wrapper that applies the appropriate layout based on user type
 * - Teachers: Use TeacherLayout
 * - Students: Use StudentLayout
 * - Others: Use MainLayout (already applied in App.tsx routing)
 */
const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  // For teachers, wrap Profile in TeacherLayout
  if (user?.user_type?.toLowerCase() === 'teacher') {
    return (
      <TeacherLayout>
        <Profile />
      </TeacherLayout>
    );
  }

  // For students, wrap Profile in StudentLayout
  if (user?.user_type?.toLowerCase() === 'student') {
    return (
      <StudentLayout>
        <Profile />
      </StudentLayout>
    );
  }

  // For others, Profile is already wrapped in MainLayout via App.tsx routing
  return <Profile />;
};

export default ProfilePage;

