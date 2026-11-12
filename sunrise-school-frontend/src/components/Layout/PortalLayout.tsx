import React, { useEffect, useMemo, useState } from 'react';
import {
  Avatar,
  Box,
  Button,
  Collapse,
  Divider,
  Drawer,
  IconButton,
  ListItemIcon,
  Menu,
  MenuItem,
  Popover,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Dashboard as DashboardIcon,
  ExpandMore as ExpandMoreIcon,
  Login as LoginIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useSchool } from '../../contexts/SchoolContext';
import NotificationBell from '../alerts/NotificationBell';
import SchoolLogo from '../common/SchoolLogo';
import { brand, ease } from '../../theme';

export interface NavItem {
  label: string;
  icon: React.ReactNode;
  path?: string;
  children?: NavItem[];
}

interface PortalLayoutProps {
  /** Shown under the school name, e.g. "Admin Portal" */
  portalName: string;
  items: NavItem[];
  children: React.ReactNode;
  /**
   * The school's public website instead of a portal: visitors need no login,
   * pages run edge to edge, and the footer is the site's own.
   */
  publicSite?: {
    onSignIn: () => void;
    footer: React.ReactNode;
    /** Where a logged-in visitor's portal starts */
    dashboardPath?: string;
  };
}

const WIDTH = 272;
const WIDTH_COLLAPSED = 84;
const COLLAPSE_KEY = 'portalSidebarCollapsed';

const readCollapsed = (): boolean => {
  try {
    return localStorage.getItem(COLLAPSE_KEY) === '1';
  } catch {
    return false;
  }
};

// ---------------------------------------------------------------------------
// Left panel pieces
// ---------------------------------------------------------------------------

const navText = 'rgba(226,232,255,0.72)';

const rowSx = (active: boolean, compact: boolean) => ({
  position: 'relative' as const,
  display: 'flex',
  alignItems: 'center',
  gap: 1.5,
  width: '100%',
  minHeight: 46,
  px: compact ? 0 : 1.25,
  justifyContent: compact ? 'center' : 'flex-start',
  border: 0,
  borderRadius: '14px',
  cursor: 'pointer',
  textAlign: 'left' as const,
  font: 'inherit',
  color: active ? '#fff' : navText,
  background: active
    ? 'linear-gradient(90deg, rgba(96,165,250,0.30) 0%, rgba(167,139,250,0.16) 100%)'
    : 'transparent',
  boxShadow: active ? 'inset 0 0 0 1px rgba(147,197,253,0.28), 0 8px 24px rgba(37,99,235,0.28)' : 'none',
  transition: `background 0.3s ${ease}, color 0.3s ${ease}, transform 0.3s ${ease}, box-shadow 0.3s ${ease}`,
  // Glowing bar on the left edge of the current page
  '&::before': {
    content: '""',
    position: 'absolute',
    left: compact ? -10 : -12,
    top: '50%',
    width: 4,
    height: active ? 26 : 0,
    borderRadius: 4,
    background: 'linear-gradient(180deg, #60a5fa, #a78bfa)',
    boxShadow: '0 0 14px rgba(96,165,250,0.9)',
    transform: 'translateY(-50%)',
    transition: `height 0.35s ${ease}`,
  },
  '&:hover': {
    color: '#fff',
    background: active
      ? 'linear-gradient(90deg, rgba(96,165,250,0.36) 0%, rgba(167,139,250,0.22) 100%)'
      : 'rgba(255,255,255,0.07)',
    transform: compact ? 'none' : 'translateX(3px)',
  },
  '&:hover .nav-icon': { transform: 'scale(1.1) rotate(-4deg)' },
  '&:focus-visible': { outline: '2px solid #93c5fd', outlineOffset: 2 },
});

const iconSx = (active: boolean) => ({
  display: 'grid',
  placeItems: 'center',
  flexShrink: 0,
  width: 36,
  height: 36,
  borderRadius: '11px',
  color: active ? '#fff' : 'rgba(199,210,254,0.9)',
  background: active ? brand.gradient : 'rgba(255,255,255,0.06)',
  boxShadow: active ? '0 6px 16px rgba(59,130,246,0.55)' : 'none',
  transition: `transform 0.35s ${ease}, background 0.3s ${ease}`,
  '& svg': { fontSize: 20 },
});

