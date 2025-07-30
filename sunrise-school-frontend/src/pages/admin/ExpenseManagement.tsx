import React, { useState } from 'react';
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
} from '@mui/icons-material';

const ExpenseManagement: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState<any>(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterMonth, setFilterMonth] = useState('all');
  const [expenseForm, setExpenseForm] = useState({
    category: '',
    description: '',
    amount: '',
    date: '',
    vendor: '',
    paymentMethod: '',
    receipt: ''
  });

  const handleOpenDialog = (expense?: any) => {
    if (expense) {
      setExpenseForm(expense);
      setSelectedExpense(expense);
    } else {
      setExpenseForm({
        category: '',
        description: '',
        amount: '',
        date: '',
        vendor: '',
        paymentMethod: '',
        receipt: ''
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
    setExpenseForm({
      ...expenseForm,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = () => {
    console.log('Expense form submitted:', expenseForm);
    handleCloseDialog();
  };

  const handleDelete = (expenseId: number) => {
    console.log('Delete expense:', expenseId);
  };

  // Mock data
  const expenses = [
    {
      id: 1,
      category: 'Infrastructure',
      description: 'Classroom furniture purchase',
      amount: 50000,
      date: '2024-01-15',
      vendor: 'ABC Furniture Ltd.',
      paymentMethod: 'Bank Transfer',
      receipt: 'RCP001.pdf'
    },
    {
      id: 2,
      category: 'Utilities',
      description: 'Electricity bill - January',
      amount: 15000,
      date: '2024-01-20',
      vendor: 'State Electricity Board',
      paymentMethod: 'Online Payment',
      receipt: 'RCP002.pdf'
    },
    {
      id: 3,
      category: 'Supplies',
      description: 'Stationery and office supplies',
      amount: 8500,
      date: '2024-01-25',
      vendor: 'Office Mart',
      paymentMethod: 'Cash',
      receipt: 'RCP003.pdf'
    },
    {
      id: 4,
      category: 'Maintenance',
      description: 'HVAC system maintenance',
      amount: 12000,
      date: '2024-01-28',
      vendor: 'Cool Air Services',
      paymentMethod: 'Cheque',
      receipt: 'RCP004.pdf'
    }
  ];

  const categories = [
    'Infrastructure',
    'Utilities',
    'Supplies',
    'Maintenance',
    'Transportation',
    'Technology',
    'Staff',
    'Events',
    'Marketing',
    'Other'
  ];

  const paymentMethods = [
    'Cash',
    'Bank Transfer',
    'Cheque',
    'Online Payment',
    'Credit Card',
    'Debit Card'
  ];

  const expenseStats = [
    { 
      title: 'Total Expenses', 
      value: '₹2,45,000', 
      icon: <AttachMoney />, 
      color: 'primary',
      change: '+12%',
      trend: 'up'
    },
    { 
      title: 'This Month', 
      value: '₹85,500', 
      icon: <Receipt />, 
      color: 'info',
      change: '-5%',
      trend: 'down'
    },
    { 
      title: 'Categories', 
      value: '8', 
      icon: <Category />, 
      color: 'success',
      change: '+2',
      trend: 'up'
    },
    { 
      title: 'Avg/Month', 
      value: '₹61,250', 
      icon: <DateRange />, 
      color: 'warning',
      change: '+8%',
      trend: 'up'
    },
  ];

  const categoryTotals = [
    { category: 'Infrastructure', amount: 75000, percentage: 30.6 },
    { category: 'Utilities', amount: 45000, percentage: 18.4 },
    { category: 'Supplies', amount: 35000, percentage: 14.3 },
    { category: 'Maintenance', amount: 30000, percentage: 12.2 },
    { category: 'Technology', amount: 25000, percentage: 10.2 },
    { category: 'Other', amount: 35000, percentage: 14.3 },
  ];

  const filteredExpenses = expenses.filter(expense => {
    if (filterCategory !== 'all' && expense.category !== filterCategory) return false;
    // Add month filter logic here
    return true;
  });

  return (
    <AdminLayout>
      <Box sx={{ py: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
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
                    <Box display="flex" alignItems="center" mt={1}>
                      {stat.trend === 'up' ? (
                        <TrendingUp color="success" fontSize="small" />
                      ) : (
                        <TrendingDown color="error" fontSize="small" />
                      )}
                      <Typography 
                        variant="caption" 
                        color={stat.trend === 'up' ? 'success.main' : 'error.main'}
                        ml={0.5}
                      >
                        {stat.change}
                      </Typography>
                    </Box>
                  </Box>
                  <Box color={`${stat.color}.main`}>
                    {React.cloneElement(stat.icon, { sx: { fontSize: 40 } })}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Category Breakdown */}
      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, md: 8 }}>
          {/* Filters and Table */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6" fontWeight="bold">
                Expense Records
              </Typography>
              <Box display="flex" gap={2}>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={filterCategory}
                    label="Category"
                    onChange={(e) => setFilterCategory(e.target.value)}
                  >
                    <MenuItem value="all">All Categories</MenuItem>
                    {categories.map((category) => (
                      <MenuItem key={category} value={category}>
                        {category}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Month</InputLabel>
                  <Select
                    value={filterMonth}
                    label="Month"
                    onChange={(e) => setFilterMonth(e.target.value)}
                  >
                    <MenuItem value="all">All Months</MenuItem>
                    <MenuItem value="2024-01">January 2024</MenuItem>
                    <MenuItem value="2024-02">February 2024</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Vendor</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredExpenses.map((expense) => (
                    <TableRow key={expense.id}>
                      <TableCell>{expense.date}</TableCell>
                      <TableCell>
                        <Chip label={expense.category} size="small" color="primary" variant="outlined" />
                      </TableCell>
                      <TableCell>{expense.description}</TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold" color="primary">
                          ₹{expense.amount.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>{expense.vendor}</TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => handleOpenDialog(expense)}>
                          <Visibility />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleOpenDialog(expense)}>
                          <Edit />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDelete(expense.id)}>
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          {/* Category Breakdown */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" mb={3}>
              Category Breakdown
            </Typography>
            {categoryTotals.map((item, index) => (
              <Box key={index} mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">{item.category}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ₹{item.amount.toLocaleString()}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    width: '100%',
                    height: 8,
                    backgroundColor: 'grey.200',
                    borderRadius: 1,
                    overflow: 'hidden'
                  }}
                >
                  <Box
                    sx={{
                      width: `${item.percentage}%`,
                      height: '100%',
                      backgroundColor: 'primary.main',
                      transition: 'width 0.3s ease'
                    }}
                  />
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {item.percentage}% of total
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>

      {/* Expense Form Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedExpense ? 'Edit Expense' : 'Add New Expense'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                select
                label="Category"
                name="category"
                value={expenseForm.category}
                onChange={handleFormChange}
                required
              >
                {categories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="number"
                label="Amount (₹)"
                name="amount"
                value={expenseForm.amount}
                onChange={handleFormChange}
                required
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                value={expenseForm.description}
                onChange={handleFormChange}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="date"
                label="Date"
                name="date"
                value={expenseForm.date}
                onChange={handleFormChange}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Vendor"
                name="vendor"
                value={expenseForm.vendor}
                onChange={handleFormChange}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                select
                label="Payment Method"
                name="paymentMethod"
                value={expenseForm.paymentMethod}
                onChange={handleFormChange}
                required
              >
                {paymentMethods.map((method) => (
                  <MenuItem key={method} value={method}>
                    {method}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Receipt/Invoice Number"
                name="receipt"
                value={expenseForm.receipt}
                onChange={handleFormChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {selectedExpense ? 'Update' : 'Add'} Expense
          </Button>
        </DialogActions>
      </Dialog>
      </Box>
    </AdminLayout>
  );
};

export default ExpenseManagement;
