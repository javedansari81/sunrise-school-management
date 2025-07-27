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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  Avatar,
  Chip,
  FormControl,
  InputLabel,
  Select,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Person,
  School,
  Phone,
  Email,
  LocationOn,
  Search,
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

const StudentProfiles: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [filterClass, setFilterClass] = useState('all');
  const [filterSection, setFilterSection] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [studentForm, setStudentForm] = useState({
    rollNumber: '',
    firstName: '',
    lastName: '',
    class: '',
    section: '',
    dateOfBirth: '',
    gender: '',
    bloodGroup: '',
    address: '',
    parentName: '',
    parentPhone: '',
    parentEmail: '',
    emergencyContact: '',
    admissionDate: ''
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenDialog = (student?: any) => {
    if (student) {
      setStudentForm(student);
      setSelectedStudent(student);
    } else {
      setStudentForm({
        rollNumber: '',
        firstName: '',
        lastName: '',
        class: '',
        section: '',
        dateOfBirth: '',
        gender: '',
        bloodGroup: '',
        address: '',
        parentName: '',
        parentPhone: '',
        parentEmail: '',
        emergencyContact: '',
        admissionDate: ''
      });
      setSelectedStudent(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedStudent(null);
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setStudentForm({
      ...studentForm,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = () => {
    console.log('Student form submitted:', studentForm);
    handleCloseDialog();
  };

  const handleDelete = (studentId: number) => {
    console.log('Delete student:', studentId);
  };

  // Mock data
  const students = [
    {
      id: 1,
      rollNumber: 'STU001',
      firstName: 'Aarav',
      lastName: 'Sharma',
      class: '10',
      section: 'A',
      dateOfBirth: '2008-05-15',
      gender: 'Male',
      bloodGroup: 'O+',
      address: '123 Main Street, City',
      parentName: 'Rajesh Sharma',
      parentPhone: '+91 98765 43210',
      parentEmail: 'rajesh.sharma@email.com',
      emergencyContact: '+91 87654 32109',
      admissionDate: '2020-04-01',
      status: 'Active'
    },
    {
      id: 2,
      rollNumber: 'STU002',
      firstName: 'Priya',
      lastName: 'Patel',
      class: '9',
      section: 'B',
      dateOfBirth: '2009-08-22',
      gender: 'Female',
      bloodGroup: 'A+',
      address: '456 Park Avenue, City',
      parentName: 'Suresh Patel',
      parentPhone: '+91 98765 43211',
      parentEmail: 'suresh.patel@email.com',
      emergencyContact: '+91 87654 32110',
      admissionDate: '2021-04-01',
      status: 'Active'
    },
    {
      id: 3,
      rollNumber: 'STU003',
      firstName: 'Arjun',
      lastName: 'Kumar',
      class: '8',
      section: 'A',
      dateOfBirth: '2010-12-10',
      gender: 'Male',
      bloodGroup: 'B+',
      address: '789 School Road, City',
      parentName: 'Amit Kumar',
      parentPhone: '+91 98765 43212',
      parentEmail: 'amit.kumar@email.com',
      emergencyContact: '+91 87654 32111',
      admissionDate: '2022-04-01',
      status: 'Active'
    }
  ];

  const classes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
  const sections = ['A', 'B', 'C', 'D'];
  const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

  const studentStats = [
    { title: 'Total Students', value: '1,245', icon: <Person />, color: 'primary' },
    { title: 'Active Students', value: '1,198', icon: <School />, color: 'success' },
    { title: 'New Admissions', value: '47', icon: <Add />, color: 'info' },
    { title: 'Classes', value: '12', icon: <School />, color: 'warning' },
  ];

  const filteredStudents = students.filter(student => {
    if (filterClass !== 'all' && student.class !== filterClass) return false;
    if (filterSection !== 'all' && student.section !== filterSection) return false;
    if (searchTerm && !`${student.firstName} ${student.lastName} ${student.rollNumber}`.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight="bold" color="primary">
          Student Profiles
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
        >
          Add Student
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        {studentStats.map((stat, index) => (
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

      {/* Filters and Search */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search students..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 2 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Class</InputLabel>
              <Select
                value={filterClass}
                label="Class"
                onChange={(e) => setFilterClass(e.target.value)}
              >
                <MenuItem value="all">All Classes</MenuItem>
                {classes.map((cls) => (
                  <MenuItem key={cls} value={cls}>
                    Class {cls}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 2 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Section</InputLabel>
              <Select
                value={filterSection}
                label="Section"
                onChange={(e) => setFilterSection(e.target.value)}
              >
                <MenuItem value="all">All Sections</MenuItem>
                {sections.map((section) => (
                  <MenuItem key={section} value={section}>
                    Section {section}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Student Table */}
      <Paper elevation={3}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="All Students" />
          <Tab label="Active" />
          <Tab label="Inactive" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Student</TableCell>
                  <TableCell>Roll Number</TableCell>
                  <TableCell>Class</TableCell>
                  <TableCell>Parent Contact</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredStudents.map((student) => (
                  <TableRow key={student.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                          {student.firstName[0]}{student.lastName[0]}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {student.firstName} {student.lastName}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            DOB: {student.dateOfBirth}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>{student.rollNumber}</TableCell>
                    <TableCell>
                      <Chip 
                        label={`${student.class}-${student.section}`} 
                        size="small" 
                        color="primary" 
                        variant="outlined" 
                      />
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">{student.parentName}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {student.parentPhone}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={student.status} 
                        size="small" 
                        color={student.status === 'Active' ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => handleOpenDialog(student)}>
                        <Visibility />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleOpenDialog(student)}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDelete(student.id)}>
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
          <Typography>Active students only</Typography>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography>Inactive students only</Typography>
        </TabPanel>
      </Paper>

      {/* Student Form Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedStudent ? 'Edit Student Profile' : 'Add New Student'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Roll Number"
                name="rollNumber"
                value={studentForm.rollNumber}
                onChange={handleFormChange}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="First Name"
                name="firstName"
                value={studentForm.firstName}
                onChange={handleFormChange}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Last Name"
                name="lastName"
                value={studentForm.lastName}
                onChange={handleFormChange}
                required
              />
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
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                select
                label="Class"
                name="class"
                value={studentForm.class}
                onChange={handleFormChange}
                required
              >
                {classes.map((cls) => (
                  <MenuItem key={cls} value={cls}>
                    Class {cls}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                select
                label="Section"
                name="section"
                value={studentForm.section}
                onChange={handleFormChange}
                required
              >
                {sections.map((section) => (
                  <MenuItem key={section} value={section}>
                    Section {section}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                select
                label="Gender"
                name="gender"
                value={studentForm.gender}
                onChange={handleFormChange}
                required
              >
                <MenuItem value="Male">Male</MenuItem>
                <MenuItem value="Female">Female</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                select
                label="Blood Group"
                name="bloodGroup"
                value={studentForm.bloodGroup}
                onChange={handleFormChange}
              >
                {bloodGroups.map((group) => (
                  <MenuItem key={group} value={group}>
                    {group}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="date"
                label="Admission Date"
                name="admissionDate"
                value={studentForm.admissionDate}
                onChange={handleFormChange}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Address"
                name="address"
                value={studentForm.address}
                onChange={handleFormChange}
                multiline
                rows={2}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Parent/Guardian Name"
                name="parentName"
                value={studentForm.parentName}
                onChange={handleFormChange}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Parent Phone"
                name="parentPhone"
                value={studentForm.parentPhone}
                onChange={handleFormChange}
                required
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="email"
                label="Parent Email"
                name="parentEmail"
                value={studentForm.parentEmail}
                onChange={handleFormChange}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Emergency Contact"
                name="emergencyContact"
                value={studentForm.emergencyContact}
                onChange={handleFormChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {selectedStudent ? 'Update' : 'Add'} Student
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default StudentProfiles;
