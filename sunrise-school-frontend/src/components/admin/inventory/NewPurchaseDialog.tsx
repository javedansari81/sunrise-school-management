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
  Autocomplete,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { calculateItemTotal, calculatePurchaseTotal, createPurchase, getPricing } from '../../../services/inventoryService';
import { API_BASE_URL } from '../../../config/apiConfig';

interface NewPurchaseDialogProps {
  open: boolean;
  onClose: () => void;
  configuration: any;
  onSuccess: () => void;
  onError: (message: string) => void;
}

interface PurchaseItem {
  inventory_item_type_id: number;
  size_type_id?: number;
  quantity: number;
  unit_price: number;
}

const NewPurchaseDialog: React.FC<NewPurchaseDialogProps> = ({
  open,
  onClose,
  configuration,
  onSuccess,
  onError
}) => {
  const [loading, setLoading] = useState(false);
  const [students, setStudents] = useState<any[]>([]);
  const [loadingStudents, setLoadingStudents] = useState(false);

  // Form state
  const [classId, setClassId] = useState<number | null>(null);
  const [studentId, setStudentId] = useState<number | null>(null);
  const [sessionYearId, setSessionYearId] = useState<number>(4); // Default to current session
  const [purchaseDate, setPurchaseDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [paymentMethodId, setPaymentMethodId] = useState<number>(0);
  const [paymentDate, setPaymentDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [transactionId, setTransactionId] = useState<string>('');
  const [purchasedBy, setPurchasedBy] = useState<string>('');
  const [contactNumber, setContactNumber] = useState<string>('');
  const [remarks, setRemarks] = useState<string>('');
  const [items, setItems] = useState<PurchaseItem[]>([
    { inventory_item_type_id: 0, size_type_id: undefined, quantity: 1, unit_price: 0 }
  ]);

  // Reset form when dialog opens
  useEffect(() => {
    if (open) {
      resetForm();
    }
  }, [open]);

  const resetForm = () => {
    setClassId(null);
    setStudentId(null);
    setSessionYearId(4);
    setPurchaseDate(new Date().toISOString().split('T')[0]);
    setPaymentMethodId(0);
    setPaymentDate(new Date().toISOString().split('T')[0]);
    setTransactionId('');
    setPurchasedBy('');
    setContactNumber('');
    setRemarks('');
    setItems([{ inventory_item_type_id: 0, size_type_id: undefined, quantity: 1, unit_price: 0 }]);
  };

  const loadStudentsByClass = async (selectedClassId: number) => {
    setLoadingStudents(true);
    setStudents([]); // Clear previous students
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/students/?class_filter=${selectedClassId}&per_page=50`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers.get('content-type'));

      if (!response.ok) {
        const text = await response.text();
        console.error('Error response:', text);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Non-JSON response:', text.substring(0, 500));
        throw new Error('Server returned non-JSON response');
      }

      const data = await response.json();
      console.log('Students loaded:', data); // Debug log

      if (data.students && Array.isArray(data.students)) {
        setStudents(data.students);
        console.log(`Loaded ${data.students.length} students for class ${selectedClassId}`);
      } else {
        console.warn('No students array in response:', data);
        setStudents([]);
      }
    } catch (err: any) {
      console.error('Error loading students:', err);
      onError(`Failed to load students: ${err.message}`);
    } finally {
      setLoadingStudents(false);
    }
  };

  // Handle class change and load students for that class
  const handleClassChange = (newClassId: number | null) => {
    setClassId(newClassId);
    setStudentId(null); // Reset student selection when class changes
    setStudents([]); // Clear students list

    if (newClassId) {
      // Load students for the selected class from API
      loadStudentsByClass(newClassId);
    }
  };

  const handleAddItem = () => {
    setItems([...items, { inventory_item_type_id: 0, size_type_id: undefined, quantity: 1, unit_price: 0 }]);
  };

  const handleRemoveItem = (index: number) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const handleItemChange = async (index: number, field: keyof PurchaseItem, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };

    // Auto-fetch price when item type or size changes
    if (field === 'inventory_item_type_id' || field === 'size_type_id') {
      const item = newItems[index];

      // Only fetch if we have an item type selected
      if (item.inventory_item_type_id && item.inventory_item_type_id !== 0) {
        try {
          // Fetch pricing based on item type, size, and session year
          const pricingList = await getPricing({
            session_year_id: sessionYearId,
            item_type_id: item.inventory_item_type_id,
            is_active: true
          });

          // Find matching price based on size (if size is selected)
          let matchingPrice = null;
          if (item.size_type_id) {
            // Try to find exact match with size
            matchingPrice = pricingList.find(
              (p: any) => p.size_type_id === item.size_type_id
            );
          }

          // If no size-specific price found, try to find a general price (no size requirement)
          if (!matchingPrice) {
            matchingPrice = pricingList.find(
              (p: any) => !p.size_type_id || p.size_type_id === null
            );
          }

          // If we found a matching price, update the unit_price
          if (matchingPrice) {
            newItems[index].unit_price = Number(matchingPrice.unit_price);
          }
        } catch (err) {
          console.error('Error fetching price:', err);
          // Don't show error to user, just keep the current price
        }
      }
    }

    setItems(newItems);
  };

  const calculateTotal = (): number => {
    return items.reduce((total, item) => {
      return total + (item.quantity * item.unit_price);
    }, 0);
  };

  const handleSubmit = async () => {
    // Validation
    if (!classId) {
      onError('Please select a class');
      return;
    }
    if (!studentId) {
      onError('Please select a student');
      return;
    }
    if (!paymentMethodId) {
      onError('Please select a payment method');
      return;
    }
    if (items.length === 0) {
      onError('Please add at least one item');
      return;
    }
    for (const item of items) {
      if (!item.inventory_item_type_id) {
        onError('Please select an item type for all items');
        return;
      }
      if (item.quantity <= 0) {
        onError('Quantity must be greater than 0');
        return;
      }
      if (item.unit_price <= 0) {
        onError('Unit price must be greater than 0');
        return;
      }
    }

    setLoading(true);
    try {
      await createPurchase({
        student_id: studentId,
        session_year_id: sessionYearId,
        purchase_date: purchaseDate,
        payment_method_id: paymentMethodId,
        payment_date: paymentDate || undefined,
        transaction_id: transactionId || undefined,
        remarks: remarks || undefined,
        purchased_by: purchasedBy || undefined,
        contact_number: contactNumber || undefined,
        items: items.map(item => ({
          inventory_item_type_id: item.inventory_item_type_id,
          size_type_id: item.size_type_id || undefined,
          quantity: item.quantity,
          unit_price: item.unit_price
        }))
      });

      resetForm();
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error creating purchase:', err);
      if (err.response?.status === 422 && Array.isArray(err.response?.data?.detail)) {
        const errorMessages = err.response.data.detail.map((e: any) => e.msg).join(', ');
        onError(`Validation error: ${errorMessages}`);
      } else {
        onError(err.response?.data?.detail || 'Failed to create purchase');
      }
    } finally {
      setLoading(false);
    }
  };

  const getItemTypeName = (id: number): string => {
    const itemType = configuration?.inventory_item_types?.find((t: any) => t.id === id);
    return itemType?.description || '';
  };

  const getSizeName = (id?: number): string => {
    if (!id) return '';
    const size = configuration?.inventory_size_types?.find((s: any) => s.id === id);
    return size?.description || '';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ bgcolor: 'white', borderBottom: 1, borderColor: 'divider' }}>
        New Purchase
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Grid container spacing={2}>
            {/* Class Selection */}
            <Grid size={{ xs: 12 }}>
              <TextField
                select
                fullWidth
                label="Class *"
                value={classId || ''}
                onChange={(e) => handleClassChange(e.target.value ? Number(e.target.value) : null)}
              >
                <MenuItem value="">Select Class</MenuItem>
                {configuration?.classes?.map((cls: any) => (
                  <MenuItem key={cls.id} value={cls.id}>
                    {cls.description}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Student Selection */}
            <Grid size={{ xs: 12 }}>
              <Autocomplete
                options={students}
                getOptionLabel={(option) =>
                  `Roll ${option.roll_number || 'N/A'}: ${option.first_name} ${option.last_name} (${option.class_name})`
                }
                value={students.find(s => s.id === studentId) || null}
                onChange={(_, newValue) => setStudentId(newValue?.id || null)}
                loading={loadingStudents}
                disabled={!classId}
                noOptionsText={classId ? "No students found" : "Please select a class first"}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Student *"
                    placeholder={classId ? "Search by name or roll number" : "Select a class first"}
                    InputProps={{
                      ...params.InputProps,
                      endAdornment: (
                        <>
                          {loadingStudents ? <CircularProgress size={20} /> : null}
                          {params.InputProps.endAdornment}
                        </>
                      ),
                    }}
                  />
                )}
              />
            </Grid>

            {/* Session Year */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                select
                label="Session Year *"
                value={sessionYearId}
                onChange={(e) => setSessionYearId(Number(e.target.value))}
              >
                {configuration?.session_years?.map((year: any) => (
                  <MenuItem key={year.id} value={year.id}>
                    {year.description}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Purchase Date */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="date"
                label="Purchase Date *"
                value={purchaseDate}
                onChange={(e) => setPurchaseDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* Items Section */}
            <Grid size={{ xs: 12 }}>
              <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 600 }}>
                Items
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'white' }}>
                      <TableCell width={60}>Image</TableCell>
                      <TableCell>Item *</TableCell>
                      <TableCell>Size</TableCell>
                      <TableCell width={100}>Qty *</TableCell>
                      <TableCell width={120}>Price *</TableCell>
                      <TableCell width={120}>Total</TableCell>
                      <TableCell width={60}></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {items.map((item, index) => {
                      const selectedItemType = configuration?.inventory_item_types?.find(
                        (type: any) => type.id === item.inventory_item_type_id
                      );

                      return (
                        <TableRow key={index}>
                          <TableCell>
                            {selectedItemType?.image_url ? (
                              <Box
                                component="img"
                                src={selectedItemType.image_url}
                                alt={selectedItemType.description}
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
                          <TableCell>
                            <TextField
                              select
                              fullWidth
                              size="small"
                              value={item.inventory_item_type_id}
                              onChange={(e) => handleItemChange(index, 'inventory_item_type_id', Number(e.target.value))}
                            >
                              <MenuItem value={0}>Select Item</MenuItem>
                              {configuration?.inventory_item_types?.map((type: any) => (
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
                            size="small"
                            value={item.size_type_id || ''}
                            onChange={(e) => handleItemChange(index, 'size_type_id', e.target.value ? Number(e.target.value) : undefined)}
                          >
                            <MenuItem value="">N/A</MenuItem>
                            {configuration?.inventory_size_types?.map((size: any) => (
                              <MenuItem key={size.id} value={size.id}>
                                {size.description}
                              </MenuItem>
                            ))}
                          </TextField>
                        </TableCell>
                        <TableCell>
                          <TextField
                            type="number"
                            size="small"
                            value={item.quantity}
                            onChange={(e) => handleItemChange(index, 'quantity', Number(e.target.value))}
                            inputProps={{ min: 1 }}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            type="number"
                            size="small"
                            value={item.unit_price}
                            onChange={(e) => handleItemChange(index, 'unit_price', Number(e.target.value))}
                            inputProps={{ min: 0, step: 0.01 }}
                          />
                        </TableCell>
                        <TableCell>
                          ₹{(item.quantity * item.unit_price).toFixed(2)}
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => handleRemoveItem(index)}
                            disabled={items.length === 1}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
              <Button
                startIcon={<AddIcon />}
                onClick={handleAddItem}
                sx={{ mt: 1 }}
              >
                Add Item
              </Button>
            </Grid>

            {/* Total Amount */}
            <Grid size={{ xs: 12 }}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="h6">
                  Total Amount: ₹{calculateTotal().toFixed(2)}
                </Typography>
              </Box>
            </Grid>

            {/* Payment Details */}
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                select
                label="Payment Method *"
                value={paymentMethodId}
                onChange={(e) => setPaymentMethodId(Number(e.target.value))}
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
                type="date"
                label="Payment Date"
                value={paymentDate}
                onChange={(e) => setPaymentDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Transaction ID"
                value={transactionId}
                onChange={(e) => setTransactionId(e.target.value)}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Purchased By"
                value={purchasedBy}
                onChange={(e) => setPurchasedBy(e.target.value)}
                placeholder="Parent/Guardian name"
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Contact Number"
                value={contactNumber}
                onChange={(e) => setContactNumber(e.target.value)}
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Remarks"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Create Purchase'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NewPurchaseDialog;

