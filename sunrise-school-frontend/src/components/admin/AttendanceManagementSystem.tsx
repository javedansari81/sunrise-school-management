import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Snackbar,
  Alert,
  Pagination,
  Card,
  CardContent,
  Typography,
  Grid
} from '@mui/material';
import {
  Delete as DeleteIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { format } from 'date-fns';
import { DEFAULT_PAGE_SIZE } from '../../config/pagination';
import { useServiceConfiguration, useConfiguration } from '../../contexts/ConfigurationContext';
import { attendanceService, AttendanceRecord, AttendanceFilters } from '../../services/attendanceService';
import CollapsibleFilterSection from '../common/CollapsibleFilterSection';
import { ClassDropdown } from '../common/MetadataDropdown';

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
      id={`attendance-tabpanel-${index}`}
      aria-labelledby={`attendance-tab-${index}`}
      {...other}
    >
      {value === index && <>{children}</>}
    </div>
  );
}

const AttendanceManagementSystem: React.FC = () => {
  const { isLoading: configLoading, isLoaded: configLoaded } = useServiceConfiguration('attendance-management');
  const { getServiceConfiguration } = useConfiguration();
  const configuration = getServiceConfiguration('attendance-management');

  // Debug: Log configuration data
  useEffect(() => {
    if (configuration) {
      console.log('Attendance Configuration:', configuration);
      console.log('Attendance Statuses:', configuration.attendance_statuses);
      console.log('Attendance Periods:', configuration.attendance_periods);
    }
  }, [configuration]);

  // State
  const [tabValue, setTabValue] = useState(0);
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [statistics, setStatistics] = useState<any>(null);

  // Filters
  const [filters, setFilters] = useState<AttendanceFilters>({
    session_year_id: 4,
    page: 1,
    per_page: DEFAULT_PAGE_SIZE
  });
  const [fromDate, setFromDate] = useState<Date | null>(null);
  const [toDate, setToDate] = useState<Date | null>(null);
  const [classId, setClassId] = useState('');
  const [statusId, setStatusId] = useState('');
  const [periodId, setPeriodId] = useState('');
  const [searchInput, setSearchInput] = useState('');

  // Load attendance records
  const loadAttendance = async () => {
    setLoading(true);
    try {
      const filterParams: AttendanceFilters = {
        ...filters,
        from_date: fromDate ? format(fromDate, 'yyyy-MM-dd') : undefined,
        to_date: toDate ? format(toDate, 'yyyy-MM-dd') : undefined,
        class_id: classId ? parseInt(classId) : undefined,
        attendance_status_id: statusId ? parseInt(statusId) : undefined,
        attendance_period_id: periodId ? parseInt(periodId) : undefined,
        search: searchInput || undefined,
        page,
        per_page: DEFAULT_PAGE_SIZE
      };

      const response = await attendanceService.listAttendance(filterParams);
      setRecords(response.records);
      setTotalRecords(response.total);
      setTotalPages(response.total_pages);
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to load attendance records',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Load statistics
  const loadStatistics = async () => {
    try {
      const stats = await attendanceService.getStatistics(
        classId ? parseInt(classId) : undefined,
        fromDate ? format(fromDate, 'yyyy-MM-dd') : undefined,
        toDate ? format(toDate, 'yyyy-MM-dd') : undefined,
        filters.session_year_id
      );
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  useEffect(() => {
    if (configLoaded) {
      loadAttendance();
      loadStatistics();
    }
  }, [configLoaded, page, filters.session_year_id]);

  // Real-time filtering - reload when filter values change
  useEffect(() => {
    if (configLoaded) {
      setPage(1); // Reset to first page when filters change
      loadAttendance();
      loadStatistics();
    }
  }, [fromDate, toDate, classId, statusId, periodId, searchInput]);

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this attendance record?')) return;

    try {
      await attendanceService.deleteAttendance(id);
      setSnackbar({ open: true, message: 'Attendance record deleted successfully', severity: 'success' });
      loadAttendance();
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to delete attendance record',
        severity: 'error'
      });
    }
  };

  const getStatusColor = (colorCode: string) => {
    return colorCode || '#757575';
  };

  if (configLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      {/* Filters */}
      <CollapsibleFilterSection
          title="Filters"
          defaultExpanded={true}
        >
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6, md: 2 }}>
              <DatePicker
                label="From Date"
                value={fromDate}
                onChange={(date) => setFromDate(date)}
                slotProps={{ textField: { fullWidth: true, size: 'small' } }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 2 }}>
              <DatePicker
                label="To Date"
                value={toDate}
                onChange={(date) => setToDate(date)}
                slotProps={{ textField: { fullWidth: true, size: 'small' } }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 2 }}>
              <ClassDropdown
                value={classId}
                onChange={(value) => setClassId(value === '' ? '' : value.toString())}
                label="Class"
                size="small"
                includeAll={true}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 2 }}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusId}
                  label="Status"
                  onChange={(e) => setStatusId(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  {configuration?.attendance_statuses && Array.isArray(configuration.attendance_statuses) ?
                    configuration.attendance_statuses.map((status: any) => (
                      <MenuItem key={status.id} value={status.id.toString()}>
                        {status.description || status.name}
                      </MenuItem>
                    )) : null}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 2 }}>
              <FormControl fullWidth size="small">
                <InputLabel>Period</InputLabel>
                <Select
                  value={periodId}
                  label="Period"
                  onChange={(e) => setPeriodId(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  {configuration?.attendance_periods && Array.isArray(configuration.attendance_periods) ?
                    configuration.attendance_periods.map((period: any) => (
                      <MenuItem key={period.id} value={period.id.toString()}>
                        {period.description || period.name}
                      </MenuItem>
                    )) : null}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 2 }}>
              <TextField
                fullWidth
                size="small"
                label="Search"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Student name, admission no..."
              />
            </Grid>
          </Grid>
        </CollapsibleFilterSection>

        {/* Tabs */}
        <Paper sx={{ mt: 2 }}>
          <Tabs value={tabValue} onChange={(_e, v) => setTabValue(v)}>
            <Tab label="All Records" />
            <Tab label="Statistics" />
          </Tabs>

          {/* Statistics Tab */}
          <TabPanel value={tabValue} index={1}>
            <Box sx={{ p: 3 }}>
              {statistics ? (
                <Grid container spacing={3}>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Total Records
                        </Typography>
                        <Typography variant="h4">
                          {statistics.total_records}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Present
                        </Typography>
                        <Typography variant="h4" color="success.main">
                          {statistics.total_present}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Absent
                        </Typography>
                        <Typography variant="h4" color="error.main">
                          {statistics.total_absent}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Attendance %
                        </Typography>
                        <Typography variant="h4" color="primary.main">
                          {statistics.overall_attendance_percentage.toFixed(1)}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Date Range
                        </Typography>
                        <Typography variant="body1">
                          {statistics.date_range}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              ) : (
                <Box display="flex" justifyContent="center" p={4}>
                  <CircularProgress />
                </Box>
              )}
            </Box>
          </TabPanel>

          {/* All Records Tab */}
          <TabPanel value={tabValue} index={0}>
            <Box sx={{ p: 2 }}>
              {loading ? (
                <Box display="flex" justifyContent="center" p={4}>
                  <CircularProgress />
                </Box>
              ) : (
                <>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ backgroundColor: '#fff' }}>
                          <TableCell>Date</TableCell>
                          <TableCell>Student</TableCell>
                          <TableCell>Class</TableCell>
                          <TableCell>Period</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Remarks</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {records.map((record) => (
                          <TableRow key={record.id}>
                            <TableCell>{format(new Date(record.attendance_date), 'dd MMM yyyy')}</TableCell>
                            <TableCell>{record.student_name || `Student ${record.student_id}`}</TableCell>
                            <TableCell>{record.class_name}</TableCell>
                            <TableCell>{record.attendance_period_name}</TableCell>
                            <TableCell>
                              <Chip
                                label={record.attendance_status_description}
                                size="small"
                                sx={{
                                  backgroundColor: getStatusColor(record.attendance_status_color || ''),
                                  color: '#fff'
                                }}
                              />
                            </TableCell>
                            <TableCell>{record.remarks || '-'}</TableCell>
                            <TableCell>
                              <IconButton size="small" color="error" onClick={() => handleDelete(record.id)}>
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  {/* Pagination */}
                  <Box display="flex" justifyContent="center" mt={2}>
                    <Pagination
                      count={totalPages}
                      page={page}
                      onChange={(_e, value) => setPage(value)}
                      color="primary"
                    />
                  </Box>
                </>
              )}
            </Box>
          </TabPanel>
        </Paper>

        {/* Snackbar */}
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
    </LocalizationProvider>
  );
};

export default AttendanceManagementSystem;

