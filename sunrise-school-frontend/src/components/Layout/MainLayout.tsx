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
  AppBar,
  Toolbar,
  Divider,
  Avatar,
  Menu,
  MenuItem,
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
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { Tooltip } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Footer from './Footer';

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

  const [mobileOpen, setMobileOpen] = useState(false);
  // Always start expanded (false = expanded, true = collapsed)
  const [drawerCollapsed, setDrawerCollapsed] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Clear any stale localStorage on mount
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

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    logout();
    navigate('/');
  };

  const isActive = (path: string) => location.pathname === path;

  const drawerContent = (
    <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      {/* Navigation Menu - Scrollable */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', overflowX: 'hidden' }}>
        <List sx={{ py: 1, px: 1 }}>
          {publicMenuItems.map((item) => {
            const active = isActive(item.path);
            return (
              <ListItem key={item.path} disablePadding sx={{ px: drawerCollapsed ? 0.5 : 1, mb: 0.5 }}>
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    borderRadius: 2,
                    minHeight: 48,
                    px: drawerCollapsed ? 1.5 : 2.5,
                    justifyContent: drawerCollapsed ? 'center' : 'flex-start',
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
                      minWidth: drawerCollapsed ? 0 : 40,
                      color: active ? 'primary.main' : 'text.secondary',
                      justifyContent: 'center',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  {!drawerCollapsed && (
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
      {/* Top AppBar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: theme.zIndex.drawer + 1,
          backgroundColor: '#1976d2',
          boxShadow: 'none',
          borderBottom: 'none',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <SchoolIcon sx={{ mr: 1, display: { xs: 'none', sm: 'block' } }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontSize: { xs: '1rem', sm: '1.25rem' } }}>
            {isMobile ? 'Sunrise School' : 'Sunrise National Public School'}
          </Typography>

          {/* User Menu */}
          {isAuthenticated && user ? (
            <>
              <IconButton onClick={handleMenuOpen} sx={{ color: 'white' }}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                  {user.first_name?.[0] || user.email?.[0] || 'U'}
                </Avatar>
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
              >
                {/* Admin Dashboard */}
                {user?.user_type?.toUpperCase() === 'ADMIN' && (
                  <MenuItem onClick={() => { 
                    handleMenuClose(); 
                    window.open('/admin/dashboard', '_blank', 'noopener,noreferrer');
                  }}>
                    <DashboardIcon sx={{ mr: 1 }} />
                    Admin Dashboard
                  </MenuItem>
                )}

                {/* Teacher Dashboard */}
                {user?.user_type?.toUpperCase() === 'TEACHER' && (
                  <MenuItem onClick={() => { handleMenuClose(); navigate('/teacher/dashboard'); }}>
                    <DashboardIcon sx={{ mr: 1 }} />
                    Dashboard
                  </MenuItem>
                )}

                {/* Student Leave Management */}
                {user?.user_type?.toUpperCase() === 'STUDENT' && (
                  <MenuItem onClick={() => { handleMenuClose(); navigate('/student/leaves'); }}>
                    <BeachAccessIcon sx={{ mr: 1 }} />
                    Leave Management
                  </MenuItem>
                )}

                {/* Teacher Leave Management */}
                {user?.user_type?.toUpperCase() === 'TEACHER' && (
                  <MenuItem onClick={() => { handleMenuClose(); navigate('/teacher/leaves'); }}>
                    <BeachAccessIcon sx={{ mr: 1 }} />
                    Leave Management
                  </MenuItem>
                )}

                {/* Profile */}
                <MenuItem onClick={() => { handleMenuClose(); navigate('/profile'); }}>
                  <PersonIcon sx={{ mr: 1 }} />
                  Profile
                </MenuItem>

                {/* Logout */}
                <MenuItem onClick={handleLogout}>
                  <LogoutIcon sx={{ mr: 1 }} />
                  Logout
                </MenuItem>
              </Menu>
            </>
          ) : (
            <IconButton color="inherit" onClick={() => navigate('/')}>
              <LoginIcon />
            </IconButton>
          )}
        </Toolbar>
      </AppBar>

      {/* Sidebar Drawer */}
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? mobileOpen : true}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          width: drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH,
          flexShrink: 0,
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          '& .MuiDrawer-paper': {
            width: drawerCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH,
            boxSizing: 'border-box',
            borderRight: '1px solid rgba(0, 0, 0, 0.12)',
            boxShadow: 'none',
            mt: '64px', // Push drawer below AppBar
            height: 'calc(100vh - 64px)', // Adjust height to account for AppBar
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
          mt: '64px', // AppBar height
          display: 'flex',
          flexDirection: 'column',
          minHeight: 'calc(100vh - 64px)',
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
    </Box>
  );
};

export default MainLayout;

