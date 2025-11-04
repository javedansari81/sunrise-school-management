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
  Chip
} from '@mui/material';
import { InventoryPurchase } from '../../../services/inventoryService';

interface PurchaseDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  purchase: InventoryPurchase | null;
}

const PurchaseDetailsDialog: React.FC<PurchaseDetailsDialogProps> = ({
  open,
  onClose,
  purchase
}) => {
  if (!purchase) return null;

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ bgcolor: 'white', borderBottom: 1, borderColor: 'divider' }}>
        Purchase Details
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          {/* Receipt Number */}
          <Box sx={{ mb: 3, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
            <Typography variant="h6" color="primary">
              Receipt: {purchase.receipt_number}
            </Typography>
          </Box>

          {/* Student Information */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Student Information
            </Typography>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Name
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.student_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Admission Number
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.student_admission_number}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Class
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.student_class_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Roll Number
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.student_roll_number || 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Purchase Information */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Purchase Information
            </Typography>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Purchase Date
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {formatDate(purchase.purchase_date)}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Session Year
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.session_year_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Purchased By
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.purchased_by || 'N/A'}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Contact Number
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.contact_number || 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Items Table */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Items Purchased
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ bgcolor: 'white' }}>
                    <TableCell width={60}>Image</TableCell>
                    <TableCell>Item</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Unit Price</TableCell>
                    <TableCell align="right">Total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {purchase.items.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        {item.item_image_url ? (
                          <Box
                            component="img"
                            src={item.item_image_url}
                            alt={item.item_type_description}
                            sx={{
                              width: 40,
                              height: 40,
                              objectFit: 'cover',
                              borderRadius: 1,
                            }}
                          />
                        ) : (
                          <Box
                            sx={{
                              width: 40,
                              height: 40,
                              bgcolor: 'grey.200',
                              borderRadius: 1,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <Typography variant="caption" color="text.secondary" fontSize={10}>
                              No Img
                            </Typography>
                          </Box>
                        )}
                      </TableCell>
                      <TableCell>{item.item_type_description}</TableCell>
                      <TableCell>{item.size_name || 'N/A'}</TableCell>
                      <TableCell align="right">{item.quantity}</TableCell>
                      <TableCell align="right">₹{Number(item.unit_price).toFixed(2)}</TableCell>
                      <TableCell align="right">₹{Number(item.total_price).toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow>
                    <TableCell colSpan={5} align="right">
                      <Typography variant="subtitle1" fontWeight={600}>
                        Total Amount:
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="subtitle1" fontWeight={600} color="primary">
                        ₹{Number(purchase.total_amount).toFixed(2)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Payment Information */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Payment Information
            </Typography>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Payment Method
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.payment_method_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Payment Date
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.payment_date ? formatDate(purchase.payment_date) : 'N/A'}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography variant="body2" color="text.secondary">
                  Transaction ID
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {purchase.transaction_id || 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </Box>

          {/* Remarks */}
          {purchase.remarks && (
            <>
              <Divider sx={{ my: 2 }} />
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Remarks
                </Typography>
                <Typography variant="body1">
                  {purchase.remarks}
                </Typography>
              </Box>
            </>
          )}

          {/* Created At */}
          <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="caption" color="text.secondary">
              Created on: {formatDate(purchase.created_at)}
            </Typography>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PurchaseDetailsDialog;

