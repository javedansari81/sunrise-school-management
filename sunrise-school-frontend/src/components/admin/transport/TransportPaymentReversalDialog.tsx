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
  IconButton,
  Alert
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import transportService from '../../../services/transportService';
import { configurationService } from '../../../services/configurationService';

interface TransportPaymentReversalDialogProps {
  open: boolean;
  onClose: () => void;
  payment: any; // Payment object with id, amount, payment_date, etc.
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

const TransportPaymentReversalDialog: React.FC<TransportPaymentReversalDialogProps> = ({
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
  const config = configurationService.getServiceConfiguration('transport-management');
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
      const response = await transportService.reversePaymentFull(payment.id, {
        reason_id: reason,
        details: details || undefined
      });

      onSuccess(response.message || 'Payment reversed successfully');
      handleClose();
    } catch (err: any) {
      console.error('Error reversing payment:', err);

      let errorMessage = 'Failed to reverse payment';
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (typeof detail === 'object') {
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
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        bgcolor: 'background.paper'
      }}>
        <Typography variant="h6" component="div" fontWeight={600}>
          Reverse Payment
        </Typography>
        <IconButton
          onClick={handleClose}
          disabled={loading}
          size="small"
          sx={{ color: 'text.secondary' }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ pt: 2 }}>
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" color="text.secondary">Payment Date</Typography>
            <Typography variant="body2">{new Date(payment.payment_date).toLocaleDateString()}</Typography>
          </Box>
        </Box>

        {/* Warning Message */}
        <Alert
          severity="warning"
          icon={<WarningAmberIcon />}
          sx={{ mb: 2, py: 0.5 }}
        >
          <Typography variant="body2">
            This will reverse the entire payment and update all affected months.
          </Typography>
        </Alert>

        {/* Reversal Reason */}
        <FormControl fullWidth size="small" sx={{ mb: 2 }}>
          <InputLabel>Reversal Reason *</InputLabel>
          <Select
            value={reason}
            onChange={(e) => setReason(Number(e.target.value))}
            label="Reversal Reason *"
            disabled={loading}
          >
            <MenuItem value={0}>
              <em>Select a reason</em>
            </MenuItem>
            {reversalReasons.map((r) => (
              <MenuItem key={r.id} value={r.id}>
                {r.description}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Additional Details */}
        <TextField
          fullWidth
          size="small"
          label="Additional Details (Optional)"
          multiline
          rows={3}
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          disabled={loading}
          placeholder="Enter any additional information about this reversal..."
        />
      </DialogContent>

      <Divider />

      {/* Actions */}
      <DialogActions sx={{ px: 3, py: 2, gap: 1 }}>
        <Button
          onClick={handleClose}
          disabled={loading}
          variant="outlined"
          size="small"
          sx={{ minWidth: 80 }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={loading || !reason}
          variant="contained"
          color="error"
          size="small"
          sx={{ minWidth: 120 }}
        >
          {loading ? (
            <>
              <CircularProgress size={16} sx={{ mr: 1 }} color="inherit" />
              Reversing...
            </>
          ) : (
            'Reverse Payment'
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TransportPaymentReversalDialog;

