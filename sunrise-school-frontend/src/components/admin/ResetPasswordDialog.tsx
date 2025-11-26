import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
  IconButton,
  CircularProgress,
  Divider
} from '@mui/material';
import { Close as CloseIcon, ContentCopy as CopyIcon } from '@mui/icons-material';
import { adminAPI } from '../../services/api';

interface ResetPasswordDialogProps {
  open: boolean;
  onClose: () => void;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    user_type?: string;
  } | null;
  onSuccess?: () => void;
}

const ResetPasswordDialog: React.FC<ResetPasswordDialogProps> = ({
  open,
  onClose,
  user,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [resetData, setResetData] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  const handleClose = () => {
    setLoading(false);
    setError(null);
    setSuccess(false);
    setResetData(null);
    setCopied(false);
    onClose();
  };

  const handleReset = async () => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      const response = await adminAPI.resetUserPassword(user.id);
      setResetData(response.data);
      setSuccess(true);
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: any) {
      let errorMessage = 'Failed to reset password';

      // Handle different error response formats
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;

        // If detail is an array (validation errors)
        if (Array.isArray(detail)) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        }
        // If detail is a string
        else if (typeof detail === 'string') {
          errorMessage = detail;
        }
        // If detail is an object
        else {
          errorMessage = JSON.stringify(detail);
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCredentials = () => {
    if (!resetData) return;

    const credentials = `Email: ${resetData.email}\nPassword: ${resetData.default_password}`;
    navigator.clipboard.writeText(credentials);
    setCopied(true);
    
    setTimeout(() => {
      setCopied(false);
    }, 2000);
  };

  if (!user) return null;

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle sx={{ bgcolor: 'white', borderBottom: '1px solid #e0e0e0' }}>
        {success ? 'Password Reset Successful' : 'Reset Password'}
        <IconButton
          onClick={handleClose}
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ mt: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {!success ? (
          <Box>
            <Typography variant="body1" gutterBottom>
              Are you sure you want to reset the password for:
            </Typography>
            
            <Box sx={{ mt: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Name:</strong> {user.first_name} {user.last_name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                <strong>Email:</strong> {user.email}
              </Typography>
              {user.user_type && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  <strong>Type:</strong> {user.user_type}
                </Typography>
              )}
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              The password will be reset to the default password: <strong>Sunrise@001</strong>
            </Alert>
          </Box>
        ) : (
          <Box>
            <Alert severity="success" sx={{ mb: 2 }}>
              Password has been reset successfully!
            </Alert>

            <Typography variant="body1" gutterBottom>
              Share these credentials with the user:
            </Typography>

            <Box sx={{ mt: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Name:</strong> {resetData?.user_name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                <strong>Email:</strong> {resetData?.email}
              </Typography>
              <Divider sx={{ my: 1.5 }} />
              <Typography variant="body2" color="text.secondary">
                <strong>Password:</strong> {resetData?.default_password}
              </Typography>
            </Box>

            <Button
              variant="outlined"
              startIcon={<CopyIcon />}
              onClick={handleCopyCredentials}
              fullWidth
              sx={{ mt: 2 }}
            >
              {copied ? 'Copied!' : 'Copy Credentials'}
            </Button>

            <Alert severity="info" sx={{ mt: 2 }}>
              The user can login with these credentials and optionally change their password later through their profile.
            </Alert>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        {!success ? (
          <>
            <Button onClick={handleClose} disabled={loading}>
              Cancel
            </Button>
            <Button
              onClick={handleReset}
              variant="contained"
              color="primary"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </Button>
          </>
        ) : (
          <Button onClick={handleClose} variant="contained">
            Close
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ResetPasswordDialog;

