/**
 * NotificationBell Component
 * Displays a bell icon with unread count badge and dropdown panel
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  IconButton,
  Badge,
  Popover,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Divider,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  NotificationsNone as NotificationsNoneIcon,
  Circle as CircleIcon,
  MarkEmailRead as MarkEmailReadIcon,
  OpenInNew as OpenInNewIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { alertAPI } from '../../services/alertService';
import { Alert } from '../../types/alert';
import { formatDistanceToNow } from 'date-fns';

// Polling interval for unread count (30 seconds)
const POLL_INTERVAL = 30000;
// Number of alerts to show in dropdown
const DROPDOWN_ALERT_COUNT = 5;

interface NotificationBellProps {
  color?: 'inherit' | 'primary' | 'secondary' | 'default';
}

const NotificationBell: React.FC<NotificationBellProps> = ({ color = 'inherit' }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch unread count
  const fetchUnreadCount = useCallback(async () => {
    try {
      const response = await alertAPI.getUnreadCount();
      setUnreadCount(response.unread_count);
    } catch (err) {
      console.error('Failed to fetch unread count:', err);
    }
  }, []);

  // Fetch recent alerts for dropdown
  const fetchRecentAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await alertAPI.getAlerts({
        page: 1,
        per_page: DROPDOWN_ALERT_COUNT,
      });
      setAlerts(response.alerts);
      setUnreadCount(response.unread_count);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
      setError('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch and polling
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  // Handle bell click
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
    fetchRecentAlerts();
  };

  // Handle close
  const handleClose = () => {
    setAnchorEl(null);
  };

  // Handle mark all as read
  const handleMarkAllRead = async () => {
    try {
      await alertAPI.markAllAsRead();
      setUnreadCount(0);
      setAlerts(alerts.map(a => ({ ...a, read_at: new Date().toISOString() })));
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  };

  // Handle alert click
  const handleAlertClick = async (alert: Alert) => {
    if (!alert.read_at) {
      try {
        await alertAPI.markAsRead(alert.id);
        setUnreadCount(prev => Math.max(0, prev - 1));
        setAlerts(alerts.map(a => 
          a.id === alert.id ? { ...a, read_at: new Date().toISOString() } : a
        ));
      } catch (err) {
        console.error('Failed to mark alert as read:', err);
      }
    }
    handleClose();
  };

  // Handle view all click
  const handleViewAll = () => {
    handleClose();
    navigate('/alerts');
  };

  const open = Boolean(anchorEl);

  // Get priority color
  const getPriorityColor = (priority: number): string => {
    switch (priority) {
      case 4: return '#d32f2f'; // Critical - Red
      case 3: return '#ed6c02'; // High - Orange
      case 2: return '#1976d2'; // Normal - Blue
      default: return '#757575'; // Low - Grey
    }
  };

  // Format time ago
  const formatTimeAgo = (dateString: string): string => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return '';
    }
  };

  return (
    <>
      <Tooltip title="Notifications">
        <IconButton color={color} onClick={handleClick} sx={{ position: 'relative' }}>
          <Badge
            badgeContent={unreadCount}
            color="error"
            max={99}
            sx={{
              '& .MuiBadge-badge': {
                fontSize: '0.7rem',
                minWidth: '18px',
                height: '18px',
              },
            }}
          >
            {unreadCount > 0 ? <NotificationsIcon /> : <NotificationsNoneIcon />}
          </Badge>
        </IconButton>
      </Tooltip>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{
          sx: { width: 360, maxHeight: 480, overflow: 'hidden' },
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" fontWeight="bold">Notifications</Typography>
          {unreadCount > 0 && (
            <Button size="small" startIcon={<MarkEmailReadIcon />} onClick={handleMarkAllRead}>
              Mark all read
            </Button>
          )}
        </Box>

        {/* Content */}
        <Box sx={{ maxHeight: 340, overflow: 'auto' }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress size={24} />
            </Box>
          ) : error ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="error">{error}</Typography>
            </Box>
          ) : alerts.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <NotificationsNoneIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
              <Typography color="text.secondary">No notifications</Typography>
            </Box>
          ) : (
            <List disablePadding>
              {alerts.map((alert, index) => (
                <React.Fragment key={alert.id}>
                  <ListItem
                    component="div"
                    onClick={() => handleAlertClick(alert)}
                    sx={{
                      cursor: 'pointer',
                      backgroundColor: !alert.read_at ? 'action.hover' : 'transparent',
                      '&:hover': { backgroundColor: 'action.selected' },
                      py: 1.5,
                      px: 2,
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <CircleIcon
                        sx={{
                          fontSize: 10,
                          color: !alert.read_at ? getPriorityColor(alert.priority_level) : 'transparent',
                        }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography
                          variant="body2"
                          fontWeight={!alert.read_at ? 600 : 400}
                          sx={{ mb: 0.5 }}
                        >
                          {alert.title}
                        </Typography>
                      }
                      secondary={
                        <Box>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                            }}
                          >
                            {alert.message}
                          </Typography>
                          <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 0.5 }}>
                            {formatTimeAgo(alert.created_at)}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < alerts.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>

        {/* Footer */}
        <Divider />
        <Box sx={{ p: 1.5, textAlign: 'center' }}>
          <Button
            fullWidth
            variant="text"
            endIcon={<OpenInNewIcon fontSize="small" />}
            onClick={handleViewAll}
          >
            View all notifications
          </Button>
        </Box>
      </Popover>
    </>
  );
};

export default NotificationBell;

