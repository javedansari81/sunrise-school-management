import React from 'react';
import {
  BeachAccess as BeachAccessIcon,
  Dashboard as DashboardIcon,
  EventNote as AttendanceIcon,
  Notifications as NotificationsIcon,
  PersonAdd as PersonAddIcon,
} from '@mui/icons-material';
import PortalLayout, { NavItem } from './PortalLayout';

interface TeacherLayoutProps {
  children: React.ReactNode;
}

const items: NavItem[] = [
  { label: 'Dashboard', icon: <DashboardIcon />, path: '/teacher/dashboard' },
  { label: 'Leave Management', icon: <BeachAccessIcon />, path: '/teacher/leaves' },
  { label: 'Student Profiles', icon: <PersonAddIcon />, path: '/teacher/students' },
  { label: 'Attendance', icon: <AttendanceIcon />, path: '/teacher/attendance' },
  { label: 'Notifications', icon: <NotificationsIcon />, path: '/teacher/alerts' },
];

const TeacherLayout: React.FC<TeacherLayoutProps> = ({ children }) => (
  <PortalLayout portalName="Teacher Portal" items={items}>
    {children}
  </PortalLayout>
);

export default TeacherLayout;
