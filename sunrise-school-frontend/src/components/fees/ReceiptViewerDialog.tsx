import React, { useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Box,
  Typography,
  Button,
  Tooltip,
  Paper
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DownloadIcon from '@mui/icons-material/Download';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

interface ReceiptViewerDialogProps {
  open: boolean;
  onClose: () => void;
  receiptUrl: string;
  receiptNumber: string;
  studentName?: string;
  receiptType?: 'fee' | 'transport';
}

const ReceiptViewerDialog: React.FC<ReceiptViewerDialogProps> = ({
  open,
  onClose,
  receiptUrl,
  receiptNumber,
  studentName,
  receiptType = 'fee'
}) => {

  // Auto-download when dialog opens (fast experience)
  useEffect(() => {
    if (open && receiptUrl) {
      // Small delay to show the dialog first
      const timer = setTimeout(() => {
        handleDownload();
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [open, receiptUrl]);

  // Handle download - triggers browser download
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = receiptUrl;
    link.download = `${receiptNumber}.pdf`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Handle open in new tab (for browser PDF viewer)
  const handleOpenInNewTab = () => {
    window.open(receiptUrl, '_blank');
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2
        }
      }}
    >
      {/* Header */}
      <DialogTitle
        sx={{
          bgcolor: receiptType === 'transport' ? '#2e7d32' : '#1976d2',
          color: 'white',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          py: 1.5,
          px: 2
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ReceiptLongIcon />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {receiptType === 'transport' ? 'Transport Receipt' : 'Fee Receipt'}
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small" sx={{ color: 'white' }}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      {/* Content */}
      <DialogContent sx={{ p: 3 }}>
        {/* Receipt Info Card */}
        <Paper
          elevation={0}
          sx={{
            p: 3,
            bgcolor: '#f8f9fa',
            borderRadius: 2,
            textAlign: 'center',
            border: '1px dashed #ccc'
          }}
        >
          <PictureAsPdfIcon sx={{ fontSize: 64, color: '#d32f2f', mb: 2 }} />

          <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
            {receiptNumber}
          </Typography>

          {studentName && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {studentName}
            </Typography>
          )}

          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 3 }}>
            Your receipt is ready! Click download to save or open in PDF viewer.
          </Typography>

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<DownloadIcon />}
              onClick={handleDownload}
              sx={{ px: 3 }}
            >
              Download
            </Button>

            <Tooltip title="Opens in browser PDF viewer">
              <Button
                variant="outlined"
                color="primary"
                startIcon={<OpenInNewIcon />}
                onClick={handleOpenInNewTab}
              >
                Open
              </Button>
            </Tooltip>
          </Box>
        </Paper>

        {/* Help Text */}
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{
            display: 'block',
            textAlign: 'center',
            mt: 2
          }}
        >
          💡 Tip: Downloaded receipts open faster with Adobe Reader or your default PDF app.
        </Typography>
      </DialogContent>
    </Dialog>
  );
};

export default ReceiptViewerDialog;

