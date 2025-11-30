import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Snackbar,
  Grid,
  Card,
  CardContent,
  ToggleButton,
  ToggleButtonGroup,
  IconButton,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tooltip,
} from '@mui/material';
import {
  CalendarMonth as CalendarIcon,
  List as ListIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  CheckCircle as PresentIcon,
  Cancel as AbsentIcon,
  Schedule as LateIcon,
  HourglassEmpty as HalfDayIcon,
  EventAvailable as ExcusedIcon,
  BeachAccess as HolidayIcon,
  EventBusy as LeaveIcon,
} from '@mui/icons-material';
import { useServiceConfiguration, useConfiguration } from '../../contexts/ConfigurationContext';
import { attendanceService } from '../../services/attendanceService';
import { SessionYearDropdown } from '../common/MetadataDropdown';

// Types - Use types from attendanceService
import type { AttendanceRecord as ServiceAttendanceRecord, StudentAttendanceSummary } from '../../services/attendanceService';

// Local interface that matches the service type
interface AttendanceRecord extends ServiceAttendanceRecord {}

const StudentAttendanceView: React.FC = () => {
  const { isLoaded, isLoading, error: configError } = useServiceConfiguration('attendance-management');
  const { getServiceConfiguration } = useConfiguration();
  const configuration = getServiceConfiguration('attendance-management');

  // State
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [sessionYearId, setSessionYearId] = useState<number | null>(null);
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [summary, setSummary] = useState<StudentAttendanceSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<AttendanceRecord | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  // Initialize session year from configuration (default to 2025-26 session)
  useEffect(() => {
    if (isLoaded && configuration?.session_years) {
      const currentSessionYear = configuration.session_years.find((sy: any) => sy.is_current);
      if (currentSessionYear) {
        setSessionYearId(currentSessionYear.id);
      }
    }
  }, [isLoaded, configuration]);

  // Load attendance data when month/year/session changes
  useEffect(() => {
    if (isLoaded && sessionYearId && !isNaN(sessionYearId) && sessionYearId > 0) {
      loadAttendanceData();
      loadSummary();
    }
  }, [currentDate, sessionYearId, isLoaded]);

  const loadAttendanceData = async () => {
    if (!sessionYearId) return;

    try {
      setLoading(true);
      const month = currentDate.getMonth() + 1;
      const year = currentDate.getFullYear();

      const response = await attendanceService.getMyAttendance(
        month,
        year,
        undefined,
        undefined,
        sessionYearId,
        1,
        500 // Get all records for the month
      );

      setAttendanceRecords(response.records || []);
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Error loading attendance records',
        severity: 'error'
      });
      setAttendanceRecords([]);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    if (!sessionYearId) return;

    try {
      const response = await attendanceService.getMyAttendanceSummary(sessionYearId);
      setSummary(response);
    } catch (error: any) {
      // Don't show error for summary - it's optional
      setSummary(null);
    }
  };

  // Navigation handlers
  const handlePreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const handleToday = () => {
    setCurrentDate(new Date());
  };

  // Get attendance for a specific date (using local date to avoid timezone issues)
  const getAttendanceForDate = (date: Date): AttendanceRecord | undefined => {
    // Format date as YYYY-MM-DD using local time (not UTC)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;

    return attendanceRecords.find(record => record.attendance_date === dateStr);
  };

  // Get status icon
  const getStatusIcon = (statusName?: string) => {
    if (!statusName) return undefined;

    switch (statusName.toUpperCase()) {
      case 'PRESENT':
        return <PresentIcon sx={{ fontSize: 20 }} />;
      case 'ABSENT':
        return <AbsentIcon sx={{ fontSize: 20 }} />;
      case 'LATE':
        return <LateIcon sx={{ fontSize: 20 }} />;
      case 'HALF_DAY':
        return <HalfDayIcon sx={{ fontSize: 20 }} />;
      case 'EXCUSED':
        return <ExcusedIcon sx={{ fontSize: 20 }} />;
      case 'HOLIDAY':
        return <HolidayIcon sx={{ fontSize: 20 }} />;
      case 'LEAVE':
        return <LeaveIcon sx={{ fontSize: 20 }} />;
      default:
        return undefined;
    }
  };

  // Get status color
  const getStatusColor = (statusName: string, statusColor?: string): string => {
    if (statusColor) return statusColor;

    switch (statusName?.toUpperCase()) {
      case 'PRESENT':
        return '#28A745';
      case 'ABSENT':
        return '#DC3545';
      case 'LATE':
        return '#FFA500';
      case 'HALF_DAY':
        return '#FFD700';
      case 'EXCUSED':
        return '#007BFF';
      case 'HOLIDAY':
      case 'LEAVE':
        return '#6C757D';
      default:
        return '#6C757D';
    }
  };

  // Handle record click
  const handleRecordClick = (record: AttendanceRecord) => {
    setSelectedRecord(record);
    setDetailDialogOpen(true);
  };

  const handleCloseDetailDialog = () => {
    setDetailDialogOpen(false);
    setSelectedRecord(null);
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Render calendar view
  const renderCalendarView = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay(); // 0 = Sunday

    // Create calendar grid
    const weeks: (Date | null)[][] = [];
    let currentWeek: (Date | null)[] = [];

    // Fill in empty cells before first day
    for (let i = 0; i < startingDayOfWeek; i++) {
      currentWeek.push(null);
    }

    // Fill in days of month
    for (let day = 1; day <= daysInMonth; day++) {
      currentWeek.push(new Date(year, month, day));

      if (currentWeek.length === 7) {
        weeks.push(currentWeek);
        currentWeek = [];
      }
    }

    // Fill in remaining empty cells
    if (currentWeek.length > 0) {
      while (currentWeek.length < 7) {
        currentWeek.push(null);
      }
      weeks.push(currentWeek);
    }

    return (
      <Paper sx={{ p: 2 }}>
        {/* Calendar Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <IconButton onClick={handlePreviousMonth} size="small">
            <ChevronLeftIcon />
          </IconButton>
          <Typography variant="h6" fontWeight="bold">
            {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </Typography>
          <IconButton onClick={handleNextMonth} size="small">
            <ChevronRightIcon />
          </IconButton>
        </Box>

        <Button size="small" onClick={handleToday} sx={{ mb: 2 }}>
          Today
        </Button>

        {/* Day headers */}
        <Grid container spacing={1} sx={{ mb: 1 }}>
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <Grid size={{ xs: 12 / 7 }} key={day}>
              <Typography variant="caption" fontWeight="bold" align="center" display="block">
                {day}
              </Typography>
            </Grid>
          ))}
        </Grid>

        {/* Calendar grid */}
        {weeks.map((week, weekIndex) => (
          <Grid container spacing={1} key={weekIndex} sx={{ mb: 1 }}>
            {week.map((date, dayIndex) => {
              if (!date) {
                return <Grid size={{ xs: 12 / 7 }} key={dayIndex} />;
              }

              const attendance = getAttendanceForDate(date);
              const isToday = date.toDateString() === new Date().toDateString();
              const statusColor = attendance ? getStatusColor(attendance.attendance_status_name || '', attendance.attendance_status_color) : undefined;

              return (
                <Grid size={{ xs: 12 / 7 }} key={dayIndex}>
                  <Tooltip title={attendance ? attendance.attendance_status_description : 'No record'}>
                    <Paper
                      sx={{
                        p: 1,
                        minHeight: 60,
                        cursor: attendance ? 'pointer' : 'default',
                        border: isToday ? '2px solid #1976d2' : '1px solid #e0e0e0',
                        backgroundColor: attendance ? `${statusColor}15` : 'white',
                        '&:hover': attendance ? {
                          backgroundColor: `${statusColor}25`,
                          transform: 'scale(1.05)',
                          transition: 'all 0.2s'
                        } : {}
                      }}
                      onClick={() => attendance && handleRecordClick(attendance)}
                    >
                      <Typography variant="body2" fontWeight={isToday ? 'bold' : 'normal'}>
                        {date.getDate()}
                      </Typography>
                      {attendance && (
                        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 0.5 }}>
                          <Box sx={{ color: statusColor }}>
                            {getStatusIcon(attendance.attendance_status_name)}
                          </Box>
                        </Box>
                      )}
                    </Paper>
                  </Tooltip>
                </Grid>
              );
            })}
          </Grid>
        ))}
      </Paper>
    );
  };

  // Render list view
  const renderListView = () => {
    const sortedRecords = [...attendanceRecords].sort((a, b) =>
      new Date(b.attendance_date).getTime() - new Date(a.attendance_date).getTime()
    );

    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: 'white' }}>
              <TableCell><strong>Date</strong></TableCell>
              <TableCell><strong>Day</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Period</strong></TableCell>
              <TableCell><strong>Remarks</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedRecords.length > 0 ? (
              sortedRecords.map((record) => {
                const date = new Date(record.attendance_date);
                const statusColor = getStatusColor(record.attendance_status_name || '', record.attendance_status_color);

                return (
                  <TableRow
                    key={record.id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => handleRecordClick(record)}
                  >
                    <TableCell>{date.toLocaleDateString('en-IN')}</TableCell>
                    <TableCell>{date.toLocaleDateString('en-US', { weekday: 'short' })}</TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(record.attendance_status_name || '')}
                        label={record.attendance_status_description}
                        size="small"
                        sx={{
                          backgroundColor: `${statusColor}15`,
                          color: statusColor,
                          borderColor: statusColor,
                          border: '1px solid'
                        }}
                      />
                    </TableCell>
                    <TableCell>{record.attendance_period_name || 'Full Day'}</TableCell>
                    <TableCell>{record.remarks || '-'}</TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                    No attendance records found for this month
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  // Loading state
  if (isLoading || !isLoaded) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  // Error state
  if (configError) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error loading configuration: {typeof configError === 'string' ? configError : 'Failed to load configuration'}
      </Alert>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
          My Attendance
        </Typography>
        <Typography variant="body2" color="text.secondary">
          View your attendance records and statistics
        </Typography>
      </Box>

      {/* Statistics Cards */}
      {summary && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="h4" fontWeight="bold" color="primary">
                  {summary.attendance_percentage.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Attendance Rate
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="h4" fontWeight="bold" sx={{ color: '#28A745' }}>
                  {summary.days_present}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Days Present
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="h4" fontWeight="bold" sx={{ color: '#DC3545' }}>
                  {summary.days_absent}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Days Absent
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="h4" fontWeight="bold">
                  {summary.total_school_days}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total School Days
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filters and View Toggle */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            {sessionYearId && (
              <SessionYearDropdown
                value={sessionYearId}
                onChange={(value) => setSessionYearId(Number(value))}
                label="Session Year"
                size="small"
              />
            )}
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={(e, newMode) => newMode && setViewMode(newMode)}
              size="small"
              fullWidth
            >
              <ToggleButton value="calendar">
                <CalendarIcon sx={{ mr: 1 }} />
                Calendar
              </ToggleButton>
              <ToggleButton value="list">
                <ListIcon sx={{ mr: 1 }} />
                List
              </ToggleButton>
            </ToggleButtonGroup>
          </Grid>
        </Grid>
      </Paper>

      {/* Legend */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom fontWeight="bold">
          Status Legend:
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {configuration?.attendance_statuses?.map((status: any) => (
            <Chip
              key={status.id}
              icon={getStatusIcon(status.name)}
              label={status.description}
              size="small"
              sx={{
                backgroundColor: `${getStatusColor(status.name, status.color_code)}15`,
                color: getStatusColor(status.name, status.color_code),
                borderColor: getStatusColor(status.name, status.color_code),
                border: '1px solid'
              }}
            />
          ))}
        </Box>
      </Paper>

      {/* Main Content */}
      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : (
        viewMode === 'calendar' ? renderCalendarView() : renderListView()
      )}

      {/* Detail Dialog */}
      <Dialog open={detailDialogOpen} onClose={handleCloseDetailDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Attendance Details</DialogTitle>
        <DialogContent>
          {selectedRecord && (
            <Box sx={{ pt: 1 }}>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="subtitle2" color="text.secondary">Date</Typography>
                  <Typography variant="body1">
                    {new Date(selectedRecord.attendance_date).toLocaleDateString('en-IN', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="subtitle2" color="text.secondary">Status</Typography>
                  <Chip
                    icon={getStatusIcon(selectedRecord.attendance_status_name || '')}
                    label={selectedRecord.attendance_status_description}
                    sx={{
                      backgroundColor: `${getStatusColor(selectedRecord.attendance_status_name || '', selectedRecord.attendance_status_color)}15`,
                      color: getStatusColor(selectedRecord.attendance_status_name || '', selectedRecord.attendance_status_color),
                      borderColor: getStatusColor(selectedRecord.attendance_status_name || '', selectedRecord.attendance_status_color),
                      border: '1px solid',
                      mt: 0.5
                    }}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="subtitle2" color="text.secondary">Period</Typography>
                  <Typography variant="body1">{selectedRecord.attendance_period_name || 'Full Day'}</Typography>
                </Grid>
                {selectedRecord.check_in_time && (
                  <Grid size={{ xs: 6 }}>
                    <Typography variant="subtitle2" color="text.secondary">Check-in Time</Typography>
                    <Typography variant="body1">{selectedRecord.check_in_time}</Typography>
                  </Grid>
                )}
                {selectedRecord.check_out_time && (
                  <Grid size={{ xs: 6 }}>
                    <Typography variant="subtitle2" color="text.secondary">Check-out Time</Typography>
                    <Typography variant="body1">{selectedRecord.check_out_time}</Typography>
                  </Grid>
                )}
                {selectedRecord.remarks && (
                  <Grid size={{ xs: 12 }}>
                    <Typography variant="subtitle2" color="text.secondary">Remarks</Typography>
                    <Typography variant="body1">{selectedRecord.remarks}</Typography>
                  </Grid>
                )}
                {selectedRecord.marked_by_name && (
                  <Grid size={{ xs: 12 }}>
                    <Typography variant="subtitle2" color="text.secondary">Marked By</Typography>
                    <Typography variant="body1">{selectedRecord.marked_by_name}</Typography>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetailDialog}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
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

export default StudentAttendanceView;

