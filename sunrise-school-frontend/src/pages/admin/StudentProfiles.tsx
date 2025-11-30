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
  Avatar,
  Chip,
  FormControl,
  InputLabel,
  Select,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Snackbar,
  Pagination,
} from '@mui/material';
import { DEFAULT_PAGE_SIZE, PAGINATION_UI_CONFIG } from '../../config/pagination';
import {
  ClassDropdown,
  GenderDropdown,
  SessionYearDropdown,
  FilterDropdown
} from '../../components/common/MetadataDropdown';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import CollapsibleFilterSection from '../../components/common/CollapsibleFilterSection';
import DetectedSiblingsDialog from '../../components/common/DetectedSiblingsDialog';
import SiblingInfoDisplay from '../../components/common/SiblingInfoDisplay';
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
  FilterList,
  VpnKey as KeyIcon,
} from '@mui/icons-material';
import AdminLayout from '../../components/Layout/AdminLayout';
import { studentsAPI, studentSiblingsAPI } from '../../services/api';
import { useErrorDialog } from '../../hooks/useErrorDialog';
import ErrorDialog from '../../components/common/ErrorDialog';
import ResetPasswordDialog from '../../components/admin/ResetPasswordDialog';

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

interface Student {
  id: number;
  user_id?: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender_id: number;
  class_id: number;
  session_year_id: number;
  section?: string;
  roll_number?: string;
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
  admission_date: string;
  previous_school?: string;
  is_active: boolean;
  is_deleted?: boolean;
  deleted_date?: string;
  created_at: string;
  updated_at: string;
  // Metadata relationships
  gender_name?: string;
  class_name?: string;
  session_year_name?: string;
  // Profile Picture
  profile_picture_url?: string;
  profile_picture_cloudinary_id?: string;
}

