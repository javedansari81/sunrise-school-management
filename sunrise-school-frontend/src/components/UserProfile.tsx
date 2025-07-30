import React, { useState } from 'react';
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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Email as EmailIcon,
  Phone as PhoneIcon,
  School as SchoolIcon,
  Work as WorkIcon,
  CalendarToday as CalendarIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const UserProfile: React.FC = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: '+1 (555) 123-4567',
    address: '123 Main Street, City, State 12345',
  });

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    console.log('Saving profile data:', profileData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setProfileData({
      ...profileData,
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
    });
    setIsEditing(false);
  };

  const handleInputChange = (field: string, value: string) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getUserTypeDisplay = () => {
    switch (user?.user_type?.toLowerCase()) {
      case 'admin':
        return 'Administrator';
      case 'teacher':
        return 'Teacher';
      case 'student':
        return 'Student';
      default:
        return 'User';
    }
  };

  const getUserTypeColor = () => {
    switch (user?.user_type?.toLowerCase()) {
      case 'admin':
        return 'error';
      case 'teacher':
        return 'primary';
      case 'student':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      {/* Profile Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 3 }}>
            <Avatar
              sx={{ 
                width: 100, 
                height: 100, 
                bgcolor: 'primary.main',
                fontSize: '2.5rem'
              }}
            >
              {profileData.first_name.charAt(0)}{profileData.last_name.charAt(0)}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" gutterBottom>
                {profileData.first_name} {profileData.last_name}
              </Typography>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {getUserTypeDisplay()}
              </Typography>
              <Chip 
                label={`Active ${getUserTypeDisplay()}`} 
                color={getUserTypeColor() as any}
                sx={{ mr: 1 }}
              />
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
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSave}
                    color="primary"
                  >
                    Save
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

      {/* Personal Information */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Personal Information
          </Typography>
          <Divider sx={{ mb: 3 }} />
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="First Name"
                value={profileData.first_name}
                onChange={(e) => handleInputChange('first_name', e.target.value)}
                disabled={!isEditing}
                variant={isEditing ? "outlined" : "filled"}
              />
              <TextField
                fullWidth
                label="Last Name"
                value={profileData.last_name}
                onChange={(e) => handleInputChange('last_name', e.target.value)}
                disabled={!isEditing}
                variant={isEditing ? "outlined" : "filled"}
              />
            </Box>
            
            <TextField
              fullWidth
              label="Email"
              value={profileData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              disabled={!isEditing}
              variant={isEditing ? "outlined" : "filled"}
            />
            
            <TextField
              fullWidth
              label="Phone"
              value={profileData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              disabled={!isEditing}
              variant={isEditing ? "outlined" : "filled"}
            />
            
            <TextField
              fullWidth
              label="Address"
              value={profileData.address}
              onChange={(e) => handleInputChange('address', e.target.value)}
              disabled={!isEditing}
              variant={isEditing ? "outlined" : "filled"}
              multiline
              rows={2}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Quick Information */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Information
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <List dense>
            <ListItem>
              <ListItemIcon>
                <EmailIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Email" 
                secondary={profileData.email} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <PhoneIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Phone" 
                secondary={profileData.phone} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <WorkIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Role" 
                secondary={getUserTypeDisplay()} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CalendarIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Member Since" 
                secondary="January 2024" 
              />
            </ListItem>
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default UserProfile;
