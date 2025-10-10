import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Divider,
  IconButton
} from '@mui/material';
import {
  Close as CloseIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { ProfileData, ProfileUpdateData, ProfileConfiguration } from '../../types/profile';
import { authAPI } from '../../services/api';
import { configurationAPI } from '../../services/configurationService';

interface ProfileEditDialogProps {
  open: boolean;
  onClose: () => void;
  profileData: ProfileData;
  onProfileUpdated: (updatedProfile: ProfileData) => void;
}

const ProfileEditDialog: React.FC<ProfileEditDialogProps> = ({
  open,
  onClose,
  profileData,
  onProfileUpdated
}) => {
  const [formData, setFormData] = useState<ProfileUpdateData>({});
  const [configuration, setConfiguration] = useState<ProfileConfiguration | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (open && profileData) {
      initializeFormData();
      loadConfiguration();
    }
  }, [open, profileData]);

  const initializeFormData = () => {
    const initialData: ProfileUpdateData = {
      first_name: profileData.user_info.first_name,
      last_name: profileData.user_info.last_name,
      phone: profileData.user_info.phone || '',
    };

    if (profileData.student_profile) {
      initialData.student_profile = {
        date_of_birth: profileData.student_profile.date_of_birth || '',
        blood_group: profileData.student_profile.blood_group || '',
        phone: profileData.student_profile.phone || '',
        email: profileData.student_profile.email || '',
        address: profileData.student_profile.address || '',
        city: profileData.student_profile.city || '',
        state: profileData.student_profile.state || '',
        postal_code: profileData.student_profile.postal_code || '',
        country: profileData.student_profile.country || 'India',
        gender_id: profileData.student_profile.gender_id || 0,
        father_phone: profileData.student_profile.father_phone || '',
        father_email: profileData.student_profile.father_email || '',
        father_occupation: profileData.student_profile.father_occupation || '',
        mother_phone: profileData.student_profile.mother_phone || '',
        mother_email: profileData.student_profile.mother_email || '',
        mother_occupation: profileData.student_profile.mother_occupation || '',
        guardian_name: profileData.student_profile.guardian_name || '',
        guardian_phone: profileData.student_profile.guardian_phone || '',
        guardian_email: profileData.student_profile.guardian_email || '',
        guardian_relation: profileData.student_profile.guardian_relation || '',
      };
    }

    if (profileData.teacher_profile) {
      initialData.teacher_profile = {
        date_of_birth: profileData.teacher_profile.date_of_birth || '',
        phone: profileData.teacher_profile.phone || '',
        email: profileData.teacher_profile.email || '',
        address: profileData.teacher_profile.address || '',
        city: profileData.teacher_profile.city || '',
        state: profileData.teacher_profile.state || '',
        postal_code: profileData.teacher_profile.postal_code || '',
        country: profileData.teacher_profile.country || 'India',
        gender_id: profileData.teacher_profile.gender_id || 0,
        emergency_contact_name: profileData.teacher_profile.emergency_contact_name || '',
        emergency_contact_phone: profileData.teacher_profile.emergency_contact_phone || '',
        emergency_contact_relation: profileData.teacher_profile.emergency_contact_relation || '',
        department_id: profileData.teacher_profile.department_id || 0,
        position_id: profileData.teacher_profile.position_id || 0,
        qualification_id: profileData.teacher_profile.qualification_id || 0,
        employment_status_id: profileData.teacher_profile.employment_status_id || 0,
        experience_years: profileData.teacher_profile.experience_years || 0,
        subjects: profileData.teacher_profile.subjects || '',
      };
    }

    if (profileData.admin_profile) {
      initialData.admin_profile = {
        date_of_birth: profileData.admin_profile.date_of_birth || '',
        phone: profileData.admin_profile.phone || '',
        email: profileData.admin_profile.email || '',
        address: profileData.admin_profile.address || '',
        city: profileData.admin_profile.city || '',
        state: profileData.admin_profile.state || '',
        postal_code: profileData.admin_profile.postal_code || '',
        country: profileData.admin_profile.country || 'India',
        gender_id: profileData.admin_profile.gender_id || 0,
        department_id: profileData.admin_profile.department_id || 0,
        position_id: profileData.admin_profile.position_id || 0,
        qualification_id: profileData.admin_profile.qualification_id || 0,
        employment_status_id: profileData.admin_profile.employment_status_id || 0,
        experience_years: profileData.admin_profile.experience_years || 0,
      };
    }

    setFormData(initialData);
  };

  const loadConfiguration = async () => {
    try {
      setLoading(true);
      // Load appropriate configuration based on user role
      let configResponse;
      if (profileData.student_profile) {
        configResponse = await configurationAPI.getStudentManagementConfiguration();
      } else if (profileData.teacher_profile || profileData.admin_profile) {
        configResponse = await configurationAPI.getTeacherManagementConfiguration();
      }

      if (configResponse) {
        setConfiguration({
          genders: configResponse.data.genders || [],
          classes: configResponse.data.classes || [],
          session_years: configResponse.data.session_years || [],
          departments: configResponse.data.departments || [],
          positions: configResponse.data.positions || [],
          qualifications: configResponse.data.qualifications || [],
          employment_statuses: configResponse.data.employment_statuses || [],
        });
      }
    } catch (err: any) {
      console.error('Failed to load configuration:', err);
      setError('Failed to load form configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any, section?: string) => {
    setFormData(prev => {
      if (section) {
        const currentSection = prev[section as keyof ProfileUpdateData] as any || {};
        return {
          ...prev,
          [section]: {
            ...currentSection,
            [field]: value
          }
        };
      } else {
        return {
          ...prev,
          [field]: value
        };
      }
    });

    // Clear field error when user starts typing
    if (formErrors[field]) {
      setFormErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // Basic validation
    if (!formData.first_name?.trim()) {
      errors.first_name = 'First name is required';
    }
    if (!formData.last_name?.trim()) {
      errors.last_name = 'Last name is required';
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.student_profile?.email && !emailRegex.test(formData.student_profile.email)) {
      errors.student_email = 'Please enter a valid email address';
    }
    if (formData.teacher_profile?.email && !emailRegex.test(formData.teacher_profile.email)) {
      errors.teacher_email = 'Please enter a valid email address';
    }
    if (formData.admin_profile?.email && !emailRegex.test(formData.admin_profile.email)) {
      errors.admin_email = 'Please enter a valid email address';
    }

    // Phone validation (basic)
    const phoneRegex = /^\d{10}$/;
    if (formData.phone && !phoneRegex.test(formData.phone.replace(/\D/g, ''))) {
      errors.phone = 'Please enter a valid 10-digit phone number';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const response = await authAPI.updateProfile(formData);
      onProfileUpdated(response.data);
      onClose();
    } catch (err: any) {
      console.error('Failed to update profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    if (!saving) {
      onClose();
    }
  };

  if (loading) {
    return (
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">Edit Profile</Typography>
          <IconButton onClick={handleClose} disabled={saving}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Common Fields */}
        <Typography variant="h6" gutterBottom>
          Personal Information
        </Typography>
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="First Name"
              value={formData.first_name || ''}
              onChange={(e) => handleInputChange('first_name', e.target.value)}
              error={!!formErrors.first_name}
              helperText={formErrors.first_name}
              required
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Last Name"
              value={formData.last_name || ''}
              onChange={(e) => handleInputChange('last_name', e.target.value)}
              error={!!formErrors.last_name}
              helperText={formErrors.last_name}
              required
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Phone Number"
              value={formData.phone || ''}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              error={!!formErrors.phone}
              helperText={formErrors.phone}
            />
          </Grid>
        </Grid>

        {/* Role-specific fields will be added in the next part */}
        <Alert severity="info">
          Additional role-specific fields and full edit functionality will be completed in the next update.
        </Alert>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={saving}>
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={saving}
          startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProfileEditDialog;
