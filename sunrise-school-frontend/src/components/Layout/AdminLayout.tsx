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
  Tooltip,
  Menu,
  MenuItem,
  Avatar,
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Dashboard as DashboardIcon,
  AttachMoney,
  BeachAccess,
  Receipt,
  PersonAdd,
  School as SchoolIcon,
  Home as HomeIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface AdminLayoutProps {
  children: React.ReactNode;
}

const DRAWER_WIDTH = 260;
const COLLAPSED_DRAWER_WIDTH = 70;

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, isAuthenticated, logout } = useAuth();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);

  // Start collapsed by default (true = collapsed, false = expanded)
  // Force collapsed state on initial load, ignore localStorage
  const [desktopCollapsed, setDesktopCollapsed] = useState(true);

  // Clear any stale localStorage on mount to ensure collapsed state
  React.useEffect(() => {
    localStorage.removeItem('adminDrawerCollapsed');
  }, []);

  const menuItems = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/admin/dashboard' },
    { label: 'Fees Management', icon: <AttachMoney />, path: '/admin/fees' },
    { label: 'Leave Management', icon: <BeachAccess />, path: '/admin/leaves' },
    { label: 'Expense Management', icon: <Receipt />, path: '/admin/expenses' },
    { label: 'Student Profiles', icon: <PersonAdd />, path: '/admin/students' },
    { label: 'Teacher Profiles', icon: <PersonAdd />, path: '/admin/teachers' },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleDesktopToggle = () => {
    setDesktopCollapsed(!desktopCollapsed);
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
    // Redirect to main website home page after logout
    window.location.href = '/';
  };

  const isActive = (path: string) => location.pathname === path;

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
        {(!desktopCollapsed || isMobile) ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SchoolIcon sx={{ fontSize: 28 }} />
            <Typography variant="h6" fontWeight="bold" sx={{ fontSize: '1.1rem' }}>
              Admin Panel
            </Typography>
          </Box>
        ) : (
          <Box
            component="img"
            src="/logo192.png"
            alt="Admin Panel"
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
          <Tooltip
            title={desktopCollapsed && !isMobile ? "Open Main Website" : ""}
            placement="right"
          >
            <ListItemButton
              onClick={() => window.open('/', '_blank', 'noopener,noreferrer')}
              sx={{
                borderRadius: 2,
                minHeight: 48,
                justifyContent: desktopCollapsed && !isMobile ? 'center' : 'flex-start',
                px: 2.5,
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
                  minWidth: desktopCollapsed && !isMobile ? 0 : 40,
                  color: '#2e7d32',
                  justifyContent: 'center',
                }}
              >
                <HomeIcon />
              </ListItemIcon>
              {(!desktopCollapsed || isMobile) && (
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
              )}
            </ListItemButton>
          </Tooltip>
        </Box>

        <Divider />

        {/* Navigation Menu */}
        <List sx={{ py: 2 }}>
          {menuItems.map((item) => {
            const active = isActive(item.path);
            const menuButton = (
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 2,
                  minHeight: 48,
                  justifyContent: desktopCollapsed && !isMobile ? 'center' : 'flex-start',
                  px: 2.5,
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
                    minWidth: desktopCollapsed && !isMobile ? 0 : 40,
                    color: active ? 'primary.main' : 'text.secondary',
                    justifyContent: 'center',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {(!desktopCollapsed || isMobile) && (
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
            );

            return (
              <ListItem key={item.path} disablePadding sx={{ px: 1, mb: 0.5 }}>
                {desktopCollapsed && !isMobile ? (
                  <Tooltip title={item.label} placement="right">
                    {menuButton}
                  </Tooltip>
                ) : (
                  menuButton
                )}
              </ListItem>
            );
          })}
        </List>
      </Box>

      <Divider />

      {/* Collapse Button - Fixed at bottom */}
      {!isMobile && (
        <Box sx={{ p: desktopCollapsed ? 0.5 : 1, flexShrink: 0 }}>
          <Tooltip title={desktopCollapsed ? "Expand Sidebar" : "Collapse Sidebar"} placement="right">
            <IconButton
              onClick={handleDesktopToggle}
              sx={{
                width: '100%',
                borderRadius: 2,
                py: 1.5,
                backgroundColor: desktopCollapsed ? 'warning.main' : 'primary.main',
                color: 'white',
                '&:hover': {
                  backgroundColor: desktopCollapsed ? 'warning.dark' : 'primary.dark',
                  transform: 'scale(1.05)',
                },
                transition: 'all 0.3s ease',
                boxShadow: desktopCollapsed
                  ? '0 4px 8px rgba(255, 152, 0, 0.4)'
                  : '0 2px 4px rgba(0,0,0,0.1)',
                animation: desktopCollapsed ? 'pulse 2s infinite' : 'none',
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
              {desktopCollapsed ? <ChevronLeftIcon sx={{ transform: 'rotate(180deg)', fontSize: 32 }} /> : <ChevronLeftIcon />}
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
        {(!desktopCollapsed || isMobile) && (
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
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <SchoolIcon sx={{ mr: 1 }} />
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Admin Dashboard
            </Typography>
            {isAuthenticated && user && (
              <IconButton
                color="inherit"
                onClick={handleUserMenuOpen}
                sx={{ ml: 1 }}
              >
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                  {user.first_name?.[0] || user.email?.[0] || 'A'}
                </Avatar>
              </IconButton>
            )}
          </Toolbar>
        </AppBar>
      )}

      {/* Sidebar Drawer */}
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? mobileOpen : true}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better mobile performance
        }}
        sx={{
          width: isMobile
            ? DRAWER_WIDTH
            : desktopCollapsed
            ? COLLAPSED_DRAWER_WIDTH
            : DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: isMobile
              ? DRAWER_WIDTH
              : desktopCollapsed
              ? COLLAPSED_DRAWER_WIDTH
              : DRAWER_WIDTH,
            boxSizing: 'border-box',
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
            overflowX: 'hidden',
            overflowY: 'hidden',
            borderRight: '1px solid rgba(0, 0, 0, 0.12)',
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
          backgroundColor: '#f5f5f5',
          minHeight: '100vh',
          width: {
            xs: '100%',
            md: `calc(100% - ${
              desktopCollapsed ? COLLAPSED_DRAWER_WIDTH : DRAWER_WIDTH
            }px)`,
          },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
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
              {menuItems.find((item) => item.path === location.pathname)?.label ||
                'Admin Dashboard'}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {isAuthenticated && user && (
                <IconButton
                  color="primary"
                  onClick={handleUserMenuOpen}
                >
                  <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main' }}>
                    {user.first_name?.[0] || user.email?.[0] || 'A'}
                  </Avatar>
                </IconButton>
              )}
            </Box>
          </Box>
        )}

        {/* Page Content */}
        <Box sx={{ p: { xs: 2, sm: 3 } }}>{children}</Box>
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
        <MenuItem onClick={handleLogout}>
          <LogoutIcon sx={{ mr: 1 }} />
          Logout
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default AdminLayout;
