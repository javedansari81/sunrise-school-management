import React, { useState, useEffect, useCallback } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  Box,
  Chip,
  Grid,
  Autocomplete,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import transportService, {
  EnhancedStudentTransportSummary,
  StudentTransportMonthlyHistory,
  TransportMonthlyTracking
} from '../../../services/transportService';

interface PaymentDialogProps {
  open: boolean;
  onClose: () => void;
  student: EnhancedStudentTransportSummary | null;
  sessionYear: string;
  sessionYearId: number | null;
  configuration: any;
  onSuccess: () => void;
  onError: (message: string) => void;
}

const PaymentDialog: React.FC<PaymentDialogProps> = ({
  open,
  onClose,
  student,
  sessionYear,
  sessionYearId,
  configuration,
  onSuccess,
  onError
}) => {
  const [loading, setLoading] = useState(false);
  const [monthlyHistory, setMonthlyHistory] = useState<StudentTransportMonthlyHistory | null>(null);
  const [selectedMonths, setSelectedMonths] = useState<TransportMonthlyTracking[]>([]);

  // Form state
  const [amount, setAmount] = useState<string>('');
  const [paymentMethodId, setPaymentMethodId] = useState<number>(0);
  const [paymentDate, setPaymentDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [transactionId, setTransactionId] = useState<string>('');
  const [receiptNumber, setReceiptNumber] = useState<string>('');
  const [notes, setNotes] = useState<string>('');

  // Reset form state when dialog opens
  useEffect(() => {
    if (open) {
      // Reset all form fields to initial state
      setAmount('');
      setPaymentMethodId(0);
      setPaymentDate(new Date().toISOString().split('T')[0]);
      setTransactionId('');
      setReceiptNumber('');
      setNotes('');
      setSelectedMonths([]);
      setMonthlyHistory(null);

      // Load monthly history if student data is available
      if (student?.enrollment_id && sessionYearId) {
        loadMonthlyHistory();
      }
    }
  }, [open, student, sessionYearId]);

  const loadMonthlyHistory = useCallback(async () => {
    if (!student || !sessionYearId) return;

    setLoading(true);
    try {
      const history = await transportService.getMonthlyHistory(
        student.student_id,
        sessionYearId
      );
      setMonthlyHistory(history);
    } catch (err: any) {
      console.error('Error loading monthly history:', err);
      // Handle FastAPI validation errors (422)
      if (err.response?.status === 422 && Array.isArray(err.response?.data?.detail)) {
        const errorMessages = err.response.data.detail.map((e: any) => e.msg).join(', ');
        onError(`Validation error: ${errorMessages}`);
      } else {
        onError(err.response?.data?.detail || 'Failed to load monthly history');
      }
    } finally {
      setLoading(false);
    }
  }, [student, sessionYearId, onError]);

  // Get available months for dropdown (unpaid/partially paid months)
  const getAvailableMonths = (): TransportMonthlyTracking[] => {
    if (!monthlyHistory || !monthlyHistory.monthly_history) return [];
    return monthlyHistory.monthly_history.filter(
      record => record.is_service_enabled && record.balance_amount > 0
    );
  };

  const calculateTotalAmount = (): number => {
    return selectedMonths.reduce((total, month) => {
      return total + Number(month?.balance_amount || 0);
    }, 0);
  };

  // Auto-calculate total when months are selected
  useEffect(() => {
    const total = calculateTotalAmount();
    if (total > 0) {
      setAmount(total.toFixed(2));
    }
  }, [selectedMonths]);

  const handleSubmit = async () => {
    if (!student || !amount || !paymentMethodId || !sessionYearId) {
      onError('Please fill all required fields');
      return;
    }

    if (selectedMonths.length === 0) {
      onError('Please select at least one month to pay');
      return;
    }

    const paymentAmount = parseFloat(amount);
    if (paymentAmount <= 0) {
      onError('Payment amount must be greater than 0');
      return;
    }

    setLoading(true);
    try {
      await transportService.processPayment(
        student.student_id,
        sessionYearId,
        {
          amount: paymentAmount,
          payment_method_id: paymentMethodId,
          selected_months: selectedMonths.map(m => m.academic_month),
          transaction_id: transactionId || undefined,
          remarks: notes || undefined
        }
      );

      // Reset form state after successful payment
      setAmount('');
      setPaymentMethodId(0);
      setPaymentDate(new Date().toISOString().split('T')[0]);
      setTransactionId('');
      setReceiptNumber('');
      setNotes('');
      setSelectedMonths([]);
      setMonthlyHistory(null);

      onSuccess();
    } catch (err: any) {
      console.error('Error processing payment:', err);
      // Handle FastAPI validation errors (422)
      if (err.response?.status === 422 && Array.isArray(err.response?.data?.detail)) {
        const errorMessages = err.response.data.detail.map((e: any) => e.msg).join(', ');
        onError(`Validation error: ${errorMessages}`);
      } else {
        onError(err.response?.data?.detail || 'Failed to process payment');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      // Reset form
      setAmount('');
      setPaymentMethodId(0);
      setPaymentDate(new Date().toISOString().split('T')[0]);
      setTransactionId('');
      setReceiptNumber('');
      setNotes('');
      setSelectedMonths([]);
      setMonthlyHistory(null);
      onClose();
    }
  };

  const getPaymentStatusLabel = (record: TransportMonthlyTracking): string => {
    // Use backend payment_status_id for accurate status display
    // 1 = PENDING, 2 = PAID, 3 = PARTIAL, 4 = OVERDUE
    switch (record.payment_status_id) {
      case 2: return 'Paid';
      case 3: return 'Partial';
      case 4: return 'Overdue';
      case 1:
      default: return 'Pending';
    }
  };

  const getPaymentStatusColor = (record: TransportMonthlyTracking): 'success' | 'warning' | 'error' | 'default' => {
    // Use backend payment_status_id for accurate color
    switch (record.payment_status_id) {
      case 2: return 'success'; // PAID
      case 3: return 'warning'; // PARTIAL
      case 4: return 'error';   // OVERDUE
      case 1:
      default: return 'error';  // PENDING
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Process Transport Payment
      </DialogTitle>
      <DialogContent>
        {student && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">
              Student Details
            </Typography>
            <Typography variant="body1">
              <strong>{student.student_name}</strong> (Roll: {student.admission_number})
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Class: {student.class_name} | Transport: {student.transport_type_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Monthly Fee: ₹{student.monthly_fee ? Number(student.monthly_fee).toFixed(2) : '0.00'} | Balance: ₹{Number(student.total_balance || 0).toFixed(2)}
            </Typography>
          </Box>
        )}

        {loading && !monthlyHistory ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Month Selection Dropdown */}
            {monthlyHistory && monthlyHistory.monthly_history && (
              <Box sx={{ mb: 3 }}>
                <Autocomplete
                  multiple
                  options={getAvailableMonths()}
                  value={selectedMonths}
                  onChange={(event, newValue) => {
                    setSelectedMonths(newValue);
                  }}
                  getOptionLabel={(option) =>
                    `${option.month_name} - Balance: ₹${Number(option.balance_amount || 0).toFixed(2)}`
                  }
                  isOptionEqualToValue={(option, value) => option.id === value.id}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Select Months to Pay"
                      placeholder="Choose one or more months"
                      helperText={
                        selectedMonths.length > 0
                          ? `${selectedMonths.length} month(s) selected`
                          : 'Select months with pending balance'
                      }
                    />
                  )}
                  renderOption={(props, option) => (
                    <li {...props} key={option.id}>
                      <Box sx={{ width: '100%' }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body2">
                            {option.month_name}
                          </Typography>
                          <Chip
                            label={getPaymentStatusLabel(option)}
                            size="small"
                            color={getPaymentStatusColor(option)}
                            sx={{ ml: 1 }}
                          />
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          Balance: ₹{Number(option.balance_amount || 0).toFixed(2)}
                          {option.paid_amount > 0 && ` (Paid: ₹${Number(option.paid_amount || 0).toFixed(2)})`}
                        </Typography>
                      </Box>
                    </li>
                  )}
                  disabled={loading}
                  noOptionsText="No months available for payment"
                />

                {/* Selected Months Summary */}
                {selectedMonths.length > 0 && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Selected Months Summary:
                    </Typography>
                    <List dense disablePadding>
                      {selectedMonths.map((month, index) => (
                        <React.Fragment key={month.id}>
                          <ListItem disablePadding sx={{ py: 0.5 }}>
                            <ListItemText
                              primary={
                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                  <Typography variant="body2">
                                    {month.month_name}
                                  </Typography>
                                  <Typography variant="body2" fontWeight="medium">
                                    ₹{Number(month.balance_amount || 0).toFixed(2)}
                                  </Typography>
                                </Box>
                              }
                              secondary={
                                <Typography variant="caption" color="text.secondary">
                                  Monthly Fee: ₹{Number(month.monthly_amount || 0).toFixed(2)} |
                                  Paid: ₹{Number(month.paid_amount || 0).toFixed(2)}
                                </Typography>
                              }
                            />
                          </ListItem>
                          {index < selectedMonths.length - 1 && <Divider />}
                        </React.Fragment>
                      ))}
                    </List>
                    <Divider sx={{ my: 1 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="subtitle2" color="primary">
                        Total Amount:
                      </Typography>
                      <Typography variant="h6" color="primary" fontWeight="bold">
                        ₹{Number(calculateTotalAmount() || 0).toFixed(2)}
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Box>
            )}

            {/* Payment Form */}
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  required
                  type="number"
                  label="Payment Amount"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  disabled={loading}
                  inputProps={{ min: 0, step: 0.01 }}
                  helperText="Enter amount to pay"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth required>
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={paymentMethodId}
                    label="Payment Method"
                    onChange={(e) => setPaymentMethodId(Number(e.target.value))}
                    disabled={loading}
                  >
                    <MenuItem value={0}>Select Payment Method</MenuItem>
                    {configuration?.payment_methods?.map((method: any) => (
                      <MenuItem key={method.id} value={method.id}>
                        {method.description}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  required
                  type="date"
                  label="Payment Date"
                  value={paymentDate}
                  onChange={(e) => setPaymentDate(e.target.value)}
                  disabled={loading}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Transaction ID"
                  value={transactionId}
                  onChange={(e) => setTransactionId(e.target.value)}
                  disabled={loading}
                  placeholder="Optional"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Receipt Number"
                  value={receiptNumber}
                  onChange={(e) => setReceiptNumber(e.target.value)}
                  disabled={loading}
                  placeholder="Optional"
                />
              </Grid>

              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  disabled={loading}
                  placeholder="Optional notes"
                />
              </Grid>
            </Grid>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || !amount || !paymentMethodId || selectedMonths.length === 0}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {loading ? 'Processing...' : 'Process Payment'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PaymentDialog;

