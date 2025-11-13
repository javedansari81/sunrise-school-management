import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Typography,
  CircularProgress,
  Box,
  FormControl,
  InputLabel,
  Select,
  Divider,
  IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import { enhancedFeesAPI } from '../../services/api';
import { configurationService } from '../../services/configurationService';

interface PaymentReversalDialogProps {
  open: boolean;
  onClose: () => void;
  payment: any; // Payment object with payment_id, amount, payment_date, etc.
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

const PaymentReversalDialog: React.FC<PaymentReversalDialogProps> = ({
  open,
  onClose,
  payment,
  onSuccess,
  onError
}) => {
  const [loading, setLoading] = useState(false);
  const [reason, setReason] = useState<number>(0);
  const [details, setDetails] = useState<string>('');

  // Get reversal reasons from configuration
  const config = configurationService.getServiceConfiguration('fee-management');
  const reversalReasons = config?.reversal_reasons?.filter(r => r.is_active) || [];

  // Reset form when dialog opens
  React.useEffect(() => {
    if (open) {
      setReason(0);
      setDetails('');
    }
  }, [open]);

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  const handleSubmit = async () => {
    if (!reason || reason === 0) {
      onError('Please select a reversal reason');
      return;
    }

    setLoading(true);
    try {
      const response = await enhancedFeesAPI.reversePaymentFull(payment.payment_id, {
        reason_id: reason,
        details: details || undefined
      });

      onSuccess(response.data.message || 'Payment reversed successfully');
      handleClose();
    } catch (err: any) {
      console.error('Error reversing payment:', err);

      // Handle different error response formats
      let errorMessage = 'Failed to reverse payment';

      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;

        // If detail is an array (validation errors), extract messages
        if (Array.isArray(detail)) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        }
        // If detail is a string, use it directly
        else if (typeof detail === 'string') {
          errorMessage = detail;
        }
        // If detail is an object, try to extract message
        else if (typeof detail === 'object') {
          errorMessage = detail.message || detail.msg || JSON.stringify(detail);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }

      onError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!payment) return null;

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          boxShadow: '0 8px 32px rgba(0,0,0,0.12)'
        }
      }}
    >
      {/* Header */}
      <DialogTitle sx={{
        pb: 1,
        pt: 2.5,
        px: 3,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        bgcolor: 'background.paper'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.1rem' }}>
            Full Reversal
          </Typography>
        </Box>
        <IconButton
          onClick={handleClose}
          size="small"
          disabled={loading}
          sx={{ color: 'text.secondary' }}
        >
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ px: 3, py: 2.5 }}>
        {/* Compact Payment Info */}
        <Box sx={{
          mb: 2,
          p: 1.5,
          bgcolor: 'grey.50',
          borderRadius: 1.5,
          border: '1px solid',
          borderColor: 'grey.200'
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">Payment Amount</Typography>
            <Typography variant="body2" fontWeight={600}>₹{payment.amount?.toLocaleString() || 0}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">Payment Date</Typography>
            <Typography variant="caption" color="text.secondary">
              {payment.payment_date ? new Date(payment.payment_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : 'N/A'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">Method</Typography>
            <Typography variant="caption" color="text.secondary">{payment.payment_method || 'N/A'}</Typography>
          </Box>
          {payment.transaction_id && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="caption" color="text.secondary">Transaction ID</Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                {payment.transaction_id}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Warning Message */}
        <Box sx={{
          mb: 2,
          p: 1.5,
          bgcolor: 'warning.50',
          borderRadius: 1.5,
          border: '1px solid',
          borderColor: 'warning.200',
          display: 'flex',
          gap: 1
        }}>
          <WarningAmberIcon sx={{ fontSize: 18, color: 'warning.main', mt: 0.2 }} />
          <Typography variant="caption" color="warning.dark" sx={{ lineHeight: 1.5 }}>
            This will reverse the entire payment and reset all associated monthly records. This action cannot be undone automatically.
          </Typography>
        </Box>

        {/* Reversal Reason */}
        <FormControl fullWidth size="small" sx={{ mb: 2 }}>
          <InputLabel>Reversal Reason *</InputLabel>
          <Select
            value={reason}
            onChange={(e) => setReason(Number(e.target.value))}
            label="Reversal Reason *"
            disabled={loading}
          >
            <MenuItem value={0} disabled>
              Select a reason
            </MenuItem>
            {reversalReasons.map((reasonOption) => (
              <MenuItem key={reasonOption.id} value={reasonOption.id}>
                {reasonOption.description}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Additional Details */}
        <TextField
          fullWidth
          multiline
          rows={2}
          size="small"
          label="Additional Details (Optional)"
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          disabled={loading}
          placeholder="Add any additional context..."
        />
      </DialogContent>

      <Divider />

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button
          onClick={handleClose}
          disabled={loading}
          sx={{ textTransform: 'none' }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="error"
          disabled={loading || !reason}
          startIcon={loading && <CircularProgress size={18} color="inherit" />}
          sx={{
            textTransform: 'none',
            fontWeight: 600,
            px: 3
          }}
        >
          {loading ? 'Processing...' : 'Reverse Payment'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PaymentReversalDialog;

