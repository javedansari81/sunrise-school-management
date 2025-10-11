import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  IconButton,
  Alert,
  Grid,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import {
  Close as CloseIcon,
  CalendarToday as CalendarIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { studentLeaveAPI } from '../../services/api';
import { configurationService } from '../../services/configurationService';
import { dialogStyles } from '../../styles/dialogTheme';

interface StudentLeaveRequestDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  selectedLeave?: any;
  isViewMode?: boolean;
  studentProfile?: any;
}

interface LeaveFormData {
  leave_type_id: string;
  start_date: Date | null;
  end_date: Date | null;
  reason: string;
  parent_consent: boolean;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  is_half_day: boolean;
  half_day_session: string;
}

const StudentLeaveRequestDialog: React.FC<StudentLeaveRequestDialogProps> = ({
  open,
  onClose,
  onSuccess,
  selectedLeave,
  isViewMode = false,
  studentProfile
}) => {
  const { isLoaded, isLoading, error: configError } = useServiceConfiguration('leave-management');

  // Get configuration data from service
  const configuration = configurationService.getServiceConfiguration('leave-management');

  // Form state
  const [formData, setFormData] = useState<LeaveFormData>({
    leave_type_id: '',
    start_date: null,
    end_date: null,
    reason: '',
    parent_consent: false,
    emergency_contact_name: '',
    emergency_contact_phone: '',
    is_half_day: false,
    half_day_session: 'morning'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
          parent_consent: selectedLeave.parent_consent || false,
          emergency_contact_name: selectedLeave.emergency_contact_name || '',
          emergency_contact_phone: selectedLeave.emergency_contact_phone || '',
          is_half_day: selectedLeave.is_half_day || false,
          half_day_session: selectedLeave.half_day_session || 'morning'
        });
      } else {
        // Reset form for new request
        setFormData({
          leave_type_id: '',
          start_date: null,
          end_date: null,
          reason: '',
          parent_consent: false,
          emergency_contact_name: '',
          emergency_contact_phone: '',
          is_half_day: false,
          half_day_session: 'morning'
        });
      }
      setError('');
    }
  }, [open, selectedLeave, isViewMode]);

  const handleFieldChange = (field: keyof LeaveFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculateTotalDays = () => {
    if (!formData.start_date || !formData.end_date) return 0;
    const diffTime = Math.abs(formData.end_date.getTime() - formData.start_date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    return formData.is_half_day ? 0.5 : diffDays;
  };

  const handleSubmit = async () => {
    if (isViewMode) return;

    // Validation
    if (!formData.leave_type_id || !formData.start_date || !formData.end_date || !formData.reason.trim()) {
      setError('Please fill in all required fields');
      return;
    }

    if (formData.start_date > formData.end_date) {
      setError('Start date cannot be after end date');
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
        parent_consent: formData.parent_consent,
        emergency_contact_name: formData.emergency_contact_name || null,
        emergency_contact_phone: formData.emergency_contact_phone || null,
        is_half_day: formData.is_half_day,
        half_day_session: formData.is_half_day ? formData.half_day_session : null
      };

      await studentLeaveAPI.createMyLeaveRequest(leaveData);
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
        slotProps={{
          paper: {
            sx: dialogStyles.paper
          }
        }}
      >
        <DialogTitle sx={dialogStyles.title}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CalendarIcon sx={{ fontSize: 28 }} />
            <Typography sx={dialogStyles.titleText}>
              {isViewMode ? 'Leave Request Details' : 'New Leave Request'}
            </Typography>
          </Box>
          <IconButton onClick={handleClose} disabled={loading} sx={dialogStyles.closeButton}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent sx={dialogStyles.content} dividers>
          {/* Student Info */}
          {studentProfile && (
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <PersonIcon color="primary" fontSize="small" />
                <Typography variant="subtitle2" color="primary">
                  Student Information
                </Typography>
              </Box>
              <Typography variant="body2">
                <strong>{studentProfile.first_name} {studentProfile.last_name}</strong> (Roll: {studentProfile.roll_number})
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Class: {studentProfile.current_class} {studentProfile.section && `- ${studentProfile.section}`}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Admission No: {studentProfile.admission_number}
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

            {/* Half Day Option */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.is_half_day}
                    onChange={(e) => handleFieldChange('is_half_day', e.target.checked)}
                    disabled={isViewMode}
                  />
                }
                label="Half Day Leave"
              />
              {formData.is_half_day && (
                <FormControl fullWidth sx={{ mt: 1 }} disabled={isViewMode}>
                  <InputLabel>Session</InputLabel>
                  <Select
                    value={formData.half_day_session}
                    onChange={(e) => handleFieldChange('half_day_session', e.target.value)}
                    label="Session"
                  >
                    <MenuItem value="morning">Morning</MenuItem>
                    <MenuItem value="afternoon">Afternoon</MenuItem>
                  </Select>
                </FormControl>
              )}
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

            {/* Total Days Display */}
            {totalDays > 0 && (
              <Grid size={{ xs: 12 }}>
                <Alert severity="info">
                  Total Days: {totalDays} {totalDays === 1 ? 'day' : 'days'}
                </Alert>
              </Grid>
            )}

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

            {/* Parent Consent */}
            <Grid size={{ xs: 12 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.parent_consent}
                    onChange={(e) => handleFieldChange('parent_consent', e.target.checked)}
                    disabled={isViewMode}
                  />
                }
                label="Parent/Guardian consent obtained"
              />
            </Grid>

            {/* Emergency Contact */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Emergency Contact Name"
                value={formData.emergency_contact_name}
                onChange={(e) => handleFieldChange('emergency_contact_name', e.target.value)}
                disabled={isViewMode}
                placeholder="Parent/Guardian name"
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Emergency Contact Phone"
                value={formData.emergency_contact_phone}
                onChange={(e) => handleFieldChange('emergency_contact_phone', e.target.value)}
                disabled={isViewMode}
                placeholder="Parent/Guardian phone number"
              />
            </Grid>

            {/* View Mode Additional Info */}
            {isViewMode && selectedLeave && (
              <>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Request Status
                  </Typography>
                  <Typography variant="body2">
                    Status: <strong>{selectedLeave.leave_status_name}</strong>
                  </Typography>
                  {selectedLeave.reviewer_name && (
                    <Typography variant="body2">
                      Reviewed by: {selectedLeave.reviewer_name}
                    </Typography>
                  )}
                  {selectedLeave.review_comments && (
                    <Typography variant="body2">
                      Comments: {selectedLeave.review_comments}
                    </Typography>
                  )}
                </Grid>
              </>
            )}
          </Grid>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            {isViewMode ? 'Close' : 'Cancel'}
          </Button>
          {!isViewMode && (
            <Button 
              onClick={handleSubmit} 
              variant="contained" 
              disabled={loading}
            >
              {loading ? 'Submitting...' : 'Submit Request'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default StudentLeaveRequestDialog;
