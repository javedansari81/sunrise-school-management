import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Snackbar,
  Pagination,
  TextField,
  Chip,
} from '@mui/material';
import { DEFAULT_PAGE_SIZE, PAGINATION_UI_CONFIG } from '../../config/pagination';
import {
  ClassDropdown,
  GenderDropdown,
  SessionYearDropdown,
} from '../../components/common/MetadataDropdown';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import {
  FilterList,
  Search,
  Download,
  PictureAsPdf,
  TableChart,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import AdminLayout from '../../components/Layout/AdminLayout';
import { reportsAPI } from '../../services/api';
import * as XLSX from 'xlsx';

interface StudentUDISEData {
  id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  date_of_birth: string;
  age: number | null;
  class_id: number;
  class_name: string;
  section: string | null;
  roll_number: string | null;
  session_year_id: number;
  session_year_name: string;
  admission_date: string;
  gender_id: number;
  gender_name: string;
  blood_group: string | null;
  aadhar_no: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  postal_code: string | null;
  country: string;
  father_name: string;
  father_phone: string | null;
  father_email: string | null;
  father_occupation: string | null;
  mother_name: string;
  mother_phone: string | null;
  mother_email: string | null;
  mother_occupation: string | null;
  guardian_name: string | null;
  guardian_phone: string | null;
  guardian_email: string | null;
  guardian_relation: string | null;
  is_active: boolean;
}

const StudentUDISEReport: React.FC = () => {
  // State management
  const [students, setStudents] = useState<StudentUDISEData[]>([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [filtersExpanded, setFiltersExpanded] = useState(true);

  // Filters
  const [filterSessionYear, setFilterSessionYear] = useState<string>('');
  const [filterClass, setFilterClass] = useState<string>('all');
  const [filterSection, setFilterSection] = useState<string>('all');
  const [filterGender, setFilterGender] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalStudents, setTotalStudents] = useState(0);
  const perPage = DEFAULT_PAGE_SIZE;

  // Available sections (dynamically populated)
  const [availableSections, setAvailableSections] = useState<string[]>([]);

  // Load students from API
  const loadStudents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('per_page', perPage.toString());

      // Add filters
      if (filterSessionYear && filterSessionYear !== 'all') params.append('session_year_id', filterSessionYear);
      if (filterClass !== 'all') params.append('class_id', filterClass);
      if (filterSection !== 'all') params.append('section', filterSection);
      if (filterGender !== 'all') params.append('gender_id', filterGender);
      if (searchTerm) params.append('search', searchTerm);

      // Add is_active filter based on status dropdown
      if (filterStatus === 'active') {
        params.append('is_active', 'true');
      } else if (filterStatus === 'inactive') {
        params.append('is_active', 'false');
      }

      const response = await reportsAPI.getStudentUDISEReport(params);
      setStudents(response.students);
      setTotalPages(response.total_pages);
      setTotalStudents(response.total);

      // Extract unique sections from students
      const sections = Array.from(new Set(response.students.map((s: StudentUDISEData) => s.section).filter(Boolean)));
      setAvailableSections(sections as string[]);

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

  useEffect(() => {
    loadStudents();
  }, [page, filterSessionYear, filterClass, filterSection, filterGender, filterStatus, searchTerm]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1);
  }, [filterSessionYear, filterClass, filterSection, filterGender, filterStatus, searchTerm]);

  // Export to Excel
  const handleExportExcel = () => {
    try {
      const exportData = students.map(student => ({
        'Admission Number': student.admission_number,
        'Full Name': student.full_name,
        'Date of Birth': student.date_of_birth,
        'Age': student.age || 'N/A',
        'Gender': student.gender_name,
        'Class': student.class_name,
        'Section': student.section || 'N/A',
        'Roll Number': student.roll_number || 'N/A',
        'Session Year': student.session_year_name,
        'Admission Date': student.admission_date,
        'Blood Group': student.blood_group || 'N/A',
        'Aadhar Number': student.aadhar_no || 'N/A',
        'Phone': student.phone || 'N/A',
        'Email': student.email || 'N/A',
        'Address': student.address || 'N/A',
        'City': student.city || 'N/A',
        'State': student.state || 'N/A',
        'Postal Code': student.postal_code || 'N/A',
        'Country': student.country,
        'Father Name': student.father_name,
        'Father Phone': student.father_phone || 'N/A',
        'Father Email': student.father_email || 'N/A',
        'Father Occupation': student.father_occupation || 'N/A',
        'Mother Name': student.mother_name,
        'Mother Phone': student.mother_phone || 'N/A',
        'Mother Email': student.mother_email || 'N/A',
        'Mother Occupation': student.mother_occupation || 'N/A',
        'Guardian Name': student.guardian_name || 'N/A',
        'Guardian Phone': student.guardian_phone || 'N/A',
        'Guardian Email': student.guardian_email || 'N/A',
        'Guardian Relation': student.guardian_relation || 'N/A',
        'Status': student.is_active ? 'Active' : 'Inactive',
      }));

      const worksheet = XLSX.utils.json_to_sheet(exportData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'UDISE Report');

      // Auto-size columns
      const maxWidth = 50;
      const colWidths = Object.keys(exportData[0] || {}).map(key => ({
        wch: Math.min(Math.max(key.length, 10), maxWidth)
      }));
      worksheet['!cols'] = colWidths;

      XLSX.writeFile(workbook, `Student_UDISE_Report_${new Date().toISOString().split('T')[0]}.xlsx`);

      setSnackbar({
        open: true,
        message: 'Report exported successfully!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      setSnackbar({
        open: true,
        message: 'Failed to export report',
        severity: 'error'
      });
    }
  };

  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="student-management">
        {/* Filters - Compact & Collapsible */}
        <Paper elevation={2} sx={{ mb: 2 }}>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              sx={{
                p: { xs: 1.5, sm: 2 },
                cursor: 'pointer',
                '&:hover': { bgcolor: 'rgba(0, 0, 0, 0.02)' }
              }}
              onClick={() => setFiltersExpanded(!filtersExpanded)}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <FilterList sx={{ fontSize: 20 }} />
                <Typography variant="subtitle1" fontWeight={600}>
                  Filters
                </Typography>
                {!filtersExpanded && (
                  <Chip
                    label={`${filterSessionYear ? 'Session: ' + filterSessionYear : 'No filters'}`}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                )}
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <Button
                  variant="contained"
                  startIcon={<TableChart />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleExportExcel();
                  }}
                  disabled={students.length === 0}
                  size="small"
                >
                  Export
                </Button>
                {filtersExpanded ? <ExpandLess /> : <ExpandMore />}
              </Box>
            </Box>

            {filtersExpanded && (
              <Box sx={{ px: { xs: 1.5, sm: 2 }, pb: 2 }}>
                <Box
                  display="grid"
                  gridTemplateColumns={{
                    xs: '1fr',
                    sm: 'repeat(2, 1fr)',
                    md: 'repeat(3, 1fr)',
                    lg: 'repeat(6, 1fr)'
                  }}
                  gap={1.5}
                >
                  <SessionYearDropdown
                    value={filterSessionYear}
                    onChange={(value) => setFilterSessionYear(value as string)}
                    label="Session Year"
                    size="small"
                  />
                  <ClassDropdown
                    value={filterClass}
                    onChange={(value) => setFilterClass(value as string)}
                    label="Class"
                    size="small"
                    includeAll
                  />
                  <FormControl size="small" fullWidth>
                    <InputLabel>Section</InputLabel>
                    <Select
                      value={filterSection}
                      label="Section"
                      onChange={(e) => setFilterSection(e.target.value)}
                    >
                      <MenuItem value="all">All Sections</MenuItem>
                      {availableSections.map((section) => (
                        <MenuItem key={section} value={section}>
                          Section {section}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <GenderDropdown
                    value={filterGender}
                    onChange={(value) => setFilterGender(value as string)}
                    label="Gender"
                    size="small"
                    includeAll
                  />
                  <FormControl size="small" fullWidth>
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={filterStatus}
                      label="Status"
                      onChange={(e) => setFilterStatus(e.target.value)}
                    >
                      <MenuItem value="all">All</MenuItem>
                      <MenuItem value="active">Active</MenuItem>
                      <MenuItem value="inactive">Inactive</MenuItem>
                    </Select>
                  </FormControl>
                  <TextField
                    size="small"
                    label="Search"
                    placeholder="Name/Admission No"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    slotProps={{
                      input: {
                        startAdornment: <Search sx={{ mr: 0.5, color: 'text.secondary', fontSize: 20 }} />,
                      }
                    }}
                    fullWidth
                  />
                </Box>
              </Box>
            )}
          </Paper>

          {/* Student Data Table */}
          <Paper elevation={2}>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Admission No</TableCell>
                        <TableCell>Full Name</TableCell>
                        <TableCell>DOB</TableCell>
                        <TableCell>Age</TableCell>
                        <TableCell>Gender</TableCell>
                        <TableCell>Class</TableCell>
                        <TableCell>Section</TableCell>
                        <TableCell>Roll No</TableCell>
                        <TableCell>Father Name</TableCell>
                        <TableCell>Mother Name</TableCell>
                        <TableCell>Phone</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {students.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={12} align="center">
                            <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                              No students found
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ) : (
                        students.map((student) => (
                          <TableRow key={student.id} hover>
                            <TableCell>{student.admission_number}</TableCell>
                            <TableCell>{student.full_name}</TableCell>
                            <TableCell>{student.date_of_birth}</TableCell>
                            <TableCell>{student.age || 'N/A'}</TableCell>
                            <TableCell>{student.gender_name}</TableCell>
                            <TableCell>{student.class_name}</TableCell>
                            <TableCell>{student.section || 'N/A'}</TableCell>
                            <TableCell>{student.roll_number || 'N/A'}</TableCell>
                            <TableCell>{student.father_name}</TableCell>
                            <TableCell>{student.mother_name}</TableCell>
                            <TableCell>{student.phone || 'N/A'}</TableCell>
                            <TableCell>
                              <Chip
                                label={student.is_active ? 'Active' : 'Inactive'}
                                color={student.is_active ? 'success' : 'default'}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>

                {/* Pagination */}
                {totalPages > 1 && (
                  <Box display="flex" justifyContent="center" mt={3} pb={3}>
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
              </>
            )}
          </Paper>

          {/* Snackbar for notifications */}
          <Snackbar
            open={snackbar.open}
            autoHideDuration={6000}
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          >
            <Alert
              onClose={() => setSnackbar({ ...snackbar, open: false })}
              severity={snackbar.severity}
              sx={{ width: '100%' }}
            >
              {snackbar.message}
          </Alert>
        </Snackbar>
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default StudentUDISEReport;

