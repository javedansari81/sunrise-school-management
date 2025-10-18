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
  Grid
} from '@mui/material';
import transportService, {
  EnhancedStudentTransportSummary,
  StudentTransportMonthlyHistory,
  TransportMonthlyTracking
} from '../../../services/transportService';

interface HistoryDialogProps {
  open: boolean;
  onClose: () => void;
  student: EnhancedStudentTransportSummary | null;
  sessionYear: string;
  sessionYearId: number | null;
}

const HistoryDialog: React.FC<HistoryDialogProps> = ({
  open,
  onClose,
  student,
  sessionYear,
  sessionYearId
}) => {
  const [loading, setLoading] = useState(false);
  const [monthlyHistory, setMonthlyHistory] = useState<StudentTransportMonthlyHistory | null>(null);

  // Load monthly history when dialog opens
  useEffect(() => {
    if (open && student?.enrollment_id && sessionYearId) {
      loadMonthlyHistory();
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
      // Handle FastAPI validation errors (422) - just log, don't show to user in history dialog
      if (err.response?.status === 422 && Array.isArray(err.response?.data?.detail)) {
        const errorMessages = err.response.data.detail.map((e: any) => e.msg).join(', ');
        console.error('Validation error:', errorMessages);
      }
    } finally {
      setLoading(false);
    }
  }, [student, sessionYearId]);

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
              Monthly Fee: ₹{student.monthly_fee ? Number(student.monthly_fee).toFixed(2) : '0.00'}
            </Typography>
          </Box>
        )}

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
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default HistoryDialog;

