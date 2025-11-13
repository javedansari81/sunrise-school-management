import React, { useState, useEffect } from 'react';
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
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  IconButton,
  Chip
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { enhancedFeesAPI } from '../../services/api';
import { configurationService } from '../../services/configurationService';

interface MonthAllocation {
  id: number;
  month_name: string;
  allocated_amount: number;
  academic_month: number;
}

interface PartialReversalDialogProps {
  open: boolean;
  onClose: () => void;
  payment: any; // Payment object with id, amount, payment_date, allocations, etc.
  allocations: MonthAllocation[]; // Array of month allocations for this payment
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

const PartialReversalDialog: React.FC<PartialReversalDialogProps> = ({
  open,
  onClose,
  payment,
  allocations,
  onSuccess,
  onError
}) => {
  const [loading, setLoading] = useState(false);
  const [reason, setReason] = useState<number>(0);
  const [details, setDetails] = useState<string>('');
  const [selectedAllocationIds, setSelectedAllocationIds] = useState<number[]>([]);

  // Get reversal reasons from configuration
  const config = configurationService.getServiceConfiguration('fee-management');
  const reversalReasons = config?.reversal_reasons?.filter(r => r.is_active) || [];

  // Reset form when dialog opens
  useEffect(() => {
    if (open) {
      setReason(0);
      setDetails('');
      setSelectedAllocationIds([]);
    }
  }, [open]);

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  const handleToggleAllocation = (allocationId: number) => {
    setSelectedAllocationIds(prev => {
      if (prev.includes(allocationId)) {
        return prev.filter(id => id !== allocationId);
      } else {
        return [...prev, allocationId];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedAllocationIds.length === allocations.length) {
      setSelectedAllocationIds([]);
    } else {
      setSelectedAllocationIds(allocations.map(a => a.id));
    }
  };

  const calculateTotalReversalAmount = () => {
    return allocations
      .filter(a => selectedAllocationIds.includes(a.id))
      .reduce((sum, a) => sum + Number(a.allocated_amount || 0), 0);
  };

  const handleSubmit = async () => {
    if (!reason || reason === 0) {
      onError('Please select a reversal reason');
      return;
    }

    if (selectedAllocationIds.length === 0) {
      onError('Please select at least one month to reverse');
      return;
    }

    if (selectedAllocationIds.length === allocations.length) {
      onError('Cannot use partial reversal for all months. Please use full reversal instead.');
      return;
    }

    setLoading(true);
    try {
      const response = await enhancedFeesAPI.reversePaymentPartial(payment.payment_id, {
        allocation_ids: selectedAllocationIds,
        reason_id: reason,
        details: details || undefined
      });

      onSuccess(response.data.message || 'Payment partially reversed successfully');
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

  if (!payment || !allocations || allocations.length === 0) return null;

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
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
            Partial Reversal
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" color="text.secondary">Date • {payment.payment_method || 'N/A'}</Typography>
            <Typography variant="caption" color="text.secondary">
              {payment.payment_date ? new Date(payment.payment_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : 'N/A'}
            </Typography>
          </Box>
        </Box>

        {/* Info Message */}
        <Box sx={{
          mb: 2,
          p: 1.5,
          bgcolor: 'info.50',
          borderRadius: 1.5,
          border: '1px solid',
          borderColor: 'info.200',
          display: 'flex',
          gap: 1
        }}>
          <InfoOutlinedIcon sx={{ fontSize: 18, color: 'info.main', mt: 0.2 }} />
          <Typography variant="caption" color="info.dark" sx={{ lineHeight: 1.5 }}>
            Select months to reverse. Selected months will be reset to unpaid status.
          </Typography>
        </Box>

        {/* Month Selection */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" fontWeight={600}>
              Select Months
            </Typography>
            <Button
              size="small"
              onClick={handleSelectAll}
              sx={{
                fontSize: '0.75rem',
                textTransform: 'none',
                minWidth: 'auto',
                px: 1.5,
                py: 0.5
              }}
            >
              {selectedAllocationIds.length === allocations.length ? 'Clear' : 'Select All'}
            </Button>
          </Box>

          <TableContainer sx={{
            border: '1px solid',
            borderColor: 'grey.200',
            borderRadius: 1.5,
            maxHeight: 240,
            overflow: 'auto'
          }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell
                    padding="checkbox"
                    sx={{
                      bgcolor: 'grey.50',
                      fontWeight: 600,
                      fontSize: '0.75rem',
                      py: 1
                    }}
                  />
                  <TableCell sx={{
                    bgcolor: 'grey.50',
                    fontWeight: 600,
                    fontSize: '0.75rem',
                    py: 1
                  }}>
                    Month
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      bgcolor: 'grey.50',
                      fontWeight: 600,
                      fontSize: '0.75rem',
                      py: 1
                    }}
                  >
                    Amount
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {allocations
                  .sort((a, b) => a.academic_month - b.academic_month)
                  .map((allocation) => (
                    <TableRow
                      key={allocation.id}
                      hover
                      sx={{
                        cursor: 'pointer',
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                    >
                      <TableCell padding="checkbox" sx={{ py: 0.75 }}>
                        <Checkbox
                          size="small"
                          checked={selectedAllocationIds.includes(allocation.id)}
                          onChange={() => handleToggleAllocation(allocation.id)}
                        />
                      </TableCell>
                      <TableCell
                        onClick={() => handleToggleAllocation(allocation.id)}
                        sx={{ py: 0.75 }}
                      >
                        <Typography variant="body2" fontWeight={500}>
                          {allocation.month_name}
                        </Typography>
                      </TableCell>
                      <TableCell
                        align="right"
                        onClick={() => handleToggleAllocation(allocation.id)}
                        sx={{ py: 0.75 }}
                      >
                        <Typography variant="body2" color="success.main" fontWeight={600}>
                          ₹{Number(allocation.allocated_amount || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Selected Summary */}
          {selectedAllocationIds.length > 0 && (
            <Box sx={{
              mt: 1.5,
              p: 1.5,
              bgcolor: 'error.50',
              borderRadius: 1.5,
              border: '1px solid',
              borderColor: 'error.200'
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" color="error.dark" fontWeight={600}>
                  {selectedAllocationIds.length} month(s) selected
                </Typography>
                <Chip
                  label={`₹${calculateTotalReversalAmount().toLocaleString()}`}
                  size="small"
                  color="error"
                  sx={{ fontWeight: 600, height: 22 }}
                />
              </Box>
            </Box>
          )}
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
          disabled={loading || !reason || selectedAllocationIds.length === 0}
          startIcon={loading && <CircularProgress size={18} color="inherit" />}
          sx={{
            textTransform: 'none',
            fontWeight: 600,
            px: 3
          }}
        >
          {loading ? 'Processing...' : `Reverse ${selectedAllocationIds.length} Month(s)`}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PartialReversalDialog;

