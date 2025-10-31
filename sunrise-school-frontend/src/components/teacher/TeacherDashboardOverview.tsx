import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  EventNote,
  Schedule,
  CheckCircle,
  Cancel,
  Pending,
  Person,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { leaveAPI, teachersAPI } from '../../services/api';

interface LeaveRequest {
  id: number;
  leave_type_name: string;
  start_date: string;
  end_date: string;
  total_days: number;
  leave_status_name: string;
  leave_status_id: number;
  reason: string;
  created_at: string;
}

interface TeacherProfile {
  id: number;
  first_name: string;
  last_name: string;
  employee_id: string;
  department: string;
  email: string;
  position: string;
}

const TeacherDashboardOverview: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recentLeaves, setRecentLeaves] = useState<LeaveRequest[]>([]);
  const [teacherProfile, setTeacherProfile] = useState<TeacherProfile | null>(null);
  const [leaveStats, setLeaveStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load teacher profile and recent leave requests
      const [profileResponse, leavesResponse] = await Promise.all([
        teachersAPI.getMyProfile(),
        leaveAPI.getMyLeaveRequests()
      ]);

      setTeacherProfile(profileResponse.data);
      
      // Process leave requests
      const leaves = Array.isArray(leavesResponse) ? leavesResponse : [];
      setRecentLeaves(leaves.slice(0, 5)); // Show only recent 5
      
      // Calculate stats
      const stats = leaves.reduce((acc, leave) => {
        acc.total++;
        if (leave.leave_status_id === 1) acc.pending++;
        else if (leave.leave_status_id === 2) acc.approved++;
        else if (leave.leave_status_id === 3) acc.rejected++;
        return acc;
      }, { total: 0, pending: 0, approved: 0, rejected: 0 });
      
      setLeaveStats(stats);
      setError(null);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (statusId: number) => {
    switch (statusId) {
      case 1: return <Pending color="warning" />;
      case 2: return <CheckCircle color="success" />;
      case 3: return <Cancel color="error" />;
      default: return <Schedule />;
    }
  };

  const getStatusColor = (statusId: number) => {
    switch (statusId) {
      case 1: return 'warning';
      case 2: return 'success';
      case 3: return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Welcome Message */}
      <Box mb={3}>
        <Typography variant="subtitle1" color="text.secondary">
          Welcome back, {teacherProfile?.first_name} {teacherProfile?.last_name}!
        </Typography>
      </Box>

      {/* Recent Leave Requests and Quick Actions */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            md: '2fr 1fr',
          },
          gap: 3,
        }}
      >
        <Box>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" fontWeight="bold">
                Recent Leave Requests
              </Typography>
              <Button
                variant="contained"
                onClick={() => navigate('/teacher/leaves')}
                size="small"
              >
                View All
              </Button>
            </Box>
            
            {recentLeaves.length === 0 ? (
              <Typography color="text.secondary" textAlign="center" py={4}>
                No leave requests found. Click "View All" to create your first request.
              </Typography>
            ) : (
              <List>
                {recentLeaves.map((leave, index) => (
                  <React.Fragment key={leave.id}>
                    <ListItem>
                      <ListItemIcon>
                        {getStatusIcon(leave.leave_status_id)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body1" fontWeight="medium">
                              {leave.leave_type_name}
                            </Typography>
                            <Chip
                              label={leave.leave_status_name}
                              size="small"
                              color={getStatusColor(leave.leave_status_id) as any}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {new Date(leave.start_date).toLocaleDateString()} - {new Date(leave.end_date).toLocaleDateString()} ({leave.total_days} days)
                            </Typography>
                            <Typography variant="body2" color="text.secondary" noWrap>
                              {leave.reason}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < recentLeaves.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Box>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Quick Actions
          </Typography>
          <Box display="flex" flexDirection="column" gap={2}>
            <Button
              variant="contained"
              startIcon={<EventNote />}
              onClick={() => navigate('/teacher/leaves')}
              fullWidth
            >
              Manage Leave Requests
            </Button>
            <Button
              variant="outlined"
              startIcon={<Person />}
              onClick={() => navigate('/profile')}
              fullWidth
            >
              View Profile
            </Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default TeacherDashboardOverview;
