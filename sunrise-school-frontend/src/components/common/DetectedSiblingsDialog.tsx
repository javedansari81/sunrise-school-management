import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
  Stack
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  People as PeopleIcon,
  School as SchoolIcon,
  Discount as DiscountIcon
} from '@mui/icons-material';

interface DetectedSibling {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  class_name: string;
  section?: string;
  date_of_birth?: string;
}

interface DetectedSiblingsInfo {
  siblings: DetectedSibling[];
  total_siblings_count: number;
  birth_order: number;
  birth_order_description: string;
  fee_waiver_percentage: number;
  waiver_reason?: string;
  message: string;
}

interface DetectedSiblingsDialogProps {
  open: boolean;
  onClose: () => void;
  detectedSiblingsInfo?: DetectedSiblingsInfo;
  studentName: string;
}

const DetectedSiblingsDialog: React.FC<DetectedSiblingsDialogProps> = ({
  open,
  onClose,
  detectedSiblingsInfo,
  studentName
}) => {
  if (!detectedSiblingsInfo) {
    return null;
  }

  const { siblings, total_siblings_count, birth_order_description, fee_waiver_percentage, waiver_reason } = detectedSiblingsInfo;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ bgcolor: 'success.lighter', borderBottom: '1px solid', borderColor: 'success.light' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CheckCircleIcon color="success" />
          <Typography variant="h6" color="success.dark">
            Siblings Detected & Linked
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 3 }}>
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="body2" fontWeight="medium" gutterBottom>
            Student created successfully!
          </Typography>
          <Typography variant="body2">
            We automatically detected and linked {siblings.length} sibling{siblings.length > 1 ? 's' : ''} based on matching father's name and phone number.
          </Typography>
        </Alert>

        {/* Student Summary */}
        <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="subtitle2" color="primary" gutterBottom>
            {studentName}
          </Typography>
          <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
            <Box>
              <Typography variant="caption" color="textSecondary">
                Total Siblings
              </Typography>
              <Typography variant="body2" fontWeight="medium">
                {total_siblings_count}
              </Typography>
            </Box>
            <Divider orientation="vertical" flexItem />
            <Box>
              <Typography variant="caption" color="textSecondary">
                Birth Order
              </Typography>
              <Typography variant="body2" fontWeight="medium">
                {birth_order_description}
              </Typography>
            </Box>
            {fee_waiver_percentage > 0 && (
              <>
                <Divider orientation="vertical" flexItem />
                <Box>
                  <Typography variant="caption" color="textSecondary">
                    Fee Waiver
                  </Typography>
                  <Typography variant="body2" fontWeight="medium" color="success.main">
                    {fee_waiver_percentage}%
                  </Typography>
                </Box>
              </>
            )}
          </Stack>
        </Box>

        {/* Fee Waiver Info */}
        {fee_waiver_percentage > 0 && waiver_reason && (
          <Alert severity="info" icon={<DiscountIcon />} sx={{ mb: 3 }}>
            <Typography variant="body2">
              {waiver_reason}
            </Typography>
          </Alert>
        )}

        {/* Detected Siblings List */}
        <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PeopleIcon fontSize="small" color="primary" />
          Detected Siblings
        </Typography>
        <List sx={{ bgcolor: 'background.paper', border: '1px solid', borderColor: 'grey.300', borderRadius: 1 }}>
          {siblings.map((sibling, index) => (
            <React.Fragment key={sibling.student_id}>
              {index > 0 && <Divider />}
              <ListItem>
                <ListItemText
                  primary={
                    <Typography variant="body2" fontWeight="medium">
                      {sibling.full_name}
                    </Typography>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, flexWrap: 'wrap' }}>
                      <Chip
                        icon={<SchoolIcon />}
                        label={`${sibling.class_name}${sibling.section ? ` - ${sibling.section}` : ''}`}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={`Roll: ${sibling.admission_number}`}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  }
                />
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      </DialogContent>

      <DialogActions sx={{ p: 2, bgcolor: 'grey.50' }}>
        <Button onClick={onClose} variant="contained" color="primary">
          Got it
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DetectedSiblingsDialog;

