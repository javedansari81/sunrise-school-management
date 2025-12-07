/**
 * AlertsPage Component
 * Full page view for managing all alerts/notifications
 * Uses AdminLayout wrapper for consistent admin interface
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Tooltip,
  Pagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  Alert as MuiAlert,
} from '@mui/material';
import {
  MarkEmailRead as MarkEmailReadIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Circle as CircleIcon,
} from '@mui/icons-material';
import { alertAPI } from '../services/alertService';
import { Alert } from '../types/alert';
import { DEFAULT_PAGE_SIZE, formatRecordCount } from '../config/pagination';
import { format } from 'date-fns';
import AdminLayout from '../components/Layout/AdminLayout';
import TeacherLayout from '../components/Layout/TeacherLayout';
import StudentLayout from '../components/Layout/StudentLayout';
import CollapsibleFilterSection from '../components/common/CollapsibleFilterSection';
import { useAuth } from '../contexts/AuthContext';

const AlertManagementSystem: React.FC = () => {
  // State
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');

  // Fetch alerts
  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = { page, per_page: DEFAULT_PAGE_SIZE };
      if (categoryFilter) params.category = categoryFilter;
      if (statusFilter === 'unread') params.is_read = false;
      if (statusFilter === 'read') params.is_read = true;
      if (priorityFilter) params.priority_level = parseInt(priorityFilter);

      const response = await alertAPI.getAlerts(params);
      setAlerts(response.alerts);
      setTotalPages(response.total_pages);
      setTotalRecords(response.total);
      setUnreadCount(response.unread_count);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
      setError('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, [page, categoryFilter, statusFilter, priorityFilter]);

  // Initial fetch
  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  // Handle mark as read
  const handleMarkAsRead = async (alertId: number) => {
    try {
      await alertAPI.markAsRead(alertId);
      setAlerts(alerts.map(a =>
        a.id === alertId ? { ...a, read_at: new Date().toISOString() } : a
      ));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  // Handle mark all as read
  const handleMarkAllRead = async () => {
    try {
      await alertAPI.markAllAsRead();
      setAlerts(alerts.map(a => ({ ...a, read_at: new Date().toISOString() })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  };

  // Handle dismiss
  const handleDismiss = async (alertId: number) => {
    try {
      await alertAPI.dismissAlert(alertId);
      setAlerts(alerts.filter(a => a.id !== alertId));
      setTotalRecords(prev => prev - 1);
    } catch (err) {
      console.error('Failed to dismiss alert:', err);
    }
  };

  // Get priority info
  const getPriorityInfo = (priority: number) => {
    switch (priority) {
      case 4: return { label: 'Critical', color: 'error' as const };
      case 3: return { label: 'High', color: 'warning' as const };
      case 2: return { label: 'Normal', color: 'info' as const };
      default: return { label: 'Low', color: 'default' as const };
    }
  };

  // Get category color
  const getCategoryColor = (category?: string) => {
    switch (category) {
      case 'LEAVE_MANAGEMENT': return 'primary';
      case 'FINANCIAL': return 'success';
      case 'ACADEMIC': return 'info';
      case 'ADMINISTRATIVE': return 'warning';
      case 'SYSTEM': return 'secondary';
      default: return 'default';
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM d, yyyy h:mm a');
    } catch {
      return dateString;
    }
  };

  // Action buttons for filter section
  const actionButtons = (
    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
      {unreadCount > 0 && (
        <Button
          variant="outlined"
          size="small"
          startIcon={<MarkEmailReadIcon />}
          onClick={handleMarkAllRead}
        >
          Mark all read ({unreadCount})
        </Button>
      )}
      <Tooltip title="Refresh">
        <IconButton size="small" onClick={fetchAlerts}>
          <RefreshIcon />
        </IconButton>
      </Tooltip>
    </Box>
  );

  return (
    <Box sx={{ width: '100%' }}>
      {/* Filters Section - Above Tabs */}
      <CollapsibleFilterSection
        title="Filters"
        defaultExpanded={true}
        persistKey="notifications-filters"
        actionButtons={actionButtons}
      >
        <Box sx={{
          display: 'flex',
          gap: { xs: 1.5, sm: 2 },
          alignItems: { xs: 'stretch', sm: 'center' },
          flexWrap: 'wrap',
          flexDirection: { xs: 'column', sm: 'row' }
        }}>
          <FormControl
            size="small"
            sx={{
              flex: { xs: '1 1 100%', sm: '1 1 auto' },
              minWidth: { xs: '100%', sm: 'auto' }
            }}
          >
            <InputLabel>Category</InputLabel>
            <Select
              value={categoryFilter}
              label="Category"
              onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}
            >
              <MenuItem value="">All Categories</MenuItem>
              <MenuItem value="LEAVE_MANAGEMENT">Leave Management</MenuItem>
              <MenuItem value="FINANCIAL">Financial</MenuItem>
              <MenuItem value="ACADEMIC">Academic</MenuItem>
              <MenuItem value="ADMINISTRATIVE">Administrative</MenuItem>
              <MenuItem value="SYSTEM">System</MenuItem>
            </Select>
          </FormControl>

          <FormControl
            size="small"
            sx={{
              flex: { xs: '1 1 100%', sm: '1 1 auto' },
              minWidth: { xs: '100%', sm: 'auto' }
            }}
          >
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="unread">Unread</MenuItem>
              <MenuItem value="read">Read</MenuItem>
            </Select>
          </FormControl>

          <FormControl
            size="small"
            sx={{
              flex: { xs: '1 1 100%', sm: '1 1 auto' },
              minWidth: { xs: '100%', sm: 'auto' }
            }}
          >
            <InputLabel>Priority</InputLabel>
            <Select
              value={priorityFilter}
              label="Priority"
              onChange={(e) => { setPriorityFilter(e.target.value); setPage(1); }}
            >
              <MenuItem value="">All Priorities</MenuItem>
              <MenuItem value="4">Critical</MenuItem>
              <MenuItem value="3">High</MenuItem>
              <MenuItem value="2">Normal</MenuItem>
              <MenuItem value="1">Low</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </CollapsibleFilterSection>

      {/* Error */}
      {error && (
        <MuiAlert severity="error" sx={{ mb: 2 }}>{error}</MuiAlert>
      )}

        {/* Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'white' }}>
                <TableCell width={40}></TableCell>
                <TableCell>Notification</TableCell>
                <TableCell width={140}>Category</TableCell>
                <TableCell width={100}>Priority</TableCell>
                <TableCell width={160}>Date</TableCell>
                <TableCell width={100} align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <CircularProgress size={32} />
                  </TableCell>
                </TableRow>
              ) : alerts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">No notifications found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                alerts.map((alert) => {
                  const priorityInfo = getPriorityInfo(alert.priority_level);
                  return (
                    <TableRow
                      key={alert.id}
                      sx={{ backgroundColor: !alert.read_at ? 'action.hover' : 'transparent' }}
                    >
                      <TableCell>
                        <CircleIcon
                          sx={{
                            fontSize: 10,
                            color: !alert.read_at ? 'primary.main' : 'transparent',
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={!alert.read_at ? 600 : 400}>
                          {alert.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" component="div">
                          {alert.message}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={alert.alert_type_category?.replace('_', ' ') || 'Unknown'}
                          size="small"
                          color={getCategoryColor(alert.alert_type_category) as any}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip label={priorityInfo.label} size="small" color={priorityInfo.color} />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">{formatDate(alert.created_at)}</Typography>
                      </TableCell>
                      <TableCell align="center">
                        {!alert.read_at && (
                          <Tooltip title="Mark as read">
                            <IconButton size="small" onClick={() => handleMarkAsRead(alert.id)}>
                              <MarkEmailReadIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Dismiss">
                          <IconButton size="small" onClick={() => handleDismiss(alert.id)}>
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mt: 3, gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {formatRecordCount(page, DEFAULT_PAGE_SIZE, totalRecords)}
          </Typography>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, value) => setPage(value)}
            color="primary"
          />
        </Box>
      )}
    </Box>
  );
};

// Main AlertsPage component wrapped in appropriate layout based on user role
const AlertsPage: React.FC = () => {
  const { user } = useAuth();

  // For teachers, wrap in TeacherLayout
  if (user?.user_type?.toLowerCase() === 'teacher') {
    return (
      <TeacherLayout>
        <AlertManagementSystem />
      </TeacherLayout>
    );
  }

  // For students, wrap in StudentLayout
  if (user?.user_type?.toLowerCase() === 'student') {
    return (
      <StudentLayout>
        <AlertManagementSystem />
      </StudentLayout>
    );
  }

  // For admins, wrap in AdminLayout
  return (
    <AdminLayout>
      <AlertManagementSystem />
    </AdminLayout>
  );
};

export default AlertsPage;

