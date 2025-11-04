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
  useMediaQuery,
  useTheme
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
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  if (!purchase) return null;

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
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
          Purchase Details
        </Typography>
      </DialogTitle>
      <DialogContent sx={{ px: { xs: 2, sm: 3 }, py: { xs: 2, sm: 2 } }}>
        <Box sx={{ mt: { xs: 1, sm: 2 } }}>
          {/* Receipt Number */}
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
              Receipt: {purchase.receipt_number}
            </Typography>
          </Box>

          {/* Student Information */}
          <Box sx={{ mb: { xs: 2, sm: 3 } }}>
            <Typography
              variant="subtitle2"
              color="text.secondary"
              gutterBottom
              sx={{ fontSize: { xs: '0.875rem', sm: '0.875rem' }, fontWeight: 600 }}
            >
              Student Information
            </Typography>
            <Grid container spacing={{ xs: 1.5, sm: 2 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Name
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.student_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Admission Number
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.student_admission_number}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Class
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.student_class_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Roll Number
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.student_roll_number || 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </Box>

          <Divider sx={{ my: { xs: 1.5, sm: 2 } }} />

          {/* Purchase Information */}
          <Box sx={{ mb: { xs: 2, sm: 3 } }}>
            <Typography
              variant="subtitle2"
              color="text.secondary"
              gutterBottom
              sx={{ fontSize: { xs: '0.875rem', sm: '0.875rem' }, fontWeight: 600 }}
            >
              Purchase Information
            </Typography>
            <Grid container spacing={{ xs: 1.5, sm: 2 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Purchase Date
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {formatDate(purchase.purchase_date)}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Session Year
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.session_year_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Purchased By
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.purchased_by || 'N/A'}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Contact Number
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.contact_number || 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </Box>

          <Divider sx={{ my: { xs: 1.5, sm: 2 } }} />

          {/* Items Table */}
          <Box sx={{ mb: { xs: 2, sm: 3 } }}>
            <Typography
              variant="subtitle2"
              color="text.secondary"
              gutterBottom
              sx={{ fontSize: { xs: '0.875rem', sm: '0.875rem' }, fontWeight: 600 }}
            >
              Items Purchased
            </Typography>
            <TableContainer
              component={Paper}
              variant="outlined"
              sx={{
                maxHeight: { xs: '300px', sm: '400px' },
                overflowX: 'auto',
                overflowY: 'auto'
              }}
            >
              <Table size={isMobile ? 'small' : 'small'} stickyHeader>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'white' }}>
                    <TableCell
                      width={isMobile ? 50 : 60}
                      sx={{
                        fontSize: { xs: '0.75rem', sm: '0.875rem' },
                        py: { xs: 1, sm: 1.5 }
                      }}
                    >
                      Image
                    </TableCell>
                    <TableCell
                      sx={{
                        fontSize: { xs: '0.75rem', sm: '0.875rem' },
                        py: { xs: 1, sm: 1.5 },
                        minWidth: { xs: 100, sm: 120 }
                      }}
                    >
                      Item
                    </TableCell>
                    <TableCell
                      sx={{
                        fontSize: { xs: '0.75rem', sm: '0.875rem' },
                        py: { xs: 1, sm: 1.5 },
                        minWidth: { xs: 60, sm: 80 }
                      }}
                    >
                      Size
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{
                        fontSize: { xs: '0.75rem', sm: '0.875rem' },
                        py: { xs: 1, sm: 1.5 },
                        minWidth: { xs: 60, sm: 80 }
                      }}
                    >
                      Quantity
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{
                        fontSize: { xs: '0.75rem', sm: '0.875rem' },
                        py: { xs: 1, sm: 1.5 },
                        minWidth: { xs: 80, sm: 100 }
                      }}
                    >
                      Unit Price
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{
                        fontSize: { xs: '0.75rem', sm: '0.875rem' },
                        py: { xs: 1, sm: 1.5 },
                        minWidth: { xs: 80, sm: 100 }
                      }}
                    >
                      Total
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {purchase.items.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell sx={{ py: { xs: 0.5, sm: 1 } }}>
                        {item.item_image_url ? (
                          <Box
                            component="img"
                            src={item.item_image_url}
                            alt={item.item_type_description}
                            sx={{
                              width: { xs: 35, sm: 40 },
                              height: { xs: 35, sm: 40 },
                              objectFit: 'cover',
                              borderRadius: 1,
                            }}
                          />
                        ) : (
                          <Box
                            sx={{
                              width: { xs: 35, sm: 40 },
                              height: { xs: 35, sm: 40 },
                              bgcolor: 'grey.200',
                              borderRadius: 1,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              fontSize={{ xs: 8, sm: 10 }}
                            >
                              No Img
                            </Typography>
                          </Box>
                        )}
                      </TableCell>
                      <TableCell sx={{
                        py: { xs: 0.5, sm: 1 },
                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                      }}>
                        {item.item_type_description}
                      </TableCell>
                      <TableCell sx={{
                        py: { xs: 0.5, sm: 1 },
                        fontSize: { xs: '0.75rem', sm: '0.875rem' }
                      }}>
                        {item.size_name || 'N/A'}
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{
                          py: { xs: 0.5, sm: 1 },
                          fontSize: { xs: '0.75rem', sm: '0.875rem' }
                        }}
                      >
                        {item.quantity}
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{
                          py: { xs: 0.5, sm: 1 },
                          fontSize: { xs: '0.75rem', sm: '0.875rem' }
                        }}
                      >
                        ₹{Number(item.unit_price).toFixed(2)}
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{
                          py: { xs: 0.5, sm: 1 },
                          fontSize: { xs: '0.75rem', sm: '0.875rem' }
                        }}
                      >
                        ₹{Number(item.total_price).toFixed(2)}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow>
                    <TableCell
                      colSpan={5}
                      align="right"
                      sx={{ py: { xs: 1, sm: 1.5 } }}
                    >
                      <Typography
                        variant="subtitle1"
                        fontWeight={600}
                        sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                      >
                        Total Amount:
                      </Typography>
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{ py: { xs: 1, sm: 1.5 } }}
                    >
                      <Typography
                        variant="subtitle1"
                        fontWeight={600}
                        color="primary"
                        sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                      >
                        ₹{Number(purchase.total_amount).toFixed(2)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Box>

          <Divider sx={{ my: { xs: 1.5, sm: 2 } }} />

          {/* Payment Information */}
          <Box sx={{ mb: { xs: 2, sm: 3 } }}>
            <Typography
              variant="subtitle2"
              color="text.secondary"
              gutterBottom
              sx={{ fontSize: { xs: '0.875rem', sm: '0.875rem' }, fontWeight: 600 }}
            >
              Payment Information
            </Typography>
            <Grid container spacing={{ xs: 1.5, sm: 2 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Payment Method
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.payment_method_name}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Payment Date
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.payment_date ? formatDate(purchase.payment_date) : 'N/A'}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                >
                  Transaction ID
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={500}
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.transaction_id || 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </Box>

          {/* Remarks */}
          {purchase.remarks && (
            <>
              <Divider sx={{ my: { xs: 1.5, sm: 2 } }} />
              <Box>
                <Typography
                  variant="subtitle2"
                  color="text.secondary"
                  gutterBottom
                  sx={{ fontSize: { xs: '0.875rem', sm: '0.875rem' }, fontWeight: 600 }}
                >
                  Remarks
                </Typography>
                <Typography
                  variant="body1"
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {purchase.remarks}
                </Typography>
              </Box>
            </>
          )}

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
              Created on: {formatDate(purchase.created_at)}
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

export default PurchaseDetailsDialog;

