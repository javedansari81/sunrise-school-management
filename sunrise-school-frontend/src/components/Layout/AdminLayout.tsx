import React, { useMemo } from 'react';
import {
  AccountBalance as AccountBalanceIcon,
  Assessment as AssessmentIcon,
  AttachMoney,
  BeachAccess,
  Dashboard as DashboardIcon,
  DirectionsBus as DirectionsBusIcon,
  EventAvailable as AttendanceIcon,
  Inventory as InventoryIcon,
  LocalShipping as LocalShippingIcon,
  Notifications as NotificationsIcon,
  People as PeopleIcon,
  PersonAdd,
  PhotoLibrary as PhotoLibraryIcon,
  PointOfSale as PointOfSaleIcon,
  PriceChange as PriceChangeIcon,
  Receipt,
  ReceiptLong as ReceiptLongIcon,
  School as SchoolIcon,
  Settings as SettingsIcon,
  Storefront as StorefrontIcon,
  TrendingUp as SessionProgressionIcon,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import PortalLayout, { NavItem } from './PortalLayout';

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const { user } = useAuth();
  const isSuperAdmin = user?.user_type?.toUpperCase() === 'SUPER_ADMIN';

  const items: NavItem[] = useMemo(() => {
    const menu: NavItem[] = [
      { label: 'Dashboard', icon: <DashboardIcon />, path: '/admin/dashboard' },
      {
        label: 'People',
        icon: <PeopleIcon />,
        children: [
          { label: 'Student Profiles', icon: <PersonAdd />, path: '/admin/students' },
          { label: 'Teacher Profiles', icon: <SchoolIcon />, path: '/admin/teachers' },
        ],
      },
      {
        label: 'Finance',
        icon: <AccountBalanceIcon />,
        children: [
          { label: 'Fees', icon: <AttachMoney />, path: '/admin/fees' },
          { label: 'Transport', icon: <DirectionsBusIcon />, path: '/admin/transport' },
          { label: 'Expenses', icon: <Receipt />, path: '/admin/expenses' },
        ],
      },
      {
        label: 'School Shop',
        icon: <StorefrontIcon />,
        children: [
          { label: 'Shop Here', icon: <PointOfSaleIcon />, path: '/admin/shop-sales' },
          { label: 'Stock Procurements', icon: <LocalShippingIcon />, path: '/admin/stock-procurement' },
          { label: 'Pricing', icon: <PriceChangeIcon />, path: '/admin/pricing' },
          { label: 'Stock Levels', icon: <InventoryIcon />, path: '/admin/stock-levels' },
        ],
      },
      {
        label: 'Operations',
        icon: <SettingsIcon />,
        children: [
          { label: 'Leave', icon: <BeachAccess />, path: '/admin/leaves' },
          { label: 'Attendance', icon: <AttendanceIcon />, path: '/admin/attendance' },
          { label: 'Gallery', icon: <PhotoLibraryIcon />, path: '/admin/gallery-management' },
          { label: 'Notifications', icon: <NotificationsIcon />, path: '/admin/alerts' },
        ],
      },
      {
        label: 'Reports',
        icon: <AssessmentIcon />,
        children: [
          { label: 'Student UDISE Report', icon: <PeopleIcon />, path: '/admin/reports/student-udise' },
          { label: 'Fee Tracking Report', icon: <ReceiptLongIcon />, path: '/admin/reports/fee-tracking' },
          { label: 'Daily Collection Report', icon: <ReceiptLongIcon />, path: '/admin/reports/daily-collection' },
        ],
      },
    ];
    if (isSuperAdmin) {
      menu.push({ label: 'Session Progression', icon: <SessionProgressionIcon />, path: '/admin/session-progression' });
    }
    return menu;
  }, [isSuperAdmin]);

  return (
    <PortalLayout portalName="Admin Portal" items={items}>
      {children}
    </PortalLayout>
  );
};

export default AdminLayout;
