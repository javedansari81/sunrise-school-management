import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  IconButton,
  Menu,
  MenuItem,
  Drawer,
  List,
  ListItem,
  ListItemText,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import SchoolIcon from '@mui/icons-material/School';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import PersonIcon from '@mui/icons-material/Person';
import DashboardIcon from '@mui/icons-material/Dashboard';
import MenuIcon from '@mui/icons-material/Menu';
import BeachAccessIcon from '@mui/icons-material/BeachAccess';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import { useAuth } from '../../contexts/AuthContext';
import LoginPopup from '../LoginPopup';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, showLoginPopup, setShowLoginPopup } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
    navigate('/');
  };

  const navigationItems = [
    { label: 'Home', path: '/' },
    { label: 'About', path: '/about' },
    { label: 'Academics', path: '/academics' },
    { label: 'Admissions', path: '/admissions' },
    { label: 'Faculty', path: '/faculty' },
    { label: 'Gallery', path: '/gallery' },
    { label: 'Contact', path: '/contact' },
  ];

  return (
    <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
      <Container maxWidth="lg" sx={{ px: { xs: 1, sm: 2, md: 3 } }}>
        <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }}>
          <SchoolIcon sx={{ mr: { xs: 1, sm: 2 } }} />
          <Typography
            variant="h6"
            component="div"
            sx={{
              flexGrow: 1,
              fontWeight: 'bold',
              fontSize: { xs: '1rem', sm: '1.25rem' },
              lineHeight: 1.2
            }}
          >
            {isMobile ? 'Sunrise School' : 'Sunrise National Public School'}
          </Typography>

          {/* Desktop Navigation */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 2 }}>
            {navigationItems.map((item) => (
              <Button
                key={item.path}
                color="inherit"
                component={Link}
                to={item.path}
                sx={{ fontSize: '0.875rem' }}
              >
                {item.label}
              </Button>
            ))}
          </Box>

          {/* Mobile Menu Button */}
          <Box sx={{ display: { xs: 'flex', md: 'none' }, alignItems: 'center', gap: 1 }}>
            <IconButton
              color="inherit"
              onClick={() => setMobileMenuOpen(true)}
              sx={{ p: 1 }}
            >
              <MenuIcon />
            </IconButton>
          </Box>

          {/* User Menu - Always visible */}
          <Box sx={{ display: 'flex', alignItems: 'center', ml: { xs: 1, md: 2 } }}>
            {!isAuthenticated ? (
              <Button
                color="inherit"
                onClick={() => setShowLoginPopup(true)}
                sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
              >
                Login
              </Button>
            ) : (
              <>
                <IconButton
                  color="inherit"
                  onClick={handleMenuOpen}
                  sx={{ p: { xs: 1, sm: 1.5 } }}
                >
                  <AccountCircleIcon />
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
                  {/* Show Dashboard for admin and super admin users */}
                  {['ADMIN', 'SUPER_ADMIN'].includes(user?.user_type?.toUpperCase() || '') && (
                    <MenuItem onClick={() => {
                      handleMenuClose();
                      window.open('/admin/dashboard', '_blank', 'noopener,noreferrer');
                    }}>
                      <DashboardIcon sx={{ mr: 1 }} />
                      Admin Dashboard
                    </MenuItem>
                  )}
                  {user?.user_type?.toUpperCase() === 'TEACHER' && (
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/teacher/dashboard'); }}>
                      <DashboardIcon sx={{ mr: 1 }} />
                      Dashboard
                    </MenuItem>
                  )}

                  {/* Show Leave Management for students and teachers */}
                  {user?.user_type?.toUpperCase() === 'STUDENT' && (
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/student/leaves'); }}>
                      <BeachAccessIcon sx={{ mr: 1 }} />
                      Leave Management
                    </MenuItem>
                  )}
                  {user?.user_type?.toUpperCase() === 'TEACHER' && (
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/teacher/leaves'); }}>
                      <BeachAccessIcon sx={{ mr: 1 }} />
                      Leave Management
                    </MenuItem>
                  )}

                  {/* Show Fee Management for students */}
                  {user?.user_type?.toUpperCase() === 'STUDENT' && (
                    <MenuItem onClick={() => { handleMenuClose(); navigate('/student/fees'); }}>
                      <AccountBalanceWalletIcon sx={{ mr: 1 }} />
                      Fee Management
                    </MenuItem>
                  )}

                  {/* Show Profile for all authenticated users */}
                  <MenuItem onClick={() => { handleMenuClose(); navigate('/profile'); }}>
                    <PersonIcon sx={{ mr: 1 }} />
                    Profile
                  </MenuItem>

                  <MenuItem onClick={handleLogout}>
                    <LogoutIcon sx={{ mr: 1 }} />
                    Logout
                  </MenuItem>
                </Menu>
              </>
            )}
          </Box>
        </Toolbar>
      </Container>

      {/* Mobile Navigation Drawer */}
      <Drawer
        anchor="right"
        open={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            width: 250,
            pt: 2,
          },
        }}
      >
        <List>
          {navigationItems.map((item) => (
            <ListItem
              key={item.path}
              component={Link}
              to={item.path}
              onClick={() => setMobileMenuOpen(false)}
              sx={{
                color: 'inherit',
                textDecoration: 'none',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                },
              }}
            >
              <ListItemText
                primary={item.label}
                sx={{
                  '& .MuiListItemText-primary': {
                    fontSize: '1rem',
                    fontWeight: 500,
                  },
                }}
              />
            </ListItem>
          ))}

          {/* Login/Logout in mobile menu */}
          {!isAuthenticated && (
            <ListItem
              onClick={() => {
                setMobileMenuOpen(false);
                setShowLoginPopup(true);
              }}
              sx={{
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                },
              }}
            >
              <ListItemText
                primary="Login"
                sx={{
                  '& .MuiListItemText-primary': {
                    fontSize: '1rem',
                    fontWeight: 500,
                    color: 'primary.main',
                  },
                }}
              />
            </ListItem>
          )}
        </List>
      </Drawer>

      <LoginPopup
        open={showLoginPopup}
        onClose={() => setShowLoginPopup(false)}
      />
    </AppBar>
  );
};

export default Header;
