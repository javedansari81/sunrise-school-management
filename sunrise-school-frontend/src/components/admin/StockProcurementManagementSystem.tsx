import React, { useState } from 'react';
import {
  Box,
  Snackbar,
  Alert,
  TextField,
  useMediaQuery,
  useTheme,
  Fab,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import StockProcurementsTab from './inventory/StockProcurementsTab';
import CollapsibleFilterSection from '../common/CollapsibleFilterSection';

interface StockProcurementManagementSystemProps {
  configuration: any;
}

const StockProcurementManagementSystem: React.FC<StockProcurementManagementSystemProps> = ({ configuration }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Filter state
  const [fromDate, setFromDate] = useState<string>('');
  const [toDate, setToDate] = useState<string>('');

  // Dialog control state
  const [procurementDialogOpen, setProcurementDialogOpen] = useState(false);

  // Snackbar
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Collapsible Filter Section */}
      <CollapsibleFilterSection
        title="Filters"
        defaultExpanded={true}
        persistKey="stock-procurement"
      >
        <Box sx={{
          display: 'flex',
          gap: { xs: 1.5, sm: 2 },
          flexWrap: 'wrap',
          flexDirection: { xs: 'column', sm: 'row' }
        }}>
          <TextField
            type="date"
            label="From Date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            slotProps={{ inputLabel: { shrink: true } }}
            size="small"
            sx={{ minWidth: { xs: '100%', sm: 200 } }}
            fullWidth={isMobile}
          />

          <TextField
            type="date"
            label="To Date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            slotProps={{ inputLabel: { shrink: true } }}
            size="small"
            sx={{ minWidth: { xs: '100%', sm: 200 } }}
            fullWidth={isMobile}
          />
        </Box>
      </CollapsibleFilterSection>

      {/* Stock Procurements */}
      <StockProcurementsTab
        configuration={configuration}
        onError={(message: string) => setSnackbar({ open: true, message, severity: 'error' })}
        onSuccess={(message: string) => setSnackbar({ open: true, message, severity: 'success' })}
        fromDate={fromDate}
        toDate={toDate}
        dialogOpen={procurementDialogOpen}
        onDialogClose={() => setProcurementDialogOpen(false)}
      />

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add procurement"
        variant="extended"
        onClick={() => setProcurementDialogOpen(true)}
        sx={{
          position: 'fixed',
          bottom: { xs: 16, sm: 24 },
          right: { xs: 16, sm: 24 },
          zIndex: 1000,
          minWidth: { xs: '48px', sm: '56px' },
          width: { xs: '48px', sm: '56px' },
          height: { xs: '48px', sm: '56px' },
          borderRadius: { xs: '24px', sm: '28px' },
          padding: { xs: '0 12px', sm: '0 16px' },
          transition: 'all 0.3s ease-in-out',
          overflow: 'hidden',
          boxShadow: 3,
          '& .MuiSvgIcon-root': {
            transition: 'margin 0.3s ease-in-out',
            marginRight: 0,
            fontSize: { xs: '1.25rem', sm: '1.5rem' },
          },
          '& .fab-text': {
            opacity: 0,
            width: 0,
            whiteSpace: 'nowrap',
            transition: 'opacity 0.3s ease-in-out, width 0.3s ease-in-out',
            overflow: 'hidden',
            fontSize: '0.875rem',
            fontWeight: 500,
            display: { xs: 'none', sm: 'inline' },
          },
          '@media (hover: hover) and (pointer: fine)': {
            '&:hover': {
              width: 'auto',
              minWidth: '180px',
              paddingRight: '20px',
              paddingLeft: '16px',
              boxShadow: 6,
              '& .MuiSvgIcon-root': {
                marginRight: '8px',
              },
              '& .fab-text': {
                opacity: 1,
                width: 'auto',
              },
            },
          },
          '&:active': {
            boxShadow: 6,
            transform: 'scale(0.95)',
          },
          '@media (max-width: 360px)': {
            bottom: '12px',
            right: '12px',
            minWidth: '44px',
            width: '44px',
            height: '44px',
            borderRadius: '22px',
          },
        }}
      >
        <AddIcon />
        <Box component="span" className="fab-text">
          New Procurement
        </Box>
      </Fab>
    </Box>
  );
};

export default StockProcurementManagementSystem;