const PortalLayout: React.FC<PortalLayoutProps> = ({ portalName, items, children, publicSite }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, logout } = useAuth();
  const { school } = useSchool();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(readCollapsed);
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const [flyout, setFlyout] = useState<{ anchor: HTMLElement; item: NavItem } | null>(null);
  const [userMenu, setUserMenu] = useState<HTMLElement | null>(null);
  const [scrolled, setScrolled] = useState(false);

  const compact = collapsed && !isMobile;
  const isActive = (path?: string) => !!path && location.pathname === path;
  const groupActive = (item: NavItem) => !!item.children?.some((child) => isActive(child.path));

  // Open the group that holds the current page
  useEffect(() => {
    const current = items.find(groupActive);
    if (current) setOpenGroup(current.label);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const toggleCollapsed = () => {
    setCollapsed((value) => {
      try {
        localStorage.setItem(COLLAPSE_KEY, value ? '0' : '1');
      } catch {
        /* the choice just won't be remembered */
      }
      return !value;
    });
  };

  const go = (path?: string) => {
    if (!path) return;
    navigate(path);
    setMobileOpen(false);
    setFlyout(null);
    setUserMenu(null);
  };

  const handleLogout = () => {
    setUserMenu(null);
    logout();
    navigate('/');
  };

  const crumbs = useMemo(() => {
    if (publicSite && location.pathname === '/') return { group: null as string | null, title: `Welcome to ${school.name}` };
    for (const item of items) {
      if (item.path === location.pathname) return { group: null as string | null, title: item.label };
      const child = item.children?.find((c) => c.path === location.pathname);
      if (child) return { group: item.label, title: child.label };
    }
    if (location.pathname === '/profile') return { group: null, title: 'My Profile' };
    return { group: null, title: portalName };
  }, [items, location.pathname, portalName, publicSite, school.name]);

  const today = useMemo(
    () => new Date().toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' }),
    []
  );

  const initials = (user?.first_name?.[0] || user?.email?.[0] || 'U').toUpperCase();
  const fullName = `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || user?.email || '';
  const roleLabel = (user?.user_type || '').replace('_', ' ').toLowerCase();

  // -------------------------------------------------------------------------
  // Left panel
  // -------------------------------------------------------------------------
  const sidebar = (
    <Box
      sx={{
        position: 'relative',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        color: '#fff',
        overflow: 'hidden',
        background: `linear-gradient(180deg, ${brand.navTop} 0%, ${brand.navMid} 52%, ${brand.navBottom} 100%)`,
        // Two soft lights drifting behind the menu
        '&::before, &::after': {
          content: '""',
          position: 'absolute',
          borderRadius: '50%',
          filter: 'blur(60px)',
          pointerEvents: 'none',
          animation: 'floatSlow 12s ease-in-out infinite',
        },
        '&::before': { width: 220, height: 220, top: -70, right: -90, background: 'rgba(59,130,246,0.45)' },
        '&::after': {
          width: 240,
          height: 240,
          bottom: 40,
          left: -130,
          background: 'rgba(139,92,246,0.40)',
          animationDelay: '-6s',
        },
      }}
    >
      {/* School */}
      <Box
        sx={{
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          px: compact ? 0 : 2.5,
          justifyContent: compact ? 'center' : 'flex-start',
          minHeight: 84,
          flexShrink: 0,
        }}
      >
        <SchoolLogo size={48} ring />
        {!compact && (
          <Box sx={{ minWidth: 0, animation: 'fadeIn 0.4s ease both' }}>
            <Typography noWrap sx={{ fontWeight: 800, fontSize: '1rem', lineHeight: 1.2, letterSpacing: '-0.01em' }}>
              {school.shortName}
            </Typography>
            <Typography
              noWrap
              sx={{
                mt: 0.25,
                fontSize: '0.7rem',
                fontWeight: 700,
                letterSpacing: '0.14em',
                textTransform: 'uppercase',
                background: 'linear-gradient(90deg, #93c5fd, #c4b5fd)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              {portalName}
            </Typography>
          </Box>
        )}
      </Box>

      <Box sx={{ mx: compact ? 1.5 : 2.5, height: '1px', background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.22), transparent)' }} />

      {/* Menu */}
      <Box
        component="nav"
        aria-label={portalName}
        sx={{
          position: 'relative',
          zIndex: 1,
          flexGrow: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          px: compact ? 1.25 : 1.75,
          py: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 0.5,
          scrollbarColor: 'rgba(255,255,255,0.25) transparent',
          '&::-webkit-scrollbar-thumb': { background: 'rgba(255,255,255,0.22)' },
        }}
      >
        {!compact && (
          <Typography sx={{ px: 1.25, pb: 0.75, fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.16em', color: 'rgba(199,210,254,0.5)' }}>
            MENU
          </Typography>
        )}

        {items.map((item, index) => {
          const hasChildren = !!item.children?.length;
          const active = hasChildren ? groupActive(item) : isActive(item.path);
          const expanded = hasChildren && openGroup === item.label;

          const row = (
            <Box
              component="button"
              type="button"
              aria-current={!hasChildren && active ? 'page' : undefined}
              aria-expanded={hasChildren && !compact ? expanded : undefined}
              onClick={(event: React.MouseEvent<HTMLElement>) => {
                if (!hasChildren) go(item.path);
                else if (compact) setFlyout({ anchor: event.currentTarget, item });
                else setOpenGroup(expanded ? null : item.label);
              }}
              sx={{
                ...rowSx(active, compact),
                animation: `fadeUp 0.45s ${ease} both`,
                animationDelay: `${index * 35}ms`,
              }}
            >
              <Box className="nav-icon" sx={iconSx(active)}>
                {item.icon}
              </Box>
              {!compact && (
                <>
                  <Typography noWrap sx={{ flexGrow: 1, fontSize: '0.9rem', fontWeight: active ? 700 : 500 }}>
                    {item.label}
                  </Typography>
                  {hasChildren && (
                    <ExpandMoreIcon
                      sx={{ fontSize: 20, opacity: 0.7, transition: `transform 0.35s ${ease}`, transform: expanded ? 'rotate(180deg)' : 'none' }}
                    />
                  )}
                </>
              )}
            </Box>
          );

          return (
            <Box key={item.label}>
              {compact ? (
                <Tooltip title={item.label} placement="right" arrow>
                  {row}
                </Tooltip>
              ) : (
                row
              )}

              {hasChildren && !compact && (
                <Collapse in={expanded} timeout={320} unmountOnExit>
                  <Box
                    sx={{
                      position: 'relative',
                      ml: 3.4,
                      pl: 2,
                      py: 0.5,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 0.25,
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        left: 0,
                        top: 6,
                        bottom: 6,
                        width: '1px',
                        background: 'linear-gradient(180deg, rgba(147,197,253,0.5), rgba(167,139,250,0.08))',
                      },
                    }}
                  >
                    {item.children!.map((child) => {
                      const childActive = isActive(child.path);
                      return (
                        <Box
                          key={child.path}
                          component="button"
                          type="button"
                          aria-current={childActive ? 'page' : undefined}
                          onClick={() => go(child.path)}
                          sx={{
                            position: 'relative',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1.25,
                            width: '100%',
                            minHeight: 38,
                            px: 1.25,
                            border: 0,
                            borderRadius: '10px',
                            cursor: 'pointer',
                            font: 'inherit',
                            textAlign: 'left',
                            color: childActive ? '#fff' : navText,
                            background: childActive ? 'rgba(96,165,250,0.20)' : 'transparent',
                            transition: `all 0.28s ${ease}`,
                            '& svg': { fontSize: 18, opacity: childActive ? 1 : 0.75 },
                            // Dot on the guide line
                            '&::before': {
                              content: '""',
                              position: 'absolute',
                              left: -19.5,
                              top: '50%',
                              width: 7,
                              height: 7,
                              borderRadius: '50%',
                              transform: `translateY(-50%) scale(${childActive ? 1 : 0})`,
                              background: '#93c5fd',
                              boxShadow: '0 0 10px #60a5fa',
                              transition: `transform 0.3s ${ease}`,
                            },
                            '&:hover': { color: '#fff', background: 'rgba(255,255,255,0.08)', transform: 'translateX(3px)' },
                            '&:focus-visible': { outline: '2px solid #93c5fd', outlineOffset: 2 },
                          }}
                        >
                          {child.icon}
                          <Typography noWrap sx={{ fontSize: '0.85rem', fontWeight: childActive ? 700 : 500 }}>
                            {child.label}
                          </Typography>
                        </Box>
                      );
                    })}
                  </Box>
                </Collapse>
              )}
            </Box>
          );
        })}
      </Box>

      {/* Signed-in user, or the way in */}
      <Box sx={{ position: 'relative', zIndex: 1, p: compact ? 1.25 : 1.75, flexShrink: 0 }}>
        {!user ? (
          <Tooltip title={compact ? 'Sign in' : ''} placement="right" arrow>
            <Box
              component="button"
              type="button"
              onClick={() => {
                setMobileOpen(false);
                publicSite?.onSignIn();
              }}
              aria-label="Sign in"
              sx={{
                position: 'relative',
                overflow: 'hidden',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 1,
                width: '100%',
                minHeight: 48,
                border: 0,
                borderRadius: '16px',
                cursor: 'pointer',
                font: 'inherit',
                fontWeight: 700,
                fontSize: '0.92rem',
                color: '#fff',
                background: brand.gradient,
                boxShadow: '0 10px 26px rgba(59,130,246,0.5)',
                transition: `transform 0.3s ${ease}, box-shadow 0.3s ${ease}`,
                '&::after': {
                  content: '""',
                  position: 'absolute',
                  inset: 0,
                  background: 'linear-gradient(110deg, transparent 30%, rgba(255,255,255,0.35) 50%, transparent 70%)',
                  transform: 'translateX(-120%)',
                  transition: `transform 0.7s ${ease}`,
                },
                '&:hover': { transform: 'translateY(-2px)', boxShadow: '0 14px 32px rgba(99,102,241,0.6)' },
                '&:hover::after': { transform: 'translateX(120%)' },
                '&:focus-visible': { outline: '2px solid #93c5fd', outlineOffset: 2 },
              }}
            >
              <LoginIcon sx={{ fontSize: 20 }} />
              {!compact && 'Sign in'}
            </Box>
          </Tooltip>
        ) : (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.25,
            p: compact ? 0.75 : 1.25,
            justifyContent: compact ? 'center' : 'flex-start',
            borderRadius: '16px',
            background: 'rgba(255,255,255,0.07)',
            border: '1px solid rgba(255,255,255,0.12)',
            backdropFilter: 'blur(10px)',
            transition: `background 0.3s ${ease}`,
            '&:hover': { background: 'rgba(255,255,255,0.11)' },
          }}
        >
          <Tooltip title={compact ? `${fullName} · Profile` : 'My profile'} placement="right" arrow>
            <Avatar
              src={user?.profile_picture_url || undefined}
              onClick={() => go('/profile')}
              sx={{
                width: 38,
                height: 38,
                cursor: 'pointer',
                fontWeight: 700,
                fontSize: '0.95rem',
                background: brand.gradientWarm,
                border: '2px solid rgba(255,255,255,0.35)',
                animation: 'pulseRing 2.6s ease-out infinite',
              }}
            >
              {initials}
            </Avatar>
          </Tooltip>
          {!compact && (
            <>
              <Box sx={{ minWidth: 0, flexGrow: 1 }}>
                <Typography noWrap sx={{ fontSize: '0.85rem', fontWeight: 700, lineHeight: 1.25 }}>
                  {fullName}
                </Typography>
                <Typography noWrap sx={{ fontSize: '0.72rem', color: 'rgba(199,210,254,0.7)', textTransform: 'capitalize' }}>
                  {roleLabel}
                </Typography>
              </Box>
              <Tooltip title="Log out" arrow>
                <IconButton
                  size="small"
                  onClick={handleLogout}
                  aria-label="Log out"
                  sx={{ color: 'rgba(226,232,255,0.8)', '&:hover': { color: '#fff', background: 'rgba(248,113,113,0.28)' } }}
                >
                  <LogoutIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}
        </Box>
        )}
      </Box>
    </Box>
  );

  const currentWidth = collapsed ? WIDTH_COLLAPSED : WIDTH;
  const paperSx = { border: 0, boxSizing: 'border-box' as const, overflow: 'hidden', boxShadow: '8px 0 40px rgba(11,20,55,0.28)' };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ '& .MuiDrawer-paper': { ...paperSx, width: WIDTH } }}
        >
          {sidebar}
        </Drawer>
      ) : (
        <Box component="aside" sx={{ width: currentWidth, flexShrink: 0, transition: `width 0.4s ${ease}` }}>
          <Box
            sx={{
              ...paperSx,
              position: 'fixed',
              top: 0,
              left: 0,
              height: '100vh',
              width: currentWidth,
              zIndex: theme.zIndex.drawer,
              transition: `width 0.4s ${ease}`,
              borderRadius: '0 26px 26px 0',
            }}
          >
            {sidebar}
          </Box>
          {/* Collapse handle on the panel's edge */}
          <Tooltip title={collapsed ? 'Expand menu' : 'Collapse menu'} placement="right" arrow>
            <IconButton
              onClick={toggleCollapsed}
              aria-label={collapsed ? 'Expand menu' : 'Collapse menu'}
              size="small"
              sx={{
                position: 'fixed',
                top: 30,
                left: currentWidth - 14,
                zIndex: theme.zIndex.drawer + 1,
                width: 28,
                height: 28,
                color: '#fff',
                background: brand.gradient,
                border: '2px solid #fff',
                boxShadow: '0 6px 16px rgba(37,99,235,0.45)',
                transition: `left 0.4s ${ease}, transform 0.3s ${ease}`,
                '&:hover': { background: brand.gradient, transform: 'scale(1.15)' },
              }}
            >
              {collapsed ? <ChevronRightIcon sx={{ fontSize: 18 }} /> : <ChevronLeftIcon sx={{ fontSize: 18 }} />}
            </IconButton>
          </Tooltip>
        </Box>
      )}

      {/* Main column */}
      <Box sx={{ flexGrow: 1, minWidth: 0, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Box
          component="header"
          sx={{
            position: 'sticky',
            top: 0,
            zIndex: theme.zIndex.appBar,
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            minHeight: 72,
            px: { xs: 1.5, sm: 3, md: 4 },
            background: scrolled ? 'rgba(255,255,255,0.78)' : 'rgba(255,255,255,0.4)',
            backdropFilter: 'saturate(180%) blur(16px)',
            WebkitBackdropFilter: 'saturate(180%) blur(16px)',
            borderBottom: '1px solid',
            borderColor: scrolled ? 'rgba(15,23,42,0.08)' : 'transparent',
            boxShadow: scrolled ? '0 10px 30px rgba(15,23,42,0.07)' : 'none',
            transition: `background 0.35s ${ease}, box-shadow 0.35s ${ease}, border-color 0.35s ${ease}`,
          }}
        >
          {isMobile && (
            <IconButton onClick={() => setMobileOpen(true)} aria-label="Open menu" sx={{ color: 'primary.main' }}>
              <MenuIcon />
            </IconButton>
          )}
          <Box key={location.pathname} sx={{ minWidth: 0, flexGrow: 1, animation: `fadeUp 0.4s ${ease} both` }}>
            <Typography noWrap sx={{ fontSize: '0.72rem', fontWeight: 600, color: 'text.secondary', letterSpacing: '0.04em' }}>
              {crumbs.group ? `${crumbs.group}  /  ${crumbs.title}` : today}
            </Typography>
            <Typography
              noWrap
              component="h1"
              sx={{
                fontSize: { xs: '1.15rem', sm: '1.4rem' },
                fontWeight: 800,
                letterSpacing: '-0.02em',
                lineHeight: 1.25,
                background: 'linear-gradient(90deg, #0f172a 0%, #1d4ed8 60%, #7c3aed 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              {crumbs.title}
            </Typography>
          </Box>

          {!user && publicSite && (
            <Button variant="contained" startIcon={<LoginIcon />} onClick={publicSite.onSignIn} sx={{ borderRadius: '999px', px: 2.5 }}>
              Sign in
            </Button>
          )}
          {user && (
            <>
              {!publicSite && <NotificationBell color="primary" />}
              <Box
                component="button"
                type="button"
                onClick={(event: React.MouseEvent<HTMLElement>) => setUserMenu(event.currentTarget)}
                aria-label="Account menu"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  p: 0.5,
                  pr: { xs: 0.5, sm: 1.5 },
                  border: '1px solid rgba(15,23,42,0.08)',
                  borderRadius: '999px',
                  background: 'rgba(255,255,255,0.8)',
                  cursor: 'pointer',
                  font: 'inherit',
                  transition: `box-shadow 0.3s ${ease}, transform 0.3s ${ease}`,
                  '&:hover': { boxShadow: brand.shadowLift, transform: 'translateY(-1px)' },
                }}
              >
                <Avatar src={user.profile_picture_url || undefined} sx={{ width: 34, height: 34, fontSize: '0.9rem', fontWeight: 700, background: brand.gradient }}>
                  {initials}
                </Avatar>
                <Typography noWrap sx={{ display: { xs: 'none', sm: 'block' }, maxWidth: 140, fontSize: '0.85rem', fontWeight: 600, color: 'text.primary' }}>
                  {user.first_name}
                </Typography>
              </Box>
            </>
          )}
        </Box>

        <Box component="main" sx={{ flexGrow: 1, ...(publicSite ? {} : { p: { xs: 1.5, sm: 3, md: 4 }, pt: { xs: 1.5, sm: 2 } }) }}>
          <Box key={location.pathname} className="fade-up">
            {children}
          </Box>
        </Box>

        {publicSite ? (
          publicSite.footer
        ) : (
          <Box component="footer" sx={{ px: { xs: 2, md: 4 }, py: 2, textAlign: 'center', color: 'text.secondary', fontSize: '0.78rem' }}>
            © {new Date().getFullYear()} {school.name}
          </Box>
        )}
      </Box>

      {/* Account menu */}
      <Menu
        anchorEl={userMenu}
        open={Boolean(userMenu)}
        onClose={() => setUserMenu(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        slotProps={{ paper: { sx: { mt: 1, minWidth: 220 } } }}
      >
        <Box sx={{ px: 2, py: 1.25 }}>
          <Typography variant="subtitle2" fontWeight={700} noWrap>
            {fullName}
          </Typography>
          <Typography variant="caption" color="text.secondary" noWrap component="div">
            {user?.email}
          </Typography>
        </Box>
        <Divider />
        {publicSite?.dashboardPath && (
          <MenuItem onClick={() => go(publicSite.dashboardPath)}>
            <ListItemIcon>
              <DashboardIcon fontSize="small" />
            </ListItemIcon>
            My dashboard
          </MenuItem>
        )}
        <MenuItem onClick={() => go('/profile')}>
          <ListItemIcon>
            <PersonIcon fontSize="small" />
          </ListItemIcon>
          My profile
        </MenuItem>
        <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" color="error" />
          </ListItemIcon>
          Log out
        </MenuItem>
      </Menu>

      {/* Sub-menu of a group while the panel is collapsed */}
      <Popover
        open={Boolean(flyout)}
        anchorEl={flyout?.anchor}
        onClose={() => setFlyout(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        slotProps={{
          paper: {
            sx: {
              ml: 1.5,
              p: 1,
              minWidth: 230,
              color: '#fff',
              borderRadius: '16px',
              background: 'linear-gradient(160deg, rgba(19,28,82,0.96), rgba(30,27,107,0.96))',
              backdropFilter: 'blur(14px)',
              border: '1px solid rgba(255,255,255,0.14)',
              boxShadow: '0 24px 60px rgba(11,20,55,0.5)',
            },
          },
        }}
      >
        <Typography sx={{ px: 1.25, py: 0.75, fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.14em', color: 'rgba(199,210,254,0.6)', textTransform: 'uppercase' }}>
          {flyout?.item.label}
        </Typography>
        {flyout?.item.children?.map((child) => {
          const childActive = isActive(child.path);
          return (
            <Box
              key={child.path}
              component="button"
              type="button"
              onClick={() => go(child.path)}
              sx={{ ...rowSx(childActive, false), minHeight: 40, '&::before': { display: 'none' }, '& svg': { fontSize: 19 } }}
            >
              {child.icon}
              <Typography noWrap sx={{ fontSize: '0.87rem', fontWeight: childActive ? 700 : 500 }}>
                {child.label}
              </Typography>
            </Box>
          );
        })}
      </Popover>
    </Box>
  );
};

export default PortalLayout;
