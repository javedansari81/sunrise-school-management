import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Avatar,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
  Snackbar,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Phone as PhoneIcon,
  Email as EmailIcon
} from '@mui/icons-material';

import { useAuth } from '../../contexts/AuthContext';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { teachersAPI } from '../../services/api';

// Teacher interface matching the backend structure
interface Teacher {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender_id: number;
  phone: string;
  email: string;
  aadhar_no?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  position: string;
  department?: string;
  subjects?: string;
  qualification_id?: number;
  employment_status_id: number;
  experience_years: number;
  joining_date: string;
  class_teacher_of_id?: number;
  classes_assigned?: string;
  salary?: number;
  is_active: boolean;
  is_deleted?: boolean;
  // Metadata fields
  gender_name?: string;
  qualification_name?: string;
  employment_status_name?: string;
  class_teacher_of_name?: string;
  user_id?: number;
}

// Tab Panel Component
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
      id={`teacher-tabpanel-${index}`}
      aria-labelledby={`teacher-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const TeacherProfilesSystem: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const {
    isLoaded: configLoaded,
    isLoading: configLoading,
    error: configError
  } = useServiceConfiguration('teacher-management');

  // State management
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('all');

  // Load teachers
  const loadTeachers = useCallback(async () => {
    if (!configLoaded || !isAuthenticated) return;

    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (filterDepartment !== 'all') params.append('department_filter', filterDepartment);

      const response = await teachersAPI.getTeachers(params.toString());
      setTeachers(response.data.teachers || []);
    } catch (err: any) {
      console.error('Error loading teachers:', err);
      setSnackbar({
        open: true,
        message: 'Failed to load teachers',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  }, [configLoaded, isAuthenticated, searchTerm, filterDepartment]);

  // Load teachers when dependencies change
  useEffect(() => {
    if (!configLoading && configLoaded && isAuthenticated) {
      loadTeachers();
    }
  }, [configLoading, configLoaded, isAuthenticated, loadTeachers]);

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle delete teacher (soft delete)
  const handleDeleteTeacher = async (teacher: Teacher) => {
    if (window.confirm(`Are you sure you want to delete ${teacher.first_name} ${teacher.last_name}? This action cannot be undone.`)) {
      try {
        setLoading(true);
        await teachersAPI.deleteTeacher(teacher.id);
        setSnackbar({
          open: true,
          message: 'Teacher deleted successfully',
          severity: 'success'
        });
        loadTeachers();
      } catch (err: any) {
        console.error('Error deleting teacher:', err);
        setSnackbar({
          open: true,
          message: 'Failed to delete teacher',
          severity: 'error'
        });
      } finally {
        setLoading(false);
      }
    }
  };

  // Filter teachers based on current filters and search
  const filteredTeachers = teachers.filter(teacher => {
    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = 
        teacher.first_name.toLowerCase().includes(searchLower) ||
        teacher.last_name.toLowerCase().includes(searchLower) ||
        teacher.employee_id.toLowerCase().includes(searchLower) ||
        teacher.email.toLowerCase().includes(searchLower) ||
        teacher.phone.includes(searchTerm);
      
      if (!matchesSearch) return false;
    }

    // Department filter
    if (filterDepartment !== 'all' && teacher.department !== filterDepartment) {
      return false;
    }

    return true;
  });

  // Loading and error states
  if (configLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Loading teacher management configuration...
        </Typography>
      </Box>
    );
  }

  if (configError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Configuration Error: {configError}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header Section with Title and New Teacher Button */}
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
          Teacher Profiles
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {/* Handle new teacher */}}
          sx={{
            fontSize: { xs: '0.875rem', sm: '1rem' },
            padding: { xs: '6px 12px', sm: '8px 16px' },
            alignSelf: { xs: 'flex-end', sm: 'auto' }
          }}
        >
          New Teacher
        </Button>
      </Box>

      {/* Filters Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} alignItems="center">
          <Box flex={1} minWidth={{ xs: '100%', sm: '300px' }}>
            <TextField
              fullWidth
              label="Search Teachers"
              variant="outlined"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
              placeholder="Name, Employee ID, Email..."
              size="small"
            />
          </Box>
          <Box minWidth={{ xs: '100%', sm: '200px' }}>
            <FormControl fullWidth size="small">
              <InputLabel>Department</InputLabel>
              <Select
                value={filterDepartment}
                label="Department"
                onChange={(e) => setFilterDepartment(e.target.value)}
              >
                <MenuItem value="all">All Departments</MenuItem>
                {/* Add department options from configuration */}
              </Select>
            </FormControl>
          </Box>
        </Box>
      </Paper>

      {/* Tabs Section */}
      <Paper sx={{ width: '100%', mb: { xs: 2, sm: 3 } }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="teacher profiles tabs"
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
        >
          <Tab label="All Teachers" />
          <Tab label="Active Teachers" />
          <Tab label="Inactive Teachers" />
        </Tabs>
      </Paper>

      {/* All Teachers Tab */}
      <TabPanel value={tabValue} index={0}>
        {loading ? (
          <Box display="flex" justifyContent="center" p={{ xs: 2, sm: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" mb={2}>
              All Teachers ({filteredTeachers.length})
            </Typography>
            <TableContainer sx={{ maxHeight: { xs: '60vh', sm: '70vh' }, overflow: 'auto' }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Teacher</TableCell>
                    <TableCell>Employee ID</TableCell>
                    <TableCell>Department</TableCell>
                    <TableCell>Position</TableCell>
                    <TableCell>Contact</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredTeachers.map((teacher) => (
                    <TableRow key={teacher.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Avatar sx={{ bgcolor: 'primary.main' }}>
                            {teacher.first_name[0]}{teacher.last_name[0]}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {teacher.first_name} {teacher.last_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {teacher.qualification_name || 'Not Specified'}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>{teacher.employee_id}</TableCell>
                      <TableCell>{teacher.department || 'Not Assigned'}</TableCell>
                      <TableCell>{teacher.position}</TableCell>
                      <TableCell>
                        <Box display="flex" flexDirection="column" gap={0.5}>
                          <Box display="flex" alignItems="center" gap={1}>
                            <PhoneIcon fontSize="small" color="action" />
                            <Typography variant="caption">{teacher.phone}</Typography>
                          </Box>
                          <Box display="flex" alignItems="center" gap={1}>
                            <EmailIcon fontSize="small" color="action" />
                            <Typography variant="caption">{teacher.email}</Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={teacher.is_active ? 'Active' : 'Inactive'}
                          color={teacher.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          <Tooltip title="View Details">
                            <IconButton size="small" onClick={() => {/* Handle view */}}>
                              <ViewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Teacher">
                            <IconButton size="small" onClick={() => {/* Handle edit */}}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Teacher">
                            <IconButton size="small" color="error" onClick={() => handleDeleteTeacher(teacher)}>
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}
      </TabPanel>

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
    </Box>
  );
};

export default TeacherProfilesSystem;
