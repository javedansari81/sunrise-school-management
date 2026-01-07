import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  CircularProgress,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Divider,
  Grid,
  IconButton,
  Menu,
  MenuItem,
  Tabs,
  Tab,
  Alert
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import VisibilityIcon from '@mui/icons-material/Visibility';
import transportService, {
  EnhancedStudentTransportSummary,
  StudentTransportMonthlyHistory,
  TransportMonthlyTracking
} from '../../../services/transportService';
import { configurationService } from '../../../services/configurationService';
import TransportPaymentReversalDialog from './TransportPaymentReversalDialog';
import TransportPartialReversalDialog from './TransportPartialReversalDialog';

interface HistoryDialogProps {
  open: boolean;
  onClose: () => void;
  student: EnhancedStudentTransportSummary | null;
  sessionYear: string;
  sessionYearId: number | null;
  onDataChange?: () => void; // Callback to refresh parent data after reversal
}

const HistoryDialog: React.FC<HistoryDialogProps> = ({
  open,
  onClose,
  student,
  sessionYear,
  sessionYearId,
  onDataChange
}) => {
  const [loading, setLoading] = useState(false);
  const [monthlyHistory, setMonthlyHistory] = useState<StudentTransportMonthlyHistory | null>(null);
  const [paymentHistory, setPaymentHistory] = useState<any[]>([]);
  const [currentTab, setCurrentTab] = useState(0);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPayment, setSelectedPayment] = useState<any>(null);
  const [reversalDialogOpen, setReversalDialogOpen] = useState(false);
  const [partialReversalDialogOpen, setPartialReversalDialogOpen] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');

  // Load configuration and data when dialog opens
  useEffect(() => {
    if (open && student?.enrollment_id && sessionYearId) {
      // Load transport-management configuration (includes reversal_reasons)
      configurationService.loadServiceConfiguration('transport-management').catch(err => {
        console.error('Failed to load transport-management configuration:', err);
      });

      loadMonthlyHistory();
      loadPaymentHistory();
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
      if (err.response?.status === 422 && Array.isArray(err.response?.data?.detail)) {
        const errorMessages = err.response.data.detail.map((e: any) => e.msg).join(', ');
        console.error('Validation error:', errorMessages);
      }
    } finally {
      setLoading(false);
    }
  }, [student, sessionYearId]);

  const loadPaymentHistory = useCallback(async () => {
    if (!student || !sessionYearId) return;

    try {
      const payments = await transportService.getPaymentHistory(
        student.student_id,
        sessionYearId
      );
      setPaymentHistory(payments);
    } catch (err: any) {
      console.error('Error loading payment history:', err);
    }
  }, [student, sessionYearId]);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, payment: any) => {
    setAnchorEl(event.currentTarget);
    setSelectedPayment(payment);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleFullReversal = () => {
    handleMenuClose();
    setReversalDialogOpen(true);
  };

  const handlePartialReversal = () => {
    handleMenuClose();
    setPartialReversalDialogOpen(true);
  };

  const handleReversalSuccess = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(''), 5000);
    loadMonthlyHistory();
    loadPaymentHistory();

    // Refresh parent component data (Transport Management System landing page)
    if (onDataChange) {
      onDataChange();
    }
  };

  const handleReversalError = (message: string) => {
    setErrorMessage(message);
    setTimeout(() => setErrorMessage(''), 5000);
  };

  // Handle view receipt - opens PDF in new browser tab using Google Docs Viewer
  // This ensures inline display without downloading for Cloudinary raw files
  const handleViewReceipt = (receiptUrl: string) => {
    if (receiptUrl) {
      // Use Google Docs Viewer to display PDF inline in new tab
      // This works reliably for Cloudinary raw files which default to attachment disposition
      const viewerUrl = `https://docs.google.com/viewer?url=${encodeURIComponent(receiptUrl)}&embedded=true`;
      window.open(viewerUrl, '_blank');
    }
  };

  const getPaymentStatusChip = (record: TransportMonthlyTracking) => {
    if (!record.is_service_enabled) {
      return <Chip label="Disabled" size="small" color="default" />;
    }

    // Use backend payment_status_id for accurate status display
    // 1 = PENDING, 2 = PAID, 3 = PARTIAL, 4 = OVERDUE
    switch (record.payment_status_id) {
      case 2: // PAID
        return <Chip label="Paid" size="small" color="success" />;
      case 3: // PARTIAL
        return <Chip label="Partial" size="small" color="warning" />;
      case 4: // OVERDUE
        return <Chip label="Overdue" size="small" color="error" />;
      case 1: // PENDING
      default:
        return <Chip label="Pending" size="small" color="error" />;
    }
  };

  const handleClose = () => {
    setMonthlyHistory(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Transport Payment History
      </DialogTitle>
      <DialogContent>
        {/* Success/Error Messages */}
        {successMessage && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage('')}>
            {successMessage}
          </Alert>
        )}
        {errorMessage && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setErrorMessage('')}>
            {errorMessage}
          </Alert>
        )}

        {student && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">
              Student Details
            </Typography>
            <Typography variant="body1">
              <strong>{student.student_name}</strong> (Roll No: {student.roll_number || 'N/A'})
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Class: {student.class_name} | Transport: {student.transport_type_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Monthly Fee: ₹{student.monthly_fee ? Number(student.monthly_fee).toFixed(2) : '0.00'}
            </Typography>
          </Box>
        )}

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
            <Tab label="Monthly Records" />
            <Tab label="Payment History" />
          </Tabs>
        </Box>

        {/* Tab Panel 0: Monthly Records */}
        {currentTab === 0 && (
          <>
            {loading ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : monthlyHistory && monthlyHistory.monthly_history ? (
              <>
            {/* Summary */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" color="primary">
                      {monthlyHistory.total_months || 0}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Total Months
                    </Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" color="success.main">
                      {monthlyHistory.paid_months || 0}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Paid Months
                    </Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" color="warning.main">
                      {monthlyHistory.pending_months || 0}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Pending Months
                    </Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" color="error.main">
                      ₹{Number(monthlyHistory.total_balance || 0).toFixed(2)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Total Balance
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>

            <Divider sx={{ my: 2 }} />

            {/* Monthly Records */}
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Monthly Records
              </Typography>
              <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>Month</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell align="right">Paid</TableCell>
                      <TableCell align="right">Balance</TableCell>
                      <TableCell>Due Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {monthlyHistory.monthly_history.map((record) => (
                      <TableRow key={record.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {record.month_name}
                          </Typography>
                        </TableCell>
                        <TableCell>{getPaymentStatusChip(record)}</TableCell>
                        <TableCell align="right">
                          {record.is_service_enabled ? (
                            `₹${Number(record.monthly_amount || 0).toFixed(2)}`
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell align="right">
                          {record.paid_amount > 0 ? (
                            `₹${Number(record.paid_amount || 0).toFixed(2)}`
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell align="right">
                          {record.is_service_enabled && record.balance_amount > 0 ? (
                            <Typography variant="body2" color="error">
                              ₹{Number(record.balance_amount || 0).toFixed(2)}
                            </Typography>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" color="text.secondary">
                            {record.due_date
                              ? new Date(record.due_date).toLocaleDateString()
                              : '-'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>

            {/* Financial Summary */}
            <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Grid container spacing={2}>
                <Grid size={{ xs: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total Amount:
                  </Typography>
                  <Typography variant="h6">
                    ₹{(Number(monthlyHistory.total_paid || 0) + Number(monthlyHistory.total_balance || 0)).toFixed(2)}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total Paid:
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    ₹{Number(monthlyHistory.total_paid || 0).toFixed(2)}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total Balance:
                  </Typography>
                  <Typography variant="h6" color="error.main">
                    ₹{Number(monthlyHistory.total_balance || 0).toFixed(2)}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
              </>
            ) : (
              <Typography variant="body2" color="text.secondary" align="center">
                No history available
              </Typography>
            )}
          </>
        )}

        {/* Tab Panel 1: Payment History */}
        {currentTab === 1 && (
          <>
            {paymentHistory.length > 0 ? (
              <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ bgcolor: 'background.paper', fontWeight: 600 }}>Date</TableCell>
                      <TableCell sx={{ bgcolor: 'background.paper', fontWeight: 600 }}>Amount</TableCell>
                      <TableCell sx={{ bgcolor: 'background.paper', fontWeight: 600 }}>Method</TableCell>
                      <TableCell sx={{ bgcolor: 'background.paper', fontWeight: 600 }}>Status</TableCell>
                      <TableCell sx={{ bgcolor: 'background.paper', fontWeight: 600 }}>Receipt</TableCell>
                      <TableCell sx={{ bgcolor: 'background.paper', fontWeight: 600 }}>Months</TableCell>
                      <TableCell align="center" sx={{ bgcolor: 'background.paper', fontWeight: 600, width: 100 }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {paymentHistory.map((payment) => (
                      <TableRow key={payment.id} hover>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(payment.payment_date).toLocaleDateString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography
                            variant="body2"
                            fontWeight={500}
                            color={payment.is_reversal ? 'error' : 'inherit'}
                          >
                            {payment.is_reversal ? '-' : ''}₹{Math.abs(payment.amount || 0).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {payment.payment_method_name || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {payment.is_reversal ? (
                            <Chip label="Reversal" size="small" color="error" />
                          ) : payment.is_reversed ? (
                            <Chip label="Reversed" size="small" color="warning" />
                          ) : (
                            <Chip label="Completed" size="small" color="success" />
                          )}
                        </TableCell>
                        <TableCell>
                          {payment.receipt_url && payment.receipt_number ? (
                            <Chip
                              label={payment.receipt_number}
                              size="small"
                              color="success"
                              variant="outlined"
                            />
                          ) : (
                            <Chip
                              label="Pending"
                              size="small"
                              color="default"
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {payment.allocations?.length || 0} month(s)
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                            {payment.receipt_url && (
                              <IconButton
                                size="small"
                                onClick={() => handleViewReceipt(payment.receipt_url)}
                                title="View Receipt"
                              >
                                <VisibilityIcon fontSize="small" />
                              </IconButton>
                            )}
                            {payment.can_be_reversed && !payment.is_reversal && (
                              <IconButton
                                size="small"
                                onClick={(e) => handleMenuOpen(e, payment)}
                                title="Reverse Payment"
                              >
                                <MoreVertIcon fontSize="small" />
                              </IconButton>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 4 }}>
                No payment history available
              </Typography>
            )}
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Close</Button>
      </DialogActions>

      {/* Reversal Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleFullReversal}>
          Full Reversal
        </MenuItem>
        {selectedPayment && selectedPayment.allocations && selectedPayment.allocations.length > 1 && (
          <MenuItem onClick={handlePartialReversal}>
            Partial Reversal (Select Months)
          </MenuItem>
        )}
      </Menu>

      {/* Reversal Dialogs */}
      {selectedPayment && (
        <>
          <TransportPaymentReversalDialog
            open={reversalDialogOpen}
            onClose={() => setReversalDialogOpen(false)}
            payment={selectedPayment}
            onSuccess={handleReversalSuccess}
            onError={handleReversalError}
          />
          <TransportPartialReversalDialog
            open={partialReversalDialogOpen}
            onClose={() => setPartialReversalDialogOpen(false)}
            payment={selectedPayment}
            onSuccess={handleReversalSuccess}
            onError={handleReversalError}
          />
        </>
      )}
    </Dialog>
  );
};

export default HistoryDialog;

