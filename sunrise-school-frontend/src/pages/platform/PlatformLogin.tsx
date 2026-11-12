import React, { useEffect, useState } from 'react';
import { Alert, Box, Button, CircularProgress, IconButton, InputAdornment, TextField, Typography } from '@mui/material';
import { AdminPanelSettings as PlatformIcon, Visibility, VisibilityOff } from '@mui/icons-material';
import { Navigate, useNavigate } from 'react-router-dom';
import { platformAuth } from '../../services/platformService';
import { apiError } from '../../components/ui';
import { brand, ease } from '../../theme';

const PlatformLogin: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.title = 'Platform admin';
  }, []);

  if (platformAuth.isLoggedIn()) return <Navigate to="/platform" replace />;

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await platformAuth.login(email.trim(), password);
      navigate('/platform', { replace: true });
    } catch (failure) {
      setError(apiError(failure, 'Login failed.'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        p: 2,
        overflow: 'hidden',
        background: `linear-gradient(135deg, ${brand.navTop} 0%, ${brand.navMid} 50%, ${brand.navBottom} 100%)`,
        '&::before, &::after': { content: '""', position: 'absolute', borderRadius: '50%', filter: 'blur(90px)', animation: 'floatSlow 12s ease-in-out infinite' },
        '&::before': { width: 420, height: 420, top: -120, left: -100, background: 'rgba(59,130,246,0.5)' },
        '&::after': { width: 460, height: 460, bottom: -160, right: -120, background: 'rgba(168,85,247,0.45)', animationDelay: '-6s' },
      }}
    >
      <Box
        component="form"
        onSubmit={submit}
        sx={{
          position: 'relative',
          zIndex: 1,
          width: '100%',
          maxWidth: 420,
          p: { xs: 3, sm: 4.5 },
          borderRadius: '28px',
          color: '#fff',
          background: 'rgba(255,255,255,0.09)',
          border: '1px solid rgba(255,255,255,0.2)',
          backdropFilter: 'blur(24px)',
          boxShadow: '0 40px 100px rgba(0,0,0,0.45)',
          animation: `fadeUp 0.6s ${ease} both`,
          display: 'flex',
          flexDirection: 'column',
          gap: 2.25,
          '& .MuiFilledInput-root': { background: 'rgba(255,255,255,0.95)', borderRadius: '10px', '&:hover, &.Mui-focused': { background: '#fff' } },
        }}
      >
        <Box sx={{ display: 'grid', placeItems: 'center', width: 64, height: 64, mx: 'auto', borderRadius: '20px', background: brand.gradient, boxShadow: '0 16px 36px rgba(59,130,246,0.55)' }}>
          <PlatformIcon sx={{ fontSize: 34 }} />
        </Box>
        <Box sx={{ textAlign: 'center' }}>
          <Typography sx={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>Platform admin</Typography>
          <Typography sx={{ opacity: 0.75, fontSize: '0.9rem' }}>Manage the schools on this service</Typography>
        </Box>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoFocus autoComplete="username" variant="filled" />
        <TextField
          label="Password"
          type={show ? 'text' : 'password'}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          autoComplete="current-password"
          variant="filled"
          slotProps={{
            input: {
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShow(!show)} edge="end" aria-label={show ? 'Hide password' : 'Show password'}>
                    {show ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            },
          }}
        />
        <Button type="submit" variant="contained" size="large" disabled={busy} startIcon={busy ? <CircularProgress size={18} color="inherit" /> : undefined} sx={{ py: 1.4, fontSize: '1rem' }}>
          {busy ? 'Signing in…' : 'Sign in'}
        </Button>
        <Typography sx={{ textAlign: 'center', fontSize: '0.8rem', opacity: 0.65 }}>
          School staff, teachers and students sign in on their own school’s address.
        </Typography>
      </Box>
    </Box>
  );
};

export default PlatformLogin;
