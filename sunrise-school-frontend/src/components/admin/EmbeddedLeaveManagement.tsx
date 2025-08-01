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

const EmbeddedLeaveManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState<any>(null);
  const [leaveForm, setLeaveForm] = useState({
    employeeName: '',
    department: '',
    leaveType: '',
    startDate: '',
    endDate: '',
    reason: '',
    status: 'Pending'
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenDialog = (leave?: any) => {
    if (leave) {
      setSelectedLeave(leave);
      setLeaveForm(leave);
    } else {
      setSelectedLeave(null);
      setLeaveForm({
        employeeName: '',
        department: '',
        leaveType: '',
        startDate: '',
        endDate: '',
        reason: '',
        status: 'Pending'
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedLeave(null);
  };

  const handleFormChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setLeaveForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    console.log('Form submitted:', leaveForm);
    handleCloseDialog();
  };

  // Mock data
  const leaveRequests = [
    {
      id: 1,
      employeeName: 'John Doe',
      department: 'Mathematics',
      leaveType: 'Sick Leave',
      startDate: '2024-01-15',
      endDate: '2024-01-17',
      days: 3,
      status: 'Pending',
      reason: 'Medical treatment'
    },
    {
      id: 2,
      employeeName: 'Jane Smith',
      department: 'English',
      leaveType: 'Annual Leave',
      startDate: '2024-01-20',
      endDate: '2024-01-25',
      days: 6,
      status: 'Approved',
      reason: 'Family vacation'
    }
  ];

  const summaryCards = [
    { title: 'Total Requests', value: '45', icon: <CalendarToday />, color: 'primary' },
    { title: 'Pending', value: '12', icon: <Pending />, color: 'warning' },
    { title: 'Approved', value: '28', icon: <CheckCircle />, color: 'success' },
    { title: 'Rejected', value: '5', icon: <Cancel />, color: 'error' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Approved': return 'success';
      case 'Rejected': return 'error';
      case 'Pending': return 'warning';
      default: return 'default';
    }
  };

  const filteredRequests = leaveRequests.filter(request => {
    if (tabValue === 0) return true; // All
    if (tabValue === 1) return request.status === 'Pending';
    if (tabValue === 2) return request.status === 'Approved';
    if (tabValue === 3) return request.status === 'Rejected';
    return true;
  });

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
        >
          New Leave Request
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {summaryCards.map((card, index) => (
          <Grid key={index} size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {card.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {card.title}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      color: `${card.color}.main`,
                      backgroundColor: `${card.color}.light`,
                      borderRadius: '50%',
                      p: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {card.icon}
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
                {filteredRequests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>{request.employeeName}</TableCell>
                    <TableCell>{request.department}</TableCell>
                    <TableCell>{request.leaveType}</TableCell>
                    <TableCell>
                      {request.startDate} to {request.endDate}
                    </TableCell>
                    <TableCell>{request.days}</TableCell>
                    <TableCell>
                      <Chip
                        label={request.status}
                        color={getStatusColor(request.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(request)}
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton size="small">
                        <Edit />
                      </IconButton>
                      <IconButton size="small" color="error">
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Alert severity="info" sx={{ mb: 2 }}>
            Showing pending leave requests that require approval.
          </Alert>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Leave Type</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Days</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredRequests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>{request.employeeName}</TableCell>
                    <TableCell>{request.department}</TableCell>
                    <TableCell>{request.leaveType}</TableCell>
                    <TableCell>
                      {request.startDate} to {request.endDate}
                    </TableCell>
                    <TableCell>{request.days}</TableCell>
                    <TableCell>
                      <Button size="small" color="success" sx={{ mr: 1 }}>
                        Approve
                      </Button>
                      <Button size="small" color="error">
                        Reject
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Alert severity="success" sx={{ mb: 2 }}>
            Showing approved leave requests.
          </Alert>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Leave Type</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Days</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredRequests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>{request.employeeName}</TableCell>
                    <TableCell>{request.department}</TableCell>
                    <TableCell>{request.leaveType}</TableCell>
                    <TableCell>
                      {request.startDate} to {request.endDate}
                    </TableCell>
                    <TableCell>{request.days}</TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Alert severity="error" sx={{ mb: 2 }}>
            Showing rejected leave requests.
          </Alert>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Leave Type</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Days</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredRequests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>{request.employeeName}</TableCell>
                    <TableCell>{request.department}</TableCell>
                    <TableCell>{request.leaveType}</TableCell>
                    <TableCell>
                      {request.startDate} to {request.endDate}
                    </TableCell>
                    <TableCell>{request.days}</TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Paper>

      {/* Dialog for Leave Request Form */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedLeave ? 'View Leave Request' : 'New Leave Request'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
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
                label="Department"
                name="department"
                value={leaveForm.department}
                onChange={handleFormChange}
                disabled={!!selectedLeave}
              >
                <MenuItem value="Mathematics">Mathematics</MenuItem>
                <MenuItem value="English">English</MenuItem>
                <MenuItem value="Science">Science</MenuItem>
                <MenuItem value="History">History</MenuItem>
              </TextField>
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
                <MenuItem value="Sick Leave">Sick Leave</MenuItem>
                <MenuItem value="Annual Leave">Annual Leave</MenuItem>
                <MenuItem value="Personal Leave">Personal Leave</MenuItem>
                <MenuItem value="Emergency Leave">Emergency Leave</MenuItem>
              </TextField>
            </Grid>
            {selectedLeave && (
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  select
                  label="Status"
                  name="status"
                  value={leaveForm.status}
                  onChange={handleFormChange}
                >
                  <MenuItem value="Pending">Pending</MenuItem>
                  <MenuItem value="Approved">Approved</MenuItem>
                  <MenuItem value="Rejected">Rejected</MenuItem>
                </TextField>
              </Grid>
            )}
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
    </Box>
  );
};

export default EmbeddedLeaveManagement;
