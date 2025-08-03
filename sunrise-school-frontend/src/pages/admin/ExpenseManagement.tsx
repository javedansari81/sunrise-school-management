import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  Chip,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Alert,
  Snackbar,
  Pagination,
  Tooltip,
  Stack,
} from '@mui/material';
import AdminLayout from '../../components/Layout/AdminLayout';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  AttachMoney,
  Receipt,
  Category,
  DateRange,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Schedule,
  Cancel,
  FilterList,
  Search,
} from '@mui/icons-material';
import { useConfiguration } from '../../contexts/ConfigurationContext';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import { expenseAPI } from '../../services/api';

interface ExpenseFormData {
  expense_date: string;
  expense_category_id: number | '';
  subcategory: string;
  description: string;
  amount: string;
  tax_amount: string;
  total_amount: string;
  vendor_name: string;
  vendor_contact: string;
  vendor_email: string;
  vendor_gst_number: string;
  payment_method_id: number | '';
  payment_reference: string;
  bank_name: string;
  cheque_number: string;
  cheque_date: string;
  budget_category: string;
  session_year_id: number | '';
  is_budgeted: boolean;
  invoice_url: string;
  receipt_url: string;
  priority: string;
  is_emergency: boolean;
  is_recurring: boolean;
  recurring_frequency: string;
}

interface ExpenseFilters {
  expense_category_id: number | '';
  expense_status_id: number | '';
  payment_status_id: number | '';
  payment_method_id: number | '';
  from_date: string;
  to_date: string;
  vendor_name: string;
  priority: string;
  is_emergency: boolean | '';
  is_recurring: boolean | '';
}

