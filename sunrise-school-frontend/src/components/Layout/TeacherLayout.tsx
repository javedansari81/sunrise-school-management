import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  useTheme,
  useMediaQuery,
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  Home as HomeIcon,
  Dashboard as DashboardIcon,
  BeachAccess as BeachAccessIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  PersonAdd as PersonAddIcon,
  EventNote as AttendanceIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Footer from './Footer';
import NotificationBell from '../alerts/NotificationBell';

interface TeacherLayoutProps {
  children: React.ReactNode;
}

const DRAWER_WIDTH = 260;
const DRAWER_WIDTH_COLLAPSED = 72;

const TeacherLayout: React.FC<TeacherLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, isAuthenticated, logout } = useAuth();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [drawerCollapsed, setDrawerCollapsed] = useState(true);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);

  // Teacher-specific menu items for right panel navigation
  const teacherMenuItems = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/teacher/dashboard' },
    { label: 'Leave Management', icon: <BeachAccessIcon />, path: '/teacher/leaves' },
    { label: 'Student Profiles', icon: <PersonAddIcon />, path: '/teacher/students' },
    { label: 'Attendance', icon: <AttendanceIcon />, path: '/teacher/attendance' },
    { label: 'Notifications', icon: <NotificationsIcon />, path: '/teacher/alerts' },
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
    // Close mobile drawer when opening user menu
    if (isMobile && mobileOpen) {
      setMobileOpen(false);
    }
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = () => {
    logout();
    handleUserMenuClose();
    if (isMobile) {
      setMobileOpen(false);
    }
    navigate('/');
  };

  const handleProfile = () => {
    handleUserMenuClose();
    if (isMobile) {
      setMobileOpen(false);
    }
    navigate('/profile');
  };

  const isActive = (path: string) => location.pathname === path;

  // Get page title based on current route
  const getPageTitle = () => {
    const currentItem = teacherMenuItems.find((item) => item.path === location.pathname);
    if (currentItem) {
      return currentItem.label;
    }
    if (location.pathname === '/profile') {
      return 'Profile';
    }
    return 'Teacher Dashboard';
  };

  const drawerContent = (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Sidebar Header */}
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

      {/* Scrollable Content Area */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', overflowX: 'hidden' }}>
        {/* Open Main Website Link */}
        <Box sx={{ px: 1, py: 2 }}>
          <Tooltip title={!isMobile ? "Open Main Website" : ""} placement="right">
            <ListItemButton
              onClick={() => window.open('/', '_blank', 'noopener,noreferrer')}
              sx={{
                borderRadius: 2,
                minHeight: isMobile ? 48 : 56,
                flexDirection: isMobile ? 'row' : 'column',
                justifyContent: 'center',
                alignItems: 'center',
                px: isMobile ? 2.5 : 1,
                py: isMobile ? 0 : 1,
                backgroundColor: 'rgba(76, 175, 80, 0.08)',
                color: '#2e7d32',
                '&:hover': {
                  backgroundColor: 'rgba(76, 175, 80, 0.15)',
                },
                transition: 'all 0.2s',
                border: '1px solid rgba(76, 175, 80, 0.3)',
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: isMobile ? 40 : 0,
                  color: '#2e7d32',
                  justifyContent: 'center',
                  mb: isMobile ? 0 : 0.5,
                }}
              >
                <HomeIcon />
              </ListItemIcon>
              {isMobile ? (
                <ListItemText
                  primary="Open Main Website"
                  slotProps={{
                    primary: {
                      sx: {
                        fontSize: '0.95rem',
                        fontWeight: 600,
                      }
                    }
                  }}
                />
              ) : (
                <Typography
                  variant="caption"
                  sx={{
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    textAlign: 'center',
                    lineHeight: 1.2,
                  }}
                >
                  Website
                </Typography>
              )}
            </ListItemButton>
          </Tooltip>
        </Box>

        <Divider />

        {/* Teacher Navigation Menu */}
        <List sx={{ py: 1 }}>
          {teacherMenuItems.map((item) => (
            <ListItem key={item.path} disablePadding sx={{ display: 'block' }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                sx={{
                  minHeight: 48,
                  justifyContent: drawerCollapsed ? 'center' : 'initial',
                  px: 2.5,
                  backgroundColor: isActive(item.path) ? 'rgba(25, 118, 210, 0.12)' : 'transparent',
                  color: isActive(item.path) ? 'primary.main' : 'text.primary',
                  '&:hover': {
                    backgroundColor: isActive(item.path)
                      ? 'rgba(25, 118, 210, 0.2)'
                      : 'rgba(0, 0, 0, 0.04)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25, 118, 210, 0.12)',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.2)',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: (drawerCollapsed && !isMobile) ? 'auto' : 3,
                    justifyContent: 'center',
                    color: isActive(item.path) ? 'primary.main' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {(!drawerCollapsed || isMobile) && (
                  <ListItemText
                    primary={item.label}
                    sx={{
                      opacity: 1,
                      '& .MuiTypography-root': {
                        fontWeight: isActive(item.path) ? 600 : 400,
                        color: isActive(item.path) ? 'primary.main' : 'text.primary',
                      },
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Collapse/Expand Button - Desktop Only */}
      {!isMobile && (
        <>
          <Divider />
          <Box sx={{ p: 1, textAlign: 'center' }}>
            <IconButton onClick={handleDrawerCollapse} size="small">
              {drawerCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
            </IconButton>
          </Box>
        </>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Mobile AppBar */}
      {isMobile && (
        <AppBar
          position="fixed"
          elevation={0}
          sx={{
            zIndex: theme.zIndex.drawer + 1,
            backgroundColor: '#1976d2',
            borderBottom: 'none',
            boxShadow: 'none',
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
            {isAuthenticated && user && (
              <>
                <NotificationBell color="inherit" />
                <IconButton
                  color="inherit"
                  onClick={handleUserMenuOpen}
                >
                  <Avatar
                    src={user.profile_picture_url || undefined}
                    sx={{ width: 36, height: 36, bgcolor: 'secondary.main' }}
                  >
                    {!user.profile_picture_url && (user.first_name?.[0] || user.email?.[0] || 'T')}
                  </Avatar>
                </IconButton>
              </>
            )}
          </Toolbar>
        </AppBar>
      )}

      {/* Sidebar Drawer */}
      <Box
        component="nav"
        sx={{
          width: { md: drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH },
          flexShrink: { md: 0 },
        }}
      >
        {/* Mobile Drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
            sx: {
              zIndex: theme.zIndex.drawer,
            }
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            zIndex: theme.zIndex.drawer,
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
              zIndex: theme.zIndex.drawer,
            },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Desktop Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              overflowX: 'hidden',
            },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          width: {
            xs: '100%',
            md: `calc(100% - ${drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH}px)`,
          },
        }}
      >
        {/* Mobile Toolbar Spacer */}
        {isMobile && <Toolbar />}

        {/* Desktop Header */}
        {!isMobile && (
          <Box
            sx={{
              backgroundColor: 'white',
              borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
              px: 3,
              py: 2,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Typography variant="h5" fontWeight="bold" color="primary">
              {getPageTitle()}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {isAuthenticated && user && (
                <>
                  <NotificationBell color="primary" />
                  <IconButton
                    color="primary"
                    onClick={handleUserMenuOpen}
                  >
                    <Avatar
                      src={user.profile_picture_url || undefined}
                      sx={{ width: 36, height: 36, bgcolor: 'primary.main' }}
                    >
                      {!user.profile_picture_url && (user.first_name?.[0] || user.email?.[0] || 'T')}
                    </Avatar>
                  </IconButton>
                </>
              )}
            </Box>
          </Box>
        )}

        {/* Page Content */}
        <Box sx={{ flexGrow: 1, backgroundColor: '#f5f5f5' }}>
          <Box sx={{ p: { xs: 2, sm: 3 } }}>{children}</Box>
        </Box>

        {/* Footer */}
        <Footer />
      </Box>

      {/* User Menu */}
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
        slotProps={{
          paper: {
            sx: {
              zIndex: theme.zIndex.drawer + 2,
            }
          }
        }}
        sx={{
          zIndex: theme.zIndex.drawer + 2,
        }}
        disableScrollLock={true}
        disablePortal={false}
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
        <MenuItem onClick={handleProfile}>
          <PersonIcon sx={{ mr: 1 }} />
          Profile
        </MenuItem>
        <MenuItem onClick={handleLogout}>
          <LogoutIcon sx={{ mr: 1 }} />
          Logout
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default TeacherLayout;
