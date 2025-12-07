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
  Alert,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Chip
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { studentLeaveAPI } from '../../services/api';
import { configurationService } from '../../services/configurationService';
import { formatDateForAPI } from '../../utils/dateUtils';

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
  half_day_period: string;
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
    half_day_period: 'Morning'
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
          half_day_period: selectedLeave.half_day_period || 'Morning'
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
          half_day_period: 'Morning'
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
        start_date: formatDateForAPI(formData.start_date),
        end_date: formatDateForAPI(formData.end_date),
        total_days: calculateTotalDays(),
        reason: formData.reason.trim(),
        parent_consent: formData.parent_consent,
        emergency_contact_name: formData.emergency_contact_name || null,
        emergency_contact_phone: formData.emergency_contact_phone || null,
        is_half_day: formData.is_half_day,
        half_day_period: formData.is_half_day ? formData.half_day_period : null
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
            sx: { maxHeight: '90vh' }
          }
        }}
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight="bold">
            {isViewMode ? 'Leave Request Details' : 'New Leave Request'}
          </Typography>
        </DialogTitle>
        <DialogContent dividers>
          <Box sx={{ pt: 2 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {/* Applicant Information Section */}
            {studentProfile && (
              <>
                <Typography variant="h6" color="primary" gutterBottom>
                  Applicant Information
                </Typography>
                <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
                  <Box flex={1}>
                    <Typography variant="body2" color="text.secondary">Name</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {studentProfile.first_name} {studentProfile.last_name} (Roll No: {studentProfile.roll_number})
                    </Typography>
                  </Box>
                  <Box flex={1}>
                    <Typography variant="body2" color="text.secondary">Class</Typography>
                    <Typography variant="body1">
                      {studentProfile.class_name}{studentProfile.section ? ` - ${studentProfile.section}` : ''}
                    </Typography>
                  </Box>
                </Box>
                <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
                  <Box flex={1}>
                    <Typography variant="body2" color="text.secondary">Admission No</Typography>
                    <Typography variant="body1">{studentProfile.admission_number}</Typography>
                  </Box>
                </Box>
              </>
            )}

            {/* Leave Details Section */}
            <Typography variant="h6" color="primary" gutterBottom sx={{ mt: 3 }}>
              Leave Details
            </Typography>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <Box flex={1}>
                <FormControl fullWidth required disabled={isViewMode} size="small">
                  <InputLabel>Leave Type</InputLabel>
                  <Select
                    value={formData.leave_type_id}
                    onChange={(e) => handleFieldChange('leave_type_id', e.target.value)}
                    label="Leave Type"
                  >
                    {configuration?.leave_types?.map((type: any) => (
                      <MenuItem key={type.id} value={type.id.toString()}>
                        {type.description || type.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
              <Box flex={1}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>Total Days</Typography>
                <Chip
                  label={`${totalDays} day${totalDays !== 1 ? 's' : ''}`}
                  color={totalDays > 0 ? 'primary' : 'default'}
                  size="small"
                  variant="outlined"
                />
              </Box>
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <DatePicker
                label="Start Date *"
                value={formData.start_date}
                onChange={(date) => handleFieldChange('start_date', date)}
                disabled={isViewMode}
                format="dd/MM/yyyy"
                slotProps={{
                  textField: {
                    fullWidth: true,
                    required: true,
                    size: 'small'
                  }
                }}
              />
              <DatePicker
                label="End Date *"
                value={formData.end_date}
                onChange={(date) => handleFieldChange('end_date', date)}
                disabled={isViewMode}
                format="dd/MM/yyyy"
                slotProps={{
                  textField: {
                    fullWidth: true,
                    required: true,
                    size: 'small'
                  }
                }}
              />
            </Box>

            {/* Half Day Option */}
            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <Box flex={1} display="flex" alignItems="center">
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.is_half_day}
                      onChange={(e) => handleFieldChange('is_half_day', e.target.checked)}
                      disabled={isViewMode}
                      size="small"
                    />
                  }
                  label="Half Day Leave"
                />
              </Box>
              {formData.is_half_day && (
                <Box flex={1}>
                  <FormControl fullWidth size="small" disabled={isViewMode}>
                    <InputLabel>Period</InputLabel>
                    <Select
                      value={formData.half_day_period}
                      onChange={(e) => handleFieldChange('half_day_period', e.target.value)}
                      label="Period"
                    >
                      <MenuItem value="Morning">Morning</MenuItem>
                      <MenuItem value="Afternoon">Afternoon</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
              )}
            </Box>

            <Box mb={3}>
              <TextField
                fullWidth
                size="small"
                label="Reason for Leave"
                multiline
                rows={3}
                value={formData.reason}
                onChange={(e) => handleFieldChange('reason', e.target.value)}
                required
                disabled={isViewMode}
                placeholder="Please provide a detailed reason for your leave request..."
              />
            </Box>

            {/* Parent/Guardian Information Section */}
            <Typography variant="h6" color="primary" gutterBottom>
              Parent/Guardian Information
            </Typography>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
              <Box flex={1} display="flex" alignItems="center">
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.parent_consent}
                      onChange={(e) => handleFieldChange('parent_consent', e.target.checked)}
                      disabled={isViewMode}
                      size="small"
                    />
                  }
                  label="Parent/Guardian consent obtained"
                />
              </Box>
            </Box>

            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={3}>
              <TextField
                fullWidth
                size="small"
                label="Emergency Contact Name"
                value={formData.emergency_contact_name}
                onChange={(e) => handleFieldChange('emergency_contact_name', e.target.value)}
                disabled={isViewMode}
                placeholder="Parent/Guardian name"
              />
              <TextField
                fullWidth
                size="small"
                label="Emergency Contact Phone"
                value={formData.emergency_contact_phone}
                onChange={(e) => handleFieldChange('emergency_contact_phone', e.target.value)}
                disabled={isViewMode}
                placeholder="Parent/Guardian phone number"
              />
            </Box>

            {/* View Mode: Request Status Section */}
            {isViewMode && selectedLeave && (
              <>
                <Typography variant="h6" color="primary" gutterBottom sx={{ mt: 3 }}>
                  Request Status
                </Typography>

                <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
                  <Box flex={1}>
                    <Typography variant="body2" color="text.secondary">Status</Typography>
                    <Chip
                      label={selectedLeave.leave_status_name}
                      color={
                        selectedLeave.leave_status_name?.toLowerCase() === 'approved' ? 'success' :
                        selectedLeave.leave_status_name?.toLowerCase() === 'rejected' ? 'error' : 'warning'
                      }
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="body2" color="text.secondary">Applied Date</Typography>
                    <Typography variant="body1">
                      {new Date(selectedLeave.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                </Box>

                {(selectedLeave.reviewer_name || selectedLeave.review_comments) && (
                  <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
                    {selectedLeave.reviewer_name && (
                      <Box flex={1}>
                        <Typography variant="body2" color="text.secondary">Reviewed By</Typography>
                        <Typography variant="body1">{selectedLeave.reviewer_name}</Typography>
                      </Box>
                    )}
                    {selectedLeave.review_comments && (
                      <Box flex={1}>
                        <Typography variant="body2" color="text.secondary">Review Comments</Typography>
                        <Typography variant="body1">{selectedLeave.review_comments}</Typography>
                      </Box>
                    )}
                  </Box>
                )}
              </>
            )}
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
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

export default StudentLeaveRequestDialog;
