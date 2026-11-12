import React, { useState } from 'react';
import {
  Assignment as AssignmentIcon,
  ContactMail as ContactMailIcon,
  Home as HomeIcon,
  Info as InfoIcon,
  People as PeopleIcon,
  PhotoLibrary as PhotoLibraryIcon,
  School as SchoolIcon,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import Footer from './Footer';
import LoginPopup from '../LoginPopup';
import PortalLayout, { NavItem } from './PortalLayout';

interface MainLayoutProps {
  children: React.ReactNode;
}

const items: NavItem[] = [
  { label: 'Home', icon: <HomeIcon />, path: '/' },
  { label: 'About', icon: <InfoIcon />, path: '/about' },
  { label: 'Academics', icon: <SchoolIcon />, path: '/academics' },
  { label: 'Admissions', icon: <AssignmentIcon />, path: '/admissions' },
  { label: 'Faculty', icon: <PeopleIcon />, path: '/faculty' },
  { label: 'Gallery', icon: <PhotoLibraryIcon />, path: '/gallery' },
  { label: 'Contact', icon: <ContactMailIcon />, path: '/contact' },
];

const DASHBOARD_BY_ROLE: Record<string, string> = {
  ADMIN: '/admin/dashboard',
  SUPER_ADMIN: '/admin/dashboard',
  TEACHER: '/teacher/dashboard',
  STUDENT: '/student/dashboard',
};

/** The school's public website, in the same shell as the portals. */
const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { user, showLoginPopup, setShowLoginPopup } = useAuth();
  const [loginOpen, setLoginOpen] = useState(false);

  return (
    <>
      <PortalLayout
        portalName="School Website"
        items={items}
        publicSite={{
          onSignIn: () => setLoginOpen(true),
          footer: <Footer />,
          dashboardPath: DASHBOARD_BY_ROLE[user?.user_type?.toUpperCase() || ''],
        }}
      >
        {children}
      </PortalLayout>
      {/* Also opens when a protected page sends a visitor back here to sign in */}
      <LoginPopup
        open={loginOpen || showLoginPopup}
        onClose={() => {
          setLoginOpen(false);
          setShowLoginPopup(false);
        }}
      />
    </>
  );
};

export default MainLayout;
