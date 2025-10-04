import React from 'react';
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
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Close as CloseIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';

export interface ErrorDialogProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  message: string;
  severity?: 'error' | 'warning' | 'info';
  errorCode?: string;
  fieldName?: string;
  details?: Record<string, any>;
  showDetails?: boolean;
  actionText?: string;
  onAction?: () => void;
  showCancel?: boolean;
  cancelText?: string;
}

const ErrorDialog: React.FC<ErrorDialogProps> = ({
  open,
  onClose,
  title,
  message,
  severity = 'error',
  errorCode,
  fieldName,
  details,
  showDetails = false,
  actionText = 'OK',
  onAction,
  showCancel = false,
  cancelText = 'Cancel'
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [showDetailedInfo, setShowDetailedInfo] = React.useState(false);

  const getSeverityIcon = () => {
    switch (severity) {
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <ErrorIcon color="error" />;
    }
  };

  const getSeverityColor = () => {
    switch (severity) {
      case 'warning':
        return theme.palette.warning.main;
      case 'info':
        return theme.palette.info.main;
      default:
        return theme.palette.error.main;
    }
  };

  const getDefaultTitle = () => {
    switch (severity) {
      case 'warning':
        return 'Warning';
      case 'info':
        return 'Information';
      default:
        return 'Error';
    }
  };

  const handleAction = () => {
    if (onAction) {
      onAction();
    } else {
      onClose();
    }
  };

  const formatErrorCode = (code: string) => {
    // Convert error codes like "UNIQUE_VIOLATION_STUDENTS_EMAIL_KEY" to readable format
    return code
      .replace(/_/g, ' ')
      .toLowerCase()
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      fullScreen={isMobile}
      PaperProps={{
        sx: {
          borderRadius: isMobile ? 0 : 2,
          maxHeight: isMobile ? '100vh' : '80vh',
          m: isMobile ? 0 : 2
        }
      }}
    >
      {/* Dialog Title */}
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          pb: 1,
          borderBottom: `1px solid ${theme.palette.divider}`,
          bgcolor: severity === 'error' ? 'error.light' : 
                  severity === 'warning' ? 'warning.light' : 'info.light',
          color: severity === 'error' ? 'error.contrastText' : 
                 severity === 'warning' ? 'warning.contrastText' : 'info.contrastText'
        }}
      >
        {getSeverityIcon()}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {title || getDefaultTitle()}
        </Typography>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{
            color: 'inherit',
            '&:hover': {
              bgcolor: 'rgba(255, 255, 255, 0.1)'
            }
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      {/* Dialog Content */}
      <DialogContent sx={{ pt: 2, pb: 1 }}>
        {/* Main Error Message */}
        <Alert 
          severity={severity} 
          sx={{ 
            mb: 2,
            '& .MuiAlert-message': {
              fontSize: '1rem',
              lineHeight: 1.5
            }
          }}
        >
          {message}
        </Alert>

        {/* Error Code Display */}
        {errorCode && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Error Code: <strong>{formatErrorCode(errorCode)}</strong>
            </Typography>
          </Box>
        )}

        {/* Field Name Display */}
        {fieldName && fieldName !== 'validation' && fieldName !== 'unknown_field' && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Related Field: <strong>{fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</strong>
            </Typography>
          </Box>
        )}

        {/* Detailed Information Toggle */}
        {(details || showDetails) && (
          <Box sx={{ mt: 2 }}>
            <Button
              variant="text"
              size="small"
              onClick={() => setShowDetailedInfo(!showDetailedInfo)}
              sx={{ mb: 1 }}
            >
              {showDetailedInfo ? 'Hide Details' : 'Show Details'}
            </Button>
            
            {showDetailedInfo && (
              <Box
                sx={{
                  bgcolor: 'grey.50',
                  border: `1px solid ${theme.palette.divider}`,
                  borderRadius: 1,
                  p: 2,
                  maxHeight: 200,
                  overflow: 'auto'
                }}
              >
                {details && (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Technical Details:
                    </Typography>
                    <pre style={{ 
                      fontSize: '0.75rem', 
                      margin: 0, 
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word'
                    }}>
                      {JSON.stringify(details, null, 2)}
                    </pre>
                  </Box>
                )}
              </Box>
            )}
          </Box>
        )}

        {/* Help Text */}
        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            💡 <strong>What to do next:</strong>
            <br />
            {severity === 'error' && 'Please correct the issue and try again. If the problem persists, contact support.'}
            {severity === 'warning' && 'Please review the warning and decide how to proceed.'}
            {severity === 'info' && 'This is for your information. No action is required.'}
          </Typography>
        </Box>
      </DialogContent>

      {/* Dialog Actions */}
      <DialogActions sx={{ p: 2, pt: 1, gap: 1 }}>
        {showCancel && (
          <Button
            onClick={onClose}
            variant="outlined"
            color="inherit"
            fullWidth={isMobile}
          >
            {cancelText}
          </Button>
        )}
        <Button
          onClick={handleAction}
          variant="contained"
          color={severity === 'error' ? 'error' : severity === 'warning' ? 'warning' : 'primary'}
          fullWidth={isMobile}
          autoFocus
        >
          {actionText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ErrorDialog;
