import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Paper,
  Divider,
  Alert,
  Stack,
  Grid
} from '@mui/material';
import {
  People as PeopleIcon,
  Person as PersonIcon,
  School as SchoolIcon,
  Discount as DiscountIcon
} from '@mui/icons-material';

interface SiblingInfo {
  id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  class_name: string;
  section?: string;
  date_of_birth?: string;
  is_active: boolean;
}

interface SiblingRelationship {
  id: number;
  sibling_student_id: number;
  relationship_type: string;
  is_auto_detected: boolean;
  birth_order: number;
  fee_waiver_percentage: number;
  is_active: boolean;
  sibling_info: SiblingInfo;
  waiver_description: string;
  birth_order_description: string;
}

interface SiblingWaiverInfo {
  has_siblings: boolean;
  total_siblings_count: number;
  birth_order: number;
  birth_order_description: string;
  fee_waiver_percentage: number;
  waiver_reason?: string;
  siblings: SiblingRelationship[];
}

interface SiblingInfoDisplayProps {
  waiverInfo?: SiblingWaiverInfo;
  compact?: boolean;
}

const SiblingInfoDisplay: React.FC<SiblingInfoDisplayProps> = ({ waiverInfo, compact = false }) => {
  if (!waiverInfo || !waiverInfo.has_siblings) {
    return null;
  }

  if (compact) {
    return (
      <Box sx={{ p: 2, bgcolor: 'info.lighter', borderRadius: 1, border: '1px solid', borderColor: 'info.light' }}>
        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PeopleIcon color="info" fontSize="small" />
            <Typography variant="body2" fontWeight="medium">
              {waiverInfo.total_siblings_count} Siblings
            </Typography>
          </Box>
          <Divider orientation="vertical" flexItem />
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PersonIcon color="info" fontSize="small" />
            <Typography variant="body2">
              {waiverInfo.birth_order_description}
            </Typography>
          </Box>
          {waiverInfo.fee_waiver_percentage > 0 && (
            <>
              <Divider orientation="vertical" flexItem />
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <DiscountIcon color="success" fontSize="small" />
                <Typography variant="body2" color="success.main" fontWeight="medium">
                  {waiverInfo.fee_waiver_percentage}% Fee Waiver
                </Typography>
              </Box>
            </>
          )}
        </Stack>
      </Box>
    );
  }

  return (
    <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50', border: '1px solid', borderColor: 'grey.200' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <PeopleIcon color="primary" />
        <Typography variant="h6" color="primary">
          Sibling Information
        </Typography>
      </Box>

      {/* Waiver Summary */}
      {waiverInfo.fee_waiver_percentage > 0 && (
        <Alert severity="success" sx={{ mb: 2 }}>
          <Typography variant="body2" fontWeight="medium">
            {waiverInfo.waiver_reason}
          </Typography>
          <Typography variant="body2" sx={{ mt: 0.5 }}>
            Fee Waiver: <strong>{waiverInfo.fee_waiver_percentage}%</strong>
          </Typography>
        </Alert>
      )}

      {/* Student's Position */}
      <Box sx={{ mb: 2, p: 2, bgcolor: 'white', borderRadius: 1 }}>
        <Grid container spacing={2}>
          <Grid size={{ xs: 6 }}>
            <Typography variant="body2" color="textSecondary">
              Total Siblings
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {waiverInfo.total_siblings_count}
            </Typography>
          </Grid>
          <Grid size={{ xs: 6 }}>
            <Typography variant="body2" color="textSecondary">
              Birth Order
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {waiverInfo.birth_order_description}
            </Typography>
          </Grid>
        </Grid>
      </Box>

      {/* Siblings List */}
      <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
        Linked Siblings ({waiverInfo.siblings.length})
      </Typography>
      <Stack spacing={1.5}>
        {waiverInfo.siblings.map((sibling) => (
          <Paper key={sibling.id} elevation={0} sx={{ p: 2, border: '1px solid', borderColor: 'grey.300' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="body1" fontWeight="medium">
                  {sibling.sibling_info.full_name}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                  <Chip
                    icon={<SchoolIcon />}
                    label={`${sibling.sibling_info.class_name}${sibling.sibling_info.section ? ` - ${sibling.sibling_info.section}` : ''}`}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label={`Admission No: ${sibling.sibling_info.admission_number}`}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label={sibling.birth_order_description}
                    size="small"
                    color="info"
                  />
                  {sibling.is_auto_detected && (
                    <Chip
                      label="Auto-detected"
                      size="small"
                      color="default"
                      variant="outlined"
                    />
                  )}
                </Box>
              </Box>
            </Box>
          </Paper>
        ))}
      </Stack>
    </Paper>
  );
};

export default SiblingInfoDisplay;

