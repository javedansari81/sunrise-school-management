import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  IconButton,
  InputAdornment,
} from '@mui/material';
import {
  Close as CloseIcon,
  Visibility,
  VisibilityOff,
  School as SchoolIcon,
  Login as LoginIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { sessionService } from '../services/sessionService';
import { dialogStyles } from '../styles/dialogTheme';

interface LoginPopupProps {
  open: boolean;
  onClose: () => void;
}

const LoginPopup: React.FC<LoginPopupProps> = ({ open, onClose }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [sessionExpiredMessage, setSessionExpiredMessage] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  // Check if this popup was triggered by session expiration
  useEffect(() => {
    if (open) {
      const token = localStorage.getItem('authToken');
      if (token && sessionService.isTokenExpired(token)) {
        setSessionExpiredMessage('Your session has expired. Please log in again to continue.');
      } else if (!token) {
        setSessionExpiredMessage('Welcome to Sunrise School. Please sign in to access your account.');
      } else {
        setSessionExpiredMessage('');
      }
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await login(email, password);

      // Close popup first
      onClose();

      // Redirect based on user role
      const userType = response.user.user_type;

      // Redirect users based on their role
      if (userType?.toUpperCase() === 'ADMIN') {
        navigate('/admin/dashboard');
      } else if (userType?.toUpperCase() === 'TEACHER') {
        navigate('/teacher/dashboard');
      } else if (userType?.toUpperCase() === 'STUDENT') {
        navigate('/student/dashboard');
      } else {
        navigate('/'); // Other users go to home
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setEmail('');
    setPassword('');
    setError('');
    setShowPassword(false);
    setSessionExpiredMessage('');
    onClose();
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };



  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      slotProps={{
        paper: {
          sx: dialogStyles.paper
        }
      }}
    >
      <DialogTitle sx={dialogStyles.title}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SchoolIcon sx={{ fontSize: 32 }} />
          <Typography sx={dialogStyles.titleText}>
            Login to Sunrise School
          </Typography>
        </Box>
        <IconButton
          onClick={handleClose}
          sx={dialogStyles.closeButton}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={dialogStyles.content}>
        {sessionExpiredMessage && (
          <Alert
            severity="info"
            sx={dialogStyles.alert}
            icon={<WarningIcon />}
          >
            {sessionExpiredMessage}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={dialogStyles.alert}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Email Address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            margin="normal"
            variant="outlined"
            sx={{ ...dialogStyles.textField, mb: 2 }}
            helperText="Please enter your registered email address"
          />

          <TextField
            fullWidth
            label="Password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            margin="normal"
            variant="outlined"
            sx={{ ...dialogStyles.textField, mb: 3 }}
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={togglePasswordVisibility}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }
            }}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
            startIcon={<LoginIcon />}
            sx={{
              ...dialogStyles.primaryButton,
              py: 1.5,
              fontSize: '1.1rem',
              mb: 2,
            }}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </Button>
        </Box>


      </DialogContent>
    </Dialog>
  );
};

export default LoginPopup;
