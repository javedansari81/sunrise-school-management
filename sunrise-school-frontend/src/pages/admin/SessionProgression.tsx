import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
} from '@mui/material';
import {
  TrendingUp as SessionProgressionIcon,
  Construction as ConstructionIcon,
} from '@mui/icons-material';
import AdminLayout from '../../components/Layout/AdminLayout';

/**
 * SessionProgression Page - SUPER_ADMIN Only Feature
 * 
 * Purpose: Manage student academic progression at the end of each session year
 * - Promote students to the next class level
 * - Retain students to repeat their current class
 * - Demote students to a lower class if necessary
 * 
 * Phase 1: Placeholder page with "Coming soon..." message
 */
const SessionProgression: React.FC = () => {
  return (
    <AdminLayout>
      <Box sx={{ p: { xs: 2, sm: 3 } }}>
        {/* Page Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <SessionProgressionIcon sx={{ fontSize: 32, color: 'primary.main' }} />
            <Typography variant="h4" fontWeight="bold" color="primary">
              Session Progression
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary">
            Manage student academic transitions between sessions
          </Typography>
        </Box>

        {/* Coming Soon Card */}
        <Card
          sx={{
            maxWidth: 600,
            mx: 'auto',
            mt: 8,
            textAlign: 'center',
            boxShadow: 3,
            borderRadius: 3,
          }}
        >
          <CardContent sx={{ py: 6, px: 4 }}>
            <ConstructionIcon
              sx={{
                fontSize: 80,
                color: 'warning.main',
                mb: 3,
              }}
            />
            <Typography
              variant="h4"
              fontWeight="bold"
              color="text.primary"
              gutterBottom
            >
              Coming soon...
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ mb: 3, maxWidth: 400, mx: 'auto' }}
            >
              The Session Progression feature is currently under development.
              This feature will allow you to:
            </Typography>
            <Box sx={{ textAlign: 'left', maxWidth: 350, mx: 'auto', mb: 3 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                • <strong>Promote</strong> students to the next class level
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                • <strong>Retain</strong> students to repeat their current class
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • <strong>Demote</strong> students to a lower class if necessary
              </Typography>
            </Box>
            <Alert severity="info" sx={{ mt: 3 }}>
              This feature is exclusive to SUPER_ADMIN users and will be available soon.
            </Alert>
          </CardContent>
        </Card>
      </Box>
    </AdminLayout>
  );
};

export default SessionProgression;

