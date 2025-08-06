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
  Divider,
  Chip,
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
        setSessionExpiredMessage('Please log in to access this page.');
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
      console.log('User logged in with role:', userType);

      // Redirect users based on their role
      if (userType?.toUpperCase() === 'ADMIN') {
        navigate('/admin/dashboard');
      } else if (userType?.toUpperCase() === 'TEACHER') {
        navigate('/teacher/dashboard');
      } else {
        navigate('/'); // Students and other users go to home
      }
    } catch (err: any) {
      console.error('Login error:', err);
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

  const fillDemoCredentials = (userType: 'admin' | 'teacher' | 'student') => {
    const credentials = {
      admin: { email: 'admin@sunriseschool.edu', password: 'admin123' },
      teacher: { email: 'teacher@sunriseschool.edu', password: 'admin123' },
      student: { email: '9876543212', password: 'Sunrise@001' },
    };
    
    setEmail(credentials[userType].email);
    setPassword(credentials[userType].password);
    setError('');
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        }
      }}
    >
      <DialogTitle sx={{ 
        textAlign: 'center', 
        pb: 1,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        position: 'relative'
      }}>
        <IconButton
          onClick={handleClose}
          sx={{ 
            position: 'absolute', 
            right: 8, 
            top: 8,
            color: 'white'
          }}
        >
          <CloseIcon />
        </IconButton>
        
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mt: 1 }}>
          <SchoolIcon sx={{ fontSize: 32 }} />
          <Typography variant="h5" fontWeight="bold">
            Login to Sunrise School
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 3 }}>
        {sessionExpiredMessage && (
          <Alert
            severity="warning"
            sx={{ mb: 2 }}
            icon={<WarningIcon />}
          >
            {sessionExpiredMessage}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
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
            sx={{ mb: 2 }}
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
            sx={{ mb: 3 }}
            InputProps={{
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
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 'bold',
              borderRadius: 2,
              mb: 2,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
              }
            }}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </Button>
        </Box>

        <Divider sx={{ my: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Demo Credentials
          </Typography>
        </Divider>

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
          <Chip
            label="👨‍💼 Admin"
            onClick={() => fillDemoCredentials('admin')}
            clickable
            variant="outlined"
            size="small"
            sx={{ '&:hover': { backgroundColor: 'primary.light', color: 'white' } }}
          />
          <Chip
            label="👨‍🏫 Teacher"
            onClick={() => fillDemoCredentials('teacher')}
            clickable
            variant="outlined"
            size="small"
            sx={{ '&:hover': { backgroundColor: 'secondary.light', color: 'white' } }}
          />
          <Chip
            label="👨‍🎓 Student"
            onClick={() => fillDemoCredentials('student')}
            clickable
            variant="outlined"
            size="small"
            sx={{ '&:hover': { backgroundColor: 'success.light', color: 'white' } }}
          />
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default LoginPopup;
