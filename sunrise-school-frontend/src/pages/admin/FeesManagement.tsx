import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Search,
  Payment,
  Visibility,
  Download,
  Add,
  Edit,
  Delete,
} from '@mui/icons-material';
import { feesAPI } from '../../services/api';
import AdminLayout from '../../components/Layout/AdminLayout';

interface FeeRecord {
  id: number;
  studentName: string;
  admissionNumber: string;
  class: string;
  sessionYear: string;
  paymentType: string;
  totalAmount: number;
  paidAmount: number;
  balanceAmount: number;
  status: 'Pending' | 'Partial' | 'Paid' | 'Overdue';
  dueDate: string;
}

const FeesManagement: React.FC = () => {
  const [filters, setFilters] = useState({
    sessionYear: '2024-25',
    class: '',
    month: '',
    status: '',
    paymentType: '',
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [addFeeDialogOpen, setAddFeeDialogOpen] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<FeeRecord | null>(null);
  const [feeRecords, setFeeRecords] = useState<FeeRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('Cash');
  const [transactionId, setTransactionId] = useState('');
  const [remarks, setRemarks] = useState('');

  // Load fee records from API
  const loadFeeRecords = async () => {
    setLoading(true);
    try {
      const response = await feesAPI.getFees({
        session_year: filters.sessionYear,
        class_name: filters.class || undefined,
        status: filters.status || undefined,
        payment_type: filters.paymentType || undefined,
      });
      setFeeRecords(response.data.records || []);
    } catch (error) {
      console.error('Error loading fee records:', error);
      setSnackbar({ open: true, message: 'Error loading fee records', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFeeRecords();
  }, [filters]);

  const handleFilterChange = (field: string, value: string) => {
    setFilters({ ...filters, [field]: value });
  };

  const handlePayment = (record: FeeRecord) => {
    setSelectedRecord(record);
    setPaymentAmount('');
    setPaymentMethod('Cash');
    setTransactionId('');
    setRemarks('');
    setPaymentDialogOpen(true);
  };

  const processPayment = async () => {
    if (!selectedRecord || !paymentAmount) return;

    try {
      const amount = parseFloat(paymentAmount);
      if (amount <= 0 || amount > selectedRecord.balanceAmount) {
        setSnackbar({ open: true, message: 'Invalid payment amount', severity: 'error' });
        return;
      }

      await feesAPI.processPayment(selectedRecord.id, {
        amount,
        payment_method: paymentMethod,
        transaction_id: transactionId,
        remarks,
        payment_date: new Date().toISOString().split('T')[0]
      });

      setSnackbar({ open: true, message: 'Payment processed successfully', severity: 'success' });
      setPaymentDialogOpen(false);
      loadFeeRecords(); // Reload data
    } catch (error) {
      console.error('Error processing payment:', error);
      setSnackbar({ open: true, message: 'Error processing payment', severity: 'error' });
    }
  };

  const processLumpSumPayment = async (studentId: number, amount: number) => {
    try {
      const response = await feesAPI.processLumpSumPayment(studentId, {
        amount,
        payment_method: paymentMethod,
        transaction_id: transactionId,
        remarks: `Lump sum payment - ${remarks}`
      });

      setSnackbar({
        open: true,
        message: `Lump sum payment processed. ${response.data.months_covered} months covered.`,
        severity: 'success'
      });
      loadFeeRecords(); // Reload data
    } catch (error) {
      console.error('Error processing lump sum payment:', error);
      setSnackbar({ open: true, message: 'Error processing lump sum payment', severity: 'error' });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Paid': return 'success';
      case 'Partial': return 'warning';
      case 'Overdue': return 'error';
      default: return 'default';
    }
  };

  const summary = {
    totalStudents: feeRecords.length,
    totalPending: feeRecords.reduce((sum, record) => sum + record.balanceAmount, 0),
    totalCollected: feeRecords.reduce((sum, record) => sum + record.paidAmount, 0),
    overdueCount: feeRecords.filter(record => record.status === 'Overdue').length,
  };

  return (
    <AdminLayout>
      <Box sx={{ py: { xs: 1, sm: 2 } }}>

      {/* Filters Section */}
      <Paper sx={{ p: { xs: 2, sm: 3 }, mb: { xs: 2, sm: 3 } }}>
        <Typography variant="h6" gutterBottom sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}>
          Filters
        </Typography>
        <Box sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: { xs: 1, sm: 2 },
          alignItems: 'center',
          '& .MuiFormControl-root': {
            minWidth: { xs: '100%', sm: 150 },
            maxWidth: { xs: '100%', sm: 'none' }
          }
        }}>
          <FormControl size="small" sx={{ minWidth: { xs: '100%', sm: 150 } }}>
            <InputLabel>Session Year</InputLabel>
            <Select
              value={filters.sessionYear}
              label="Session Year"
              onChange={(e) => handleFilterChange('sessionYear', e.target.value)}
            >
              <MenuItem value="2024-25">2024-25</MenuItem>
              <MenuItem value="2023-24">2023-24</MenuItem>
              <MenuItem value="2022-23">2022-23</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: { xs: '100%', sm: 120 } }}>
            <InputLabel>Class</InputLabel>
            <Select
              value={filters.class}
              label="Class"
              onChange={(e) => handleFilterChange('class', e.target.value)}
            >
              <MenuItem value="">All Classes</MenuItem>
              <MenuItem value="Class 1">Class 1</MenuItem>
              <MenuItem value="Class 2">Class 2</MenuItem>
              <MenuItem value="Class 3">Class 3</MenuItem>
              <MenuItem value="Class 4">Class 4</MenuItem>
              <MenuItem value="Class 5">Class 5</MenuItem>
              <MenuItem value="Class 6">Class 6</MenuItem>
              <MenuItem value="Class 7">Class 7</MenuItem>
              <MenuItem value="Class 8">Class 8</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: { xs: '100%', sm: 120 } }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status}
              label="Status"
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <MenuItem value="">All Status</MenuItem>
              <MenuItem value="Paid">Paid</MenuItem>
              <MenuItem value="Partial">Partial</MenuItem>
              <MenuItem value="Pending">Pending</MenuItem>
              <MenuItem value="Overdue">Overdue</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: { xs: '100%', sm: 140 } }}>
            <InputLabel>Payment Type</InputLabel>
            <Select
              value={filters.paymentType}
              label="Payment Type"
              onChange={(e) => handleFilterChange('paymentType', e.target.value)}
            >
              <MenuItem value="">All Types</MenuItem>
              <MenuItem value="Monthly">Monthly</MenuItem>
              <MenuItem value="Quarterly">Quarterly</MenuItem>
              <MenuItem value="Half Yearly">Half Yearly</MenuItem>
              <MenuItem value="Yearly">Yearly</MenuItem>
            </Select>
          </FormControl>

          <TextField
            size="small"
            placeholder="Search by name or admission number"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
            sx={{
              minWidth: { xs: '100%', sm: 250 },
              '& .MuiInputBase-input': {
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }
            }}
          />

          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddFeeDialogOpen(true)}
            sx={{
              minWidth: { xs: '100%', sm: 'auto' },
              fontSize: { xs: '0.875rem', sm: '1rem' },
              py: { xs: 1, sm: 0.75 }
            }}
          >
            Add Fee Record
          </Button>
        </Box>
      </Paper>

      {/* Fees Records Table */}
      <Paper sx={{
        width: '100%',
        overflow: 'hidden',
        '& .MuiTableContainer-root': {
          overflowX: 'auto'
        }
      }}>
        <TableContainer sx={{
          maxHeight: { xs: 400, sm: 500, md: 600 },
          overflowX: 'auto'
        }}>
          <Table stickyHeader size="small" sx={{
            minWidth: { xs: 800, sm: 1000 },
            '& .MuiTableCell-root': {
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              padding: { xs: '8px 4px', sm: '16px' },
              whiteSpace: 'nowrap'
            },
            '& .MuiTableCell-head': {
              fontWeight: 600,
              backgroundColor: 'grey.50'
            }
          }}>
            <TableHead>
              <TableRow>
                <TableCell>Student Name</TableCell>
                <TableCell>Admission No.</TableCell>
                <TableCell>Class</TableCell>
                <TableCell>Payment Type</TableCell>
                <TableCell align="right">Total Amount</TableCell>
                <TableCell align="right">Paid Amount</TableCell>
                <TableCell align="right">Balance</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Due Date</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : feeRecords.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    No fee records found
                  </TableCell>
                </TableRow>
              ) : (
                feeRecords.map((record) => (
                  <TableRow key={record.id} hover>
                    <TableCell>{record.studentName}</TableCell>
                    <TableCell>{record.admissionNumber}</TableCell>
                    <TableCell>{record.class}</TableCell>
                    <TableCell>{record.paymentType}</TableCell>
                    <TableCell align="right">₹{record.totalAmount.toLocaleString()}</TableCell>
                    <TableCell align="right">₹{record.paidAmount.toLocaleString()}</TableCell>
                    <TableCell align="right">₹{record.balanceAmount.toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={record.status}
                        color={getStatusColor(record.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{record.dueDate}</TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        onClick={() => handlePayment(record)}
                        color="primary"
                        disabled={record.balanceAmount <= 0}
                      >
                        <Payment />
                      </IconButton>
                      <IconButton size="small" color="default">
                        <Visibility />
                      </IconButton>
                      <IconButton size="small" color="default">
                        <Download />
                      </IconButton>
                      <IconButton size="small" color="secondary">
                        <Edit />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        disabled={record.paidAmount > 0}
                      >
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Payment Dialog */}
      <Dialog open={paymentDialogOpen} onClose={() => setPaymentDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Process Payment</DialogTitle>
        <DialogContent>
          {selectedRecord && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedRecord.studentName} ({selectedRecord.admissionNumber})
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Balance Amount: ₹{selectedRecord.balanceAmount.toLocaleString()}
              </Typography>
              <TextField
                fullWidth
                label="Payment Amount"
                type="number"
                margin="normal"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(e.target.value)}
                placeholder={`Max: ₹${selectedRecord.balanceAmount}`}
                inputProps={{ max: selectedRecord.balanceAmount, min: 0 }}
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Payment Method</InputLabel>
                <Select
                  label="Payment Method"
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                >
                  <MenuItem value="Cash">Cash</MenuItem>
                  <MenuItem value="Cheque">Cheque</MenuItem>
                  <MenuItem value="Online">Online Transfer</MenuItem>
                  <MenuItem value="UPI">UPI</MenuItem>
                  <MenuItem value="Card">Card</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Transaction ID / Reference"
                margin="normal"
                value={transactionId}
                onChange={(e) => setTransactionId(e.target.value)}
              />
              <TextField
                fullWidth
                label="Remarks"
                multiline
                rows={3}
                margin="normal"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={processPayment}
            disabled={!paymentAmount || parseFloat(paymentAmount) <= 0}
          >
            Process Payment
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
      </Box>
    </AdminLayout>
  );
};

export default FeesManagement;
