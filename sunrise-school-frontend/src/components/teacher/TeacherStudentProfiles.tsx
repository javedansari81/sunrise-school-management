import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Avatar,
  Chip,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Snackbar,
  Pagination,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
} from '@mui/material';
import {
  Visibility,
  FilterList,
  Close as CloseIcon,
} from '@mui/icons-material';
import { DEFAULT_PAGE_SIZE, formatRecordCount, calculateTotalPages } from '../../config/pagination';
import { studentsAPI } from '../../services/api';

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
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

interface Student {
  id: number;
  admission_number: string;
  roll_number?: string;
  first_name: string;
  last_name: string;
  class_id: number;
  class_name: string;
  section?: string;
  session_year_id: number;
  session_year_name: string;
  date_of_birth: string;
  gender_id: number;
  gender_name: string;
  gender_description?: string;
  blood_group?: string;
  phone?: string;
  email?: string;
  aadhar_no?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  father_name: string;
  father_phone?: string;
  father_email?: string;
  father_occupation?: string;
  mother_name: string;
  mother_phone?: string;
  mother_email?: string;
  mother_occupation?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  admission_date?: string;
  previous_school?: string;
  is_active: boolean;
  profile_picture_url?: string;
}

const TeacherStudentProfiles: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [filterSection, setFilterSection] = useState('all');
  const [filterGender, setFilterGender] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [page, setPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  const perPage = DEFAULT_PAGE_SIZE;
  const totalPages = calculateTotalPages(totalRecords, perPage);

  useEffect(() => {
    loadStudents();
  }, [page, filterSection, filterGender, searchTerm, tabValue]);

  const loadStudents = async () => {
    try {
      setLoading(true);
      
      // Determine is_active filter based on tab
      let isActiveFilter: boolean | undefined = undefined;
      if (tabValue === 1) isActiveFilter = true;  // Active Students tab
      if (tabValue === 2) isActiveFilter = false; // Inactive Students tab

      const response = await studentsAPI.getMyClassStudents({
        section_filter: filterSection !== 'all' ? filterSection : undefined,
        gender_filter: filterGender !== 'all' ? parseInt(filterGender) : undefined,
        search: searchTerm || undefined,
        is_active: isActiveFilter,
        page,
        per_page: perPage,
      });

      setStudents(response.data.students);
      setTotalRecords(response.data.total);
    } catch (error: any) {
      console.error('Error loading students:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to load students',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setPage(1); // Reset to first page when changing tabs
  };

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleViewStudent = (student: Student) => {
    setSelectedStudent(student);
    setViewDialogOpen(true);
  };

  const handleCloseViewDialog = () => {
    setViewDialogOpen(false);
    setSelectedStudent(null);
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not specified';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  // Get unique sections from students
  const sections = Array.from(new Set(students.map(s => s.section).filter(Boolean)));

  return (
    <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
      {/* Filters */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" fontWeight="bold" mb={2}>
          <FilterList sx={{ mr: 1 }} />
          Filters
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              fullWidth
              select
              label="Section"
              value={filterSection}
              onChange={(e) => {
                setFilterSection(e.target.value);
                setPage(1);
              }}
            >
              <MenuItem value="all">All Sections</MenuItem>
              {sections.map((section) => (
                <MenuItem key={section} value={section}>
                  Section {section}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              fullWidth
              select
              label="Gender"
              value={filterGender}
              onChange={(e) => {
                setFilterGender(e.target.value);
                setPage(1);
              }}
            >
              <MenuItem value="all">All Genders</MenuItem>
              <MenuItem value="1">Male</MenuItem>
              <MenuItem value="2">Female</MenuItem>
            </TextField>
          </Grid>
          <Grid size={{ xs: 12, sm: 12, md: 6 }}>
            <TextField
              fullWidth
              label="Search by name, roll number, or admission number"
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(1);
              }}
              placeholder="Type to search..."
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Student Table */}
      <Paper elevation={3}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="All Students" />
          <Tab label="Active Students" />
          <Tab label="Inactive Students" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <TableContainer sx={{ maxHeight: { xs: '60vh', sm: '70vh' }, overflow: 'auto' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Student</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Roll Number</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Class</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Parent Contact</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : students.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No students found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  students.map((student) => (
                    <TableRow key={student.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Avatar
                            src={student.profile_picture_url || undefined}
                            sx={{ bgcolor: 'primary.main' }}
                          >
                            {!student.profile_picture_url && `${student.first_name[0]}${student.last_name[0]}`}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {student.first_name} {student.last_name}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>{student.roll_number || 'Not Assigned'}</TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">{student.class_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {student.section ? `Section ${student.section}` : 'No Section'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">{student.father_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {student.father_phone || student.phone || 'No Phone'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={student.is_active ? 'Active' : 'Inactive'}
                          color={student.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => handleViewStudent(student)}>
                          <Visibility />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          {!loading && students.length > 0 && (
            <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {formatRecordCount(page, perPage, totalRecords)}
              </Typography>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                showFirstButton
                showLastButton
              />
            </Box>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <TableContainer sx={{ maxHeight: { xs: '60vh', sm: '70vh' }, overflow: 'auto' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Student</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Roll Number</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Class</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Parent Contact</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : students.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No active students found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  students.map((student) => (
                    <TableRow key={student.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Avatar
                            src={student.profile_picture_url || undefined}
                            sx={{ bgcolor: 'primary.main' }}
                          >
                            {!student.profile_picture_url && `${student.first_name[0]}${student.last_name[0]}`}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {student.first_name} {student.last_name}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>{student.roll_number || 'Not Assigned'}</TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">{student.class_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {student.section ? `Section ${student.section}` : 'No Section'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">{student.father_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {student.father_phone || student.phone || 'No Phone'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip label="Active" color="success" size="small" />
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => handleViewStudent(student)}>
                          <Visibility />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          {!loading && students.length > 0 && (
            <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {formatRecordCount(page, perPage, totalRecords)}
              </Typography>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                showFirstButton
                showLastButton
              />
            </Box>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <TableContainer sx={{ maxHeight: { xs: '60vh', sm: '70vh' }, overflow: 'auto' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Student</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Roll Number</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Class</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Parent Contact</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : students.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No inactive students found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  students.map((student) => (
                    <TableRow key={student.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Avatar
                            src={student.profile_picture_url || undefined}
                            sx={{ bgcolor: 'grey.500' }}
                          >
                            {!student.profile_picture_url && `${student.first_name[0]}${student.last_name[0]}`}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {student.first_name} {student.last_name}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>{student.roll_number || 'Not Assigned'}</TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">{student.class_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {student.section ? `Section ${student.section}` : 'No Section'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">{student.father_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {student.father_phone || student.phone || 'No Phone'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip label="Inactive" color="default" size="small" />
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => handleViewStudent(student)}>
                          <Visibility />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          {!loading && students.length > 0 && (
            <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {formatRecordCount(page, perPage, totalRecords)}
              </Typography>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                showFirstButton
                showLastButton
              />
            </Box>
          )}
        </TabPanel>
      </Paper>

      {/* View Student Dialog */}
      <Dialog open={viewDialogOpen} onClose={handleCloseViewDialog} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: 'white', borderBottom: '1px solid #e0e0e0' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">Student Details</Typography>
            <IconButton onClick={handleCloseViewDialog} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          {selectedStudent && (
            <Grid container spacing={3}>
              {/* Basic Information */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom>
                  Basic Information
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Admission Number</Typography>
                <Typography variant="body1">{selectedStudent.admission_number}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Roll Number</Typography>
                <Typography variant="body1">{selectedStudent.roll_number || 'Not Assigned'}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">First Name</Typography>
                <Typography variant="body1">{selectedStudent.first_name}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Last Name</Typography>
                <Typography variant="body1">{selectedStudent.last_name}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Date of Birth</Typography>
                <Typography variant="body1">{formatDate(selectedStudent.date_of_birth)}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Gender</Typography>
                <Typography variant="body1">{selectedStudent.gender_description || selectedStudent.gender_name}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Blood Group</Typography>
                <Typography variant="body1">{selectedStudent.blood_group || 'Not specified'}</Typography>
              </Grid>

              {/* Academic Information */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom sx={{ mt: 2 }}>
                  Academic Information
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Class</Typography>
                <Typography variant="body1">{selectedStudent.class_name}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Section</Typography>
                <Typography variant="body1">{selectedStudent.section || 'No Section'}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Session Year</Typography>
                <Typography variant="body1">{selectedStudent.session_year_name}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Admission Date</Typography>
                <Typography variant="body1">{formatDate(selectedStudent.admission_date)}</Typography>
              </Grid>
              {selectedStudent.previous_school && (
                <Grid size={{ xs: 12 }}>
                  <Typography variant="caption" color="text.secondary">Previous School</Typography>
                  <Typography variant="body1">{selectedStudent.previous_school}</Typography>
                </Grid>
              )}

              {/* Contact Information */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom sx={{ mt: 2 }}>
                  Contact Information
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Phone</Typography>
                <Typography variant="body1">{selectedStudent.phone || 'Not provided'}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Email</Typography>
                <Typography variant="body1">{selectedStudent.email || 'Not provided'}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Aadhar Number</Typography>
                <Typography variant="body1">{selectedStudent.aadhar_no || 'Not provided'}</Typography>
              </Grid>

              {/* Address Information */}
              {(selectedStudent.address || selectedStudent.city || selectedStudent.state) && (
                <>
                  <Grid size={{ xs: 12 }}>
                    <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom sx={{ mt: 2 }}>
                      Address Information
                    </Typography>
                  </Grid>
                  {selectedStudent.address && (
                    <Grid size={{ xs: 12 }}>
                      <Typography variant="caption" color="text.secondary">Address</Typography>
                      <Typography variant="body1">{selectedStudent.address}</Typography>
                    </Grid>
                  )}
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="caption" color="text.secondary">City</Typography>
                    <Typography variant="body1">{selectedStudent.city || 'Not provided'}</Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="caption" color="text.secondary">State</Typography>
                    <Typography variant="body1">{selectedStudent.state || 'Not provided'}</Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="caption" color="text.secondary">Postal Code</Typography>
                    <Typography variant="body1">{selectedStudent.postal_code || 'Not provided'}</Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="caption" color="text.secondary">Country</Typography>
                    <Typography variant="body1">{selectedStudent.country || 'India'}</Typography>
                  </Grid>
                </>
              )}

              {/* Parent Information */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom sx={{ mt: 2 }}>
                  Parent Information
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Father's Name</Typography>
                <Typography variant="body1">{selectedStudent.father_name}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Father's Phone</Typography>
                <Typography variant="body1">{selectedStudent.father_phone || 'Not provided'}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Father's Email</Typography>
                <Typography variant="body1">{selectedStudent.father_email || 'Not provided'}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Father's Occupation</Typography>
                <Typography variant="body1">{selectedStudent.father_occupation || 'Not provided'}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Mother's Name</Typography>
                <Typography variant="body1">{selectedStudent.mother_name}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Mother's Phone</Typography>
                <Typography variant="body1">{selectedStudent.mother_phone || 'Not provided'}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Mother's Email</Typography>
                <Typography variant="body1">{selectedStudent.mother_email || 'Not provided'}</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="caption" color="text.secondary">Mother's Occupation</Typography>
                <Typography variant="body1">{selectedStudent.mother_occupation || 'Not provided'}</Typography>
              </Grid>

              {/* Emergency Contact */}
              {(selectedStudent.emergency_contact_name || selectedStudent.emergency_contact_phone) && (
                <>
                  <Grid size={{ xs: 12 }}>
                    <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom sx={{ mt: 2 }}>
                      Emergency Contact
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="caption" color="text.secondary">Contact Name</Typography>
                    <Typography variant="body1">{selectedStudent.emergency_contact_name || 'Not provided'}</Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="caption" color="text.secondary">Contact Phone</Typography>
                    <Typography variant="body1">{selectedStudent.emergency_contact_phone || 'Not provided'}</Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="caption" color="text.secondary">Relation</Typography>
                    <Typography variant="body1">{selectedStudent.emergency_contact_relation || 'Not provided'}</Typography>
                  </Grid>
                </>
              )}

              {/* Status */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom sx={{ mt: 2 }}>
                  Status
                </Typography>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Chip
                  label={selectedStudent.is_active ? 'Active' : 'Inactive'}
                  color={selectedStudent.is_active ? 'success' : 'default'}
                  size="medium"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: 'white', borderTop: '1px solid #e0e0e0' }}>
          <Button onClick={handleCloseViewDialog} variant="contained">
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default TeacherStudentProfiles;

