/**
 * Session Progression System Component
 * Provides UI for SUPER_ADMIN to manage student academic progression between sessions
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  Alert,
  CircularProgress,
  Snackbar,
  Card,
  CardContent,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Checkbox,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import {
  TrendingUp,
  ArrowForward,
  Refresh,
  School,
  CheckCircle,
  Warning,
  History,
  Undo,
} from '@mui/icons-material';
import { useServiceConfiguration, useConfiguration } from '../../contexts/ConfigurationContext';
import { useAuth } from '../../contexts/AuthContext';
import { sessionProgressionAPI } from '../../services/sessionProgressionService';
import {
  StudentProgressionPreviewItem,
  StudentProgressionItem,
  BulkProgressionResponse,
  StudentProgressionHistoryItem,
  ProgressionAction,
  PROGRESSION_ACTION_IDS,
  HIGHEST_CLASS_ID,
} from '../../types/sessionProgression';

// Wizard steps
const STEPS = ['Select Sessions', 'Preview Students', 'Confirm Actions', 'View Results'];

const SessionProgressionSystem: React.FC = () => {
  const { user } = useAuth();
  const { getSessionYears, getClasses, getProgressionActions } = useConfiguration();

  // Wizard state
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Session selection
  const [fromSessionYearId, setFromSessionYearId] = useState<number | ''>('');
  const [toSessionYearId, setToSessionYearId] = useState<number | ''>('');
  const [selectedClassIds, setSelectedClassIds] = useState<number[]>([]);

  // Preview data
  const [previewStudents, setPreviewStudents] = useState<StudentProgressionPreviewItem[]>([]);
  const [selectedStudents, setSelectedStudents] = useState<Map<number, StudentProgressionItem>>(new Map());

  // Results
  const [progressionResults, setProgressionResults] = useState<BulkProgressionResponse | null>(null);

  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  // Get metadata from configuration
  const sessionYears = getSessionYears();
  const classes = getClasses();
  const progressionActions: ProgressionAction[] = getProgressionActions();

  // Check if user is SUPER_ADMIN (user_type = 'SUPER_ADMIN')
  const isSuperAdmin = user?.user_type?.toUpperCase() === 'SUPER_ADMIN';

  // Get action color from metadata
  const getActionColor = (actionId: number): string => {
    const action = progressionActions.find((a: ProgressionAction) => a.id === actionId);
    return action?.color_code || '#9E9E9E';
  };

  // Get action name from metadata (shows description for better readability)
  const getActionName = (actionId: number): string => {
    const action = progressionActions.find((a: ProgressionAction) => a.id === actionId);
    return action?.description || action?.name || 'Unknown';
  };

  // Preview students for progression
  const handlePreview = async () => {
    if (!fromSessionYearId || !toSessionYearId) {
      setError('Please select both source and target session years');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await sessionProgressionAPI.previewEligibleStudents({
        from_session_year_id: Number(fromSessionYearId),
        to_session_year_id: Number(toSessionYearId),
        class_ids: selectedClassIds.length > 0 ? selectedClassIds : undefined,
      });
      
      setPreviewStudents(response.students);
      
      // Initialize selected students with default suggested actions
      const newSelected = new Map<number, StudentProgressionItem>();
      response.students.forEach(student => {
        newSelected.set(student.student_id, {
          student_id: student.student_id,
          progression_action_id: student.suggested_action_id,
          target_class_id: student.target_class_id,
        });
      });
      setSelectedStudents(newSelected);
      
      setActiveStep(1);
    } catch (err: any) {
      setError(err.message || 'Failed to preview students');
    } finally {
      setLoading(false);
    }
  };

  // Handle student selection toggle
  const handleStudentToggle = (studentId: number) => {
    const newSelected = new Map(selectedStudents);
    if (newSelected.has(studentId)) {
      newSelected.delete(studentId);
    } else {
      const student = previewStudents.find(s => s.student_id === studentId);
      if (student) {
        newSelected.set(studentId, {
          student_id: studentId,
          progression_action_id: student.suggested_action_id,
          target_class_id: student.target_class_id,
        });
      }
    }
    setSelectedStudents(newSelected);
  };

  // Calculate target class based on action
  // Classes are sorted by sort_order, so we can use array index for navigation
  const calculateTargetClass = (currentClassId: number, actionId: number): { id: number; name: string } | null => {
    const sortedClasses = classes.filter(c => c.is_active);
    const currentIndex = sortedClasses.findIndex(c => c.id === currentClassId);

    if (currentIndex === -1) return null;

    switch (actionId) {
      case PROGRESSION_ACTION_IDS.PROMOTED:
        // Next class (if exists)
        if (currentIndex < sortedClasses.length - 1) {
          const nextClass = sortedClasses[currentIndex + 1];
          return { id: nextClass.id, name: nextClass.description || nextClass.name };
        }
        // Already at highest class, stay in same class
        return { id: currentClassId, name: sortedClasses[currentIndex].description || sortedClasses[currentIndex].name };

      case PROGRESSION_ACTION_IDS.DEMOTED:
        // Previous class (if exists)
        if (currentIndex > 0) {
          const prevClass = sortedClasses[currentIndex - 1];
          return { id: prevClass.id, name: prevClass.description || prevClass.name };
        }
        // Already at lowest class, stay in same class
        return { id: currentClassId, name: sortedClasses[currentIndex].description || sortedClasses[currentIndex].name };

      case PROGRESSION_ACTION_IDS.RETAINED:
      default:
        // Same class
        return { id: currentClassId, name: sortedClasses[currentIndex].description || sortedClasses[currentIndex].name };
    }
  };

  // Get target class name for display
  const getTargetClassName = (studentId: number): string => {
    const selected = selectedStudents.get(studentId);
    if (!selected?.target_class_id) return '-';

    const targetClass = classes.find(c => c.id === selected.target_class_id);
    return targetClass?.description || targetClass?.name || '-';
  };

  // Handle action change for a student
  const handleActionChange = (studentId: number, actionId: number) => {
    const newSelected = new Map(selectedStudents);
    const current = newSelected.get(studentId);

    if (current) {
      // Find the student to get their current class
      const student = previewStudents.find(s => s.student_id === studentId);
      if (student) {
        // Calculate new target class based on action
        const targetClass = calculateTargetClass(student.current_class_id, actionId);
        newSelected.set(studentId, {
          ...current,
          progression_action_id: actionId,
          target_class_id: targetClass?.id || student.current_class_id,
        });
      } else {
        // Fallback if student not found
        newSelected.set(studentId, { ...current, progression_action_id: actionId });
      }
    }
    setSelectedStudents(newSelected);
  };

  // Execute bulk progression
  const handleBulkProgress = async () => {
    if (selectedStudents.size === 0) {
      setError('Please select at least one student to progress');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await sessionProgressionAPI.bulkProgressStudents({
        from_session_year_id: Number(fromSessionYearId),
        to_session_year_id: Number(toSessionYearId),
        students: Array.from(selectedStudents.values()),
      });

      setProgressionResults(response);
      setActiveStep(3);
      setSuccess(`Successfully processed ${response.successful_count} students`);
    } catch (err: any) {
      setError(err.message || 'Failed to progress students');
    } finally {
      setLoading(false);
    }
  };

  // Reset wizard
  const handleReset = () => {
    setActiveStep(0);
    setFromSessionYearId('');
    setToSessionYearId('');
    setSelectedClassIds([]);
    setPreviewStudents([]);
    setSelectedStudents(new Map());
    setProgressionResults(null);
    setError(null);
    setSuccess(null);
  };

  // Render session selection step
  const renderSessionSelection = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <School sx={{ mr: 1, verticalAlign: 'middle' }} />
          Select Academic Sessions
        </Typography>
        <Grid container spacing={2} sx={{ mt: 1 }} alignItems="center">
          <Grid size={{ xs: 12, md: 5 }}>
            <FormControl fullWidth size="small">
              <InputLabel>From Session Year</InputLabel>
              <Select
                value={fromSessionYearId}
                label="From Session Year"
                onChange={(e) => setFromSessionYearId(e.target.value as number)}
              >
                {sessionYears.map(sy => (
                  <MenuItem key={sy.id} value={sy.id}>{sy.description || sy.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 2 }} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ArrowForward sx={{ fontSize: 28, color: 'primary.main' }} />
          </Grid>
          <Grid size={{ xs: 12, md: 5 }}>
            <FormControl fullWidth size="small">
              <InputLabel>To Session Year</InputLabel>
              <Select
                value={toSessionYearId}
                label="To Session Year"
                onChange={(e) => setToSessionYearId(e.target.value as number)}
              >
                {sessionYears.map(sy => (
                  <MenuItem key={sy.id} value={sy.id}>{sy.description || sy.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 5 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Filter by Classes (Optional)</InputLabel>
              <Select
                multiple
                value={selectedClassIds}
                label="Filter by Classes (Optional)"
                onChange={(e) => setSelectedClassIds(e.target.value as number[])}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {(selected as number[]).map(id => {
                      const cls = classes.find(c => c.id === id);
                      return <Chip key={id} label={cls?.description || cls?.name || id} size="small" />;
                    })}
                  </Box>
                )}
                MenuProps={{
                  PaperProps: {
                    style: {
                      maxHeight: 300,
                    },
                  },
                }}
              >
                {classes.map(cls => (
                  <MenuItem key={cls.id} value={cls.id}>
                    <Checkbox checked={selectedClassIds.indexOf(cls.id) > -1} size="small" />
                    {cls.description || cls.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, md: 7 }} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              onClick={handlePreview}
              disabled={!fromSessionYearId || !toSessionYearId || loading}
              endIcon={loading ? <CircularProgress size={20} /> : <ArrowForward />}
            >
              Preview Students
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  // Render student preview step
  const renderStudentPreview = () => (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Preview: {previewStudents.length} Students Found
          </Typography>
          <Chip
            label={`${selectedStudents.size} Selected`}
            color="primary"
          />
        </Box>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={selectedStudents.size > 0 && selectedStudents.size < previewStudents.length}
                    checked={selectedStudents.size === previewStudents.length}
                    onChange={() => {
                      if (selectedStudents.size === previewStudents.length) {
                        setSelectedStudents(new Map());
                      } else {
                        const newSelected = new Map<number, StudentProgressionItem>();
                        previewStudents.forEach(s => {
                          newSelected.set(s.student_id, {
                            student_id: s.student_id,
                            progression_action_id: s.suggested_action_id,
                            target_class_id: s.target_class_id,
                          });
                        });
                        setSelectedStudents(newSelected);
                      }
                    }}
                  />
                </TableCell>
                <TableCell>Admission No</TableCell>
                <TableCell>Student Name</TableCell>
                <TableCell>Current Class</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Target Class</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {previewStudents
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map(student => (
                  <TableRow key={student.student_id} hover>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedStudents.has(student.student_id)}
                        onChange={() => handleStudentToggle(student.student_id)}
                      />
                    </TableCell>
                    <TableCell>{student.admission_number}</TableCell>
                    <TableCell>{student.first_name} {student.last_name}</TableCell>
                    <TableCell>{student.current_class_name}</TableCell>
                    <TableCell>
                      <Select
                        size="small"
                        value={selectedStudents.get(student.student_id)?.progression_action_id || student.suggested_action_id}
                        onChange={(e) => handleActionChange(student.student_id, e.target.value as number)}
                        disabled={!selectedStudents.has(student.student_id)}
                        sx={{ minWidth: 140 }}
                      >
                        {progressionActions.map(action => (
                          <MenuItem key={action.id} value={action.id}>
                            {action.description || action.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </TableCell>
                    <TableCell>{getTargetClassName(student.student_id)}</TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={previewStudents.length}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
          <Button onClick={() => setActiveStep(0)}>Back</Button>
          <Button
            variant="contained"
            onClick={() => setActiveStep(2)}
            disabled={selectedStudents.size === 0}
            endIcon={<ArrowForward />}
          >
            Review & Confirm
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  // Render confirmation step
  const renderConfirmation = () => {
    // Group students by action
    const actionCounts: Record<number, number> = {};
    selectedStudents.forEach(student => {
      const actionId = student.progression_action_id;
      actionCounts[actionId] = (actionCounts[actionId] || 0) + 1;
    });

    return (
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <CheckCircle sx={{ mr: 1, verticalAlign: 'middle', color: 'success.main' }} />
            Confirm Progression
          </Typography>
          <Typography variant="subtitle1" gutterBottom>Summary by Action:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
            {Object.entries(actionCounts).map(([actionId, count]) => (
              <Chip
                key={actionId}
                label={`${getActionName(Number(actionId))}: ${count}`}
                sx={{ bgcolor: getActionColor(Number(actionId)), color: 'white' }}
              />
            ))}
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button onClick={() => setActiveStep(1)}>Back</Button>
            <Button
              variant="contained"
              color="success"
              onClick={handleBulkProgress}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <TrendingUp />}
            >
              Execute Progression
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  };

  // Render results step
  const renderResults = () => (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {progressionResults?.successful_count === progressionResults?.total_processed ? (
            <CheckCircle sx={{ mr: 1, verticalAlign: 'middle', color: 'success.main' }} />
          ) : (
            <Warning sx={{ mr: 1, verticalAlign: 'middle', color: 'warning.main' }} />
          )}
          Progression Results
        </Typography>
        {progressionResults && (
          <>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid size={{ xs: 4 }}>
                <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light' }}>
                  <Typography variant="h4" color="primary.contrastText">
                    {progressionResults.total_processed}
                  </Typography>
                  <Typography color="primary.contrastText">Total Processed</Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 4 }}>
                <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light' }}>
                  <Typography variant="h4" color="success.contrastText">
                    {progressionResults.successful_count}
                  </Typography>
                  <Typography color="success.contrastText">Successful</Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 4 }}>
                <Paper sx={{ p: 2, textAlign: 'center', bgcolor: progressionResults.failed_count > 0 ? 'error.light' : 'grey.200' }}>
                  <Typography variant="h4" color={progressionResults.failed_count > 0 ? 'error.contrastText' : 'text.secondary'}>
                    {progressionResults.failed_count}
                  </Typography>
                  <Typography color={progressionResults.failed_count > 0 ? 'error.contrastText' : 'text.secondary'}>Failed</Typography>
                </Paper>
              </Grid>
            </Grid>
            <Alert severity="info" sx={{ mb: 2 }}>
              Batch ID: {progressionResults.batch_id} (Save this for rollback if needed)
            </Alert>
          </>
        )}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="contained" onClick={handleReset} startIcon={<Refresh />}>
            Start New Progression
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  // If not SUPER_ADMIN, show access denied
  if (!isSuperAdmin) {
    return (
      <Box sx={{ width: '100%' }}>
        <Alert severity="error">
          Access Denied: Only SUPER_ADMIN users can access the Session Progression feature.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {activeStep === 0 && renderSessionSelection()}
      {activeStep === 1 && renderStudentPreview()}
      {activeStep === 2 && renderConfirmation()}
      {activeStep === 3 && renderResults()}

      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
        message={success}
      />
    </Box>
  );
};

export default SessionProgressionSystem;

