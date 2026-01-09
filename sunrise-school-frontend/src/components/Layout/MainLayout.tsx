import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  useTheme,
  useMediaQuery,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  AppBar,
  Toolbar,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  Info as InfoIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
  People as PeopleIcon,
  PhotoLibrary as PhotoLibraryIcon,
  ContactMail as ContactMailIcon,
  Login as LoginIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  Dashboard as DashboardIcon,
  BeachAccess as BeachAccessIcon,
  AccountBalanceWallet as AccountBalanceWalletIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { Tooltip } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Footer from './Footer';
import LoginPopup from '../LoginPopup';

interface MainLayoutProps {
  children: React.ReactNode;
}

const DRAWER_WIDTH = 260;
const DRAWER_WIDTH_COLLAPSED = 72;

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isAuthenticated, user, logout } = useAuth();

  // Mobile drawer starts closed by default to not obstruct content
  const [mobileOpen, setMobileOpen] = useState(false);
  // Desktop drawer starts collapsed by default (true = collapsed, false = expanded)
  const [drawerCollapsed, setDrawerCollapsed] = useState(true);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [loginPopupOpen, setLoginPopupOpen] = useState(false);

  // Clear any stale localStorage on mount to ensure collapsed state
  React.useEffect(() => {
    localStorage.removeItem('mainDrawerCollapsed');
  }, []);

  const publicMenuItems = [
    { label: 'Home', icon: <HomeIcon />, path: '/' },
    { label: 'About', icon: <InfoIcon />, path: '/about' },
    { label: 'Academics', icon: <SchoolIcon />, path: '/academics' },
    { label: 'Admissions', icon: <AssignmentIcon />, path: '/admissions' },
    { label: 'Faculty', icon: <PeopleIcon />, path: '/faculty' },
    { label: 'Gallery', icon: <PhotoLibraryIcon />, path: '/gallery' },
    { label: 'Contact', icon: <ContactMailIcon />, path: '/contact' },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleDrawerCollapse = () => {
    setDrawerCollapsed(!drawerCollapsed);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = () => {
    handleUserMenuClose();
    logout();
    navigate('/');
  };

  const handleLoginClick = () => {
    setLoginPopupOpen(true);
  };

  const handleLoginClose = () => {
    setLoginPopupOpen(false);
  };

  const isActive = (path: string) => location.pathname === path;

  // Get dynamic page title based on current route
  const getPageTitle = () => {
    const currentItem = publicMenuItems.find((item) => item.path === location.pathname);
    if (currentItem) {
      if (currentItem.path === '/') {
        return 'Welcome to Sunrise National Public School';
      }
      return currentItem.label;
    }
    return 'Sunrise National Public School';
  };

  const drawerContent = (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Sidebar Header - Fixed at top */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
          color: 'white',
          minHeight: 64,
          flexShrink: 0,
        }}
      >
        {(!drawerCollapsed || isMobile) ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              component="img"
              src="/images/logo/school_logo.jpeg"
              alt="Sunrise School Logo"
              sx={{
                width: 40,
                height: 40,
                objectFit: 'contain',
                borderRadius: 1,
              }}
            />
            <Typography variant="h6" fontWeight="bold" sx={{ fontSize: '1.1rem' }}>
              Sunrise School
            </Typography>
          </Box>
        ) : (
          <Box
            component="img"
            src="/images/logo/school_logo.jpeg"
            alt="Sunrise School Logo"
            sx={{
              width: 48,
              height: 48,
              objectFit: 'contain',
              borderRadius: 1,
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              p: 0.5,
            }}
          />
        )}
      </Box>

      <Divider />

      {/* Navigation Menu - Scrollable */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', overflowX: 'hidden' }}>
        <List sx={{ py: 1, px: 1 }}>
          {publicMenuItems.map((item) => {
            const active = isActive(item.path);
            return (
              <ListItem key={item.path} disablePadding sx={{ px: (drawerCollapsed && !isMobile) ? 0.5 : 1, mb: 0.5 }}>
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    borderRadius: 2,
                    minHeight: 48,
                    px: (drawerCollapsed && !isMobile) ? 1.5 : 2.5,
                    justifyContent: (drawerCollapsed && !isMobile) ? 'center' : 'flex-start',
                    backgroundColor: active ? 'rgba(25, 118, 210, 0.12)' : 'transparent',
                    color: active ? 'primary.main' : 'text.primary',
                    '&:hover': {
                      backgroundColor: active
                        ? 'rgba(25, 118, 210, 0.2)'
                        : 'rgba(0, 0, 0, 0.04)',
                    },
                    transition: 'all 0.2s',
                    ...(active && {
                      borderLeft: '4px solid',
                      borderColor: 'primary.main',
                      fontWeight: 600,
                    }),
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: (drawerCollapsed && !isMobile) ? 0 : 40,
                      color: active ? 'primary.main' : 'text.secondary',
                      justifyContent: 'center',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  {(!drawerCollapsed || isMobile) && (
                    <ListItemText
                      primary={item.label}
                      slotProps={{
                        primary: {
                          sx: {
                            fontSize: '0.95rem',
                            fontWeight: active ? 600 : 500,
                          }
                        }
                      }}
                    />
                  )}
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>

      <Divider />

      {/* Collapse Button - Fixed at bottom */}
      {!isMobile && (
        <Box sx={{ p: drawerCollapsed ? 0.5 : 1, flexShrink: 0 }}>
          <Tooltip title={drawerCollapsed ? "Expand Sidebar" : "Collapse Sidebar"} placement="right">
            <IconButton
              onClick={handleDrawerCollapse}
              sx={{
                width: '100%',
                borderRadius: 2,
                py: 1.5,
                backgroundColor: drawerCollapsed ? 'warning.main' : 'primary.main',
                color: 'white',
                '&:hover': {
                  backgroundColor: drawerCollapsed ? 'warning.dark' : 'primary.dark',
                  transform: 'scale(1.05)',
                },
                transition: 'all 0.3s ease',
                boxShadow: drawerCollapsed
                  ? '0 4px 8px rgba(255, 152, 0, 0.4)'
                  : '0 2px 4px rgba(0,0,0,0.1)',
                animation: drawerCollapsed ? 'pulse 2s infinite' : 'none',
                '@keyframes pulse': {
                  '0%, 100%': {
                    boxShadow: '0 4px 8px rgba(255, 152, 0, 0.4)',
                  },
                  '50%': {
                    boxShadow: '0 4px 12px rgba(255, 152, 0, 0.6)',
                  },
                },
              }}
            >
              {drawerCollapsed ? <ChevronRightIcon fontSize="large" /> : <ChevronLeftIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      )}

      {/* Footer - Fixed at bottom */}
      <Box
        sx={{
          p: 1.5,
          textAlign: 'center',
          color: 'text.secondary',
          fontSize: '0.75rem',
          flexShrink: 0,
        }}
      >
        {(!drawerCollapsed || isMobile) && (
          <Typography variant="caption">
            © 2025 Sunrise School
          </Typography>
        )}
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Mobile AppBar */}
      {isMobile && (
        <AppBar
          position="fixed"
          sx={{
            zIndex: theme.zIndex.drawer + 1,
            backgroundColor: '#1976d2',
            color: 'white',
            boxShadow: 1,
            height: 72,
          }}
        >
          <Toolbar sx={{ minHeight: 72, height: 72 }}>
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Box
              component="img"
              src="/images/logo/school_logo.jpeg"
              alt="Sunrise School Logo"
              sx={{
                width: 40,
                height: 40,
                objectFit: 'contain',
                mr: 1,
              }}
            />
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, color: 'white', fontWeight: 'bold' }}>
              Sunrise School
            </Typography>
            {isAuthenticated && user ? (
              <IconButton
                color="inherit"
                onClick={handleUserMenuOpen}
                sx={{ ml: 1 }}
              >
                <Avatar
                  src={user.profile_picture_url || undefined}
                  sx={{ width: 36, height: 36, bgcolor: 'white', color: '#1976d2' }}
                >
                  {!user.profile_picture_url && (user.first_name?.[0] || user.email?.[0] || 'U')}
                </Avatar>
              </IconButton>
            ) : (
              <IconButton color="inherit" onClick={handleLoginClick}>
                <LoginIcon />
              </IconButton>
            )}
          </Toolbar>
        </AppBar>
      )}

      {/* Desktop AppBar - Positioned next to sidebar */}
      {!isMobile && (
        <AppBar
          position="fixed"
          sx={{
            zIndex: theme.zIndex.drawer - 1,
            backgroundColor: 'white',
            color: 'text.primary',
            boxShadow: 'none',
            borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
            height: 72,
            width: `calc(100% - ${drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH}px)`,
            ml: `${drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH}px`,
            transition: theme.transitions.create(['width', 'margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }}
        >
          <Toolbar sx={{ minHeight: 72, height: 72 }}>
            {/* Dynamic Page Title */}
            <Typography variant="h5" fontWeight="bold" color="primary" sx={{ flexGrow: 1 }}>
              {getPageTitle()}
            </Typography>

            {/* User Profile Menu */}
            {isAuthenticated && user ? (
              <IconButton onClick={handleUserMenuOpen} sx={{ color: 'primary.main' }}>
                <Avatar
                  src={user.profile_picture_url || undefined}
                  sx={{ width: 36, height: 36, bgcolor: 'primary.main' }}
                >
                  {!user.profile_picture_url && (user.first_name?.[0] || user.email?.[0] || 'U')}
                </Avatar>
              </IconButton>
            ) : (
              <IconButton color="primary" onClick={handleLoginClick}>
                <LoginIcon />
              </IconButton>
            )}
          </Toolbar>
        </AppBar>
      )}

      {/* User Menu Dropdown */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        {user && (
          <Box sx={{ px: 2, py: 1, borderBottom: '1px solid rgba(0, 0, 0, 0.12)' }}>
            <Typography variant="subtitle2" fontWeight="bold">
              {user.first_name} {user.last_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {user.email}
            </Typography>
          </Box>
        )}

        {/* Admin Dashboard - Available for ADMIN and SUPER_ADMIN */}
        {['ADMIN', 'SUPER_ADMIN'].includes(user?.user_type?.toUpperCase() || '') && (
          <MenuItem onClick={() => {
            handleUserMenuClose();
            window.open('/admin/dashboard', '_blank', 'noopener,noreferrer');
          }}>
            <DashboardIcon sx={{ mr: 1 }} />
            Admin Dashboard
          </MenuItem>
        )}

        {/* Teacher Dashboard */}
        {user?.user_type?.toUpperCase() === 'TEACHER' && (
          <MenuItem onClick={() => { handleUserMenuClose(); navigate('/teacher/dashboard'); }}>
            <DashboardIcon sx={{ mr: 1 }} />
            Dashboard
          </MenuItem>
        )}

        {/* Student Leave Management */}
        {user?.user_type?.toUpperCase() === 'STUDENT' && (
          <MenuItem onClick={() => { handleUserMenuClose(); navigate('/student/leaves'); }}>
            <BeachAccessIcon sx={{ mr: 1 }} />
            Leave Management
          </MenuItem>
        )}

        {/* Teacher Leave Management */}
        {user?.user_type?.toUpperCase() === 'TEACHER' && (
          <MenuItem onClick={() => { handleUserMenuClose(); navigate('/teacher/leaves'); }}>
            <BeachAccessIcon sx={{ mr: 1 }} />
            Leave Management
          </MenuItem>
        )}

        {/* Teacher Student Profiles */}
        {user?.user_type?.toUpperCase() === 'TEACHER' && (
          <MenuItem onClick={() => { handleUserMenuClose(); navigate('/teacher/students'); }}>
            <PeopleIcon sx={{ mr: 1 }} />
            Student Profiles
          </MenuItem>
        )}

        {/* Student Fee Management */}
        {user?.user_type?.toUpperCase() === 'STUDENT' && (
          <MenuItem onClick={() => { handleUserMenuClose(); navigate('/student/fees'); }}>
            <AccountBalanceWalletIcon sx={{ mr: 1 }} />
            Fee Management
          </MenuItem>
        )}

        {/* Profile */}
        <MenuItem onClick={() => { handleUserMenuClose(); navigate('/profile'); }}>
          <PersonIcon sx={{ mr: 1 }} />
          Profile
        </MenuItem>

        {/* Logout */}
        <MenuItem onClick={handleLogout}>
          <LogoutIcon sx={{ mr: 1 }} />
          Logout
        </MenuItem>
      </Menu>

      {/* Sidebar Drawer */}
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? mobileOpen : true}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          width: isMobile ? DRAWER_WIDTH : (drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH),
          flexShrink: 0,
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          '& .MuiDrawer-paper': {
            width: isMobile ? DRAWER_WIDTH : (drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH),
            boxSizing: 'border-box',
            borderRight: '1px solid rgba(0, 0, 0, 0.12)',
            boxShadow: 'none',
            top: 0,
            height: '100vh',
            position: 'fixed',
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
            overflowX: 'hidden',
            overflowY: 'hidden',
          },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: {
            xs: '100%',
            md: `calc(100% - ${drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH}px)`,
          },
          ml: { xs: 0, md: 0 },
          mt: '72px', // Add top margin for AppBar (72px for both mobile and desktop)
          display: 'flex',
          flexDirection: 'column',
          minHeight: 'calc(100vh - 72px)',
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        <Box sx={{ flexGrow: 1 }}>
          {children}
        </Box>
        <Footer />
      </Box>

      {/* Login Popup */}
      <LoginPopup open={loginPopupOpen} onClose={handleLoginClose} />
    </Box>
  );
};

export default MainLayout;

