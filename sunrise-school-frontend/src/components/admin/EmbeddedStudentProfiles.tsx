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
  Avatar,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Person,
  School,
  Grade,
  Phone,
  Email,
  Home,
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
      id={`student-tabpanel-${index}`}
      aria-labelledby={`student-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const EmbeddedStudentProfiles: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [studentForm, setStudentForm] = useState({
    firstName: '',
    lastName: '',
    admissionNumber: '',
    class: '',
    section: '',
    dateOfBirth: '',
    gender: '',
    phone: '',
    email: '',
    address: '',
    parentName: '',
    parentPhone: '',
    status: 'Active'
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenDialog = (student?: any) => {
    if (student) {
      setSelectedStudent(student);
      setStudentForm(student);
    } else {
      setSelectedStudent(null);
      setStudentForm({
        firstName: '',
        lastName: '',
        admissionNumber: '',
        class: '',
        section: '',
        dateOfBirth: '',
        gender: '',
        phone: '',
        email: '',
        address: '',
        parentName: '',
        parentPhone: '',
        status: 'Active'
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedStudent(null);
  };

  const handleFormChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setStudentForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    console.log('Form submitted:', studentForm);
    handleCloseDialog();
  };

  // Mock data
  const students = [
    {
      id: 1,
      firstName: 'Aarav',
      lastName: 'Sharma',
      admissionNumber: 'STU001',
      class: 'Pre-Nursery',
      section: 'A',
      dateOfBirth: '2020-05-15',
      gender: 'Male',
      phone: '9876543210',
      email: 'aarav@example.com',
      address: '123 Main St, Delhi',
      parentName: 'Raj Sharma',
      parentPhone: '9876543211',
      status: 'Active'
    },
    {
      id: 2,
      firstName: 'Arjun',
      lastName: 'Singh',
      admissionNumber: 'STU003',
      class: 'Lower Kindergarten',
      section: 'B',
      dateOfBirth: '2019-08-22',
      gender: 'Male',
      phone: '9876543212',
      email: 'arjun@example.com',
      address: '456 Park Ave, Mumbai',
      parentName: 'Vikram Singh',
      parentPhone: '9876543213',
      status: 'Active'
    }
  ];

  const summaryCards = [
    { title: 'Total Students', value: '245', icon: <Person />, color: 'primary' },
    { title: 'Active', value: '240', icon: <School />, color: 'success' },
    { title: 'Inactive', value: '5', icon: <Grade />, color: 'warning' },
    { title: 'New Admissions', value: '12', icon: <Add />, color: 'info' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'success';
      case 'Inactive': return 'warning';
      case 'Suspended': return 'error';
      default: return 'default';
    }
  };

  const filteredStudents = students.filter(student => {
    if (tabValue === 0) return true; // All
    if (tabValue === 1) return student.status === 'Active';
    if (tabValue === 2) return student.status === 'Inactive';
    if (tabValue === 3) return student.class.includes('Pre') || student.class.includes('Nursery');
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
          Add New Student
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
          <Tab label="All Students" />
          <Tab label="Active" />
          <Tab label="Inactive" />
          <Tab label="Early Years" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Student</TableCell>
                  <TableCell>Admission No.</TableCell>
                  <TableCell>Class</TableCell>
                  <TableCell>Parent</TableCell>
                  <TableCell>Contact</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredStudents.map((student) => (
                  <TableRow key={student.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          {student.firstName[0]}{student.lastName[0]}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {student.firstName} {student.lastName}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {student.gender} • DOB: {student.dateOfBirth}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>{student.admissionNumber}</TableCell>
                    <TableCell>{student.class} - {student.section}</TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {student.parentName}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {student.parentPhone}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {student.phone}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {student.email}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={student.status}
                        color={getStatusColor(student.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(student)}
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
          <Alert severity="success" sx={{ mb: 2 }}>
            Showing active students currently enrolled.
          </Alert>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Student</TableCell>
                  <TableCell>Admission No.</TableCell>
                  <TableCell>Class</TableCell>
                  <TableCell>Parent</TableCell>
                  <TableCell>Contact</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredStudents.map((student) => (
                  <TableRow key={student.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Avatar sx={{ bgcolor: 'success.main' }}>
                          {student.firstName[0]}{student.lastName[0]}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {student.firstName} {student.lastName}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {student.gender} • DOB: {student.dateOfBirth}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>{student.admissionNumber}</TableCell>
                    <TableCell>{student.class} - {student.section}</TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {student.parentName}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {student.parentPhone}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {student.phone}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {student.email}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                      <IconButton size="small">
                        <Edit />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Showing inactive students.
          </Alert>
          <Typography variant="body2" color="textSecondary" sx={{ p: 2, textAlign: 'center' }}>
            No inactive students found.
          </Typography>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Alert severity="info" sx={{ mb: 2 }}>
            Showing early years students (Pre-Nursery, Nursery, LKG, UKG).
          </Alert>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Student</TableCell>
                  <TableCell>Admission No.</TableCell>
                  <TableCell>Class</TableCell>
                  <TableCell>Age</TableCell>
                  <TableCell>Parent</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredStudents.map((student) => (
                  <TableRow key={student.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Avatar sx={{ bgcolor: 'info.main' }}>
                          {student.firstName[0]}{student.lastName[0]}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {student.firstName} {student.lastName}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {student.gender}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>{student.admissionNumber}</TableCell>
                    <TableCell>{student.class} - {student.section}</TableCell>
                    <TableCell>
                      {new Date().getFullYear() - new Date(student.dateOfBirth).getFullYear()} years
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {student.parentName}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {student.parentPhone}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                      <IconButton size="small">
                        <Edit />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Paper>

      {/* Dialog for Student Form */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedStudent ? 'View Student Profile' : 'Add New Student'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="First Name"
                name="firstName"
                value={studentForm.firstName}
                onChange={handleFormChange}
                disabled={!!selectedStudent}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Last Name"
                name="lastName"
                value={studentForm.lastName}
                onChange={handleFormChange}
                disabled={!!selectedStudent}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Admission Number"
                name="admissionNumber"
                value={studentForm.admissionNumber}
                onChange={handleFormChange}
                disabled={!!selectedStudent}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                select
                label="Class"
                name="class"
                value={studentForm.class}
                onChange={handleFormChange}
                disabled={!!selectedStudent}
              >
                <MenuItem value="Pre-Nursery">Pre-Nursery</MenuItem>
                <MenuItem value="Nursery">Nursery</MenuItem>
                <MenuItem value="Lower Kindergarten">Lower Kindergarten</MenuItem>
                <MenuItem value="Upper Kindergarten">Upper Kindergarten</MenuItem>
                <MenuItem value="Class 1">Class 1</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="date"
                label="Date of Birth"
                name="dateOfBirth"
                value={studentForm.dateOfBirth}
                onChange={handleFormChange}
                InputLabelProps={{ shrink: true }}
                disabled={!!selectedStudent}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                select
                label="Gender"
                name="gender"
                value={studentForm.gender}
                onChange={handleFormChange}
                disabled={!!selectedStudent}
              >
                <MenuItem value="Male">Male</MenuItem>
                <MenuItem value="Female">Female</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Parent Name"
                name="parentName"
                value={studentForm.parentName}
                onChange={handleFormChange}
                disabled={!!selectedStudent}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Parent Phone"
                name="parentPhone"
                value={studentForm.parentPhone}
                onChange={handleFormChange}
                disabled={!!selectedStudent}
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Address"
                name="address"
                value={studentForm.address}
                onChange={handleFormChange}
                disabled={!!selectedStudent}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          {!selectedStudent && (
            <Button onClick={handleSubmit} variant="contained">
              Add Student
            </Button>
          )}
          {selectedStudent && (
            <Button onClick={handleSubmit} variant="contained">
              Update Profile
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EmbeddedStudentProfiles;
