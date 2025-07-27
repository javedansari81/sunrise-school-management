import React, { useState } from 'react';
import {
  Box,
  Container,
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
  Card,
  CardContent,
} from '@mui/material';
import {
  Search,
  FilterList,
  Payment,
  Visibility,
  Download,
  Add,
} from '@mui/icons-material';

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
  const [selectedRecord, setSelectedRecord] = useState<FeeRecord | null>(null);

  // Sample data
  const feeRecords: FeeRecord[] = [
    {
      id: 1,
      studentName: 'John Doe',
      admissionNumber: 'SNS2024001',
      class: 'Class 5',
      sessionYear: '2024-25',
      paymentType: 'Quarterly',
      totalAmount: 15000,
      paidAmount: 10000,
      balanceAmount: 5000,
      status: 'Partial',
      dueDate: '2024-02-15',
    },
    {
      id: 2,
      studentName: 'Sarah Johnson',
      admissionNumber: 'SNS2024002',
      class: 'Class 3',
      sessionYear: '2024-25',
      paymentType: 'Monthly',
      totalAmount: 5000,
      paidAmount: 5000,
      balanceAmount: 0,
      status: 'Paid',
      dueDate: '2024-01-15',
    },
    {
      id: 3,
      studentName: 'Mike Davis',
      admissionNumber: 'SNS2024003',
      class: 'Class 7',
      sessionYear: '2024-25',
      paymentType: 'Half Yearly',
      totalAmount: 20000,
      paidAmount: 0,
      balanceAmount: 20000,
      status: 'Overdue',
      dueDate: '2024-01-01',
    },
  ];

  const handleFilterChange = (field: string, value: string) => {
    setFilters({ ...filters, [field]: value });
  };

  const handlePayment = (record: FeeRecord) => {
    setSelectedRecord(record);
    setPaymentDialogOpen(true);
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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Fees Management
      </Typography>

      {/* Summary Cards */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 250px', minWidth: 250 }}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="primary" fontWeight="bold">
                {summary.totalStudents}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Students
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 250px', minWidth: 250 }}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="success.main" fontWeight="bold">
                ₹{summary.totalCollected.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Collected
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 250px', minWidth: 250 }}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="warning.main" fontWeight="bold">
                ₹{summary.totalPending.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Pending
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 250px', minWidth: 250 }}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="error.main" fontWeight="bold">
                {summary.overdueCount}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Overdue Records
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Filters
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
          <Box sx={{ minWidth: 150, flex: '0 0 auto' }}>
            <FormControl fullWidth size="small">
              <InputLabel>Session Year</InputLabel>
              <Select
                value={filters.sessionYear}
                label="Session Year"
                onChange={(e) => handleFilterChange('sessionYear', e.target.value)}
              >
                <MenuItem value="2024-25">2024-25</MenuItem>
                <MenuItem value="2023-24">2023-24</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Box sx={{ minWidth: 150, flex: '0 0 auto' }}>
            <FormControl fullWidth size="small">
              <InputLabel>Class</InputLabel>
              <Select
                value={filters.class}
                label="Class"
                onChange={(e) => handleFilterChange('class', e.target.value)}
              >
                <MenuItem value="">All Classes</MenuItem>
                <MenuItem value="PG">PG</MenuItem>
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
          </Box>
          <Box sx={{ minWidth: 150, flex: '0 0 auto' }}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.status}
                label="Status"
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="Pending">Pending</MenuItem>
                <MenuItem value="Partial">Partial</MenuItem>
                <MenuItem value="Paid">Paid</MenuItem>
                <MenuItem value="Overdue">Overdue</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Box sx={{ minWidth: 150, flex: '0 0 auto' }}>
            <FormControl fullWidth size="small">
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
          </Box>
          <Box sx={{ minWidth: 250, flex: '1 1 auto' }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search by name or admission number"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Box>
          <Box sx={{ minWidth: 100, flex: '0 0 auto' }}>
            <Button
              variant="contained"
              startIcon={<Add />}
              fullWidth
            >
              Add
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Fee Records Table */}
      <Paper>
        <TableContainer>
          <Table>
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
              {feeRecords.map((record) => (
                <TableRow key={record.id}>
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
                    <IconButton size="small" onClick={() => handlePayment(record)}>
                      <Payment />
                    </IconButton>
                    <IconButton size="small">
                      <Visibility />
                    </IconButton>
                    <IconButton size="small">
                      <Download />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
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
                placeholder={`Max: ₹${selectedRecord.balanceAmount}`}
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Payment Method</InputLabel>
                <Select label="Payment Method">
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
              />
              <TextField
                fullWidth
                label="Remarks"
                multiline
                rows={3}
                margin="normal"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Process Payment</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FeesManagement;
