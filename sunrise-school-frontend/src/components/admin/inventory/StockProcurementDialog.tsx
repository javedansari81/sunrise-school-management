import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Typography,
  CircularProgress,
  Box,
  Grid,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { createStockProcurement, updateStockProcurement, InventoryStockProcurement } from '../../../services/inventoryService';
import { vendorAPI } from '../../../services/api';

interface StockProcurementDialogProps {
  open: boolean;
  onClose: () => void;
  configuration: any;
  onSuccess: () => void;
  onError: (message: string) => void;
  procurement?: InventoryStockProcurement | null;  // For edit mode
}

interface ProcurementItem {
  inventory_item_category_id?: number;
  inventory_item_type_id: number;
  size_type_id?: number;
  quantity: number;
  unit_cost: number;
}

const StockProcurementDialog: React.FC<StockProcurementDialogProps> = ({
  open,
  onClose,
  configuration,
  onSuccess,
  onError,
  procurement
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Determine if we're in edit mode
  const isEditMode = !!procurement;

  // State
  const [loading, setLoading] = useState(false);
  const [vendors, setVendors] = useState<any[]>([]);
  const [vendorId, setVendorId] = useState<number | ''>('');
  const [procurementDate, setProcurementDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [invoiceNumber, setInvoiceNumber] = useState<string>('');
  const [paymentMethodId, setPaymentMethodId] = useState<number>(0);
  const [paymentStatusId, setPaymentStatusId] = useState<number>(0);
  const [paymentDate, setPaymentDate] = useState<string>('');
  const [paymentReference, setPaymentReference] = useState<string>('');
  const [remarks, setRemarks] = useState<string>('');
  const [items, setItems] = useState<ProcurementItem[]>([
    { inventory_item_category_id: undefined, inventory_item_type_id: 0, size_type_id: undefined, quantity: 1, unit_cost: 0 }
  ]);

  // Fetch vendors and initialize form
  useEffect(() => {
    if (open) {
      fetchVendors();
      if (procurement) {
        initializeFormWithProcurement(procurement);
      } else {
        resetForm();
      }
    }
  }, [open, procurement]);

  const fetchVendors = async () => {
    try {
      const data = await vendorAPI.getVendors();
      setVendors(data);
    } catch (err) {
      console.error('Error fetching vendors:', err);
    }
  };

  const initializeFormWithProcurement = (proc: InventoryStockProcurement) => {
    setVendorId(proc.vendor_id || '');
    setProcurementDate(proc.procurement_date);
    setInvoiceNumber(proc.invoice_number || '');
    setPaymentMethodId(proc.payment_method_id);
    setPaymentStatusId(proc.payment_status_id);
    setPaymentDate(proc.payment_date || '');
    setPaymentReference(proc.payment_reference || '');
    setRemarks(proc.remarks || '');

    // Note: In edit mode, we only allow updating payment details, not items
    // Items are displayed as read-only
    if (proc.items && proc.items.length > 0) {
      const procItems = proc.items.map((item: any) => ({
        inventory_item_category_id: undefined, // We don't have category in the response
        inventory_item_type_id: item.inventory_item_type_id,
        size_type_id: item.size_type_id,
        quantity: item.quantity,
        unit_cost: item.unit_cost
      }));
      setItems(procItems);
    }
  };

  const resetForm = () => {
    setVendorId('');
    setProcurementDate(new Date().toISOString().split('T')[0]);
    setInvoiceNumber('');
    setPaymentMethodId(0);
    setPaymentStatusId(0);
    setPaymentDate('');
    setPaymentReference('');
    setRemarks('');
    setItems([{ inventory_item_category_id: undefined, inventory_item_type_id: 0, size_type_id: undefined, quantity: 1, unit_cost: 0 }]);
  };

  const handleAddItem = () => {
    setItems([...items, { inventory_item_category_id: undefined, inventory_item_type_id: 0, size_type_id: undefined, quantity: 1, unit_cost: 0 }]);
  };

  const handleRemoveItem = (index: number) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const handleItemChange = (index: number, field: keyof ProcurementItem, value: any) => {
    const newItems = [...items];

    // If category changes, reset the item selection
    if (field === 'inventory_item_category_id') {
      newItems[index] = { ...newItems[index], inventory_item_category_id: value, inventory_item_type_id: 0, size_type_id: undefined };
    } else {
      newItems[index] = { ...newItems[index], [field]: value };
    }

    setItems(newItems);
  };

  const calculateItemTotal = (item: ProcurementItem): number => {
    return item.quantity * item.unit_cost;
  };

  const calculateTotalAmount = (): number => {
    return items.reduce((sum, item) => sum + calculateItemTotal(item), 0);
  };

  const handleSubmit = async () => {
    // Validation
    if (isEditMode) {
      // In edit mode, only validate payment fields
      if (paymentMethodId === 0) {
        onError('Please select a payment method');
        return;
      }
    } else {
      // In create mode, validate all fields
      if (!procurementDate) {
        onError('Procurement date is required');
        return;
      }

      if (paymentMethodId === 0) {
        onError('Please select a payment method');
        return;
      }

      if (items.length === 0) {
        onError('Please add at least one item');
        return;
      }

      for (const item of items) {
        if (item.inventory_item_type_id === 0) {
          onError('Please select an item type for all items');
          return;
        }
        if (item.quantity <= 0) {
          onError('Quantity must be greater than 0');
          return;
        }
        if (item.unit_cost <= 0) {
          onError('Unit cost must be greater than 0');
          return;
        }
      }
    }

    setLoading(true);
    try {
      if (isEditMode && procurement) {
        // Update mode - only update payment details
        const updateData: any = {};
        if (paymentStatusId) updateData.payment_status_id = paymentStatusId;
        if (paymentDate) updateData.payment_date = paymentDate;
        if (paymentReference) updateData.payment_reference = paymentReference;
        if (remarks) updateData.remarks = remarks;

        await updateStockProcurement(procurement.id, updateData);
      } else {
        // Create mode - create new procurement
        const procurementData: any = {
          procurement_date: procurementDate,
          payment_method_id: paymentMethodId,
          items: items.map(item => ({
            inventory_item_type_id: item.inventory_item_type_id,
            size_type_id: item.size_type_id || undefined,
            quantity: item.quantity,
            unit_cost: item.unit_cost
          }))
        };

        if (vendorId) procurementData.vendor_id = vendorId;
        if (invoiceNumber) procurementData.invoice_number = invoiceNumber;
        if (paymentStatusId) procurementData.payment_status_id = paymentStatusId;
        if (paymentDate) procurementData.payment_date = paymentDate;
        if (paymentReference) procurementData.payment_reference = paymentReference;
        if (remarks) procurementData.remarks = remarks;

        await createStockProcurement(procurementData);
      }

      resetForm();
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error creating procurement:', err);
      onError(err.response?.data?.detail || 'Failed to create procurement');
    } finally {
      setLoading(false);
    }
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
          {isEditMode ? 'Edit Stock Procurement' : 'New Stock Procurement'}
        </Typography>
      </DialogTitle>
      <DialogContent sx={{ px: { xs: 2, sm: 3 }, py: { xs: 2, sm: 2 } }}>
        <Box sx={{ mt: { xs: 1, sm: 2 } }}>
          {/* Procurement Details */}
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                select
                fullWidth
                label="Vendor (Optional)"
                value={vendorId}
                onChange={(e) => setVendorId(e.target.value === '' ? '' : Number(e.target.value))}
                size={isMobile ? 'small' : 'medium'}
                disabled={isEditMode}
              >
                <MenuItem value="">No Vendor</MenuItem>
                {vendors.map((vendor) => (
                  <MenuItem key={vendor.id} value={vendor.id}>
                    {vendor.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Procurement Date"
                type="date"
                value={procurementDate}
                onChange={(e) => setProcurementDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                required
                size={isMobile ? 'small' : 'medium'}
                disabled={isEditMode}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Invoice Number"
                value={invoiceNumber}
                onChange={(e) => setInvoiceNumber(e.target.value)}
                size={isMobile ? 'small' : 'medium'}
                disabled={isEditMode}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                select
                fullWidth
                label="Payment Method"
                value={paymentMethodId}
                onChange={(e) => setPaymentMethodId(Number(e.target.value))}
                required
                size={isMobile ? 'small' : 'medium'}
                disabled={isEditMode}
              >
                <MenuItem value={0}>Select Payment Method</MenuItem>
                {configuration?.payment_methods?.map((method: any) => (
                  <MenuItem key={method.id} value={method.id}>
                    {method.description}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Payment Date"
                type="date"
                value={paymentDate}
                onChange={(e) => setPaymentDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                size={isMobile ? 'small' : 'medium'}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Payment Reference"
                value={paymentReference}
                onChange={(e) => setPaymentReference(e.target.value)}
                size={isMobile ? 'small' : 'medium'}
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Remarks"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                multiline
                rows={2}
                size={isMobile ? 'small' : 'medium'}
              />
            </Grid>
          </Grid>

          {/* Items Section */}
          <Box sx={{ mt: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Items {isEditMode && <Typography component="span" variant="caption" color="text.secondary">(Read-only in edit mode)</Typography>}
              </Typography>
              {!isEditMode && (
                <Button
                  startIcon={<AddIcon />}
                  onClick={handleAddItem}
                  size="small"
                  variant="outlined"
                >
                  Add Item
                </Button>
              )}
            </Box>

            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Category</TableCell>
                    <TableCell>Item</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell align="right">Qty</TableCell>
                    <TableCell align="right">Unit Cost</TableCell>
                    <TableCell align="right">Total</TableCell>
                    <TableCell align="center">Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {items.map((item, index) => {
                    // Filter items by selected category
                    const filteredItems = (item.inventory_item_category_id !== null && item.inventory_item_category_id !== undefined)
                      ? configuration?.inventory_item_types?.filter((type: any) => type.inventory_item_category_id === item.inventory_item_category_id) || []
                      : configuration?.inventory_item_types || [];

                    return (
                    <TableRow key={index}>
                      <TableCell>
                        <TextField
                          select
                          fullWidth
                          placeholder="Category"
                          value={item.inventory_item_category_id ?? ''}
                          onChange={(e) => {
                            const value = e.target.value;
                            handleItemChange(index, 'inventory_item_category_id', value === '' ? undefined : Number(value));
                          }}
                          size="small"
                          disabled={isEditMode}
                          slotProps={{
                            select: {
                              displayEmpty: true
                            }
                          }}
                        >
                          <MenuItem value="">All Categories</MenuItem>
                          {configuration?.inventory_item_categories?.map((cat: any) => (
                            <MenuItem key={cat.id} value={cat.id}>
                              {cat.description || cat.name}
                            </MenuItem>
                          ))}
                        </TextField>
                      </TableCell>
                      <TableCell>
                        <TextField
                          select
                          fullWidth
                          value={item.inventory_item_type_id}
                          onChange={(e) => handleItemChange(index, 'inventory_item_type_id', Number(e.target.value))}
                          size="small"
                          required
                          disabled={isEditMode}
                        >
                          <MenuItem value={0}>Select Item</MenuItem>
                          {filteredItems.map((type: any) => (
                            <MenuItem key={type.id} value={type.id}>
                              {type.description}
                            </MenuItem>
                          ))}
                        </TextField>
                      </TableCell>
                      <TableCell>
                        <TextField
                          select
                          fullWidth
                          value={item.size_type_id || ''}
                          onChange={(e) => handleItemChange(index, 'size_type_id', e.target.value ? Number(e.target.value) : undefined)}
                          size="small"
                          disabled={isEditMode}
                        >
                          <MenuItem value="">N/A</MenuItem>
                          {configuration?.inventory_size_types?.map((size: any) => (
                            <MenuItem key={size.id} value={size.id}>
                              {size.name}
                            </MenuItem>
                          ))}
                        </TextField>
                      </TableCell>
                      <TableCell>
                        <TextField
                          type="number"
                          value={item.quantity}
                          onChange={(e) => handleItemChange(index, 'quantity', Number(e.target.value))}
                          inputProps={{ min: 1 }}
                          size="small"
                          sx={{ width: 80 }}
                          disabled={isEditMode}
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          type="number"
                          value={item.unit_cost}
                          onChange={(e) => handleItemChange(index, 'unit_cost', Number(e.target.value))}
                          inputProps={{ min: 0, step: 0.01 }}
                          size="small"
                          sx={{ width: 100 }}
                          disabled={isEditMode}
                        />
                      </TableCell>
                      <TableCell align="right">
                        ₹{calculateItemTotal(item).toFixed(2)}
                      </TableCell>
                      <TableCell align="center">
                        {!isEditMode && (
                          <IconButton
                            size="small"
                            onClick={() => handleRemoveItem(index)}
                            disabled={items.length === 1}
                            color="error"
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        )}
                      </TableCell>
                    </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Total Amount */}
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Typography variant="h6">
                Total Amount: ₹{calculateTotalAmount().toFixed(2)}
              </Typography>
            </Box>
          </Box>
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
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={loading}
          variant="contained"
          fullWidth={isMobile}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Creating...' : 'Create Procurement'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StockProcurementDialog;