const StudentProfilesContent: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<'view' | 'edit' | 'create'>('view');
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [filterClass, setFilterClass] = useState('all');
  const [filterSection, setFilterSection] = useState('all');
  const [filterSessionYear, setFilterSessionYear] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  // Use error dialog hook for better error handling
  const errorDialog = useErrorDialog();

  // Pagination state
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalStudents, setTotalStudents] = useState(0);
  const perPage = DEFAULT_PAGE_SIZE;

  // Sibling-related state
  const [detectedSiblingsDialogOpen, setDetectedSiblingsDialogOpen] = useState(false);
  const [detectedSiblingsInfo, setDetectedSiblingsInfo] = useState<any>(null);
  const [createdStudentName, setCreatedStudentName] = useState('');

  // Password reset state
  const [resetPasswordDialogOpen, setResetPasswordDialogOpen] = useState(false);
  const [selectedUserForReset, setSelectedUserForReset] = useState<any>(null);
  const [siblingWaiverInfo, setSiblingWaiverInfo] = useState<any>(null);
  const [studentForm, setStudentForm] = useState({
    admission_number: '',
    roll_number: '',
    first_name: '',
    last_name: '',
    class_id: '',
    session_year_id: '4', // Default to current session year
    section: '',
    date_of_birth: '',
    gender_id: '',
    blood_group: '',
    phone: '',
    email: '',
    aadhar_no: '',
    address: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'India',
    father_name: '',
    father_phone: '',
    father_email: '',
    father_occupation: '',
    mother_name: '',
    mother_phone: '',
    mother_email: '',
    mother_occupation: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    emergency_contact_relation: '',
    admission_date: '',
    previous_school: '',
    is_active: true
  });

  // Load students from API
  const loadStudents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('per_page', perPage.toString());

      // Add filters
      if (filterClass !== 'all') params.append('class_filter', filterClass);
      if (filterSection !== 'all') params.append('section_filter', filterSection);
      if (searchTerm) params.append('search', searchTerm);

      // Add is_active filter based on tab
      if (tabValue === 1) {
        params.append('is_active', 'true');
      } else if (tabValue === 2) {
        params.append('is_active', 'false');
      }

      const response = await studentsAPI.getStudents(params);
      const studentsData = response.data.students || [];
      setStudents(studentsData);
      setTotalPages(response.data.total_pages || 1);
      setTotalStudents(response.data.total || 0);

      // Debug student data structure
      if (studentsData.length > 0) {
        console.log('👨‍🎓 Student Data Debug:', {
          totalStudents: response.data.total,
          currentPage: page,
          totalPages: response.data.total_pages,
          studentsOnPage: studentsData.length,
          firstStudent: studentsData[0],
          studentFields: Object.keys(studentsData[0]),
          classIds: Array.from(new Set(studentsData.map((s: any) => s.class_id))),
          sessionYearIds: Array.from(new Set(studentsData.map((s: any) => s.session_year_id))),
          sections: Array.from(new Set(studentsData.map((s: any) => s.section)))
        });
      }
    } catch (error) {
      console.error('Error loading students:', error);
      setSnackbar({ open: true, message: 'Error loading students', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Load sibling waiver info for a student
  const loadSiblingWaiverInfo = async (studentId: number) => {
    try {
      const waiverInfo = await studentSiblingsAPI.getSiblingWaiverInfo(studentId);
      setSiblingWaiverInfo(waiverInfo);
    } catch (error) {
      console.error('Error loading sibling waiver info:', error);
      // Don't show error snackbar - just log it
      setSiblingWaiverInfo(null);
    }
  };

  // Load students when page, filters, or tab changes
  useEffect(() => {
    loadStudents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filterClass, filterSection, filterSessionYear, searchTerm, tabValue]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setPage(1); // Reset to first page when changing tabs
  };

  // Reset to page 1 when filters change
  const handleFilterChange = (filterType: 'class' | 'section' | 'sessionYear', value: string) => {
    setPage(1);
    if (filterType === 'class') setFilterClass(value);
    else if (filterType === 'section') setFilterSection(value);
    else if (filterType === 'sessionYear') setFilterSessionYear(value);
  };

  // Reset to page 1 when search term changes (with debounce)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== '') {
        setPage(1);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const handleOpenDialog = async (mode: 'view' | 'edit' | 'create', student?: Student) => {
    // Validate mandatory fields for existing students
    if (student && (mode === 'view' || mode === 'edit')) {
      const missingFields = [];
      if (!student.admission_number) missingFields.push('Admission Number');
      if (!student.first_name) missingFields.push('First Name');
      if (!student.last_name) missingFields.push('Last Name');
      if (!student.date_of_birth) missingFields.push('Date of Birth');
      if (!student.class_id) missingFields.push('Class');
      if (!student.session_year_id) missingFields.push('Session Year');
      if (!student.gender_id) missingFields.push('Gender');
      if (!student.father_name) missingFields.push('Father Name');
      if (!student.mother_name) missingFields.push('Mother Name');
      if (!student.admission_date) missingFields.push('Admission Date');

      if (missingFields.length > 0) {
        setSnackbar({
          open: true,
          message: `Cannot ${mode} student: Missing required fields - ${missingFields.join(', ')}`,
          severity: 'error'
        });
        return;
      }
    }

    setDialogMode(mode);
    if (student) {
      setStudentForm({
        admission_number: student.admission_number,
        roll_number: student.roll_number || '',
        first_name: student.first_name,
        last_name: student.last_name,
        class_id: student.class_id.toString(),
        session_year_id: student.session_year_id.toString(),
        section: student.section || '',
        date_of_birth: student.date_of_birth,
        gender_id: student.gender_id.toString(),
        blood_group: student.blood_group || '',
        phone: student.phone || '',
        email: student.email || '',
        aadhar_no: student.aadhar_no || '',
        address: student.address || '',
        city: student.city || '',
        state: student.state || '',
        postal_code: student.postal_code || '',
        country: student.country || 'India',
        father_name: student.father_name,
        father_phone: student.father_phone || '',
        father_email: student.father_email || '',
        father_occupation: student.father_occupation || '',
        mother_name: student.mother_name,
        mother_phone: student.mother_phone || '',
        mother_email: student.mother_email || '',
        mother_occupation: student.mother_occupation || '',
        emergency_contact_name: student.emergency_contact_name || '',
        emergency_contact_phone: student.emergency_contact_phone || '',
        emergency_contact_relation: student.emergency_contact_relation || '',
        admission_date: student.admission_date,
        previous_school: student.previous_school || '',
        is_active: student.is_active
      });
      setSelectedStudent(student);

      // Load sibling waiver info for view mode
      if (mode === 'view') {
        loadSiblingWaiverInfo(student.id);
      } else {
        setSiblingWaiverInfo(null);
      }
    } else {
      // For new student, fetch next admission number
      try {
        const response = await studentsAPI.getNextAdmissionNumber();
        const nextAdmissionNumber = response.data?.next_admission_number || '';

        setStudentForm({
          admission_number: nextAdmissionNumber,
          roll_number: '',
          first_name: '',
          last_name: '',
          class_id: '',
          session_year_id: '4', // Default to current session year
          section: '',
          date_of_birth: '',
          gender_id: '',
          blood_group: '',
          phone: '',
          email: '',
          aadhar_no: '',
          address: '',
          city: '',
          state: '',
          postal_code: '',
          country: 'India',
          father_name: '',
          father_phone: '',
          father_email: '',
          father_occupation: '',
          mother_name: '',
          mother_phone: '',
          mother_email: '',
          mother_occupation: '',
          emergency_contact_name: '',
          emergency_contact_phone: '',
          emergency_contact_relation: '',
          admission_date: '',
          previous_school: '',
          is_active: true
        });
      } catch (error) {
        console.error('Error fetching next admission number:', error);
        // If error, just use empty string
        setStudentForm({
          admission_number: '',
          roll_number: '',
          first_name: '',
          last_name: '',
          class_id: '',
          session_year_id: '4', // Default to current session year
          section: '',
          date_of_birth: '',
          gender_id: '',
          blood_group: '',
          phone: '',
          email: '',
          aadhar_no: '',
          address: '',
          city: '',
          state: '',
          postal_code: '',
          country: 'India',
          father_name: '',
          father_phone: '',
          father_email: '',
          father_occupation: '',
          mother_name: '',
          mother_phone: '',
          mother_email: '',
          mother_occupation: '',
          emergency_contact_name: '',
          emergency_contact_phone: '',
          emergency_contact_relation: '',
          admission_date: '',
          previous_school: '',
          is_active: true
        });
      }
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

  const handleSubmit = async () => {
    try {
      // Validate required fields
      if (!studentForm.admission_number || !studentForm.first_name || !studentForm.last_name ||
          !studentForm.date_of_birth || !studentForm.class_id || !studentForm.session_year_id ||
          !studentForm.gender_id || !studentForm.father_name || !studentForm.mother_name ||
          !studentForm.admission_date) {
        setSnackbar({ open: true, message: 'Please fill in all required fields', severity: 'error' });
        return;
      }

      // Convert form data to API format
      const studentData = {
        ...studentForm,
        class_id: parseInt(studentForm.class_id),
        session_year_id: parseInt(studentForm.session_year_id),
        gender_id: parseInt(studentForm.gender_id),
        // Ensure dates are in YYYY-MM-DD format
        date_of_birth: studentForm.date_of_birth,
        admission_date: studentForm.admission_date,
        // Remove empty strings and convert to null for optional fields
        phone: studentForm.phone || null,
        email: studentForm.email || null,
        address: studentForm.address || null,
        city: studentForm.city || null,
        state: studentForm.state || null,
        postal_code: studentForm.postal_code || null,
        section: studentForm.section || null,
        roll_number: studentForm.roll_number || null,
        blood_group: studentForm.blood_group || null,
        father_phone: studentForm.father_phone || null,
        father_email: studentForm.father_email || null,
        father_occupation: studentForm.father_occupation || null,
        mother_phone: studentForm.mother_phone || null,
        mother_email: studentForm.mother_email || null,
        mother_occupation: studentForm.mother_occupation || null,
        emergency_contact_name: studentForm.emergency_contact_name || null,
        emergency_contact_phone: studentForm.emergency_contact_phone || null,
        emergency_contact_relation: studentForm.emergency_contact_relation || null,
        previous_school: studentForm.previous_school || null,
      };

      if (selectedStudent) {
        // Update existing student
        await studentsAPI.updateStudent(selectedStudent.id, studentData);
        setSnackbar({ open: true, message: 'Student updated successfully', severity: 'success' });
        handleCloseDialog();
        loadStudents(); // Reload the list
      } else {
        // Create new student
        const response = await studentsAPI.createStudent(studentData);

        // Check if siblings were detected
        if (response.data?.detected_siblings && response.data.detected_siblings.siblings.length > 0) {
          // Show detected siblings dialog
          setDetectedSiblingsInfo(response.data.detected_siblings);
          setCreatedStudentName(`${studentForm.first_name} ${studentForm.last_name}`);
          setDetectedSiblingsDialogOpen(true);
        } else {
          setSnackbar({ open: true, message: 'Student created successfully', severity: 'success' });
        }

        handleCloseDialog();
        loadStudents(); // Reload the list
      }
    } catch (error: any) {
      console.error('Error saving student:', error);

      // Use error dialog for better error handling
      errorDialog.handleApiError(error, 'student_creation');
      // Don't close dialog on error - allow user to fix and retry
    }
  };

  const handleDelete = async (studentId: number) => {
    if (window.confirm('Are you sure you want to delete this student?')) {
      try {
        await studentsAPI.deleteStudent(studentId);
        setSnackbar({ open: true, message: 'Student deleted successfully', severity: 'success' });
        loadStudents(); // Reload the list
      } catch (error) {
        console.error('Error deleting student:', error);
        setSnackbar({ open: true, message: 'Error deleting student', severity: 'error' });
      }
    }
  };

  const handleResetPassword = (student: Student) => {
    // Check if student has a user account
    if (!student.user_id) {
      setSnackbar({
        open: true,
        message: 'This student does not have a user account. Cannot reset password.',
        severity: 'error'
      });
      return;
    }

    // Prepare user data for reset dialog
    const userData = {
      id: student.user_id,
      email: student.email,
      first_name: student.first_name,
      last_name: student.last_name,
      user_type: 'STUDENT'
    };
    setSelectedUserForReset(userData);
    setResetPasswordDialogOpen(true);
  };

  const handlePasswordResetSuccess = () => {
    setSnackbar({
      open: true,
      message: 'Password reset successfully',
      severity: 'success'
    });
  };

  // Hardcoded sections and blood groups (these are not in metadata yet)
  const sections = ['A', 'B', 'C', 'D'];
  const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

  // Calculate stats from actual data (exclude soft deleted students)
  const validStudents = students.filter(s => !s.is_deleted);
  const studentStats = [
    { title: 'Total Students', value: validStudents.length.toString(), icon: <Person />, color: 'primary' },
    { title: 'Active Students', value: validStudents.filter(s => s.is_active).length.toString(), icon: <School />, color: 'success' },
    { title: 'New Admissions', value: validStudents.filter(s => new Date(s.admission_date).getFullYear() === new Date().getFullYear()).length.toString(), icon: <LocationOn />, color: 'info' },
    { title: 'Classes', value: new Set(validStudents.map(s => s.class_name)).size.toString(), icon: <Email />, color: 'warning' },
  ];

  // Filter students based on search and filters
  const filteredStudents = students.filter(student => {
    // Exclude soft deleted students
    if (student.is_deleted) {
      return false;
    }

    const matchesSearch = searchTerm === '' ||
      student.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.admission_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.father_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.mother_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesClass = filterClass === 'all' || student.class_id.toString() === filterClass.toString();
    const matchesSection = filterSection === 'all' || student.section === filterSection;
    const matchesSessionYear = filterSessionYear === 'all' || student.session_year_id.toString() === filterSessionYear.toString();
    const matchesTab = tabValue === 0 || (tabValue === 1 && student.is_active) || (tabValue === 2 && !student.is_active);

    // Debug logging for first student
    if (student.id === students[0]?.id) {
      console.log('🔍 Filter Debug for first student:', {
        student: `${student.first_name} ${student.last_name}`,
        filterClass,
        filterClassType: typeof filterClass,
        filterSection,
        filterSessionYear,
        filterSessionYearType: typeof filterSessionYear,
        student_class_id: student.class_id,
        student_class_id_type: typeof student.class_id,
        student_section: student.section,
        student_session_year_id: student.session_year_id,
        student_session_year_id_type: typeof student.session_year_id,
        matchesClass,
        matchesSection,
        matchesSessionYear,
        matchesSearch,
        matchesTab,
        finalResult: matchesSearch && matchesClass && matchesSection && matchesSessionYear && matchesTab
      });
    }

    return matchesSearch && matchesClass && matchesSection && matchesSessionYear && matchesTab;
  });

  // Debug filtered results
  console.log('🔍 Filter Results Debug:', {
    totalStudents: students.length,
    validStudents: validStudents.length,
    filteredStudents: filteredStudents.length,
    currentFilters: { filterClass, filterSection, filterSessionYear, searchTerm, tabValue }
  });



  return (
    <AdminLayout>
      {/* Filters and Search */}
      <CollapsibleFilterSection
          title="Filters"
          defaultExpanded={true}
          persistKey="student-profiles-filters"
          actionButtons={
            <Button
              variant="contained"
              size="small"
              startIcon={<Add />}
              onClick={() => handleOpenDialog('create')}
              sx={{
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                padding: { xs: '4px 8px', sm: '6px 12px' },
                whiteSpace: 'nowrap'
              }}
            >
              New Student
            </Button>
          }
        >
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <FilterDropdown
                metadataType="sessionYears"
                label="Session Year"
                value={filterSessionYear}
                onChange={(value) => {
                  console.log('🔄 Session Year filter changed:', value);
                  setFilterSessionYear(value as string);
                }}
                allLabel="All Session Years"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <FilterDropdown
                metadataType="classes"
                label="Class"
                value={filterClass}
                onChange={(value) => {
                  console.log('🔄 Class filter changed:', value);
                  handleFilterChange('class', value as string);
                }}
                allLabel="All Classes"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <FormControl fullWidth>
                <InputLabel>Section</InputLabel>
                <Select
                  value={filterSection}
                  label="Section"
                  onChange={(e) => handleFilterChange('section', e.target.value)}
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
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField
                fullWidth
                label="Search Students"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search />
                }}
              />
            </Grid>
          </Grid>
        </CollapsibleFilterSection>

        {/* Student Table */}
        <Paper elevation={3}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="All Students" />
            <Tab label="Active Students" />
            <Tab label="Inactive Students" />
            <Tab label="Statistics" />
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
                    <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Login Info</TableCell>
                    <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Status</TableCell>
                    <TableCell sx={{ backgroundColor: 'white', fontWeight: 600 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <CircularProgress />
                      </TableCell>
                    </TableRow>
                  ) : filteredStudents.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="text.secondary">
                          No students found
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredStudents.map((student) => (
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
                              <Typography variant="caption" color="text.secondary">
                                DOB: {student.date_of_birth}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>{student.roll_number || 'Not Assigned'}</TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2">
                              {student.class_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {student.section ? `Section ${student.section}` : 'No Section'}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2">
                              {student.father_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {student.father_phone || student.phone || 'No Phone'}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {student.phone || student.email || 'No login'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Password: Sunrise@001
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
                          <IconButton size="small" onClick={() => handleOpenDialog('view', student)}>
                            <Visibility />
                          </IconButton>
                          <IconButton size="small" onClick={() => handleOpenDialog('edit', student)}>
                            <Edit />
                          </IconButton>
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => handleResetPassword(student)}
                            disabled={!student.user_id}
                            title={!student.user_id ? 'No user account' : 'Reset password'}
                          >
                            <KeyIcon />
                          </IconButton>
                          <IconButton size="small" color="error" onClick={() => handleDelete(student.id)}>
                            <Delete />
                          </IconButton>
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
                  color={PAGINATION_UI_CONFIG.color}
                  showFirstButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
                  showLastButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
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
                  {filteredStudents.filter(student => student.is_active).map((student) => (
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
                        <IconButton size="small" onClick={() => handleOpenDialog('view', student)}>
                          <Visibility />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleOpenDialog('edit', student)}>
                          <Edit />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleResetPassword(student)}
                          disabled={!student.user_id}
                          title={!student.user_id ? 'No user account' : 'Reset password'}
                        >
                          <KeyIcon />
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

            {/* Pagination */}
            {totalPages > 1 && (
              <Box display="flex" justifyContent="center" mt={3}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={(_, newPage) => setPage(newPage)}
                  color={PAGINATION_UI_CONFIG.color}
                  showFirstButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
                  showLastButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
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
                  {filteredStudents.filter(student => !student.is_active).map((student) => (
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
                        <IconButton size="small" onClick={() => handleOpenDialog('view', student)}>
                          <Visibility />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleOpenDialog('edit', student)}>
                          <Edit />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleResetPassword(student)}
                          disabled={!student.user_id}
                          title={!student.user_id ? 'No user account' : 'Reset password'}
                        >
                          <KeyIcon />
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

            {/* Pagination */}
            {totalPages > 1 && (
              <Box display="flex" justifyContent="center" mt={3}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={(_, newPage) => setPage(newPage)}
                  color={PAGINATION_UI_CONFIG.color}
                  showFirstButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
                  showLastButton={PAGINATION_UI_CONFIG.showFirstLastButtons}
                />
              </Box>
            )}
          </TabPanel>

          {/* Statistics Tab */}
          <TabPanel value={tabValue} index={3}>
            {loading ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Student Statistics
                </Typography>

                {/* Statistics Cards */}
                <Grid container spacing={3}>
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
              </Box>
            )}
          </TabPanel>
        </Paper>

        {/* Student Form Dialog */}
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>
            {dialogMode === 'view' ? 'View Student Details' :
             dialogMode === 'edit' ? 'Edit Student' : 'Add New Student'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              {/* Basic Information */}
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Admission Number"
                  name="admission_number"
                  value={studentForm.admission_number}
                  onChange={handleFormChange}
                  required
                  disabled={dialogMode === 'view'}
                  helperText={dialogMode === 'create' ? 'Auto-generated (editable)' : ''}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Roll Number"
                  name="roll_number"
                  value={studentForm.roll_number}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="First Name"
                  name="first_name"
                  value={studentForm.first_name}
                  onChange={handleFormChange}
                  required
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Last Name"
                  name="last_name"
                  value={studentForm.last_name}
                  onChange={handleFormChange}
                  required
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  type="date"
                  label="Date of Birth"
                  name="date_of_birth"
                  value={studentForm.date_of_birth}
                  onChange={handleFormChange}
                  InputLabelProps={{ shrink: true }}
                  required
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  type="date"
                  label="Admission Date"
                  name="admission_date"
                  value={studentForm.admission_date}
                  onChange={handleFormChange}
                  InputLabelProps={{ shrink: true }}
                  required
                  disabled={dialogMode === 'view'}
                />
              </Grid>

              {/* Class and Section */}
              <Grid size={{ xs: 12, sm: 6 }}>
                <ClassDropdown
                  value={studentForm.class_id}
                  onChange={(value) => setStudentForm(prev => ({ ...prev, class_id: value as string }))}
                  required
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  select
                  label="Section"
                  name="section"
                  value={studentForm.section}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="">No Section</MenuItem>
                  {sections.map((section) => (
                    <MenuItem key={section} value={section}>
                      Section {section}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              {/* Gender and Session Year */}
              <Grid size={{ xs: 12, sm: 6 }}>
                <GenderDropdown
                  value={studentForm.gender_id}
                  onChange={(value) => setStudentForm(prev => ({ ...prev, gender_id: value as string }))}
                  required
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <SessionYearDropdown
                  value={studentForm.session_year_id}
                  onChange={(value) => setStudentForm(prev => ({ ...prev, session_year_id: value as string }))}
                  required
                  disabled={dialogMode === 'view'}
                />
              </Grid>

              {/* Additional Information */}
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  select
                  label="Blood Group"
                  name="blood_group"
                  value={studentForm.blood_group}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="">Not Specified</MenuItem>
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
                  select
                  label="Status"
                  name="is_active"
                  value={studentForm.is_active.toString()}
                  onChange={(e) => setStudentForm(prev => ({ ...prev, is_active: e.target.value === 'true' }))}
                  disabled={dialogMode === 'view'}
                >
                  <MenuItem value="true">Active</MenuItem>
                  <MenuItem value="false">Inactive</MenuItem>
                </TextField>
              </Grid>

              {/* Contact Information */}
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Phone"
                  name="phone"
                  value={studentForm.phone}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              {/* Email field only shown in view mode */}
              {dialogMode === 'view' && (
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Email (System Generated)"
                    name="email"
                    type="email"
                    value={studentForm.email}
                    disabled={true}
                  />
                </Grid>
              )}
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Aadhar Number"
                  name="aadhar_no"
                  value={studentForm.aadhar_no}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                  inputProps={{ maxLength: 12, pattern: '[0-9]{12}' }}
                  helperText="12-digit Aadhar number"
                />
              </Grid>
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Address"
                  name="address"
                  multiline
                  rows={2}
                  value={studentForm.address}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="City"
                  name="city"
                  value={studentForm.city}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="State"
                  name="state"
                  value={studentForm.state}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>

              {/* Father Information */}
              <Grid size={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Father Information</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Father Name"
                  name="father_name"
                  value={studentForm.father_name}
                  onChange={handleFormChange}
                  required
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Father Phone"
                  name="father_phone"
                  value={studentForm.father_phone}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Father Email"
                  name="father_email"
                  type="email"
                  value={studentForm.father_email}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Father Occupation"
                  name="father_occupation"
                  value={studentForm.father_occupation}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>

              {/* Mother Information */}
              <Grid size={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Mother Information</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Mother Name"
                  name="mother_name"
                  value={studentForm.mother_name}
                  onChange={handleFormChange}
                  required
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Mother Phone"
                  name="mother_phone"
                  value={studentForm.mother_phone}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Mother Email"
                  name="mother_email"
                  type="email"
                  value={studentForm.mother_email}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Mother Occupation"
                  name="mother_occupation"
                  value={studentForm.mother_occupation}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>

              {/* Emergency Contact */}
              <Grid size={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Emergency Contact</Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Emergency Contact Name"
                  name="emergency_contact_name"
                  value={studentForm.emergency_contact_name}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Emergency Contact Phone"
                  name="emergency_contact_phone"
                  value={studentForm.emergency_contact_phone}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Emergency Contact Relation"
                  name="emergency_contact_relation"
                  value={studentForm.emergency_contact_relation}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Previous School"
                  name="previous_school"
                  value={studentForm.previous_school}
                  onChange={handleFormChange}
                  disabled={dialogMode === 'view'}
                />
              </Grid>

              {/* Sibling Information - Only show in view mode */}
              {dialogMode === 'view' && siblingWaiverInfo && siblingWaiverInfo.has_siblings && (
                <Grid size={12} sx={{ mt: 2 }}>
                  <SiblingInfoDisplay waiverInfo={siblingWaiverInfo} />
                </Grid>
              )}
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>
              {dialogMode === 'view' ? 'Close' : 'Cancel'}
            </Button>
            {dialogMode !== 'view' && (
              <Button onClick={handleSubmit} variant="contained">
                {dialogMode === 'edit' ? 'Update' : 'Add'} Student
              </Button>
            )}
          </DialogActions>
        </Dialog>

        {/* Detected Siblings Dialog */}
        <DetectedSiblingsDialog
          open={detectedSiblingsDialogOpen}
          onClose={() => {
            setDetectedSiblingsDialogOpen(false);
            setSnackbar({ open: true, message: 'Student created successfully with sibling links', severity: 'success' });
          }}
          detectedSiblingsInfo={detectedSiblingsInfo}
          studentName={createdStudentName}
        />

        {/* Reset Password Dialog */}
        <ResetPasswordDialog
          open={resetPasswordDialogOpen}
          onClose={() => {
            setResetPasswordDialogOpen(false);
            setSelectedUserForReset(null);
          }}
          user={selectedUserForReset}
          onSuccess={handlePasswordResetSuccess}
        />

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

      {/* Error Dialog for better error handling */}
      <ErrorDialog {...errorDialog.dialogProps} />
    </AdminLayout>
  );
};

// Main wrapper component with service-specific configuration
const StudentProfiles: React.FC = () => {
  return (
    <ServiceConfigurationLoader service="student-management">
      <StudentProfilesContent />
    </ServiceConfigurationLoader>
  );
};

export default StudentProfiles;
