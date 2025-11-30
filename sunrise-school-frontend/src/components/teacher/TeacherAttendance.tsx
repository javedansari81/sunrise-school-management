/**
 * Teacher Attendance Management Component
 * 
 * Features:
 * - Fast attendance marking with auto-advance workflow
 * - Keyboard shortcuts (P=Present, A=Absent, L=Late, H=Half Day)
 * - Visual progress tracking
 * - Bulk actions for remaining students
 * - Real-time saving
 * - Cross-class access for substitute teachers
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  Chip,
  LinearProgress,
  Alert,
  Snackbar,
  IconButton,
  Tooltip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as PresentIcon,
  Cancel as AbsentIcon,
  Schedule as LateIcon,
  HourglassEmpty as HalfDayIcon,
  EventAvailable as ExcusedIcon,
  BeachAccess as HolidayIcon,
  EventBusy as LeaveIcon,
  Save as SaveIcon,
  CheckCircleOutline as MarkAllIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ClassDropdown } from '../common/MetadataDropdown';
import { useServiceConfiguration, useConfiguration } from '../../contexts/ConfigurationContext';
import { useAuth } from '../../contexts/AuthContext';
import attendanceService from '../../services/attendanceService';

interface Student {
  id: number;
  roll_number: string;
  first_name: string;
  last_name: string;
  attendance_status_id?: number;
  attendance_status_description?: string;
  attendance_status_color?: string;
  remarks?: string;
  attendance_record_id?: number;
  is_saving?: boolean;
}

const TeacherAttendance: React.FC = () => {
  const { isLoading: configLoading, isLoaded: configLoaded } = useServiceConfiguration('attendance-management');
  const { getServiceConfiguration } = useConfiguration();
  const configuration = getServiceConfiguration('attendance-management');
  const { user } = useAuth();

  // Filter state
  const [classId, setClassId] = useState('');
  const [attendanceDate, setAttendanceDate] = useState<string>(format(new Date(), 'yyyy-MM-dd'));
  const [periodId, setPeriodId] = useState('1'); // Default: Full Day
  const sessionYearId = 4; // Current session year

  // Data state
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState<number>(0);

  // UI state
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Refs for keyboard navigation
  const rowRefs = useRef<{ [key: number]: HTMLTableRowElement | null }>({});

  // Pre-select class if teacher has assigned class
  useEffect(() => {
    if (user?.teacher_profile?.class_teacher_of_id && !classId && configLoaded) {
      setClassId(user.teacher_profile.class_teacher_of_id.toString());
    }
  }, [user, classId, configLoaded]);

  // Load students when filters change
  useEffect(() => {
    if (classId && attendanceDate && configLoaded) {
      loadStudents();
    }
  }, [classId, attendanceDate, periodId, configLoaded]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only handle shortcuts if not typing in a text field
      if ((e.target as HTMLElement).tagName === 'INPUT' || (e.target as HTMLElement).tagName === 'TEXTAREA') {
        return;
      }

      const student = students[focusedIndex];
      if (!student) return;

      let statusId: number | null = null;

      switch (e.key.toLowerCase()) {
        case 'p':
          statusId = 1; // Present
          break;
        case 'a':
          statusId = 2; // Absent
          break;
        case 'l':
          statusId = 3; // Late
          break;
        case 'h':
          statusId = 4; // Half Day
          break;
        case 'e':
          statusId = 5; // Excused
          break;
        case 'arrowdown':
          e.preventDefault();
          setFocusedIndex((prev) => Math.min(prev + 1, students.length - 1));
          break;
        case 'arrowup':
          e.preventDefault();
          setFocusedIndex((prev) => Math.max(prev - 1, 0));
          break;
        default:
          return;
      }

      if (statusId) {
        e.preventDefault();
        markAttendance(student.id, statusId, focusedIndex);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [students, focusedIndex]);

  // Auto-scroll to focused row
  useEffect(() => {
    const focusedRow = rowRefs.current[focusedIndex];
    if (focusedRow) {
      focusedRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [focusedIndex]);

  const loadStudents = async () => {
    if (!classId || !attendanceDate) return;

    setLoading(true);
    try {
      const response = await attendanceService.getClassAttendanceByDate(
        parseInt(classId),
        attendanceDate,
        sessionYearId
      );

      // Transform the response to match our Student interface
      const transformedStudents: Student[] = response.students.map((s: any) => {
        // Backend returns student_name as "FirstName LastName" concatenated
        const nameParts = (s.student_name || '').split(' ');
        const firstName = nameParts[0] || '';
        const lastName = nameParts.slice(1).join(' ') || '';

        return {
          id: s.student_id,
          roll_number: s.student_roll_number || s.roll_number || '',
          first_name: firstName,
          last_name: lastName,
          attendance_status_id: s.attendance_status_id,
          attendance_status_description: s.attendance_status_description,
          attendance_status_color: s.attendance_status_color,
          remarks: s.remarks || '',
          attendance_record_id: s.attendance_record_id,
          is_saving: false,
        };
      });

      // Sort by roll number
      transformedStudents.sort((a, b) => {
        const rollA = parseInt(a.roll_number) || 0;
        const rollB = parseInt(b.roll_number) || 0;
        return rollA - rollB;
      });

      setStudents(transformedStudents);

      // Set focus to first unmarked student
      const firstUnmarkedIndex = transformedStudents.findIndex(s => !s.attendance_status_id);
      setFocusedIndex(firstUnmarkedIndex >= 0 ? firstUnmarkedIndex : 0);

      setSnackbar({
        open: true,
        message: `Loaded ${transformedStudents.length} students`,
        severity: 'success',
      });
    } catch (error: any) {
      console.error('Error loading students:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to load students',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const markAttendance = async (studentId: number, statusId: number, studentIndex: number) => {
    const student = students[studentIndex];
    if (!student) return;

    // Update UI immediately (optimistic update)
    const updatedStudents = [...students];
    updatedStudents[studentIndex] = {
      ...student,
      is_saving: true,
    };
    setStudents(updatedStudents);

    try {
      const attendanceData = {
        student_id: studentId,
        class_id: parseInt(classId),
        session_year_id: sessionYearId,
        attendance_date: attendanceDate,
        attendance_status_id: statusId,
        attendance_period_id: parseInt(periodId),
        remarks: student.remarks || undefined,
      };

      let response;
      if (student.attendance_record_id) {
        // Update existing record
        response = await attendanceService.updateAttendance(student.attendance_record_id, {
          attendance_status_id: statusId,
          remarks: student.remarks || undefined,
        });
      } else {
        // Create new record
        response = await attendanceService.createAttendance(attendanceData);
      }

      // Update with server response
      const statusInfo = configuration?.attendance_statuses?.find((s: any) => s.id === statusId);
      updatedStudents[studentIndex] = {
        ...student,
        attendance_status_id: statusId,
        attendance_status_description: statusInfo?.description || '',
        attendance_status_color: statusInfo?.color_code || '#666',
        attendance_record_id: response.id,
        is_saving: false,
      };
      setStudents(updatedStudents);

      // Auto-advance to next unmarked student
      const nextUnmarkedIndex = updatedStudents.findIndex(
        (s, idx) => idx > studentIndex && !s.attendance_status_id
      );
      if (nextUnmarkedIndex >= 0) {
        setFocusedIndex(nextUnmarkedIndex);
      } else {
        // All marked, move to next student anyway
        setFocusedIndex(Math.min(studentIndex + 1, students.length - 1));
      }

      setSnackbar({
        open: true,
        message: `Marked ${student.first_name} ${student.last_name} as ${statusInfo?.description}`,
        severity: 'success',
      });
    } catch (error: any) {
      console.error('Error marking attendance:', error);
      updatedStudents[studentIndex] = {
        ...student,
        is_saving: false,
      };
      setStudents(updatedStudents);

      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to mark attendance',
        severity: 'error',
      });
    }
  };

  const markAllRemaining = async (statusId: number) => {
    const unmarkedStudents = students.filter(s => !s.attendance_status_id);
    if (unmarkedStudents.length === 0) {
      setSnackbar({
        open: true,
        message: 'All students already marked',
        severity: 'info',
      });
      return;
    }

    setSaving(true);
    try {
      const bulkData = {
        class_id: parseInt(classId),
        session_year_id: sessionYearId,
        attendance_date: attendanceDate,
        attendance_period_id: parseInt(periodId),
        records: unmarkedStudents.map(s => ({
          student_id: s.id,
          attendance_status_id: statusId,
        })),
      };

      await attendanceService.bulkCreateAttendance(bulkData);

      // Reload students to get updated data
      await loadStudents();

      setSnackbar({
        open: true,
        message: `Marked ${unmarkedStudents.length} remaining students`,
        severity: 'success',
      });
    } catch (error: any) {
      console.error('Error bulk marking:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to bulk mark attendance',
        severity: 'error',
      });
    } finally {
      setSaving(false);
    }
  };

  const updateRemarks = (studentIndex: number, remarks: string) => {
    const updatedStudents = [...students];
    updatedStudents[studentIndex] = {
      ...updatedStudents[studentIndex],
      remarks,
    };
    setStudents(updatedStudents);
  };

  const getStatusIcon = (statusId: number) => {
    switch (statusId) {
      case 1: return <PresentIcon sx={{ color: '#28A745' }} />;
      case 2: return <AbsentIcon sx={{ color: '#DC3545' }} />;
      case 3: return <LateIcon sx={{ color: '#FFC107' }} />;
      case 4: return <HalfDayIcon sx={{ color: '#17A2B8' }} />;
      case 5: return <ExcusedIcon sx={{ color: '#6C757D' }} />;
      case 6: return <HolidayIcon sx={{ color: '#007BFF' }} />;
      case 7: return <LeaveIcon sx={{ color: '#6F42C1' }} />;
      default: return undefined;
    }
  };

  const markedCount = students.filter(s => s.attendance_status_id).length;
  const totalCount = students.length;
  const progress = totalCount > 0 ? (markedCount / totalCount) * 100 : 0;

  if (configLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <ClassDropdown
              value={classId}
              onChange={(value) => setClassId(value.toString())}
              label="Class"
              size="small"
              required
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              fullWidth
              size="small"
              label="Date"
              type="date"
              value={attendanceDate}
              onChange={(e) => setAttendanceDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              required
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Period</InputLabel>
              <Select
                value={periodId}
                label="Period"
                onChange={(e) => setPeriodId(e.target.value)}
              >
                {configuration?.attendance_periods && Array.isArray(configuration.attendance_periods) ?
                  configuration.attendance_periods.map((period: any) => (
                    <MenuItem key={period.id} value={period.id.toString()}>
                      {period.description || period.name}
                    </MenuItem>
                  )) : null}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Progress Bar */}
      {students.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="h6">
                Progress: {markedCount} / {totalCount} students
              </Typography>
              <Typography variant="h6" color="primary">
                {progress.toFixed(0)}%
              </Typography>
            </Box>
            <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 1 }} />
          </CardContent>
        </Card>
      )}

      {/* Bulk Actions */}
      {students.length > 0 && markedCount < totalCount && (
        <Paper sx={{ p: 2, mb: 3, backgroundColor: '#F8F9FA' }}>
          <Typography variant="subtitle2" gutterBottom>
            Quick Actions for Remaining Students:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Button
              size="small"
              variant="outlined"
              startIcon={<MarkAllIcon />}
              onClick={() => markAllRemaining(1)}
              disabled={saving}
              sx={{ color: '#28A745', borderColor: '#28A745' }}
            >
              Mark All Present
            </Button>
            <Button
              size="small"
              variant="outlined"
              startIcon={<MarkAllIcon />}
              onClick={() => markAllRemaining(2)}
              disabled={saving}
              sx={{ color: '#DC3545', borderColor: '#DC3545' }}
            >
              Mark All Absent
            </Button>
          </Box>
        </Paper>
      )}

      {/* Students Table */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : students.length === 0 ? (
        <Alert severity="info">
          Please select a class and date to load students
        </Alert>
      ) : (
        <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#F8F9FA' }}>
                <TableCell sx={{ width: { xs: '60px', sm: '80px' }, fontSize: { xs: '0.75rem', sm: '0.875rem' } }}><strong>Roll</strong></TableCell>
                <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, minWidth: { xs: 120, sm: 150 } }}><strong>Student Name</strong></TableCell>
                <TableCell sx={{ width: { xs: '200px', sm: '400px' }, fontSize: { xs: '0.75rem', sm: '0.875rem' } }}><strong>Quick Actions</strong></TableCell>
                <TableCell sx={{ width: { xs: '100px', sm: '150px' }, fontSize: { xs: '0.75rem', sm: '0.875rem' } }}><strong>Status</strong></TableCell>
                <TableCell sx={{ width: { xs: '150px', sm: '200px' }, fontSize: { xs: '0.75rem', sm: '0.875rem' }, display: { xs: 'none', md: 'table-cell' } }}><strong>Remarks</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {students.map((student, index) => (
                <TableRow
                  key={student.id}
                  ref={(el) => {
                    rowRefs.current[index] = el;
                  }}
                  sx={{
                    backgroundColor: index === focusedIndex ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
                    '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' },
                    transition: 'background-color 0.2s',
                  }}
                >
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                    <Chip
                      label={student.roll_number}
                      size="small"
                      color={index === focusedIndex ? 'primary' : 'default'}
                      sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}
                    />
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                    <Typography variant="body2" sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                      {student.first_name} {student.last_name}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                    <Box sx={{ display: 'flex', gap: { xs: 0.25, sm: 0.5 }, flexWrap: 'wrap' }}>
                      <Tooltip title="Present (P)">
                        <IconButton
                          size="small"
                          onClick={() => markAttendance(student.id, 1, index)}
                          disabled={student.is_saving}
                          sx={{
                            color: student.attendance_status_id === 1 ? '#28A745' : 'inherit',
                            backgroundColor: student.attendance_status_id === 1 ? 'rgba(40, 167, 69, 0.1)' : 'transparent',
                            minWidth: { xs: 36, sm: 40 },
                            minHeight: { xs: 36, sm: 40 },
                          }}
                        >
                          <PresentIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Absent (A)">
                        <IconButton
                          size="small"
                          onClick={() => markAttendance(student.id, 2, index)}
                          disabled={student.is_saving}
                          sx={{
                            color: student.attendance_status_id === 2 ? '#DC3545' : 'inherit',
                            backgroundColor: student.attendance_status_id === 2 ? 'rgba(220, 53, 69, 0.1)' : 'transparent',
                            minWidth: { xs: 36, sm: 40 },
                            minHeight: { xs: 36, sm: 40 },
                          }}
                        >
                          <AbsentIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Late (L)">
                        <IconButton
                          size="small"
                          onClick={() => markAttendance(student.id, 3, index)}
                          disabled={student.is_saving}
                          sx={{
                            color: student.attendance_status_id === 3 ? '#FFC107' : 'inherit',
                            backgroundColor: student.attendance_status_id === 3 ? 'rgba(255, 193, 7, 0.1)' : 'transparent',
                            minWidth: { xs: 36, sm: 40 },
                            minHeight: { xs: 36, sm: 40 },
                          }}
                        >
                          <LateIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Half Day (H)">
                        <IconButton
                          size="small"
                          onClick={() => markAttendance(student.id, 4, index)}
                          disabled={student.is_saving}
                          sx={{
                            color: student.attendance_status_id === 4 ? '#17A2B8' : 'inherit',
                            backgroundColor: student.attendance_status_id === 4 ? 'rgba(23, 162, 184, 0.1)' : 'transparent',
                            minWidth: { xs: 36, sm: 40 },
                            minHeight: { xs: 36, sm: 40 },
                          }}
                        >
                          <HalfDayIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Excused (E)">
                        <IconButton
                          size="small"
                          onClick={() => markAttendance(student.id, 5, index)}
                          disabled={student.is_saving}
                          sx={{
                            color: student.attendance_status_id === 5 ? '#6C757D' : 'inherit',
                            backgroundColor: student.attendance_status_id === 5 ? 'rgba(108, 117, 125, 0.1)' : 'transparent',
                            minWidth: { xs: 36, sm: 40 },
                            minHeight: { xs: 36, sm: 40 },
                          }}
                        >
                          <ExcusedIcon sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }} />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                    {student.is_saving ? (
                      <CircularProgress size={20} />
                    ) : student.attendance_status_id ? (
                      <Chip
                        {...(getStatusIcon(student.attendance_status_id) && {
                          icon: getStatusIcon(student.attendance_status_id)
                        })}
                        label={student.attendance_status_description}
                        size="small"
                        sx={{
                          backgroundColor: student.attendance_status_color + '20',
                          color: student.attendance_status_color,
                          fontWeight: 600,
                          fontSize: { xs: '0.65rem', sm: '0.75rem' },
                        }}
                      />
                    ) : (
                      <Chip label="Not Marked" size="small" variant="outlined" sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }} />
                    )}
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, display: { xs: 'none', md: 'table-cell' } }}>
                    <TextField
                      size="small"
                      placeholder="Optional"
                      value={student.remarks || ''}
                      onChange={(e) => updateRemarks(index, e.target.value)}
                      onBlur={() => {
                        if (student.attendance_record_id && student.remarks !== undefined) {
                          // Save remarks if attendance already marked
                          attendanceService.updateAttendance(student.attendance_record_id, {
                            remarks: student.remarks || undefined,
                          });
                        }
                      }}
                      disabled={student.is_saving}
                      sx={{ width: '100%' }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
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

export default TeacherAttendance;

