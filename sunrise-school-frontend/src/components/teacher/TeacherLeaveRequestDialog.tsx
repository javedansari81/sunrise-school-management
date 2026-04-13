import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';

import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { leaveAPI } from '../../services/api';
import { configurationService } from '../../services/configurationService';
import { formatDateForAPI } from '../../utils/dateUtils';
import { SessionYearDropdown } from '../common/MetadataDropdown';

interface TeacherLeaveRequestDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  selectedLeave?: any;
  isViewMode?: boolean;
  teacherProfile?: any;
}

interface LeaveFormData {
  session_year_id: string;
  leave_type_id: string;
  start_date: Date | null;
  end_date: Date | null;
  reason: string;
}

const TeacherLeaveRequestDialog: React.FC<TeacherLeaveRequestDialogProps> = ({
  open,
  onClose,
  onSuccess,
  selectedLeave,
  isViewMode = false,
  teacherProfile
}) => {
  const { isLoaded, isLoading, error: configError } = useServiceConfiguration('leave-management');

  // Get configuration data from service
  const configuration = configurationService.getServiceConfiguration('leave-management');

  // Form state
  const [formData, setFormData] = useState<LeaveFormData>({
    session_year_id: '',
    leave_type_id: '',
    start_date: null,
    end_date: null,
    reason: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Initialize form data when dialog opens
  useEffect(() => {
    if (open) {
      const currentSessionYearId = configurationService.getCurrentSessionYearId();

      if (selectedLeave) {
        // Populate form with existing leave data for viewing or editing
        setFormData({
          session_year_id: selectedLeave.session_year_id?.toString() || currentSessionYearId?.toString() || '',
          leave_type_id: selectedLeave.leave_type_id?.toString() || '',
          start_date: selectedLeave.start_date ? new Date(selectedLeave.start_date) : null,
          end_date: selectedLeave.end_date ? new Date(selectedLeave.end_date) : null,
          reason: selectedLeave.reason || ''
        });
      } else {
        // Reset form for new leave request with default session year
        setFormData({
          session_year_id: currentSessionYearId?.toString() || '',
          leave_type_id: '',
          start_date: null,
          end_date: null,
          reason: ''
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
    if (!formData.session_year_id) return 'Please select a session year';
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
        session_year_id: parseInt(formData.session_year_id),
        leave_type_id: parseInt(formData.leave_type_id),
        start_date: formatDateForAPI(formData.start_date),
        end_date: formatDateForAPI(formData.end_date),
        total_days: calculateTotalDays(),
        reason: formData.reason.trim()
      };

      if (selectedLeave) {
        // Update existing leave request
        await leaveAPI.updateLeave(selectedLeave.id, leaveData);
      } else {
        // Create new leave request
        await leaveAPI.createMyLeaveRequest(leaveData);
      }

      onSuccess();
      onClose();
    } catch (error: any) {
      console.error(`Error ${selectedLeave ? 'updating' : 'creating'} leave request:`, error);
      setError(error.response?.data?.detail || `Error ${selectedLeave ? 'updating' : 'creating'} leave request`);
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
            {isViewMode ? 'Leave Request Details' : selectedLeave ? 'Edit Leave Request' : 'New Leave Request'}
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
            {teacherProfile && (
              <>
                <Typography variant="h6" color="primary" gutterBottom>
                  Applicant Information
                </Typography>
                <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mb={2}>
                  <Box flex={1}>
                    <Typography variant="body2" color="text.secondary">Name</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {teacherProfile.first_name} {teacherProfile.last_name}
                    </Typography>
                  </Box>
                  <Box flex={1}>
                    <Typography variant="body2" color="text.secondary">Employee ID</Typography>
                    <Typography variant="body1">{teacherProfile.employee_id}</Typography>
                  </Box>
                </Box>
              </>
            )}

            {/* Leave Details Section */}
            <Typography variant="h6" color="primary" gutterBottom sx={{ mt: 3 }}>
              Leave Details
            </Typography>

            {/* Session Year - First Field */}
            <Box mb={2}>
              <SessionYearDropdown
                value={formData.session_year_id}
                onChange={(value) => handleFieldChange('session_year_id', value)}
                required
                disabled={isViewMode}
                size="small"
                fullWidth
              />
            </Box>

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
              {loading
                ? (selectedLeave ? 'Updating...' : 'Submitting...')
                : (selectedLeave ? 'Update Request' : 'Submit Request')
              }
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default TeacherLeaveRequestDialog;
