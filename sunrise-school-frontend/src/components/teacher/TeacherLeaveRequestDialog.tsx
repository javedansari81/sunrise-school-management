import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Box,
  IconButton,
  CircularProgress,
  Alert,
  Divider,
  Chip
} from '@mui/material';

import {
  Close as CloseIcon,
  CalendarToday as CalendarIcon,
  Person as PersonIcon,
  Work as WorkIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useConfiguration } from '../../contexts/ConfigurationContext';
import { leaveAPI, teachersAPI } from '../../services/api';

interface TeacherLeaveRequestDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  selectedLeave?: any;
  isViewMode?: boolean;
  teacherProfile?: any;
}

interface LeaveFormData {
  leave_type_id: string;
  start_date: Date | null;
  end_date: Date | null;
  reason: string;
  substitute_teacher_id: string;
  substitute_arranged: boolean;
  medical_certificate_url: string;
  supporting_document_url: string;
}

const TeacherLeaveRequestDialog: React.FC<TeacherLeaveRequestDialogProps> = ({
  open,
  onClose,
  onSuccess,
  selectedLeave,
  isViewMode = false,
  teacherProfile
}) => {
  const { getServiceConfiguration } = useConfiguration();
  const configuration = getServiceConfiguration('leave-management');

  // Form state
  const [formData, setFormData] = useState<LeaveFormData>({
    leave_type_id: '',
    start_date: null,
    end_date: null,
    reason: '',
    substitute_teacher_id: '',
    substitute_arranged: false,
    medical_certificate_url: '',
    supporting_document_url: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [teachers, setTeachers] = useState<any[]>([]);
  const [loadingTeachers, setLoadingTeachers] = useState(false);

  // Load teachers for substitute selection
  useEffect(() => {
    const loadTeachers = async () => {
      if (!open) return;
      
      try {
        setLoadingTeachers(true);
        const response = await teachersAPI.getTeachers();
        setTeachers(response.data?.teachers || []);
      } catch (error) {
        console.error('Error loading teachers:', error);
      } finally {
        setLoadingTeachers(false);
      }
    };

    loadTeachers();
  }, [open]);

  // Initialize form data when dialog opens
  useEffect(() => {
    if (open) {
      if (selectedLeave && isViewMode) {
        // Populate form with existing leave data for viewing
        setFormData({
          leave_type_id: selectedLeave.leave_type_id?.toString() || '',
          start_date: selectedLeave.start_date ? new Date(selectedLeave.start_date) : null,
          end_date: selectedLeave.end_date ? new Date(selectedLeave.end_date) : null,
          reason: selectedLeave.reason || '',
          substitute_teacher_id: selectedLeave.substitute_teacher_id?.toString() || '',
          substitute_arranged: selectedLeave.substitute_arranged || false,
          medical_certificate_url: selectedLeave.medical_certificate_url || '',
          supporting_document_url: selectedLeave.supporting_document_url || ''
        });
      } else {
        // Reset form for new leave request
        setFormData({
          leave_type_id: '',
          start_date: null,
          end_date: null,
          reason: '',
          substitute_teacher_id: '',
          substitute_arranged: false,
          medical_certificate_url: '',
          supporting_document_url: ''
        });
      }
      setError('');
    }
  }, [open, selectedLeave, isViewMode]);

  // Handle form field changes
  const handleFieldChange = (field: keyof LeaveFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Calculate total days
  const calculateTotalDays = () => {
    if (formData.start_date && formData.end_date) {
      const diffTime = Math.abs(formData.end_date.getTime() - formData.start_date.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
      return diffDays;
    }
    return 0;
  };

  // Validate form
  const validateForm = () => {
    if (!formData.leave_type_id) return 'Please select a leave type';
    if (!formData.start_date) return 'Please select start date';
    if (!formData.end_date) return 'Please select end date';
    if (!formData.reason.trim()) return 'Please provide a reason for leave';
    if (formData.start_date > formData.end_date) return 'End date must be after start date';
    return '';
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (isViewMode) {
      onClose();
      return;
    }

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    if (!teacherProfile) {
      setError('Teacher profile not found');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const leaveData = {
        leave_type_id: parseInt(formData.leave_type_id),
        start_date: formData.start_date?.toISOString().split('T')[0],
        end_date: formData.end_date?.toISOString().split('T')[0],
        total_days: calculateTotalDays(),
        reason: formData.reason.trim(),
        substitute_teacher_id: formData.substitute_teacher_id ? parseInt(formData.substitute_teacher_id) : null,
        substitute_arranged: formData.substitute_arranged,
        medical_certificate_url: formData.medical_certificate_url || null,
        supporting_document_url: formData.supporting_document_url || null
      };

      await leaveAPI.createMyLeaveRequest(leaveData);
      onSuccess();
      onClose();
    } catch (error: any) {
      console.error('Error creating leave request:', error);
      setError(error.response?.data?.detail || 'Error creating leave request');
    } finally {
      setLoading(false);
    }
  };

  // Handle close
  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  const totalDays = calculateTotalDays();

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Dialog
        open={open}
        onClose={handleClose}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            maxHeight: '90vh'
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          pb: 1
        }}>
          <Box display="flex" alignItems="center" gap={1}>
            <CalendarIcon color="primary" />
            <Typography variant="h6">
              {isViewMode ? 'Leave Request Details' : 'New Leave Request'}
            </Typography>
          </Box>
          <IconButton onClick={handleClose} disabled={loading}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent dividers>
          {/* Teacher Info */}
          {teacherProfile && (
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <PersonIcon color="primary" fontSize="small" />
                <Typography variant="subtitle2" color="primary">
                  Applicant Information
                </Typography>
              </Box>
              <Typography variant="body2">
                <strong>{teacherProfile.first_name} {teacherProfile.last_name}</strong> ({teacherProfile.employee_id})
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {teacherProfile.position} - {teacherProfile.department}
              </Typography>
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Leave Type */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth required disabled={isViewMode}>
                <InputLabel>Leave Type</InputLabel>
                <Select
                  value={formData.leave_type_id}
                  onChange={(e) => handleFieldChange('leave_type_id', e.target.value)}
                  label="Leave Type"
                >
                  {configuration?.leave_types?.map((type: any) => (
                    <MenuItem key={type.id} value={type.id.toString()}>
                      {type.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Total Days Display */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <Box sx={{ pt: 2 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Total Days
                </Typography>
                <Chip
                  label={`${totalDays} day${totalDays !== 1 ? 's' : ''}`}
                  color={totalDays > 0 ? 'primary' : 'default'}
                  variant="outlined"
                />
              </Box>
            </Grid>

            {/* Start Date */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <DatePicker
                label="Start Date *"
                value={formData.start_date}
                onChange={(date) => handleFieldChange('start_date', date)}
                disabled={isViewMode}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    required: true
                  }
                }}
              />
            </Grid>

            {/* End Date */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <DatePicker
                label="End Date *"
                value={formData.end_date}
                onChange={(date) => handleFieldChange('end_date', date)}
                disabled={isViewMode}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    required: true
                  }
                }}
              />
            </Grid>

            {/* Reason */}
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Reason for Leave"
                multiline
                rows={3}
                value={formData.reason}
                onChange={(e) => handleFieldChange('reason', e.target.value)}
                required
                disabled={isViewMode}
                placeholder="Please provide a detailed reason for your leave request..."
              />
            </Grid>

            {/* Substitute Teacher */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth disabled={isViewMode || loadingTeachers}>
                <InputLabel>Substitute Teacher</InputLabel>
                <Select
                  value={formData.substitute_teacher_id}
                  onChange={(e) => handleFieldChange('substitute_teacher_id', e.target.value)}
                  label="Substitute Teacher"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {teachers
                    .filter(teacher => teacher.id !== teacherProfile?.id) // Exclude self
                    .map((teacher: any) => (
                    <MenuItem key={teacher.id} value={teacher.id.toString()}>
                      {teacher.first_name} {teacher.last_name} ({teacher.employee_id})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Substitute Arranged Checkbox */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.substitute_arranged}
                    onChange={(e) => handleFieldChange('substitute_arranged', e.target.checked)}
                    disabled={isViewMode}
                  />
                }
                label="Substitute arrangement confirmed"
              />
            </Grid>

            {/* Supporting Documents */}
            <Grid size={{ xs: 12 }}>
              <Divider sx={{ my: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  Supporting Documents (Optional)
                </Typography>
              </Divider>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Medical Certificate URL"
                value={formData.medical_certificate_url}
                onChange={(e) => handleFieldChange('medical_certificate_url', e.target.value)}
                disabled={isViewMode}
                placeholder="https://..."
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Supporting Document URL"
                value={formData.supporting_document_url}
                onChange={(e) => handleFieldChange('supporting_document_url', e.target.value)}
                disabled={isViewMode}
                placeholder="https://..."
              />
            </Grid>

            {/* View Mode: Additional Details */}
            {isViewMode && selectedLeave && (
              <>
                <Grid size={{ xs: 12 }}>
                  <Divider sx={{ my: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      Request Status
                    </Typography>
                  </Divider>
                </Grid>

                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Status
                  </Typography>
                  <Chip
                    label={selectedLeave.leave_status_name}
                    color={
                      selectedLeave.leave_status_name?.toLowerCase() === 'approved' ? 'success' :
                      selectedLeave.leave_status_name?.toLowerCase() === 'rejected' ? 'error' : 'warning'
                    }
                    variant="outlined"
                  />
                </Grid>

                <Grid size={{ xs: 12, sm: 6 }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Applied Date
                  </Typography>
                  <Typography variant="body2">
                    {new Date(selectedLeave.created_at).toLocaleDateString()}
                  </Typography>
                </Grid>

                {selectedLeave.reviewer_name && (
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Reviewed By
                    </Typography>
                    <Typography variant="body2">
                      {selectedLeave.reviewer_name}
                    </Typography>
                  </Grid>
                )}

                {selectedLeave.review_comments && (
                  <Grid size={{ xs: 12 }}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Review Comments
                    </Typography>
                    <Typography variant="body2">
                      {selectedLeave.review_comments}
                    </Typography>
                  </Grid>
                )}
              </>
            )}
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button onClick={handleClose} disabled={loading}>
            {isViewMode ? 'Close' : 'Cancel'}
          </Button>
          {!isViewMode && (
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={16} /> : null}
            >
              {loading ? 'Submitting...' : 'Submit Request'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default TeacherLeaveRequestDialog;
