import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import AdminLayout from '../components/Layout/AdminLayout';
import TeacherLayout from '../components/Layout/TeacherLayout';
import StudentLayout from '../components/Layout/StudentLayout';
import Profile from './Profile';

/** The profile page inside the portal of whoever is logged in. */
const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const role = user?.user_type?.toUpperCase();

  if (role === 'TEACHER') return <TeacherLayout><Profile /></TeacherLayout>;
  if (role === 'STUDENT') return <StudentLayout><Profile /></StudentLayout>;
  if (role === 'ADMIN' || role === 'SUPER_ADMIN') return <AdminLayout><Profile /></AdminLayout>;
  return <Profile />;
};

export default ProfilePage;
