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
  fieldName?: string;
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
  fieldName,
  actionText = 'OK',
  onAction,
  showCancel = false,
  cancelText = 'Cancel'
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

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
      {/* Dialog Title - Clean and Simple */}
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          bgcolor: 'background.paper',
          borderBottom: `3px solid ${getSeverityColor()}`,
          py: 2,
          px: 3
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {getSeverityIcon()}
          <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
            {title || getDefaultTitle()}
          </Typography>
        </Box>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{
            color: 'text.secondary',
            '&:hover': {
              bgcolor: 'action.hover'
            }
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      {/* Dialog Content */}
      <DialogContent sx={dialogStyles.content}>
        {/* Main Error Message - Prominent Display */}
        <Alert
          severity={severity}
          icon={getSeverityIcon()}
          sx={{
            ...dialogStyles.alert,
            fontSize: '1rem',
            '& .MuiAlert-message': {
              width: '100%',
              fontSize: '1rem',
              lineHeight: 1.6
            }
          }}
        >
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            {message}
          </Typography>
        </Alert>

        {/* Field Name Display - Only if meaningful */}
        {fieldName && fieldName !== 'validation' && fieldName !== 'unknown_field' && (
          <Box sx={{ mt: 2, p: 1.5, bgcolor: 'grey.50', borderRadius: 1, borderLeft: `4px solid ${getSeverityColor()}` }}>
            <Typography variant="body2" color="text.secondary">
              <strong>Field:</strong> {fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </Typography>
          </Box>
        )}
      </DialogContent>

      {/* Dialog Actions - Clean and Prominent */}
      <DialogActions
        sx={{
          px: 3,
          py: 2,
          bgcolor: 'grey.50',
          borderTop: `1px solid ${theme.palette.divider}`,
          gap: 1
        }}
      >
        {showCancel && (
          <Button
            onClick={onClose}
            variant="outlined"
            fullWidth={isMobile}
            sx={{
              textTransform: 'none',
              fontWeight: 500
            }}
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
          sx={{
            textTransform: 'none',
            fontWeight: 600,
            px: 4,
            py: 1
          }}
        >
          {actionText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ErrorDialog;
