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
  School as SchoolIcon,
  Person as PersonIcon,
  Home as HomeIcon,
  ContactPhone as ContactPhoneIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  CalendarToday as CalendarIcon,
  LocalHospital as BloodtypeIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { studentsAPI } from '../services/api';

interface StudentProfileData {
  id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender_name: string;
  class_name: string;
  session_year_name: string;
  section: string;
  roll_number: string;
  blood_group: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  father_name: string;
  father_phone: string;
  father_email: string;
  father_occupation: string;
  mother_name: string;
  mother_phone: string;
  mother_email: string;
  mother_occupation: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relation: string;
  admission_date: string;
  previous_school: string;
  is_active: boolean;
}

const StudentProfile: React.FC = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profileData, setProfileData] = useState<StudentProfileData | null>(null);
  const [editData, setEditData] = useState<Partial<StudentProfileData>>({});

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await studentsAPI.getMyProfile();
      setProfileData(response.data);
    } catch (err: any) {
      console.error('Error fetching student profile:', err);
      setError(err.response?.data?.detail || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    if (profileData) {
      setEditData({
        first_name: profileData.first_name,
        last_name: profileData.last_name,
        date_of_birth: profileData.date_of_birth,
        blood_group: profileData.blood_group,
        phone: profileData.phone,
        email: profileData.email,
        address: profileData.address,
        city: profileData.city,
        state: profileData.state,
        postal_code: profileData.postal_code,
        country: profileData.country,
        father_name: profileData.father_name,
        father_phone: profileData.father_phone,
        father_email: profileData.father_email,
        father_occupation: profileData.father_occupation,
        mother_name: profileData.mother_name,
        mother_phone: profileData.mother_phone,
        mother_email: profileData.mother_email,
        mother_occupation: profileData.mother_occupation,
        emergency_contact_name: profileData.emergency_contact_name,
        emergency_contact_phone: profileData.emergency_contact_phone,
        emergency_contact_relation: profileData.emergency_contact_relation,
        previous_school: profileData.previous_school,
      });
    }
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      const response = await studentsAPI.updateMyProfile(editData);
      setProfileData(response.data);
      setIsEditing(false);
    } catch (err: any) {
      console.error('Error updating profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditData({});
    setIsEditing(false);
    setError(null);
  };

  const handleInputChange = (field: string, value: string) => {
    setEditData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!profileData) {
    return (
      <Alert severity="error">
        Failed to load student profile. Please try again.
      </Alert>
    );
  }

  const getInitials = () => {
    return `${profileData.first_name[0]}${profileData.last_name[0]}`;
  };

  const getStatusColor = () => {
    return profileData.is_active ? 'success' : 'error';
  };

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
          <Box display="flex" alignItems="center" gap={3}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: 'primary.main',
                fontSize: '2rem'
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
                  icon={<SchoolIcon />}
                  label={`${profileData.class_name} - ${profileData.section}`}
                  color="primary"
                />
                <Chip
                  label={profileData.is_active ? 'Active' : 'Inactive'}
                  color={getStatusColor() as any}
                />
                <Chip
                  label={`Roll: ${profileData.roll_number}`}
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
                    disabled={saving}
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
                  primary="Admission Number"
                  secondary={profileData.admission_number}
                />
              </ListItem>

              <ListItem>
                <ListItemIcon><CalendarIcon /></ListItemIcon>
                <ListItemText
                  primary="Date of Birth"
                  secondary={isEditing ? (
                    <TextField
                      type="date"
                      value={editData.date_of_birth || ''}
                      onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.date_of_birth}
                />
              </ListItem>

              <ListItem>
                <ListItemIcon><BloodtypeIcon /></ListItemIcon>
                <ListItemText
                  primary="Blood Group"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.blood_group || ''}
                      onChange={(e) => handleInputChange('blood_group', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.blood_group || 'Not specified'}
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

        {/* Parent Information */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Parent Information
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Typography variant="subtitle2" color="primary" gutterBottom>
              Father's Details
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText
                  primary="Name"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.father_name || ''}
                      onChange={(e) => handleInputChange('father_name', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.father_name}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Phone"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.father_phone || ''}
                      onChange={(e) => handleInputChange('father_phone', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.father_phone || 'Not provided'}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Occupation"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.father_occupation || ''}
                      onChange={(e) => handleInputChange('father_occupation', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.father_occupation || 'Not specified'}
                />
              </ListItem>
            </List>

            <Typography variant="subtitle2" color="primary" gutterBottom sx={{ mt: 2 }}>
              Mother's Details
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText
                  primary="Name"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.mother_name || ''}
                      onChange={(e) => handleInputChange('mother_name', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.mother_name}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Phone"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.mother_phone || ''}
                      onChange={(e) => handleInputChange('mother_phone', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.mother_phone || 'Not provided'}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Occupation"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.mother_occupation || ''}
                      onChange={(e) => handleInputChange('mother_occupation', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.mother_occupation || 'Not specified'}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        {/* Emergency Contact */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Emergency Contact
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <List>
              <ListItem>
                <ListItemIcon><ContactPhoneIcon /></ListItemIcon>
                <ListItemText
                  primary="Contact Name"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.emergency_contact_name || ''}
                      onChange={(e) => handleInputChange('emergency_contact_name', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.emergency_contact_name || 'Not provided'}
                />
              </ListItem>

              <ListItem>
                <ListItemIcon><PhoneIcon /></ListItemIcon>
                <ListItemText
                  primary="Contact Phone"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.emergency_contact_phone || ''}
                      onChange={(e) => handleInputChange('emergency_contact_phone', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.emergency_contact_phone || 'Not provided'}
                />
              </ListItem>

              <ListItem>
                <ListItemIcon><PersonIcon /></ListItemIcon>
                <ListItemText
                  primary="Relation"
                  secondary={isEditing ? (
                    <TextField
                      value={editData.emergency_contact_relation || ''}
                      onChange={(e) => handleInputChange('emergency_contact_relation', e.target.value)}
                      size="small"
                      fullWidth
                    />
                  ) : profileData.emergency_contact_relation || 'Not specified'}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        {/* Academic Information */}
        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Academic Information
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 3 }}>
                <Typography variant="body2" color="textSecondary">
                  Session Year
                </Typography>
                <Typography variant="body1">
                  {profileData.session_year_name}
                </Typography>
              </Grid>

              <Grid size={{ xs: 12, md: 3 }}>
                <Typography variant="body2" color="textSecondary">
                  Admission Date
                </Typography>
                <Typography variant="body1">
                  {profileData.admission_date}
                </Typography>
              </Grid>

              <Grid size={{ xs: 12, md: 6 }}>
                <Typography variant="body2" color="textSecondary">
                  Previous School
                </Typography>
                {isEditing ? (
                  <TextField
                    value={editData.previous_school || ''}
                    onChange={(e) => handleInputChange('previous_school', e.target.value)}
                    size="small"
                    fullWidth
                    placeholder="Enter previous school name"
                  />
                ) : (
                  <Typography variant="body1">
                    {profileData.previous_school || 'Not specified'}
                  </Typography>
                )}
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default StudentProfile;
