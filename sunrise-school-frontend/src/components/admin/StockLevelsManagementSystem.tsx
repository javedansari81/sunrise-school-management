import React, { useState } from 'react';
import {
  Box,
  Snackbar,
  Alert,
  TextField,
  MenuItem,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import StockLevelsTab from './inventory/StockLevelsTab';
import CollapsibleFilterSection from '../common/CollapsibleFilterSection';

interface StockLevelsManagementSystemProps {
  configuration: any;
}

const StockLevelsManagementSystem: React.FC<StockLevelsManagementSystemProps> = ({ configuration }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Filter state
  const [itemTypeId, setItemTypeId] = useState<number | null>(null);
  const [sizeTypeId, setSizeTypeId] = useState<number | null>(null);
  const [stockStatus, setStockStatus] = useState<string>('all');

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
        persistKey="stock-levels-management"
      >
        <Box sx={{
          display: 'flex',
          gap: { xs: 1.5, sm: 2 },
          flexWrap: 'wrap',
          flexDirection: { xs: 'column', sm: 'row' }
        }}>
          <TextField
            select
            label="Item Type"
            value={itemTypeId || ''}
            onChange={(e) => setItemTypeId(e.target.value ? Number(e.target.value) : null)}
            sx={{ minWidth: { xs: '100%', sm: 200 } }}
            size="small"
            fullWidth={isMobile}
          >
            <MenuItem value="">All Items</MenuItem>
            {configuration?.inventory_item_types?.map((item: any) => (
              <MenuItem key={item.id} value={item.id}>
                {item.description}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Size"
            value={sizeTypeId || ''}
            onChange={(e) => setSizeTypeId(e.target.value ? Number(e.target.value) : null)}
            sx={{ minWidth: { xs: '100%', sm: 150 } }}
            size="small"
            fullWidth={isMobile}
          >
            <MenuItem value="">All Sizes</MenuItem>
            {configuration?.inventory_size_types?.map((size: any) => (
              <MenuItem key={size.id} value={size.id}>
                {size.name}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Stock Status"
            value={stockStatus}
            onChange={(e) => setStockStatus(e.target.value)}
            sx={{ minWidth: { xs: '100%', sm: 150 } }}
            size="small"
            fullWidth={isMobile}
          >
            <MenuItem value="all">All Stock</MenuItem>
            <MenuItem value="low">Low Stock Only</MenuItem>
          </TextField>
        </Box>
      </CollapsibleFilterSection>

      {/* Stock Levels Tab */}
      <StockLevelsTab
        configuration={configuration}
        onError={(message: string) => setSnackbar({ open: true, message, severity: 'error' })}
        itemTypeId={itemTypeId}
        sizeTypeId={sizeTypeId}
        stockStatus={stockStatus}
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
    </Box>
  );
};

export default StockLevelsManagementSystem;

