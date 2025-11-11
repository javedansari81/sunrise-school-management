import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  CircularProgress,
  Box,
  Grid,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { updateStockThreshold, InventoryStock } from '../../../services/inventoryService';

interface StockThresholdDialogProps {
  open: boolean;
  onClose: () => void;
  stock: InventoryStock | null;
  onSuccess: () => void;
  onError: (message: string) => void;
}

const StockThresholdDialog: React.FC<StockThresholdDialogProps> = ({
  open,
  onClose,
  stock,
  onSuccess,
  onError
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [currentQuantity, setCurrentQuantity] = useState<number>(0);
  const [minimumThreshold, setMinimumThreshold] = useState<number>(0);
  const [reorderQuantity, setReorderQuantity] = useState<number>(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (stock) {
      setCurrentQuantity(stock.current_quantity);
      setMinimumThreshold(stock.minimum_threshold);
      setReorderQuantity(stock.reorder_quantity);
    }
  }, [stock]);

  const handleSubmit = async () => {
    if (!stock) return;

    // Validation
    if (currentQuantity < 0 || minimumThreshold < 0 || reorderQuantity < 0) {
      onError('All values must be non-negative');
      return;
    }

    setLoading(true);
    try {
      await updateStockThreshold(stock.id, {
        current_quantity: currentQuantity,
        minimum_threshold: minimumThreshold,
        reorder_quantity: reorderQuantity
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error updating stock threshold:', err);
      onError(err.response?.data?.detail || 'Failed to update stock threshold');
    } finally {
      setLoading(false);
    }
  };

  if (!stock) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      fullScreen={isMobile}
      PaperProps={{
        sx: {
          m: { xs: 0, sm: 2 },
          maxHeight: { xs: '100%', sm: '90vh' }
        }
      }}
    >
      <DialogTitle sx={{
        bgcolor: 'white',
        borderBottom: 1,
        borderColor: 'divider',
        py: { xs: 1.5, sm: 2 },
        px: { xs: 2, sm: 3 }
      }}>
        <Typography variant="h6" sx={{ fontSize: { xs: '1.125rem', sm: '1.25rem' } }}>
          Update Stock Thresholds
        </Typography>
      </DialogTitle>
      <DialogContent sx={{ px: { xs: 2, sm: 3 }, py: { xs: 2, sm: 2 } }}>
        <Box sx={{ mt: { xs: 1, sm: 2 } }}>
          {/* Item Info */}
          <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
              {stock.item_type_description}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Size: {stock.size_name || 'N/A'}
            </Typography>
            {stock.item_category && (
              <Typography variant="body2" color="text.secondary">
                Category: {stock.item_category}
              </Typography>
            )}
          </Box>

          {/* Form Fields */}
          <Grid container spacing={2}>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Current Quantity"
                type="number"
                value={currentQuantity}
                onChange={(e) => setCurrentQuantity(Number(e.target.value))}
                inputProps={{ min: 0 }}
                helperText="Actual quantity in stock"
                size={isMobile ? 'small' : 'medium'}
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Minimum Threshold"
                type="number"
                value={minimumThreshold}
                onChange={(e) => setMinimumThreshold(Number(e.target.value))}
                inputProps={{ min: 0 }}
                helperText="Alert when stock falls below this level"
                size={isMobile ? 'small' : 'medium'}
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Reorder Quantity"
                type="number"
                value={reorderQuantity}
                onChange={(e) => setReorderQuantity(Number(e.target.value))}
                inputProps={{ min: 0 }}
                helperText="Suggested quantity to reorder"
                size={isMobile ? 'small' : 'medium'}
              />
            </Grid>
          </Grid>

          {/* Warning Message */}
          {currentQuantity <= minimumThreshold && (
            <Box sx={{ mt: 2, p: 1.5, bgcolor: 'warning.50', borderRadius: 1, border: 1, borderColor: 'warning.main' }}>
              <Typography variant="body2" color="warning.dark">
                ⚠️ Warning: Current quantity is at or below minimum threshold
              </Typography>
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions sx={{
        px: { xs: 2, sm: 3 },
        py: { xs: 1.5, sm: 2 },
        gap: 1
      }}>
        <Button
          onClick={onClose}
          disabled={loading}
          variant="outlined"
          fullWidth={isMobile}
          size={isMobile ? 'medium' : 'medium'}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={loading}
          variant="contained"
          fullWidth={isMobile}
          size={isMobile ? 'medium' : 'medium'}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Updating...' : 'Update'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StockThresholdDialog;