const ExpenseManagement: React.FC = () => {
  const { configuration, isLoading: configLoading } = useConfiguration();

  // State management
  const [expenses, setExpenses] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState<any>(null);
  const [dialogMode, setDialogMode] = useState<'add' | 'edit' | 'view'>('add');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [statistics, setStatistics] = useState<any>({});

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalExpenses, setTotalExpenses] = useState(0);
  const perPage = 20;

  // Filters
  const [filters, setFilters] = useState<ExpenseFilters>({
    expense_category_id: '',
    expense_status_id: '',
    payment_status_id: '',
    payment_method_id: '',
    from_date: '',
    to_date: '',
    vendor_name: '',
    priority: '',
    is_emergency: '',
    is_recurring: ''
  });

  // Form data
  const [expenseForm, setExpenseForm] = useState<ExpenseFormData>({
    expense_date: new Date().toISOString().split('T')[0],
    expense_category_id: '',
    subcategory: '',
    description: '',
    amount: '',
    tax_amount: '0',
    total_amount: '',
    vendor_name: '',
    vendor_contact: '',
    vendor_email: '',
    vendor_gst_number: '',
    payment_method_id: '',
    payment_reference: '',
    bank_name: '',
    cheque_number: '',
    cheque_date: '',
    budget_category: '',
    session_year_id: '',
    is_budgeted: false,
    invoice_url: '',
    receipt_url: '',
    priority: 'Medium',
    is_emergency: false,
    is_recurring: false,
    recurring_frequency: ''
  });

  // API Functions
  const fetchExpenses = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('per_page', perPage.toString());

      // Add filters
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          params.append(key, value.toString());
        }
      });

      const response = await expenseAPI.getExpenses(params);
      setExpenses(response.expenses);
      setTotalPages(response.total_pages);
      setTotalExpenses(response.total);
    } catch (error) {
      console.error('Error fetching expenses:', error);
      setSnackbar({ open: true, message: 'Error fetching expenses', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const stats = await expenseAPI.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const handleOpenDialog = (expense?: any, mode: 'add' | 'edit' | 'view' = 'add') => {
    setDialogMode(mode);
    if (expense) {
      setExpenseForm({
        expense_date: expense.expense_date || new Date().toISOString().split('T')[0],
        expense_category_id: expense.expense_category_id || '',
        subcategory: expense.subcategory || '',
        description: expense.description || '',
        amount: expense.amount?.toString() || '',
        tax_amount: expense.tax_amount?.toString() || '0',
        total_amount: expense.total_amount?.toString() || '',
        vendor_name: expense.vendor_name || '',
        vendor_contact: expense.vendor_contact || '',
        vendor_email: expense.vendor_email || '',
        vendor_gst_number: expense.vendor_gst_number || '',
        payment_method_id: expense.payment_method_id || '',
        payment_reference: expense.payment_reference || '',
        bank_name: expense.bank_name || '',
        cheque_number: expense.cheque_number || '',
        cheque_date: expense.cheque_date || '',
        budget_category: expense.budget_category || '',
        session_year_id: expense.session_year_id || '',
        is_budgeted: expense.is_budgeted || false,
        invoice_url: expense.invoice_url || '',
        receipt_url: expense.receipt_url || '',
        priority: expense.priority || 'Medium',
        is_emergency: expense.is_emergency || false,
        is_recurring: expense.is_recurring || false,
        recurring_frequency: expense.recurring_frequency || ''
      });
      setSelectedExpense(expense);
    } else {
      // Reset form for new expense
      setExpenseForm({
        expense_date: new Date().toISOString().split('T')[0],
        expense_category_id: '',
        subcategory: '',
        description: '',
        amount: '',
        tax_amount: '0',
        total_amount: '',
        vendor_name: '',
        vendor_contact: '',
        vendor_email: '',
        vendor_gst_number: '',
        payment_method_id: '',
        payment_reference: '',
        bank_name: '',
        cheque_number: '',
        cheque_date: '',
        budget_category: '',
        session_year_id: '',
        is_budgeted: false,
        invoice_url: '',
        receipt_url: '',
        priority: 'Medium',
        is_emergency: false,
        is_recurring: false,
        recurring_frequency: ''
      });
      setSelectedExpense(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedExpense(null);
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setExpenseForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Auto-calculate total amount
    if (name === 'amount' || name === 'tax_amount') {
      const amount = parseFloat(name === 'amount' ? value : expenseForm.amount) || 0;
      const taxAmount = parseFloat(name === 'tax_amount' ? value : expenseForm.tax_amount) || 0;
      setExpenseForm(prev => ({
        ...prev,
        total_amount: (amount + taxAmount).toString()
      }));
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);

      // Prepare form data
      const formData = {
        ...expenseForm,
        amount: parseFloat(expenseForm.amount),
        tax_amount: parseFloat(expenseForm.tax_amount),
        total_amount: parseFloat(expenseForm.total_amount),
        expense_category_id: Number(expenseForm.expense_category_id),
        payment_method_id: Number(expenseForm.payment_method_id),
        session_year_id: expenseForm.session_year_id ? Number(expenseForm.session_year_id) : null
      };

      if (selectedExpense) {
        await expenseAPI.updateExpense(selectedExpense.id, formData);
        setSnackbar({ open: true, message: 'Expense updated successfully', severity: 'success' });
      } else {
        await expenseAPI.createExpense(formData);
        setSnackbar({ open: true, message: 'Expense created successfully', severity: 'success' });
      }

      handleCloseDialog();
      fetchExpenses();
    } catch (error: any) {
      console.error('Error submitting expense:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Error submitting expense',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (expenseId: number) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await expenseAPI.deleteExpense(expenseId);
        setSnackbar({ open: true, message: 'Expense deleted successfully', severity: 'success' });
        fetchExpenses();
      } catch (error: any) {
        console.error('Error deleting expense:', error);
        setSnackbar({
          open: true,
          message: error.response?.data?.detail || 'Error deleting expense',
          severity: 'error'
        });
      }
    }
  };

  const handleApprove = async (expenseId: number, statusId: number, comments?: string) => {
    try {
      await expenseAPI.approveExpense(expenseId, { expense_status_id: statusId, approval_comments: comments });
      setSnackbar({ open: true, message: 'Expense status updated successfully', severity: 'success' });
      fetchExpenses();
    } catch (error: any) {
      console.error('Error updating expense status:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Error updating expense status',
        severity: 'error'
      });
    }
  };

  const handleFilterChange = (field: keyof ExpenseFilters, value: any) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPage(1); // Reset to first page when filtering
  };

  const getStatusColor = (statusName: string) => {
    switch (statusName?.toLowerCase()) {
      case 'pending': return 'warning';
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'paid': return 'info';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  // Effects
  useEffect(() => {
    if (!configLoading && configuration) {
      fetchExpenses();
      fetchStatistics();
    }
  }, [page, filters, configLoading, configuration]);

  useEffect(() => {
    if (configuration?.session_years && configuration.session_years.length > 0) {
      const currentSessionYear = configuration.session_years.find((sy: any) => sy.is_current);
      if (currentSessionYear && !expenseForm.session_year_id) {
        setExpenseForm(prev => ({ ...prev, session_year_id: currentSessionYear.id }));
      }
    }
  }, [configuration]);

  // Loading state
  if (configLoading) {
    return (
      <AdminLayout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </AdminLayout>
    );
  }

  // Computed values
  const expenseStats = [
    {
      title: 'Total Expenses',
      value: `₹${(statistics.total_amount || 0).toLocaleString()}`,
      icon: <AttachMoney />,
      color: 'primary',
      count: statistics.total_expenses || 0
    },
    {
      title: 'Pending Approval',
      value: statistics.pending_expenses || 0,
      icon: <Schedule />,
      color: 'warning',
      amount: `₹${(statistics.pending_amount || 0).toLocaleString()}`
    },
    {
      title: 'Approved',
      value: statistics.approved_expenses || 0,
      icon: <CheckCircle />,
      color: 'success',
      amount: `₹${(statistics.approved_amount || 0).toLocaleString()}`
    },
    {
      title: 'Rejected',
      value: statistics.rejected_expenses || 0,
      icon: <Cancel />,
      color: 'error',
      count: statistics.rejected_expenses || 0
    },
  ];

  return (
    <AdminLayout>
      <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
        <ServiceConfigurationLoader service="expense-management">
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems={{ xs: 'flex-start', sm: 'center' }}
            flexDirection={{ xs: 'column', sm: 'row' }}
            gap={{ xs: 2, sm: 0 }}
            mb={{ xs: 3, sm: 4 }}
          >
            <Typography
              variant="h4"
              fontWeight="bold"
              sx={{
                fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' }
              }}
            >
              Expense Management
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => handleOpenDialog()}
              sx={{
                fontSize: { xs: '0.875rem', sm: '1rem' },
                padding: { xs: '6px 12px', sm: '8px 16px' },
                alignSelf: { xs: 'flex-end', sm: 'auto' }
              }}
            >
              Add Expense
            </Button>
          </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        {expenseStats.map((stat, index) => (
          <Grid key={index} size={{ xs: 12, sm: 6, md: 3 }}>
            <Card elevation={3}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h5" fontWeight="bold" color={`${stat.color}.main`}>
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.title}
                    </Typography>
                    {stat.amount && (
                      <Typography variant="caption" color="text.secondary">
                        {stat.amount}
                      </Typography>
                    )}
                  </Box>
                  <Box color={`${stat.color}.main`}>
                    {stat.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Filters */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" fontWeight="bold" mb={2}>
          <FilterList sx={{ mr: 1 }} />
          Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Category</InputLabel>
              <Select
                value={filters.expense_category_id}
                label="Category"
                onChange={(e) => handleFilterChange('expense_category_id', e.target.value)}
              >
                <MenuItem value="">All Categories</MenuItem>
                {configuration?.expense_categories?.map((category: any) => (
                  <MenuItem key={category.id} value={category.id}>
                    {category.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.expense_status_id}
                label="Status"
                onChange={(e) => handleFilterChange('expense_status_id', e.target.value)}
              >
                <MenuItem value="">All Statuses</MenuItem>
                {configuration?.expense_statuses?.map((status: any) => (
                  <MenuItem key={status.id} value={status.id}>
                    {status.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              fullWidth
              size="small"
              label="From Date"
              type="date"
              value={filters.from_date}
              onChange={(e) => handleFilterChange('from_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              fullWidth
              size="small"
              label="To Date"
              type="date"
              value={filters.to_date}
              onChange={(e) => handleFilterChange('to_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Expense Table */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6" fontWeight="bold">
            Expense Records ({totalExpenses} total)
          </Typography>
        </Box>

        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Vendor</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {expenses.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        <Typography variant="body2" color="text.secondary">
                          No expenses found
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    expenses.map((expense) => (
                      <TableRow key={expense.id}>
                        <TableCell>{new Date(expense.expense_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Chip
                            label={expense.expense_category_name}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                            {expense.description}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold" color="primary">
                            ₹{parseFloat(expense.total_amount).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={expense.expense_status_name}
                            size="small"
                            color={getStatusColor(expense.expense_status_name) as any}
                            variant="filled"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={expense.priority}
                            size="small"
                            color={getPriorityColor(expense.priority) as any}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                            {expense.vendor_name || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Stack direction="row" spacing={1}>
                            <Tooltip title="View Details">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => handleOpenDialog(expense, 'view')}
                              >
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            {expense.expense_status_name === 'Pending' && (
                              <>
                                <Tooltip title="Edit">
                                  <IconButton
                                    size="small"
                                    color="secondary"
                                    onClick={() => handleOpenDialog(expense, 'edit')}
                                  >
                                    <Edit />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Delete">
                                  <IconButton
                                    size="small"
                                    color="error"
                                    onClick={() => handleDelete(expense.id)}
                                  >
                                    <Delete />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Approve">
                                  <IconButton
                                    size="small"
                                    color="success"
                                    onClick={() => handleApprove(expense.id, 2, 'Approved')}
                                  >
                                    <CheckCircle />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Reject">
                                  <IconButton
                                    size="small"
                                    color="error"
                                    onClick={() => handleApprove(expense.id, 3, 'Rejected')}
                                  >
                                    <Cancel />
                                  </IconButton>
                                </Tooltip>
                              </>
                            )}
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            {totalPages > 1 && (
              <Box display="flex" justifyContent="center" mt={3}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={(_, newPage) => setPage(newPage)}
                  color="primary"
                  showFirstButton
                  showLastButton
                />
              </Box>
            )}
          </>
        )}
      </Paper>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Expense Form Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="lg" fullWidth>
        <DialogTitle>
          {dialogMode === 'view' ? 'View Expense Details' :
           dialogMode === 'edit' ? 'Edit Expense' : 'Add New Expense'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* Basic Information */}
            <Grid size={12}>
              <Typography variant="h6" color="primary" gutterBottom>
                Basic Information
              </Typography>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="date"
                label="Expense Date"
                name="expense_date"
                value={expenseForm.expense_date}
                onChange={handleFormChange}
                InputLabelProps={{ shrink: true }}
                required
                disabled={dialogMode === 'view'}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth required disabled={dialogMode === 'view'}>
                <InputLabel>Category</InputLabel>
                <Select
                  name="expense_category_id"
                  value={expenseForm.expense_category_id}
                  label="Category"
                  onChange={(e) => handleFormChange({ target: { name: 'expense_category_id', value: e.target.value } } as any)}
                >
                  {configuration?.expense_categories?.map((category: any) => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid size={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                name="description"
                value={expenseForm.description}
                onChange={handleFormChange}
                required
                disabled={dialogMode === 'view'}
              />
            </Grid>

            {/* Financial Details */}
            <Grid size={12}>
              <Typography variant="h6" color="primary" gutterBottom sx={{ mt: 2 }}>
                Financial Details
              </Typography>
            </Grid>

            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Amount (₹)"
                name="amount"
                value={expenseForm.amount}
                onChange={handleFormChange}
                required
                disabled={dialogMode === 'view'}
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Tax Amount (₹)"
                name="tax_amount"
                value={expenseForm.tax_amount}
                onChange={handleFormChange}
                disabled={dialogMode === 'view'}
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Total Amount (₹)"
                name="total_amount"
                value={expenseForm.total_amount}
                onChange={handleFormChange}
                required
                disabled={dialogMode === 'view'}
                inputProps={{ min: 0, step: 0.01 }}
                InputProps={{ readOnly: true }}
                helperText="Auto-calculated"
              />
            </Grid>

            {/* Vendor Information */}
            <Grid size={12}>
              <Typography variant="h6" color="primary" gutterBottom sx={{ mt: 2 }}>
                Vendor Information
              </Typography>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Vendor Name"
                name="vendor_name"
                value={expenseForm.vendor_name}
                onChange={handleFormChange}
                disabled={dialogMode === 'view'}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Vendor Contact"
                name="vendor_contact"
                value={expenseForm.vendor_contact}
                onChange={handleFormChange}
                disabled={dialogMode === 'view'}
              />
            </Grid>

            {/* Payment Details */}
            <Grid size={12}>
              <Typography variant="h6" color="primary" gutterBottom sx={{ mt: 2 }}>
                Payment Details
              </Typography>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth required disabled={dialogMode === 'view'}>
                <InputLabel>Payment Method</InputLabel>
                <Select
                  name="payment_method_id"
                  value={expenseForm.payment_method_id}
                  label="Payment Method"
                  onChange={(e) => handleFormChange({ target: { name: 'payment_method_id', value: e.target.value } } as any)}
                >
                  {configuration?.payment_methods?.map((method: any) => (
                    <MenuItem key={method.id} value={method.id}>
                      {method.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Payment Reference"
                name="payment_reference"
                value={expenseForm.payment_reference}
                onChange={handleFormChange}
                disabled={dialogMode === 'view'}
                placeholder="Transaction ID, Cheque No, etc."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            {dialogMode === 'view' ? 'Close' : 'Cancel'}
          </Button>
          {dialogMode !== 'view' && (
            <Button
              onClick={handleSubmit}
              variant="contained"
              disabled={loading}
            >
              {loading ? <CircularProgress size={20} /> :
               (selectedExpense ? 'Update' : 'Create') + ' Expense'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
        </ServiceConfigurationLoader>
      </Box>
    </AdminLayout>
  );
};

export default ExpenseManagement;
