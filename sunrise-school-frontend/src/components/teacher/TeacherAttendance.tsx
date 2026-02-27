/**
 * Teacher Attendance Management Component
 *
 * Features:
 * - Fast attendance marking with auto-advance workflow
 * - Keyboard shortcuts (P=Present, A=Absent, L=Leave)
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
  EventBusy as LeaveIcon,
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
          statusId = 7; // Leave (status id 7 in database)
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

      // Handle validation errors from backend
      let errorMessage = 'Failed to load students';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // Pydantic validation errors
          errorMessage = error.response.data.detail.map((err: any) => err.msg).join(', ');
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        }
      }

      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error',
      });

      // Clear students on error
      setStudents([]);
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

      // Handle validation errors from backend
      let errorMessage = 'Failed to mark attendance';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // Pydantic validation errors
          errorMessage = error.response.data.detail.map((err: any) => err.msg).join(', ');
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        }
      }

      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error',
      });
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
                    <Box sx={{ display: 'flex', gap: { xs: 0.5, sm: 0.75 }, flexWrap: 'wrap' }}>
                      <Tooltip title="Present (P)">
                        <IconButton
                          size="small"
                          onClick={() => markAttendance(student.id, 1, index)}
                          disabled={student.is_saving}
                          sx={{
                            color: student.attendance_status_id === 1 ? '#28A745' : 'inherit',
                            backgroundColor: student.attendance_status_id === 1 ? 'rgba(40, 167, 69, 0.1)' : 'transparent',
                            minWidth: { xs: 40, sm: 44 },
                            minHeight: { xs: 40, sm: 44 },
                            transition: 'transform 0.2s ease-in-out, background-color 0.2s ease-in-out',
                            '&:hover': {
                              transform: 'scale(1.15)',
                              backgroundColor: student.attendance_status_id === 1 ? 'rgba(40, 167, 69, 0.2)' : 'rgba(0, 0, 0, 0.04)',
                            },
                          }}
                        >
                          <PresentIcon sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }} />
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
                            minWidth: { xs: 40, sm: 44 },
                            minHeight: { xs: 40, sm: 44 },
                            transition: 'transform 0.2s ease-in-out, background-color 0.2s ease-in-out',
                            '&:hover': {
                              transform: 'scale(1.15)',
                              backgroundColor: student.attendance_status_id === 2 ? 'rgba(220, 53, 69, 0.2)' : 'rgba(0, 0, 0, 0.04)',
                            },
                          }}
                        >
                          <AbsentIcon sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Leave (L)">
                        <IconButton
                          size="small"
                          onClick={() => markAttendance(student.id, 7, index)}
                          disabled={student.is_saving}
                          sx={{
                            color: student.attendance_status_id === 7 ? '#6F42C1' : 'inherit',
                            backgroundColor: student.attendance_status_id === 7 ? 'rgba(111, 66, 193, 0.1)' : 'transparent',
                            minWidth: { xs: 40, sm: 44 },
                            minHeight: { xs: 40, sm: 44 },
                            transition: 'transform 0.2s ease-in-out, background-color 0.2s ease-in-out',
                            '&:hover': {
                              transform: 'scale(1.15)',
                              backgroundColor: student.attendance_status_id === 7 ? 'rgba(111, 66, 193, 0.2)' : 'rgba(0, 0, 0, 0.04)',
                            },
                          }}
                        >
                          <LeaveIcon sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }} />
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

