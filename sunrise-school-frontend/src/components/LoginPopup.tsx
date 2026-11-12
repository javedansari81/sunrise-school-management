import React, { useEffect, useState } from 'react';
import { Alert, Box, Button, CircularProgress, Dialog, IconButton, InputAdornment, TextField, Typography } from '@mui/material';
import { Close as CloseIcon, Login as LoginIcon, Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSchool } from '../contexts/SchoolContext';
import { sessionService } from '../services/sessionService';
import SchoolLogo from './common/SchoolLogo';
import { brand, ease } from '../theme';

interface LoginPopupProps {
  open: boolean;
  onClose: () => void;
}

const HOME_BY_ROLE: Record<string, string> = {
  ADMIN: '/admin/dashboard',
  SUPER_ADMIN: '/admin/dashboard',
  TEACHER: '/teacher/dashboard',
  STUDENT: '/student/dashboard',
};

const LoginPopup: React.FC<LoginPopupProps> = ({ open, onClose }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);

  const { login } = useAuth();
  const { school } = useSchool();
  const navigate = useNavigate();

  // Was the popup opened because the session ran out?
  useEffect(() => {
    if (!open) return;
    const token = localStorage.getItem('authToken');
    setSessionExpired(Boolean(token && sessionService.isTokenExpired(token)));
  }, [open]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      // The API knows the school from this site's address, so the same email can exist at two schools
      const response = await login(email, password);
      onClose();
      navigate(HOME_BY_ROLE[response.user.user_type?.toUpperCase()] || '/');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : err.message || 'Login failed. Please check your email and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setEmail('');
    setPassword('');
    setError('');
    setShowPassword(false);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="xs"
      fullWidth
      slotProps={{ paper: { sx: { overflow: 'hidden', borderRadius: '26px', animation: `fadeUp 0.45s ${ease} both` } } }}
    >
      {/* School banner */}
      <Box
        sx={{
          position: 'relative',
          overflow: 'hidden',
          px: 3,
          pt: 4,
          pb: 3.5,
          color: '#fff',
          textAlign: 'center',
          background: brand.gradientHero,
          '&::before, &::after': { content: '""', position: 'absolute', borderRadius: '50%', filter: 'blur(46px)', animation: 'floatSlow 9s ease-in-out infinite' },
          '&::before': { width: 200, height: 200, top: -90, right: -60, background: 'rgba(244,114,182,0.5)' },
          '&::after': { width: 180, height: 180, bottom: -100, left: -50, background: 'rgba(56,189,248,0.45)', animationDelay: '-4s' },
        }}
      >
        <IconButton onClick={handleClose} aria-label="Close" sx={{ position: 'absolute', top: 10, right: 10, zIndex: 1, color: '#fff' }}>
          <CloseIcon />
        </IconButton>
        <Box sx={{ position: 'relative', display: 'inline-block' }}>
          <SchoolLogo size={72} ring />
        </Box>
        <Typography sx={{ position: 'relative', mt: 1.5, fontSize: '1.3rem', fontWeight: 800, letterSpacing: '-0.01em', lineHeight: 1.25 }}>
          {school.name}
        </Typography>
        <Typography sx={{ position: 'relative', mt: 0.5, opacity: 0.85, fontSize: '0.9rem' }}>
          Sign in to your school account
        </Typography>
      </Box>

      <Box component="form" onSubmit={handleSubmit} sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {sessionExpired && <Alert severity="info">Your session has ended. Please sign in again to continue.</Alert>}
        {error && <Alert severity="error">{error}</Alert>}

        <TextField
          label="Email address"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
          autoFocus
          autoComplete="username"
        />
        <TextField
          label="Password"
          type={showPassword ? 'text' : 'password'}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          autoComplete="current-password"
          slotProps={{
            input: {
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton aria-label={showPassword ? 'Hide password' : 'Show password'} onClick={() => setShowPassword(!showPassword)} edge="end">
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            },
          }}
        />
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <LoginIcon />}
          sx={{ py: 1.4, fontSize: '1rem' }}
        >
          {loading ? 'Signing in…' : 'Sign in'}
        </Button>
        <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center' }}>
          Admins, teachers and students all sign in here.
        </Typography>
      </Box>
    </Dialog>
  );
};

export default LoginPopup;
