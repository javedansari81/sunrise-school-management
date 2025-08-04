import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  TextField,
  Button,
  Divider,
  Chip,
  Grid,
  Alert,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Email as EmailIcon,
  Phone as PhoneIcon,
  Work as WorkIcon,
  Person as PersonIcon,
  Home as HomeIcon,
  ContactPhone as ContactPhoneIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  CalendarToday as CalendarIcon,
  School as SchoolIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { teachersAPI } from '../services/api';

interface TeacherProfileData {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender_name: string;
  phone: string;
  email: string;
  aadhar_no: string;
  address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relation: string;
  position: string;
  department: string;
  qualification_name: string;
  employment_status_name: string;
  experience_years: number;
  joining_date: string;
  salary: number;
  is_active: boolean;
}

const TeacherProfile: React.FC = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState<TeacherProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editData, setEditData] = useState<any>({});

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      // Assuming there's a teacher profile endpoint similar to student
      const response = await teachersAPI.getMyProfile();

      // Validate response data
      if (response.data && typeof response.data === 'object' && !Array.isArray(response.data)) {
        setProfileData(response.data);
      } else {
        throw new Error('Invalid profile data received from server');
      }
    } catch (err: any) {
      console.error('Error fetching teacher profile:', err);
      console.error('Error response data:', err.response?.data);

      // Handle different error response formats
      let errorMessage = 'Failed to load profile';
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data)) {
          // Handle validation errors array
          errorMessage = err.response.data.map((error: any) => error.msg || error.message || 'Validation error').join(', ');
        } else {
          errorMessage = 'An error occurred while loading profile';
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setEditData((prev: any) => ({ ...prev, [field]: value }));
  };

  const getInitials = () => {
    if (!profileData || !profileData.first_name || !profileData.last_name) return 'T';
    return `${profileData.first_name.charAt(0)}${profileData.last_name.charAt(0)}`;
  };

  const getStatusColor = () => {
    return profileData?.is_active ? 'success' : 'error';
  };

  // Helper function to safely render values
  const safeRender = (value: any, fallback: string = 'Not provided'): string => {
    if (value === null || value === undefined) return fallback;
    if (typeof value === 'string') return value;
    if (typeof value === 'number') return value.toString();
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    return fallback;
  };

  const handleEdit = () => {
    if (profileData) {
      setEditData({
        phone: profileData.phone,
        email: profileData.email,
        aadhar_no: profileData.aadhar_no,
        address: profileData.address,
        city: profileData.city,
        state: profileData.state,
        postal_code: profileData.postal_code,
        emergency_contact_name: profileData.emergency_contact_name,
        emergency_contact_phone: profileData.emergency_contact_phone,
        emergency_contact_relation: profileData.emergency_contact_relation,
      });
    }
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      const response = await teachersAPI.updateMyProfile(editData);
      setProfileData(response.data);
      setIsEditing(false);
    } catch (err: any) {
      console.error('Error updating profile:', err);
      console.error('Error response data:', err.response?.data);

      // Handle different error response formats
      let errorMessage = 'Failed to update profile';
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data)) {
          // Handle validation errors array
          errorMessage = err.response.data.map((error: any) => error.msg || error.message || 'Validation error').join(', ');
        } else {
          errorMessage = 'An error occurred while updating profile';
        }
      }

      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditData({});
    setIsEditing(false);
    setError(null);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
        <Button onClick={fetchProfile} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  if (!profileData) {
    return (
      <Alert severity="info">
        No teacher profile found. Please contact administration.
      </Alert>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Header Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={3} flexWrap="wrap">
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: 'primary.main',
                fontSize: '2rem',
                fontWeight: 'bold'
              }}
            >
              {getInitials()}
            </Avatar>
            <Box flex={1}>
              <Typography variant="h4" gutterBottom>
                {profileData.first_name} {profileData.last_name}
              </Typography>
              <Box display="flex" gap={2} flexWrap="wrap">
                <Chip
                  icon={<WorkIcon />}
                  label={`${profileData.position} - ${profileData.department}`}
                  color="primary"
                />
                <Chip
                  label={profileData.is_active ? 'Active' : 'Inactive'}
                  color={getStatusColor() as any}
                />
                <Chip
                  label={`ID: ${profileData.employee_id}`}
                  variant="outlined"
                />
              </Box>
            </Box>
            <Box>
              {!isEditing ? (
                <Button
                  variant="contained"
                  startIcon={<EditIcon />}
                  onClick={handleEdit}
                >
                  Edit Profile
                </Button>
              ) : (
                <Box display="flex" gap={1}>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSave}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save'}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<CancelIcon />}
                    onClick={handleCancel}
                  >
                    Cancel
                  </Button>
                </Box>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Personal Information */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Personal Information
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <List>
              <ListItem>
                <ListItemIcon><PersonIcon /></ListItemIcon>
                <ListItemText
                  primary="Employee ID"
                  secondary={safeRender(profileData.employee_id)}
                />
              </ListItem>

              <ListItem>
                <ListItemIcon><CalendarIcon /></ListItemIcon>
                <ListItemText
                  primary="Date of Birth"
                  secondary={safeRender(profileData.date_of_birth)}
                />
              </ListItem>

              <ListItem>
                <ListItemIcon><SchoolIcon /></ListItemIcon>
                <ListItemText
                  primary="Qualification"
                  secondary={safeRender(profileData.qualification_name, 'Not specified')}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        {/* Contact Information */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Contact Information
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <List>
              <ListItem>
                <ListItemIcon><PhoneIcon /></ListItemIcon>
                <ListItemText
                  primary="Phone"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.phone || ''}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.phone || 'Not provided'}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon><EmailIcon /></ListItemIcon>
                <ListItemText
                  primary="Email"
                  secondary={isEditing ? (
                    <TextField
                      type="email"
                      value={editData.email || ''}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.email || 'Not provided'}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon><PersonIcon /></ListItemIcon>
                <ListItemText
                  primary="Aadhar Number"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.aadhar_no || ''}
                      onChange={(e) => handleInputChange('aadhar_no', e.target.value)}
                      size="small"
                      fullWidth
                      inputProps={{ maxLength: 12, pattern: '[0-9]{12}' }}
                      helperText="12-digit Aadhar number"
                    />
                  ) : profileData.aadhar_no || 'Not provided'}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon><HomeIcon /></ListItemIcon>
                <ListItemText
                  primary="Address"
                  secondary={isEditing ? (
                    <TextField
                      multiline
                      rows={2}
                      value={editData.address || ''}
                      onChange={(e) => handleInputChange('address', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.address || 'Not provided'}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TeacherProfile;
