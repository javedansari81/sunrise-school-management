import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  Chip,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { InventoryStockProcurement } from '../../../services/inventoryService';

interface StockProcurementDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  procurement: InventoryStockProcurement | null;
}

const StockProcurementDetailsDialog: React.FC<StockProcurementDetailsDialogProps> = ({
  open,
  onClose,
  procurement
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  if (!procurement) return null;

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount: number): string => {
    return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
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
          Procurement Details
        </Typography>
      </DialogTitle>
      <DialogContent sx={{ px: { xs: 2, sm: 3 }, py: { xs: 2, sm: 2 } }}>
        <Box sx={{ mt: { xs: 1, sm: 2 } }}>
          {/* Invoice Number */}
          {procurement.invoice_number && (
            <Box sx={{
              mb: { xs: 2, sm: 3 },
              p: { xs: 1.5, sm: 2 },
              bgcolor: 'primary.50',
              borderRadius: 1
            }}>
              <Typography
                variant="h6"
                color="primary"
                sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
              >
                Invoice: {procurement.invoice_number}
              </Typography>
            </Box>
          )}

          {/* Procurement Information */}
          <Grid container spacing={{ xs: 2, sm: 3 }}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
              >
                Procurement Date
              </Typography>
              <Typography
                variant="body1"
                sx={{ fontSize: { xs: '0.875rem', sm: '1rem' }, fontWeight: 500 }}
              >
                {formatDate(procurement.procurement_date)}
              </Typography>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
              >
                Vendor
              </Typography>
              <Typography
                variant="body1"
                sx={{ fontSize: { xs: '0.875rem', sm: '1rem' }, fontWeight: 500 }}
              >
                {procurement.vendor_name || 'No Vendor'}
              </Typography>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
              >
                Payment Method
              </Typography>
              <Typography
                variant="body1"
                sx={{ fontSize: { xs: '0.875rem', sm: '1rem' }, fontWeight: 500 }}
              >
                {procurement.payment_method_name}
              </Typography>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
              >
                Payment Status
              </Typography>
              <Box sx={{ mt: 0.5 }}>
                <Chip
                  label={procurement.payment_status_name}
                  size="small"
                  color={procurement.payment_status_name === 'Paid' ? 'success' : 'warning'}
                  sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
                />
              </Box>
            </Grid>

            {procurement.payment_date && (
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
                >
                  Payment Date
                </Typography>
                <Typography
                  variant="body1"
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' }, fontWeight: 500 }}
                >
                  {formatDate(procurement.payment_date)}
                </Typography>
              </Grid>
            )}

            {procurement.payment_reference && (
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
                >
                  Payment Reference
                </Typography>
                <Typography
                  variant="body1"
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' }, fontWeight: 500 }}
                >
                  {procurement.payment_reference}
                </Typography>
              </Grid>
            )}

            {procurement.remarks && (
              <Grid size={{ xs: 12 }}>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
                >
                  Remarks
                </Typography>
                <Typography
                  variant="body1"
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {procurement.remarks}
                </Typography>
              </Grid>
            )}
          </Grid>

          <Divider sx={{ my: { xs: 2, sm: 3 } }} />

          {/* Items Table */}
          <Typography
            variant="subtitle1"
            sx={{ mb: 2, fontWeight: 600, fontSize: { xs: '0.875rem', sm: '1rem' } }}
          >
            Items Purchased
          </Typography>

          <TableContainer
            component={Paper}
            variant="outlined"
            sx={{ mb: { xs: 2, sm: 3 } }}
          >
            <Table size={isMobile ? 'small' : 'medium'}>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' }, fontWeight: 600 }}>
                    Item
                  </TableCell>
                  <TableCell sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' }, fontWeight: 600 }}>
                    Size
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' }, fontWeight: 600 }}
                  >
                    Quantity
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' }, fontWeight: 600 }}
                  >
                    Unit Cost
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' }, fontWeight: 600 }}
                  >
                    Total
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {procurement.items.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                      {item.item_type_description}
                    </TableCell>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                      {item.size_name || 'N/A'}
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                    >
                      {item.quantity}
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                    >
                      {formatCurrency(item.unit_cost)}
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, fontWeight: 500 }}
                    >
                      {formatCurrency(item.total_cost || item.quantity * item.unit_cost)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Total Amount */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'flex-end',
              p: { xs: 1.5, sm: 2 },
              bgcolor: 'grey.50',
              borderRadius: 1
            }}
          >
            <Typography
              variant="h6"
              sx={{ fontSize: { xs: '1rem', sm: '1.25rem' }, fontWeight: 600 }}
            >
              Total Amount: {formatCurrency(procurement.total_amount)}
            </Typography>
          </Box>

          {/* Created At */}
          <Box sx={{
            mt: { xs: 2, sm: 3 },
            pt: { xs: 1.5, sm: 2 },
            borderTop: 1,
            borderColor: 'divider'
          }}>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ fontSize: { xs: '0.7rem', sm: '0.75rem' } }}
            >
              Created on: {formatDate(procurement.created_at)}
            </Typography>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions sx={{
        px: { xs: 2, sm: 3 },
        py: { xs: 1.5, sm: 2 }
      }}>
        <Button
          onClick={onClose}
          variant="contained"
          fullWidth={isMobile}
          size={isMobile ? 'medium' : 'medium'}
          sx={{ fontSize: { xs: '0.875rem', sm: '0.875rem' } }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StockProcurementDetailsDialog;

