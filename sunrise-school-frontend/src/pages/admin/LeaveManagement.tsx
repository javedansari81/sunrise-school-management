import React, { useState } from 'react';
import {
  Container,
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
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  CheckCircle,
  Cancel,
  Pending,
  CalendarToday,
  Person,
  Work,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`leave-tabpanel-${index}`}
      aria-labelledby={`leave-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const LeaveManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState<any>(null);
  const [leaveForm, setLeaveForm] = useState({
    employeeId: '',
    employeeName: '',
    leaveType: '',
    startDate: '',
    endDate: '',
    reason: '',
    status: 'pending'
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenDialog = (leave?: any) => {
    if (leave) {
      setLeaveForm(leave);
      setSelectedLeave(leave);
    } else {
      setLeaveForm({
        employeeId: '',
        employeeName: '',
        leaveType: '',
        startDate: '',
        endDate: '',
        reason: '',
        status: 'pending'
      });
      setSelectedLeave(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedLeave(null);
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLeaveForm({
      ...leaveForm,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = () => {
    // Handle form submission
    console.log('Leave form submitted:', leaveForm);
    handleCloseDialog();
  };

  const handleStatusChange = (leaveId: number, newStatus: string) => {
    // Handle status change
    console.log(`Leave ${leaveId} status changed to ${newStatus}`);
  };

  // Mock data
  const leaveRequests = [
    {
      id: 1,
      employeeId: 'EMP001',
      employeeName: 'John Doe',
      department: 'Mathematics',
      leaveType: 'Sick Leave',
      startDate: '2024-02-01',
      endDate: '2024-02-03',
      days: 3,
      reason: 'Fever and cold',
      status: 'pending',
      appliedDate: '2024-01-28'
    },
    {
      id: 2,
      employeeId: 'EMP002',
      employeeName: 'Jane Smith',
      department: 'Science',
      leaveType: 'Casual Leave',
      startDate: '2024-02-05',
      endDate: '2024-02-05',
      days: 1,
      reason: 'Personal work',
      status: 'approved',
      appliedDate: '2024-01-30'
    },
    {
      id: 3,
      employeeId: 'EMP003',
      employeeName: 'Mike Johnson',
      department: 'English',
      leaveType: 'Annual Leave',
      startDate: '2024-02-10',
      endDate: '2024-02-15',
      days: 6,
      reason: 'Family vacation',
      status: 'rejected',
      appliedDate: '2024-01-25'
    }
  ];

  const leaveTypes = [
    'Sick Leave',
    'Casual Leave',
    'Annual Leave',
    'Maternity Leave',
    'Paternity Leave',
    'Emergency Leave'
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircle />;
      case 'rejected': return <Cancel />;
      case 'pending': return <Pending />;
      default: return <Pending />;
    }
  };

  const leaveStats = [
    { title: 'Total Requests', value: '45', icon: <CalendarToday />, color: 'primary' },
    { title: 'Pending Approval', value: '12', icon: <Pending />, color: 'warning' },
    { title: 'Approved', value: '28', icon: <CheckCircle />, color: 'success' },
    { title: 'Rejected', value: '5', icon: <Cancel />, color: 'error' },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight="bold" color="primary">
          Leave Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
        >
          New Leave Request
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        {leaveStats.map((stat, index) => (
          <Grid key={index} size={{ xs: 12, sm: 6, md: 3 }}>
            <Card elevation={3}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" fontWeight="bold" color={`${stat.color}.main`}>
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.title}
                    </Typography>
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

      {/* Tabs */}
      <Paper elevation={3}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="All Requests" />
          <Tab label="Pending" />
          <Tab label="Approved" />
          <Tab label="Rejected" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Leave Type</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Days</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {leaveRequests.map((leave) => (
                  <TableRow key={leave.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {leave.employeeName}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {leave.employeeId}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{leave.department}</TableCell>
                    <TableCell>{leave.leaveType}</TableCell>
                    <TableCell>
                      {leave.startDate} to {leave.endDate}
                    </TableCell>
                    <TableCell>{leave.days}</TableCell>
                    <TableCell>
                      <Chip
                        label={leave.status}
                        color={getStatusColor(leave.status) as any}
                        icon={getStatusIcon(leave.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => handleOpenDialog(leave)}>
                        <Visibility />
                      </IconButton>
                      {leave.status === 'pending' && (
                        <>
                          <IconButton 
                            size="small" 
                            color="success"
                            onClick={() => handleStatusChange(leave.id, 'approved')}
                          >
                            <CheckCircle />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => handleStatusChange(leave.id, 'rejected')}
                          >
                            <Cancel />
                          </IconButton>
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Other tab panels would filter the data accordingly */}
        <TabPanel value={tabValue} index={1}>
          <Alert severity="info">
            Showing only pending leave requests. Use the filters above to view different categories.
          </Alert>
        </TabPanel>
        <TabPanel value={tabValue} index={2}>
          <Alert severity="success">
            Showing only approved leave requests.
          </Alert>
        </TabPanel>
        <TabPanel value={tabValue} index={3}>
          <Alert severity="error">
            Showing only rejected leave requests.
          </Alert>
        </TabPanel>
      </Paper>

      {/* Leave Form Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedLeave ? 'Leave Request Details' : 'New Leave Request'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Employee ID"
                name="employeeId"
                value={leaveForm.employeeId}
                onChange={handleFormChange}
                disabled={!!selectedLeave}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Employee Name"
                name="employeeName"
                value={leaveForm.employeeName}
                onChange={handleFormChange}
                disabled={!!selectedLeave}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                select
                label="Leave Type"
                name="leaveType"
                value={leaveForm.leaveType}
                onChange={handleFormChange}
                disabled={!!selectedLeave}
              >
                {leaveTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                select
                label="Status"
                name="status"
                value={leaveForm.status}
                onChange={handleFormChange}
                disabled={!selectedLeave}
              >
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="approved">Approved</MenuItem>
                <MenuItem value="rejected">Rejected</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="date"
                label="Start Date"
                name="startDate"
                value={leaveForm.startDate}
                onChange={handleFormChange}
                InputLabelProps={{ shrink: true }}
                disabled={!!selectedLeave}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="date"
                label="End Date"
                name="endDate"
                value={leaveForm.endDate}
                onChange={handleFormChange}
                InputLabelProps={{ shrink: true }}
                disabled={!!selectedLeave}
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Reason"
                name="reason"
                value={leaveForm.reason}
                onChange={handleFormChange}
                disabled={!!selectedLeave}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          {!selectedLeave && (
            <Button onClick={handleSubmit} variant="contained">
              Submit Request
            </Button>
          )}
          {selectedLeave && (
            <Button onClick={handleSubmit} variant="contained">
              Update Status
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LeaveManagement;
