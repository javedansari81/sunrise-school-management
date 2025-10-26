import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Button,
  TextField,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Typography,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Alert,
  Tooltip,
  Grid
} from '@mui/material';
import {
  Add as AddIcon,
  History as HistoryIcon,
  Payment as PaymentIcon,
  DirectionsBus as BusIcon,
  Cancel as CancelIcon,
  FilterList
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import transportService, {
  EnhancedStudentTransportSummary,
  TransportType,
  TransportDistanceSlab
} from '../../services/transportService';
import { DEFAULT_PAGE_SIZE, PAGE_SIZE_OPTIONS } from '../../config/pagination';
import EnrollDialog from './transport/EnrollDialog';
import PaymentDialog from './transport/PaymentDialog';
import HistoryDialog from './transport/HistoryDialog';

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
      id={`transport-tabpanel-${index}`}
      aria-labelledby={`transport-tab-${index}`}
      {...other}
    >
      {value === index && <>{children}</>}
    </div>
  );
}

const TransportManagementSystem: React.FC = () => {
  const { user } = useAuth();
  const [configuration, setConfiguration] = useState<any>(null);
  const [configLoading, setConfigLoading] = useState(false);

  // State
  const [activeTab, setActiveTab] = useState(0);
  const [students, setStudents] = useState<EnhancedStudentTransportSummary[]>([]);
  const [filteredStudents, setFilteredStudents] = useState<EnhancedStudentTransportSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Filters
  const [sessionYear, setSessionYear] = useState<string>('2025-26');
  const [sessionYearId, setSessionYearId] = useState<number | null>(null);
  const [classFilter, setClassFilter] = useState<string | number>('all');
  const [nameSearch, setNameSearch] = useState<string>('');

  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_PAGE_SIZE);

  // Transport Configuration
  const [transportTypes, setTransportTypes] = useState<TransportType[]>([]);

  // Dialogs
  const [enrollDialogOpen, setEnrollDialogOpen] = useState(false);
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<EnhancedStudentTransportSummary | null>(null);

  // Handle URL parameters for direct navigation from Fee Management
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const studentIdParam = urlParams.get('student_id');
    const sessionYearIdParam = urlParams.get('session_year_id');
    const autoOpenPayment = urlParams.get('auto_open_payment');

    if (studentIdParam && sessionYearIdParam && autoOpenPayment === 'true') {
      // Store these for later use after students are loaded
      sessionStorage.setItem('transport_auto_open_student_id', studentIdParam);
      sessionStorage.setItem('transport_auto_open_session_year_id', sessionYearIdParam);
    }
  }, []);

  // Load configuration and data
  useEffect(() => {
    if (user) {
      loadTransportConfiguration();
    }
  }, [user]);

  // Load students when filters change
  useEffect(() => {
    if (user && sessionYear) {
      loadStudents();
    }
  }, [user, sessionYear, classFilter]);

  // Filter students based on active tab and name search (client-side)
  useEffect(() => {
    filterStudents();
  }, [students, activeTab, nameSearch]);

  // Auto-open payment dialog if coming from Fee Management
  useEffect(() => {
    if (students.length > 0 && !loading) {
      const autoOpenStudentId = sessionStorage.getItem('transport_auto_open_student_id');
      const autoOpenSessionYearId = sessionStorage.getItem('transport_auto_open_session_year_id');

      if (autoOpenStudentId && autoOpenSessionYearId) {
        // Clear session storage
        sessionStorage.removeItem('transport_auto_open_student_id');
        sessionStorage.removeItem('transport_auto_open_session_year_id');

        // Find the student
        const student = students.find(s => s.student_id === parseInt(autoOpenStudentId));

        if (student && student.is_enrolled) {
          // Set name search to filter to this student
          setNameSearch(student.student_name);

          // Open payment dialog
          setSelectedStudent(student);
          setPaymentDialogOpen(true);
        } else if (student && !student.is_enrolled) {
          setError(`Student ${student.student_name} is not enrolled in transport service`);
        } else {
          setError('Student not found in transport system');
        }
      }
    }
  }, [students, loading]);

  const loadTransportConfiguration = async () => {
    try {
      setConfigLoading(true);
      const config = await transportService.getConfiguration();
      setConfiguration(config);
      const types = await transportService.getTransportTypes();
      setTransportTypes(types);

      // Set default session year ID if available
      if (config?.session_years && config.session_years.length > 0) {
        const currentYear = config.session_years.find((y: any) => y.name === sessionYear);
        if (currentYear) {
          setSessionYearId(currentYear.id);
        } else {
          // Default to first session year
          setSessionYear(config.session_years[0].name);
          setSessionYearId(config.session_years[0].id);
        }
      }
    } catch (err: any) {
      console.error('Error loading transport configuration:', err);
      setError(err.response?.data?.detail || 'Failed to load transport configuration');
    } finally {
      setConfigLoading(false);
    }
  };

  const loadStudents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = { session_year: sessionYear };

      // Add class_id filter if not 'all'
      if (classFilter && classFilter !== 'all') {
        params.class_id = classFilter;
      }

      const data = await transportService.getStudents(params);
      setStudents(data);
    } catch (err: any) {
      console.error('Error loading students:', err);
      setError(err.response?.data?.detail || 'Failed to load students');
    } finally {
      setLoading(false);
    }
  }, [sessionYear, classFilter]);

  const filterStudents = useCallback(() => {
    let filtered = [...students];

    // Filter by tab
    if (activeTab === 1) {
      // Enrolled
      filtered = filtered.filter(s => s.is_enrolled);
    } else if (activeTab === 2) {
      // Not Enrolled
      filtered = filtered.filter(s => !s.is_enrolled);
    }

    // Class filtering is now done server-side in loadStudents()

    // Filter by name (client-side for better UX)
    if (nameSearch) {
      const search = nameSearch.toLowerCase();
      filtered = filtered.filter(s =>
        s.student_name.toLowerCase().includes(search) ||
        s.admission_number.toLowerCase().includes(search)
      );
    }

    setFilteredStudents(filtered);
    setPage(0); // Reset to first page when filters change
  }, [students, activeTab, nameSearch]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleEnrollClick = (student: EnhancedStudentTransportSummary) => {
    setSelectedStudent(student);
    setEnrollDialogOpen(true);
  };

  const handlePaymentClick = (student: EnhancedStudentTransportSummary) => {
    setSelectedStudent(student);
    setPaymentDialogOpen(true);
  };

  const handleHistoryClick = (student: EnhancedStudentTransportSummary) => {
    setSelectedStudent(student);
    setHistoryDialogOpen(true);
  };

  const handleDiscontinue = async (student: EnhancedStudentTransportSummary) => {
    if (!window.confirm(`Are you sure you want to discontinue transport service for ${student.student_name}?`)) {
      return;
    }

    try {
      setLoading(true);
      const today = new Date().toISOString().split('T')[0];
      await transportService.discontinueService(student.enrollment_id!, today);
      setSuccess('Transport service discontinued successfully');
      loadStudents();
    } catch (err: any) {
      console.error('Error discontinuing service:', err);
      // Handle FastAPI validation errors (422)
      if (err.response?.status === 422 && Array.isArray(err.response?.data?.detail)) {
        const errorMessages = err.response.data.detail.map((e: any) => e.msg).join(', ');
        setError(`Validation error: ${errorMessages}`);
      } else {
        setError(err.response?.data?.detail || 'Failed to discontinue service');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getStatusChip = (student: EnhancedStudentTransportSummary) => {
    if (!student.is_enrolled) {
      return <Chip label="Not Enrolled" size="small" color="default" />;
    }
    if (student.discontinue_date) {
      return <Chip label="Discontinued" size="small" color="warning" />;
    }
    return <Chip label="Enrolled" size="small" color="success" />;
  };

  const paginatedStudents = filteredStudents.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  if (configLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Alerts */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: { xs: 2, sm: 3 } }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: { xs: 2, sm: 3 } }}>
          {success}
        </Alert>
      )}

      {/* Filters Section - Above Tabs */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" fontWeight="bold" mb={2}>
          <FilterList sx={{ mr: 1 }} />
          Filters
        </Typography>
        <Box sx={{
          display: 'flex',
          gap: { xs: 1.5, sm: 2 },
          alignItems: { xs: 'stretch', sm: 'center' },
          flexWrap: 'wrap',
          flexDirection: { xs: 'column', sm: 'row' }
        }}>
          <FormControl
            size="small"
            sx={{
              flex: { xs: '1 1 100%', sm: '1 1 auto' },
              minWidth: { xs: '100%', sm: 'auto' }
            }}
          >
            <InputLabel>Session Year</InputLabel>
            <Select
              value={sessionYear}
              label="Session Year"
              onChange={(e) => {
                const selectedYear = configuration?.session_years?.find((y: any) => y.name === e.target.value);
                setSessionYear(e.target.value);
                if (selectedYear) {
                  setSessionYearId(selectedYear.id);
                }
              }}
            >
              {configuration?.session_years?.map((year: any) => (
                <MenuItem key={year.id} value={year.name}>
                  {year.description}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl
            size="small"
            sx={{
              flex: { xs: '1 1 100%', sm: '1 1 auto' },
              minWidth: { xs: '100%', sm: 'auto' }
            }}
          >
            <InputLabel>Class</InputLabel>
            <Select
              value={classFilter}
              label="Class"
              onChange={(e) => setClassFilter(e.target.value)}
            >
              <MenuItem value="all">All Classes</MenuItem>
              {configuration?.classes?.map((cls: any) => (
                <MenuItem key={cls.id} value={cls.id}>
                  {cls.description}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            size="small"
            label="Search by Name or Admission Number"
            placeholder="Enter student name or admission number..."
            value={nameSearch}
            onChange={(e) => setNameSearch(e.target.value)}
            sx={{
              flex: { xs: '1 1 100%', sm: '1 1 auto' },
              minWidth: { xs: '100%', sm: 'auto' }
            }}
          />
        </Box>
      </Paper>

      {/* Tabs Section */}
      <Paper sx={{ width: '100%', mb: { xs: 2, sm: 3 } }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
          sx={{
            '& .MuiTab-root': {
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              minHeight: { xs: 40, sm: 48 },
              minWidth: { xs: 80, sm: 120 },
              textTransform: 'none',
              fontWeight: 500,
            },
            '& .Mui-selected': {
              fontWeight: 600,
            }
          }}
        >
          <Tab label="All Students" />
          <Tab label="Enrolled" />
          <Tab label="Not Enrolled" />
          <Tab label="Statistics" />
        </Tabs>

        {/* All Students / Enrolled / Not Enrolled Tabs */}
        {[0, 1, 2].includes(activeTab) && (
          <TabPanel value={activeTab} index={activeTab}>
            {loading ? (
              <Box display="flex" justifyContent="center" p={{ xs: 2, sm: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Paper elevation={3} sx={{ p: 3 }}>
                <TableContainer
                  sx={{
                    maxHeight: { xs: '60vh', sm: '70vh' },
                    overflow: 'auto'
                  }}
                >
                  <Table
                    stickyHeader
                    sx={{
                      '& .MuiTableCell-root': {
                        fontSize: '0.875rem',
                        padding: '12px 16px',
                        borderBottom: '1px solid rgba(224, 224, 224, 1)'
                      },
                      '& .MuiTableHead-root .MuiTableCell-root': {
                        backgroundColor: 'white',
                        fontWeight: 600,
                        fontSize: '0.875rem'
                      }
                    }}
                  >
                    <TableHead>
                      <TableRow>
                        <TableCell>Admission No</TableCell>
                        <TableCell>Student Name</TableCell>
                        <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>Class</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Transport Type</TableCell>
                        <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Monthly Fee</TableCell>
                        <TableCell sx={{ display: { xs: 'none', lg: 'table-cell' } }}>Distance (KM)</TableCell>
                        <TableCell align="right">Balance</TableCell>
                        <TableCell align="center">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {paginatedStudents.map((student) => (
                        <TableRow key={student.student_id} hover>
                          <TableCell>{student.admission_number}</TableCell>
                          <TableCell>{student.student_name}</TableCell>
                          <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>{student.class_name}</TableCell>
                          <TableCell>{getStatusChip(student)}</TableCell>
                          <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>{student.transport_type_name || '-'}</TableCell>
                          <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>₹{student.monthly_fee ? Number(student.monthly_fee).toFixed(2) : '-'}</TableCell>
                          <TableCell sx={{ display: { xs: 'none', lg: 'table-cell' } }}>{student.distance_km || '-'}</TableCell>
                          <TableCell align="right">
                            {student.is_enrolled ? `₹${Number(student.total_balance || 0).toFixed(2)}` : '-'}
                          </TableCell>
                          <TableCell align="center">
                            {student.is_enrolled ? (
                              <>
                                <Tooltip title="Make Payment">
                                  <IconButton size="small" onClick={() => handlePaymentClick(student)}>
                                    <PaymentIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="View History">
                                  <IconButton size="small" onClick={() => handleHistoryClick(student)}>
                                    <HistoryIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Discontinue">
                                  <IconButton size="small" onClick={() => handleDiscontinue(student)} color="error">
                                    <CancelIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </>
                            ) : (
                              <Button
                                size="small"
                                variant="outlined"
                                startIcon={<AddIcon />}
                                onClick={() => handleEnrollClick(student)}
                              >
                                Enroll
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <TablePagination
                  rowsPerPageOptions={PAGE_SIZE_OPTIONS}
                  component="div"
                  count={filteredStudents.length}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={handleChangePage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                />
              </Paper>
            )}
          </TabPanel>
        )}

        {/* Statistics Tab */}
        <TabPanel value={activeTab} index={3}>
          {loading ? (
            <Box display="flex" justifyContent="center" p={{ xs: 2, sm: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Paper elevation={3} sx={{ p: 3 }}>
              <Box>
              <Typography variant="h6" gutterBottom>
                Transport Statistics - {sessionYear}
              </Typography>

              {/* Summary Cards */}
              <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* Total Students */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'primary.light', color: 'white' }}>
                    <Typography variant="h3" fontWeight="bold">
                      {students.length}
                    </Typography>
                    <Typography variant="body1">Total Students</Typography>
                  </Paper>
                </Grid>

                {/* Enrolled Students */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'success.light', color: 'white' }}>
                    <Typography variant="h3" fontWeight="bold">
                      {students.filter(s => s.is_enrolled).length}
                    </Typography>
                    <Typography variant="body1">Enrolled Students</Typography>
                  </Paper>
                </Grid>

                {/* Not Enrolled Students */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.400', color: 'white' }}>
                    <Typography variant="h3" fontWeight="bold">
                      {students.filter(s => !s.is_enrolled).length}
                    </Typography>
                    <Typography variant="body1">Not Enrolled</Typography>
                  </Paper>
                </Grid>

                {/* Enrollment Rate */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'info.light', color: 'white' }}>
                    <Typography variant="h3" fontWeight="bold">
                      {students.length > 0
                        ? ((students.filter(s => s.is_enrolled).length / students.length) * 100).toFixed(1)
                        : '0.0'}%
                    </Typography>
                    <Typography variant="body1">Enrollment Rate</Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Financial Summary */}
              <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
                Financial Summary
              </Typography>
              <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* Total Expected Amount */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="h4" fontWeight="bold" color="primary">
                      ₹{students
                        .filter(s => s.is_enrolled)
                        .reduce((sum, s) => sum + Number(s.total_amount || 0), 0)
                        .toFixed(2)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Expected
                    </Typography>
                  </Paper>
                </Grid>

                {/* Total Collected */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="h4" fontWeight="bold" color="success.main">
                      ₹{students
                        .filter(s => s.is_enrolled)
                        .reduce((sum, s) => sum + Number(s.total_paid || 0), 0)
                        .toFixed(2)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Collected
                    </Typography>
                  </Paper>
                </Grid>

                {/* Total Pending */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="h4" fontWeight="bold" color="error.main">
                      ₹{students
                        .filter(s => s.is_enrolled)
                        .reduce((sum, s) => sum + Number(s.total_balance || 0), 0)
                        .toFixed(2)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Pending
                    </Typography>
                  </Paper>
                </Grid>

                {/* Collection Rate */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="h4" fontWeight="bold" color="info.main">
                      {(() => {
                        const totalExpected = students
                          .filter(s => s.is_enrolled)
                          .reduce((sum, s) => sum + Number(s.total_amount || 0), 0);
                        const totalCollected = students
                          .filter(s => s.is_enrolled)
                          .reduce((sum, s) => sum + Number(s.total_paid || 0), 0);
                        return totalExpected > 0
                          ? ((totalCollected / totalExpected) * 100).toFixed(1)
                          : '0.0';
                      })()}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Collection Rate
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Transport Type Breakdown */}
              <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
                Transport Type Breakdown
              </Typography>
              <TableContainer component={Paper} sx={{ mb: 4 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Transport Type</TableCell>
                      <TableCell align="center">Students</TableCell>
                      <TableCell align="right">Total Expected</TableCell>
                      <TableCell align="right">Total Collected</TableCell>
                      <TableCell align="right">Total Pending</TableCell>
                      <TableCell align="center">Collection %</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(() => {
                      const typeBreakdown = students
                        .filter(s => s.is_enrolled && s.transport_type_name)
                        .reduce((acc, student) => {
                          const typeName = student.transport_type_name || 'Unknown';
                          if (!acc[typeName]) {
                            acc[typeName] = {
                              count: 0,
                              totalExpected: 0,
                              totalCollected: 0,
                              totalPending: 0
                            };
                          }
                          acc[typeName].count += 1;
                          acc[typeName].totalExpected += Number(student.total_amount || 0);
                          acc[typeName].totalCollected += Number(student.total_paid || 0);
                          acc[typeName].totalPending += Number(student.total_balance || 0);
                          return acc;
                        }, {} as Record<string, { count: number; totalExpected: number; totalCollected: number; totalPending: number }>);

                      return Object.entries(typeBreakdown).map(([typeName, data]) => (
                        <TableRow key={typeName}>
                          <TableCell>{typeName}</TableCell>
                          <TableCell align="center">{data.count}</TableCell>
                          <TableCell align="right">₹{data.totalExpected.toFixed(2)}</TableCell>
                          <TableCell align="right">₹{data.totalCollected.toFixed(2)}</TableCell>
                          <TableCell align="right">₹{data.totalPending.toFixed(2)}</TableCell>
                          <TableCell align="center">
                            {data.totalExpected > 0
                              ? ((data.totalCollected / data.totalExpected) * 100).toFixed(1)
                              : '0.0'}%
                          </TableCell>
                        </TableRow>
                      ));
                    })()}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Payment Status Summary */}
              <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
                Payment Status Summary
              </Typography>
              <Grid container spacing={3}>
                {/* Fully Paid Students */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'success.light', color: 'white' }}>
                    <Typography variant="h3" fontWeight="bold">
                      {students.filter(s => s.is_enrolled && Number(s.total_balance || 0) === 0).length}
                    </Typography>
                    <Typography variant="body1">Fully Paid</Typography>
                  </Paper>
                </Grid>

                {/* Partially Paid Students */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'warning.light', color: 'white' }}>
                    <Typography variant="h3" fontWeight="bold">
                      {students.filter(s =>
                        s.is_enrolled &&
                        Number(s.total_paid || 0) > 0 &&
                        Number(s.total_balance || 0) > 0
                      ).length}
                    </Typography>
                    <Typography variant="body1">Partially Paid</Typography>
                  </Paper>
                </Grid>

                {/* No Payment Students */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'error.light', color: 'white' }}>
                    <Typography variant="h3" fontWeight="bold">
                      {students.filter(s => s.is_enrolled && Number(s.total_paid || 0) === 0).length}
                    </Typography>
                    <Typography variant="body1">No Payment</Typography>
                  </Paper>
                </Grid>

                {/* Students with Overdue */}
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'error.dark', color: 'white' }}>
                    <Typography variant="h3" fontWeight="bold">
                      {students.filter(s => s.is_enrolled && (s.overdue_months || 0) > 0).length}
                    </Typography>
                    <Typography variant="body1">With Overdue</Typography>
                  </Paper>
                </Grid>
              </Grid>
              </Box>
            </Paper>
          )}
        </TabPanel>
      </Paper>

      {/* Enroll Dialog */}
      <EnrollDialog
        open={enrollDialogOpen}
        onClose={() => {
          setEnrollDialogOpen(false);
          setSelectedStudent(null);
        }}
        student={selectedStudent}
        transportTypes={transportTypes}
        sessionYear={sessionYear}
        configuration={configuration}
        onSuccess={() => {
          setSuccess('Student enrolled successfully');
          loadStudents();
          setEnrollDialogOpen(false);
          setSelectedStudent(null);
        }}
        onError={(msg) => setError(msg)}
      />

      {/* Payment Dialog */}
      <PaymentDialog
        open={paymentDialogOpen}
        onClose={() => {
          setPaymentDialogOpen(false);
          setSelectedStudent(null);
        }}
        student={selectedStudent}
        sessionYear={sessionYear}
        sessionYearId={sessionYearId}
        configuration={configuration}
        onSuccess={() => {
          setSuccess('Payment processed successfully');
          loadStudents();
          setPaymentDialogOpen(false);
          setSelectedStudent(null);
        }}
        onError={(msg) => setError(msg)}
      />

      {/* History Dialog */}
      <HistoryDialog
        open={historyDialogOpen}
        onClose={() => {
          setHistoryDialogOpen(false);
          setSelectedStudent(null);
        }}
        student={selectedStudent}
        sessionYear={sessionYear}
        sessionYearId={sessionYearId}
      />
    </Box>
  );
};

export default TransportManagementSystem;

