import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Card,
  CardContent,
  Avatar,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Edit as EditIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Home as HomeIcon,
  School as SchoolIcon,
  Work as WorkIcon,
  CalendarToday as CalendarIcon,
  Badge as BadgeIcon,
  CameraAlt as CameraIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { authAPI, studentsAPI, teachersAPI } from '../services/api';
import { ProfileData } from '../types/profile';
import ProfileEditDialog from '../components/profile/ProfileEditDialog';

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [uploadingPicture, setUploadingPicture] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await authAPI.getProfile();
      console.log('Profile data received:', response.data);
      console.log('Student profile:', response.data.student_profile);
      console.log('Teacher profile:', response.data.teacher_profile);
      console.log('Profile picture URL:', response.data.student_profile?.profile_picture_url || response.data.teacher_profile?.profile_picture_url);
      setProfileData(response.data);
    } catch (err: any) {
      console.error('Failed to fetch profile data:', err);
      setError(err.response?.data?.detail || 'Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };

  const getProfileDescription = () => {
    if (user?.user_type?.toLowerCase() === 'student') {
      return 'View and update your student profile information.';
    }
    if (user?.user_type?.toLowerCase() === 'teacher') {
      return 'View and update your teacher profile information.';
    }
    return 'Manage your personal information and account settings.';
  };

  const getUserTypeDisplay = () => {
    if (!user?.user_type) return 'User';
    return user.user_type.charAt(0).toUpperCase() + user.user_type.slice(1).toLowerCase();
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not provided';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const getFullName = () => {
    if (profileData?.user_info) {
      return `${profileData.user_info.first_name} ${profileData.user_info.last_name}`;
    }
    return `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || 'User';
  };

  const getInitials = () => {
    const name = getFullName();
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const handleProfileUpdated = (updatedProfile: ProfileData) => {
    setProfileData(updatedProfile);
  };

  const handleProfilePictureUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Invalid file type. Please upload an image file (JPEG, PNG, GIF, or WebP).');
      return;
    }

    // Validate file size (5MB max)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      setError('File size exceeds 5MB. Please upload a smaller image.');
      return;
    }

    try {
      setUploadingPicture(true);
      setError(null);
      setSuccessMessage(null);

      if (user?.user_type?.toLowerCase() === 'student') {
        await studentsAPI.uploadMyProfilePicture(file);
      } else if (user?.user_type?.toLowerCase() === 'teacher') {
        await teachersAPI.uploadMyProfilePicture(file);
      } else {
        setError('Profile picture upload is only available for students and teachers.');
        return;
      }

      setSuccessMessage('Profile picture uploaded successfully!');

      // Refresh profile data
      await fetchProfileData();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error uploading profile picture:', err);
      setError(err.response?.data?.detail || 'Failed to upload profile picture. Please try again.');
    } finally {
      setUploadingPicture(false);
      // Reset file input
      event.target.value = '';
    }
  };

  const handleProfilePictureDelete = async () => {
    if (!window.confirm('Are you sure you want to delete your profile picture?')) {
      return;
    }

    try {
      setUploadingPicture(true);
      setError(null);
      setSuccessMessage(null);

      if (user?.user_type?.toLowerCase() === 'student') {
        await studentsAPI.deleteMyProfilePicture();
      } else if (user?.user_type?.toLowerCase() === 'teacher') {
        await teachersAPI.deleteMyProfilePicture();
      } else {
        setError('Profile picture deletion is only available for students and teachers.');
        return;
      }

      setSuccessMessage('Profile picture deleted successfully!');

      // Refresh profile data
      await fetchProfileData();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Error deleting profile picture:', err);
      setError(err.response?.data?.detail || 'Failed to delete profile picture. Please try again.');
    } finally {
      setUploadingPicture(false);
    }
  };

  const getProfilePictureUrl = () => {
    console.log('Getting profile picture URL...');
    console.log('User type:', user?.user_type);
    console.log('Profile data:', profileData);

    if (user?.user_type?.toLowerCase() === 'student') {
      const url = profileData?.student_profile?.profile_picture_url;
      console.log('Student profile picture URL:', url);
      return url;
    } else if (user?.user_type?.toLowerCase() === 'teacher') {
      const url = profileData?.teacher_profile?.profile_picture_url;
      console.log('Teacher profile picture URL:', url);
      return url;
    }
    console.log('No profile picture URL found');
    return null;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="outlined" onClick={fetchProfileData}>
          Retry
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {getProfileDescription()}
        </Typography>
      </Box>

      {/* Success Message */}
      {successMessage && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      {/* Profile Header Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={3}>
            {/* Profile Picture with Upload/Delete Buttons */}
            <Box position="relative">
              <Avatar
                src={getProfilePictureUrl() || undefined}
                sx={{
                  width: 100,
                  height: 100,
                  bgcolor: 'primary.main',
                  fontSize: '2rem'
                }}
              >
                {!getProfilePictureUrl() && getInitials()}
              </Avatar>

              {/* Upload/Delete Buttons */}
              <Box
                sx={{
                  position: 'absolute',
                  bottom: -8,
                  right: -8,
                  display: 'flex',
                  gap: 0.5
                }}
              >
                {/* Upload Button */}
                <Tooltip title="Upload Picture">
                  <IconButton
                    component="label"
                    size="small"
                    disabled={uploadingPicture}
                    sx={{
                      bgcolor: 'primary.main',
                      color: 'white',
                      '&:hover': { bgcolor: 'primary.dark' },
                      boxShadow: 2
                    }}
                  >
                    {uploadingPicture ? (
                      <CircularProgress size={16} color="inherit" />
                    ) : (
                      <CameraIcon fontSize="small" />
                    )}
                    <input
                      type="file"
                      hidden
                      accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                      onChange={handleProfilePictureUpload}
                    />
                  </IconButton>
                </Tooltip>

                {/* Delete Button (only show if picture exists) */}
                {getProfilePictureUrl() && (
                  <Tooltip title="Delete Picture">
                    <IconButton
                      size="small"
                      disabled={uploadingPicture}
                      onClick={handleProfilePictureDelete}
                      sx={{
                        bgcolor: 'error.main',
                        color: 'white',
                        '&:hover': { bgcolor: 'error.dark' },
                        boxShadow: 2
                      }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            </Box>

            <Box flex={1}>
              <Typography variant="h5" gutterBottom>
                {getFullName()}
              </Typography>
              <Chip
                label={getUserTypeDisplay()}
                color="primary"
                variant="outlined"
                sx={{ mb: 1 }}
              />
              <Typography variant="body2" color="text.secondary">
                Member since {formatDate(profileData?.user_info.created_at)}
              </Typography>
            </Box>
            <Tooltip title="Edit Profile">
              <IconButton
                color="primary"
                onClick={() => setEditDialogOpen(true)}
                size="large"
              >
                <EditIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </CardContent>
      </Card>

      {/* Common Information */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <PersonIcon color="primary" />
          <Typography variant="h6">
            Personal Information
          </Typography>
        </Box>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="First Name"
              value={profileData?.user_info.first_name || ''}
              disabled
              variant="outlined"
              InputProps={{
                startAdornment: <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Last Name"
              value={profileData?.user_info.last_name || ''}
              disabled
              variant="outlined"
              InputProps={{
                startAdornment: <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Email Address"
              value={profileData?.user_info.email || ''}
              disabled
              variant="outlined"
              InputProps={{
                startAdornment: <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Phone Number"
              value={profileData?.user_info.phone || 'Not provided'}
              disabled
              variant="outlined"
              InputProps={{
                startAdornment: <PhoneIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Account Created"
              value={formatDate(profileData?.user_info.created_at)}
              disabled
              variant="outlined"
              InputProps={{
                startAdornment: <CalendarIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Account Status"
              value={profileData?.user_info.is_active ? 'Active' : 'Inactive'}
              disabled
              variant="outlined"
              InputProps={{
                startAdornment: <BadgeIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Role-specific Information */}
      {profileData?.student_profile && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <SchoolIcon color="primary" />
            <Typography variant="h6">
              Student Information
            </Typography>
          </Box>

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Admission Number"
                value={profileData.student_profile.admission_number || ''}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Roll Number"
                value={profileData.student_profile.roll_number || 'Not assigned'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Class"
                value={profileData.student_profile.class_description || profileData.student_profile.class_name || 'Not assigned'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Section"
                value={profileData.student_profile.section || 'Not assigned'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Session Year"
                value={profileData.student_profile.session_year_description || profileData.student_profile.session_year_name || 'Not assigned'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Date of Birth"
                value={formatDate(profileData.student_profile.date_of_birth)}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Gender"
                value={profileData.student_profile.gender_description || profileData.student_profile.gender_name || 'Not specified'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Blood Group"
                value={profileData.student_profile.blood_group || 'Not specified'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Admission Date"
                value={formatDate(profileData.student_profile.admission_date)}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Aadhar Number"
                value={profileData.student_profile.aadhar_no || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            Address Information
          </Typography>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Address"
                value={profileData.student_profile.address || 'Not provided'}
                disabled
                variant="outlined"
                multiline
                rows={2}
                InputProps={{
                  startAdornment: <HomeIcon sx={{ mr: 1, color: 'text.secondary', alignSelf: 'flex-start', mt: 1 }} />
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="City"
                value={profileData.student_profile.city || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="State"
                value={profileData.student_profile.state || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Postal Code"
                value={profileData.student_profile.postal_code || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Country"
                value={profileData.student_profile.country || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            Parent/Guardian Information
          </Typography>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Father's Name"
                value={profileData.student_profile.father_name || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Father's Phone"
                value={profileData.student_profile.father_phone || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Father's Email"
                value={profileData.student_profile.father_email || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Father's Occupation"
                value={profileData.student_profile.father_occupation || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Mother's Name"
                value={profileData.student_profile.mother_name || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Mother's Phone"
                value={profileData.student_profile.mother_phone || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Mother's Email"
                value={profileData.student_profile.mother_email || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Mother's Occupation"
                value={profileData.student_profile.mother_occupation || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            {(profileData.student_profile.guardian_name || profileData.student_profile.guardian_phone) && (
              <>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Guardian's Name"
                    value={profileData.student_profile.guardian_name || 'Not provided'}
                    disabled
                    variant="outlined"
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Guardian's Phone"
                    value={profileData.student_profile.guardian_phone || 'Not provided'}
                    disabled
                    variant="outlined"
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Guardian's Email"
                    value={profileData.student_profile.guardian_email || 'Not provided'}
                    disabled
                    variant="outlined"
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Guardian's Relation"
                    value={profileData.student_profile.guardian_relation || 'Not provided'}
                    disabled
                    variant="outlined"
                  />
                </Grid>
              </>
            )}
          </Grid>
        </Paper>
      )}

      {/* Teacher Profile */}
      {profileData?.teacher_profile && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <WorkIcon color="primary" />
            <Typography variant="h6">
              Teacher Information
            </Typography>
          </Box>

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Employee ID"
                value={profileData.teacher_profile.employee_id || ''}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Department"
                value={profileData.teacher_profile.department_description || profileData.teacher_profile.department_name || 'Not assigned'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Position/Designation"
                value={profileData.teacher_profile.position_description || profileData.teacher_profile.position_name || 'Not assigned'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Employment Status"
                value={profileData.teacher_profile.employment_status_description || profileData.teacher_profile.employment_status_name || 'Not specified'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Qualification"
                value={profileData.teacher_profile.qualification_description || profileData.teacher_profile.qualification_name || 'Not specified'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Date of Joining"
                value={formatDate(profileData.teacher_profile.joining_date)}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Experience Years"
                value={profileData.teacher_profile.experience_years?.toString() || '0'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Date of Birth"
                value={formatDate(profileData.teacher_profile.date_of_birth)}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Gender"
                value={profileData.teacher_profile.gender_description || profileData.teacher_profile.gender_name || 'Not specified'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Aadhar Number"
                value={profileData.teacher_profile.aadhar_no || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            {profileData.teacher_profile.subjects && (
              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Subjects Taught"
                  value={profileData.teacher_profile.subjects}
                  disabled
                  variant="outlined"
                  multiline
                  rows={2}
                />
              </Grid>
            )}
            {profileData.teacher_profile.class_teacher_of_name && (
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Class Teacher Of"
                  value={profileData.teacher_profile.class_teacher_of_name}
                  disabled
                  variant="outlined"
                />
              </Grid>
            )}
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            Address Information
          </Typography>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Address"
                value={profileData.teacher_profile.address || 'Not provided'}
                disabled
                variant="outlined"
                multiline
                rows={2}
                InputProps={{
                  startAdornment: <HomeIcon sx={{ mr: 1, color: 'text.secondary', alignSelf: 'flex-start', mt: 1 }} />
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="City"
                value={profileData.teacher_profile.city || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="State"
                value={profileData.teacher_profile.state || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Postal Code"
                value={profileData.teacher_profile.postal_code || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Country"
                value={profileData.teacher_profile.country || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
          </Grid>

          {(profileData.teacher_profile.emergency_contact_name || profileData.teacher_profile.emergency_contact_phone) && (
            <>
              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Emergency Contact
              </Typography>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Emergency Contact Name"
                    value={profileData.teacher_profile.emergency_contact_name || 'Not provided'}
                    disabled
                    variant="outlined"
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Emergency Contact Phone"
                    value={profileData.teacher_profile.emergency_contact_phone || 'Not provided'}
                    disabled
                    variant="outlined"
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Emergency Contact Relation"
                    value={profileData.teacher_profile.emergency_contact_relation || 'Not provided'}
                    disabled
                    variant="outlined"
                  />
                </Grid>
              </Grid>
            </>
          )}
        </Paper>
      )}

      {/* Admin Profile */}
      {profileData?.admin_profile && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <WorkIcon color="primary" />
            <Typography variant="h6">
              Administrative Information
            </Typography>
          </Box>

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Employee ID"
                value={profileData.admin_profile.employee_id || ''}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Department"
                value={profileData.admin_profile.department_description || profileData.admin_profile.department_name || 'Not assigned'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Position/Designation"
                value={profileData.admin_profile.position_description || profileData.admin_profile.position_name || 'Not assigned'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Employment Status"
                value={profileData.admin_profile.employment_status_description || profileData.admin_profile.employment_status_name || 'Not specified'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Qualification"
                value={profileData.admin_profile.qualification_description || profileData.admin_profile.qualification_name || 'Not specified'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Date of Joining"
                value={formatDate(profileData.admin_profile.joining_date)}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Experience Years"
                value={profileData.admin_profile.experience_years?.toString() || '0'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Date of Birth"
                value={formatDate(profileData.admin_profile.date_of_birth)}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Gender"
                value={profileData.admin_profile.gender_description || profileData.admin_profile.gender_name || 'Not specified'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Aadhar Number"
                value={profileData.admin_profile.aadhar_no || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            Address Information
          </Typography>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Address"
                value={profileData.admin_profile.address || 'Not provided'}
                disabled
                variant="outlined"
                multiline
                rows={2}
                InputProps={{
                  startAdornment: <HomeIcon sx={{ mr: 1, color: 'text.secondary', alignSelf: 'flex-start', mt: 1 }} />
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="City"
                value={profileData.admin_profile.city || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="State"
                value={profileData.admin_profile.state || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Postal Code"
                value={profileData.admin_profile.postal_code || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Country"
                value={profileData.admin_profile.country || 'Not provided'}
                disabled
                variant="outlined"
              />
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Edit Profile Button */}
      <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="contained"
          startIcon={<EditIcon />}
          onClick={() => setEditDialogOpen(true)}
          size="large"
        >
          Edit Profile
        </Button>
      </Box>

      {/* Profile Edit Dialog */}
      {profileData && (
        <ProfileEditDialog
          open={editDialogOpen}
          onClose={() => setEditDialogOpen(false)}
          profileData={profileData}
          onProfileUpdated={handleProfileUpdated}
        />
      )}
    </Container>
  );
};

export default Profile;
