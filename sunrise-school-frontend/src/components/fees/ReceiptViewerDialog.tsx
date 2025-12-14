import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Box,
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

interface ReceiptViewerDialogProps {
  open: boolean;
  onClose: () => void;
  receiptUrl: string;
  receiptNumber: string;
  studentName?: string;
}

const ReceiptViewerDialog: React.FC<ReceiptViewerDialogProps> = ({
  open,
  onClose,
  receiptUrl,
  receiptNumber,
  studentName
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // Use Google Docs Viewer to display PDF inline (workaround for Cloudinary download issue)
  const getViewerUrl = (url: string) => {
    if (!url) return url;

    // Use Google Docs Viewer to display PDF inline
    // This works around Cloudinary's Content-Disposition: attachment header
    return `https://docs.google.com/viewer?url=${encodeURIComponent(url)}&embedded=true`;
  };

  const viewerUrl = getViewerUrl(receiptUrl);

  // Reset loading state when dialog opens
  React.useEffect(() => {
    if (open) {
      setLoading(true);
      setError(false);
      // Set a timeout to hide loading after 1 second
      const timer = setTimeout(() => {
        setLoading(false);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [open, receiptUrl]);

  // Reset state when dialog closes
  const handleClose = () => {
    setLoading(true);
    setError(false);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          height: '90vh',
          maxHeight: '900px'
        }
      }}
    >
      {/* Header */}
      <DialogTitle
        sx={{
          bgcolor: 'white',
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          py: 1.5,
          px: 2
        }}
      >
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Fee Receipt
          </Typography>
          {studentName && (
            <Typography variant="caption" color="text.secondary">
              {studentName} - {receiptNumber}
            </Typography>
          )}
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {/* Close Button */}
          <IconButton onClick={handleClose} size="small">
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
      </DialogTitle>

      {/* Content */}
      <DialogContent sx={{ p: 0, position: 'relative', bgcolor: '#f5f5f5' }}>
        {/* Loading Indicator */}
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 1
            }}
          >
            <CircularProgress />
          </Box>
        )}

        {/* Error Message */}
        {error && (
          <Box sx={{ p: 3 }}>
            <Alert severity="error">
              Failed to load receipt. Please close and try again.
            </Alert>
          </Box>
        )}

        {/* PDF Viewer using Google Docs Viewer */}
        {!error && (
          <iframe
            src={viewerUrl}
            title="Receipt Viewer"
            style={{
              width: '100%',
              height: '100%',
              border: 'none'
            }}
          />
        )}
      </DialogContent>
    </Dialog>
  );
};

export default ReceiptViewerDialog;

