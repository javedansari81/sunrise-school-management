import React, { useState, useRef, useEffect } from 'react';
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
  Popover,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  AttachMoney,
  BeachAccess,
  Receipt,
  PersonAdd,
  School as SchoolIcon,
  Home as HomeIcon,
  Logout as LogoutIcon,
  DirectionsBus as DirectionsBusIcon,
  PhotoLibrary as PhotoLibraryIcon,
  Assessment as AssessmentIcon,
  People as PeopleIcon,
  ReceiptLong as ReceiptLongIcon,
  ChevronRight as ChevronRightIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  AccountBalance as AccountBalanceIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface MenuItem {
  label: string;
  shortLabel?: string;  // Short label for collapsed mode
  icon: React.ReactNode;
  path?: string;  // Optional for parent items with children
  children?: MenuItem[];  // For submenu items
}

interface AdminLayoutProps {
  children: React.ReactNode;
}

const DRAWER_WIDTH = 260; // For mobile only
const SIDEBAR_WIDTH = 110; // Fixed compact width for desktop

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, isAuthenticated, logout } = useAuth();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);

  // Flyout menu state for submenu items (desktop)
  const [flyoutMenuAnchor, setFlyoutMenuAnchor] = useState<null | HTMLElement>(null);
  const [flyoutMenuItems, setFlyoutMenuItems] = useState<MenuItem[]>([]);

  // Mobile submenu expansion state
  const [expandedMobileMenu, setExpandedMobileMenu] = useState<string | null>(null);

  // Refs for auto-scrolling to expanded submenu on mobile
  const submenuRefs = useRef<{ [key: string]: HTMLElement | null }>({});

  const menuItems: MenuItem[] = [
    { label: 'Dashboard', shortLabel: 'Dashboard', icon: <DashboardIcon />, path: '/admin/dashboard' },

    // User Management Group
    {
      label: 'User Management',
      shortLabel: 'Users',
      icon: <PeopleIcon />,
      children: [
        { label: 'Student Profiles', icon: <PersonAdd />, path: '/admin/students' },
        { label: 'Teacher Profiles', icon: <SchoolIcon />, path: '/admin/teachers' },
      ],
    },

    // Financial Management Group (includes Transport)
    {
      label: 'Financial Management',
      shortLabel: 'Finance',
      icon: <AccountBalanceIcon />,
      children: [
        { label: 'Fees Management', icon: <AttachMoney />, path: '/admin/fees' },
        { label: 'Expense Management', icon: <Receipt />, path: '/admin/expenses' },
        { label: 'Transport Service', icon: <DirectionsBusIcon />, path: '/admin/transport' },
      ],
    },

    // Operations Management Group
    {
      label: 'Operations',
      shortLabel: 'Operations',
      icon: <SettingsIcon />,
      children: [
        { label: 'Leave Management', icon: <BeachAccess />, path: '/admin/leaves' },
        { label: 'Gallery Management', icon: <PhotoLibraryIcon />, path: '/admin/gallery-management' },
      ],
    },

    // Reports & Analytics
    {
      label: 'Reports & Analytics',
      shortLabel: 'Reports',
      icon: <AssessmentIcon />,
      children: [
        { label: 'Student UDISE Report', icon: <PeopleIcon />, path: '/admin/reports/student-udise' },
        { label: 'Fee Tracking Report', icon: <ReceiptLongIcon />, path: '/admin/reports/fee-tracking' },
      ],
    },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleFlyoutOpen = (event: React.MouseEvent<HTMLElement>, children: MenuItem[]) => {
    setFlyoutMenuAnchor(event.currentTarget);
    setFlyoutMenuItems(children);
  };

  const handleFlyoutClose = () => {
    setFlyoutMenuAnchor(null);
    setFlyoutMenuItems([]);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
    // Close flyout menu if open
    handleFlyoutClose();
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

  // Helper function to check if any child is active
  const isAnyChildActive = (children?: MenuItem[]) => {
    if (!children) return false;
    return children.some(child => child.path && isActive(child.path));
  };

  // Auto-scroll to expanded submenu on mobile
  useEffect(() => {
    if (isMobile && expandedMobileMenu && submenuRefs.current[expandedMobileMenu]) {
      // Small delay to allow submenu to render
      const timer = setTimeout(() => {
        const submenuElement = submenuRefs.current[expandedMobileMenu];
        if (submenuElement) {
          submenuElement.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
            inline: 'nearest'
          });
        }
      }, 100);

      return () => clearTimeout(timer);
    }
  }, [expandedMobileMenu, isMobile]);

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
        {isMobile ? (
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
              Admin Panel
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

        {/* Navigation Menu */}
        <List sx={{ py: 2 }}>
          {menuItems.map((item, index) => {
            // Check if item has children (submenu)
            if (item.children) {
              const hasActiveChild = isAnyChildActive(item.children);
              const isExpanded = expandedMobileMenu === item.label;

              return (
                <React.Fragment key={item.label}>
                  <ListItem disablePadding sx={{ px: 1, mb: 0.5 }}>
                    <Tooltip title={!isMobile ? item.label : ""} placement="right">
                      <ListItemButton
                        onClick={(e) => {
                          if (isMobile) {
                            // Mobile: toggle submenu expansion
                            setExpandedMobileMenu(isExpanded ? null : item.label);
                          } else {
                            // Desktop: open flyout
                            handleFlyoutOpen(e, item.children!);
                          }
                        }}
                        sx={{
                          borderRadius: 2,
                          minHeight: isMobile ? 48 : 56,
                          flexDirection: isMobile ? 'row' : 'column',
                          justifyContent: 'center',
                          alignItems: 'center',
                          px: isMobile ? 2.5 : 1,
                          py: isMobile ? 0 : 1,
                          backgroundColor: hasActiveChild ? 'rgba(25, 118, 210, 0.12)' : 'transparent',
                          color: hasActiveChild ? 'primary.main' : 'text.primary',
                          '&:hover': {
                            backgroundColor: hasActiveChild
                              ? 'rgba(25, 118, 210, 0.2)'
                              : 'rgba(0, 0, 0, 0.04)',
                          },
                          transition: 'all 0.2s',
                        }}
                      >
                        <ListItemIcon
                          sx={{
                            minWidth: isMobile ? 40 : 0,
                            color: hasActiveChild ? 'primary.main' : 'text.secondary',
                            justifyContent: 'center',
                            mb: isMobile ? 0 : 0.5,
                          }}
                        >
                          {item.icon}
                        </ListItemIcon>
                        {isMobile ? (
                          <>
                            <ListItemText
                              primary={item.label}
                              slotProps={{
                                primary: {
                                  sx: {
                                    fontSize: '0.95rem',
                                    fontWeight: hasActiveChild ? 600 : 500,
                                  }
                                }
                              }}
                            />
                            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </>
                        ) : (
                          <Typography
                            variant="caption"
                            sx={{
                              fontSize: '0.7rem',
                              fontWeight: hasActiveChild ? 600 : 500,
                              textAlign: 'center',
                              lineHeight: 1.2,
                              color: hasActiveChild ? 'primary.main' : 'text.secondary',
                            }}
                          >
                            {item.shortLabel || item.label}
                          </Typography>
                        )}
                      </ListItemButton>
                    </Tooltip>
                  </ListItem>

                  {/* Mobile submenu items - shown inline when expanded */}
                  {isMobile && isExpanded && (
                    <List
                      ref={(el) => {
                        submenuRefs.current[item.label] = el;
                      }}
                      sx={{ pl: 2, pr: 1 }}
                    >
                      {item.children.map((child) => {
                        const childActive = child.path ? isActive(child.path) : false;
                        return (
                          <ListItem key={child.path} disablePadding sx={{ mb: 0.5 }}>
                            <ListItemButton
                              onClick={() => child.path && handleNavigation(child.path)}
                              sx={{
                                borderRadius: 1.5,
                                minHeight: 40,
                                px: 2,
                                backgroundColor: childActive ? 'rgba(25, 118, 210, 0.12)' : 'transparent',
                                color: childActive ? 'primary.main' : 'text.primary',
                                '&:hover': {
                                  backgroundColor: childActive
                                    ? 'rgba(25, 118, 210, 0.2)'
                                    : 'rgba(0, 0, 0, 0.04)',
                                },
                                transition: 'all 0.2s',
                              }}
                            >
                              <ListItemIcon
                                sx={{
                                  minWidth: 36,
                                  color: childActive ? 'primary.main' : 'text.secondary',
                                }}
                              >
                                {child.icon}
                              </ListItemIcon>
                              <ListItemText
                                primary={child.label}
                                slotProps={{
                                  primary: {
                                    sx: {
                                      fontSize: '0.875rem',
                                      fontWeight: childActive ? 600 : 500,
                                    }
                                  }
                                }}
                              />
                            </ListItemButton>
                          </ListItem>
                        );
                      })}
                    </List>
                  )}
                </React.Fragment>
              );
            }

            // Regular menu item (no children)
            const active = item.path ? isActive(item.path) : false;

            return (
              <ListItem key={item.path || `menu-${index}`} disablePadding sx={{ px: 1, mb: 0.5 }}>
                <Tooltip title={!isMobile ? item.label : ""} placement="right">
                  <ListItemButton
                    onClick={() => item.path && handleNavigation(item.path)}
                    sx={{
                      borderRadius: 2,
                      minHeight: isMobile ? 48 : 56,
                      flexDirection: isMobile ? 'row' : 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                      px: isMobile ? 2.5 : 1,
                      py: isMobile ? 0 : 1,
                      backgroundColor: active ? 'rgba(25, 118, 210, 0.12)' : 'transparent',
                      color: active ? 'primary.main' : 'text.primary',
                      '&:hover': {
                        backgroundColor: active
                          ? 'rgba(25, 118, 210, 0.2)'
                          : 'rgba(0, 0, 0, 0.04)',
                      },
                      transition: 'all 0.2s',
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: isMobile ? 40 : 0,
                        color: active ? 'primary.main' : 'text.secondary',
                        justifyContent: 'center',
                        mb: isMobile ? 0 : 0.5,
                      }}
                    >
                      {item.icon}
                    </ListItemIcon>
                    {isMobile ? (
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
                    ) : (
                      <Typography
                        variant="caption"
                        sx={{
                          fontSize: '0.7rem',
                          fontWeight: active ? 600 : 500,
                          textAlign: 'center',
                          lineHeight: 1.2,
                          color: active ? 'primary.main' : 'text.secondary',
                        }}
                      >
                        {item.shortLabel || item.label}
                      </Typography>
                    )}
                  </ListItemButton>
                </Tooltip>
              </ListItem>
            );
          })}
        </List>
      </Box>

      <Divider />

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
        {isMobile && (
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
            <SchoolIcon sx={{ mr: 1, fontSize: 32 }} />
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Admin Dashboard
            </Typography>
            {isAuthenticated && user && (
              <IconButton
                color="inherit"
                onClick={handleUserMenuOpen}
                sx={{ ml: 1 }}
              >
                <Avatar sx={{ width: 36, height: 36, bgcolor: 'secondary.main' }}>
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
          width: isMobile ? DRAWER_WIDTH : SIDEBAR_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: isMobile ? DRAWER_WIDTH : SIDEBAR_WIDTH,
            boxSizing: 'border-box',
            overflowX: 'hidden',
            overflowY: 'hidden',
            borderRight: '1px solid rgba(0, 0, 0, 0.12)',
            top: 0,
            height: '100vh',
            position: 'fixed',
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
            md: `calc(100% - ${SIDEBAR_WIDTH}px)`,
          },
        }}
      >
        {/* Mobile Toolbar Spacer */}
        {isMobile && <Toolbar sx={{ minHeight: 72 }} />}

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
              {(() => {
                // Check top-level items
                const topLevelItem = menuItems.find((item) => item.path === location.pathname);
                if (topLevelItem) return topLevelItem.label;

                // Check submenu items
                for (const item of menuItems) {
                  if (item.children) {
                    const childItem = item.children.find((child) => child.path === location.pathname);
                    if (childItem) return childItem.label;
                  }
                }

                return 'Admin Dashboard';
              })()}
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

      {/* Flyout Menu for Collapsed Sidebar */}
      <Popover
        open={Boolean(flyoutMenuAnchor)}
        anchorEl={flyoutMenuAnchor}
        onClose={handleFlyoutClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        sx={{
          '& .MuiPopover-paper': {
            ml: 0.5,
            minWidth: 220,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
            borderRadius: 2,
          },
        }}
      >
        <List sx={{ py: 1 }}>
          {flyoutMenuItems.map((child) => {
            const childActive = child.path ? isActive(child.path) : false;
            return (
              <ListItem key={child.path} disablePadding sx={{ px: 1 }}>
                <ListItemButton
                  onClick={() => child.path && handleNavigation(child.path)}
                  sx={{
                    borderRadius: 1.5,
                    minHeight: 44,
                    px: 2,
                    backgroundColor: childActive ? 'rgba(25, 118, 210, 0.12)' : 'transparent',
                    color: childActive ? 'primary.main' : 'text.primary',
                    '&:hover': {
                      backgroundColor: childActive
                        ? 'rgba(25, 118, 210, 0.2)'
                        : 'rgba(0, 0, 0, 0.04)',
                    },
                    transition: 'all 0.2s',
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 36,
                      color: childActive ? 'primary.main' : 'text.secondary',
                    }}
                  >
                    {child.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={child.label}
                    slotProps={{
                      primary: {
                        sx: {
                          fontSize: '0.9rem',
                          fontWeight: childActive ? 600 : 500,
                        }
                      }
                    }}
                  />
                  {childActive && (
                    <ChevronRightIcon sx={{ fontSize: 18, color: 'primary.main' }} />
                  )}
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Popover>
    </Box>
  );
};

export default AdminLayout;
