import React from 'react';
import {
  AccountBalance as AccountBalanceIcon,
  BeachAccess as BeachAccessIcon,
  CalendarMonth as CalendarMonthIcon,
  Dashboard as DashboardIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import PortalLayout, { NavItem } from './PortalLayout';

interface StudentLayoutProps {
  children: React.ReactNode;
}

const items: NavItem[] = [
  { label: 'Dashboard', icon: <DashboardIcon />, path: '/student/dashboard' },
  { label: 'Leave Management', icon: <BeachAccessIcon />, path: '/student/leaves' },
  { label: 'My Fees', icon: <AccountBalanceIcon />, path: '/student/fees' },
  { label: 'My Attendance', icon: <CalendarMonthIcon />, path: '/student/attendance' },
  { label: 'Notifications', icon: <NotificationsIcon />, path: '/student/alerts' },
];

const StudentLayout: React.FC<StudentLayoutProps> = ({ children }) => (
  <PortalLayout portalName="Student Portal" items={items}>
    {children}
  </PortalLayout>
);

export default StudentLayout;
