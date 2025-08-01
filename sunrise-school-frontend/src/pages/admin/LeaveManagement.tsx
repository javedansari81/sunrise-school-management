import React from 'react';
import {
  Typography,
  Box,
} from '@mui/material';
import AdminLayout from '../../components/Layout/AdminLayout';
import EmbeddedLeaveManagement from '../../components/admin/EmbeddedLeaveManagement';

const LeaveManagement: React.FC = () => {
  return (
    <AdminLayout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Leave Management System
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
          Manage employee leave requests and approvals
        </Typography>

        <EmbeddedLeaveManagement />
      </Box>
    </AdminLayout>
  );
};

export default LeaveManagement;
