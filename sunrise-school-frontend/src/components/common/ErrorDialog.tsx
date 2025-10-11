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
import { dialogStyles } from '../../styles/dialogTheme';

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
      slotProps={{
        paper: {
          sx: {
            ...dialogStyles.paper,
            borderRadius: isMobile ? 0 : 3,
            maxHeight: isMobile ? '100vh' : '90vh',
            m: isMobile ? 0 : 2
          }
        }
      }}
    >
      {/* Dialog Title */}
      <DialogTitle
        sx={{
          ...dialogStyles.title,
          bgcolor: severity === 'error' ? 'error.main' :
                  severity === 'warning' ? 'warning.main' : 'info.main',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {getSeverityIcon()}
          <Typography sx={dialogStyles.titleText}>
            {title || getDefaultTitle()}
          </Typography>
        </Box>
        <IconButton
          onClick={onClose}
          sx={dialogStyles.closeButton}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      {/* Dialog Content */}
      <DialogContent sx={dialogStyles.content}>
        {/* Main Error Message */}
        <Alert
          severity={severity}
          sx={dialogStyles.alert}
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
      <DialogActions sx={dialogStyles.actions}>
        {showCancel && (
          <Button
            onClick={onClose}
            variant="outlined"
            fullWidth={isMobile}
            sx={dialogStyles.secondaryButton}
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
          sx={dialogStyles.primaryButton}
        >
          {actionText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ErrorDialog;
