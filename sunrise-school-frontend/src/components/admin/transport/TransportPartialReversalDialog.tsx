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
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Chip
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import transportService from '../../../services/transportService';
import { configurationService } from '../../../services/configurationService';

interface TransportPartialReversalDialogProps {
  open: boolean;
  onClose: () => void;
  payment: any; // Payment object with id, amount, allocations, etc.
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

const TransportPartialReversalDialog: React.FC<TransportPartialReversalDialogProps> = ({
  open,
  onClose,
  payment,
  onSuccess,
  onError
}) => {
  const [loading, setLoading] = useState(false);
  const [reason, setReason] = useState<number>(0);
  const [details, setDetails] = useState<string>('');
  const [selectedAllocations, setSelectedAllocations] = useState<number[]>([]);

  // Get reversal reasons from configuration
  const config = configurationService.getServiceConfiguration('transport-management');
  const reversalReasons = config?.reversal_reasons?.filter(r => r.is_active) || [];

  // Get allocations (filter out reversal allocations)
  const allocations = payment.allocations?.filter((a: any) => !a.is_reversal) || [];

  // Reset form when dialog opens
  React.useEffect(() => {
    if (open) {
      setReason(0);
      setDetails('');
      setSelectedAllocations([]);
    }
  }, [open]);

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  const handleToggleAllocation = (allocationId: number) => {
    setSelectedAllocations(prev => {
      if (prev.includes(allocationId)) {
        return prev.filter(id => id !== allocationId);
      } else {
        return [...prev, allocationId];
      }
    });
  };

  const handleCellClick = (allocationId: number) => {
    handleToggleAllocation(allocationId);
  };

  const calculateSelectedTotal = () => {
    return allocations
      .filter((a: any) => selectedAllocations.includes(a.id))
      .reduce((sum: number, a: any) => sum + parseFloat(a.allocated_amount || 0), 0);
  };

  const handleSubmit = async () => {
    if (selectedAllocations.length === 0) {
      onError('Please select at least one month to reverse');
      return;
    }

    if (!reason || reason === 0) {
      onError('Please select a reversal reason');
      return;
    }

    // Check if all allocations are selected
    if (selectedAllocations.length === allocations.length) {
      onError('Cannot use partial reversal for all months. Please use full reversal instead.');
      return;
    }

    setLoading(true);
    try {
      const response = await transportService.reversePaymentPartial(payment.id, {
        allocation_ids: selectedAllocations,
        reason_id: reason,
        details: details || undefined
      });

      onSuccess(response.message || 'Selected months reversed successfully');
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
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        bgcolor: 'background.paper'
      }}>
        <Typography variant="h6" component="div" fontWeight={600}>
          Partial Reversal (Select Months)
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
            <Typography variant="caption" color="text.secondary">Total Payment</Typography>
            <Typography variant="body2" fontWeight={600}>₹{payment.amount?.toLocaleString() || 0}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" color="text.secondary">Payment Date</Typography>
            <Typography variant="body2">{new Date(payment.payment_date).toLocaleDateString()}</Typography>
          </Box>
        </Box>

        {/* Info Message */}
        <Alert
          severity="info"
          icon={<InfoOutlinedIcon />}
          sx={{ mb: 2, py: 0.5 }}
        >
          <Typography variant="body2">
            Select the months you want to reverse from this payment.
          </Typography>
        </Alert>

        {/* Month Selection Table */}
        <TableContainer sx={{
          mb: 2,
          border: '1px solid',
          borderColor: 'grey.200',
          borderRadius: 1.5,
          maxHeight: 280
        }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox" sx={{ bgcolor: 'background.paper', width: 48 }}>
                  <Checkbox
                    size="small"
                    indeterminate={selectedAllocations.length > 0 && selectedAllocations.length < allocations.length}
                    checked={allocations.length > 0 && selectedAllocations.length === allocations.length}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedAllocations(allocations.map((a: any) => a.id));
                      } else {
                        setSelectedAllocations([]);
                      }
                    }}
                    disabled={loading}
                  />
                </TableCell>
                <TableCell sx={{ bgcolor: 'background.paper', fontWeight: 600 }}>Month</TableCell>
                <TableCell align="right" sx={{ bgcolor: 'background.paper', fontWeight: 600 }}>Amount</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {allocations.map((allocation: any) => (
                <TableRow
                  key={allocation.id}
                  hover
                  sx={{
                    cursor: 'pointer',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      size="small"
                      checked={selectedAllocations.includes(allocation.id)}
                      onChange={() => handleToggleAllocation(allocation.id)}
                      disabled={loading}
                    />
                  </TableCell>
                  <TableCell onClick={() => handleCellClick(allocation.id)}>
                    <Typography variant="body2">
                      {allocation.month_name} {allocation.academic_year}
                    </Typography>
                  </TableCell>
                  <TableCell align="right" onClick={() => handleCellClick(allocation.id)}>
                    <Typography variant="body2" fontWeight={500}>
                      ₹{parseFloat(allocation.allocated_amount || 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Selection Summary */}
        {selectedAllocations.length > 0 && (
          <Box sx={{
            mb: 2,
            p: 1.5,
            bgcolor: 'primary.50',
            borderRadius: 1.5,
            border: '1px solid',
            borderColor: 'primary.200'
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" fontWeight={600}>Selected Months</Typography>
              <Chip
                label={`${selectedAllocations.length} month(s)`}
                size="small"
                color="primary"
                sx={{ height: 20, fontSize: '0.75rem' }}
              />
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">Reversal Amount</Typography>
              <Typography variant="body2" fontWeight={600} color="primary.main">
                ₹{calculateSelectedTotal().toLocaleString()}
              </Typography>
            </Box>
          </Box>
        )}

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
          rows={2}
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          disabled={loading}
          placeholder="Enter any additional information..."
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
          disabled={loading || selectedAllocations.length === 0 || !reason}
          variant="contained"
          color="error"
          size="small"
          sx={{ minWidth: 140 }}
        >
          {loading ? (
            <>
              <CircularProgress size={16} sx={{ mr: 1 }} color="inherit" />
              Reversing...
            </>
          ) : (
            `Reverse ${selectedAllocations.length} Month(s)`
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TransportPartialReversalDialog;

