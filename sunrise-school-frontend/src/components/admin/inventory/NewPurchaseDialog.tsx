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
  Paper,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { createPurchase, getPricing } from '../../../services/inventoryService';
import { API_BASE_URL } from '../../../config/apiConfig';
import { configurationService } from '../../../services/configurationService';

interface NewPurchaseDialogProps {
  open: boolean;
  onClose: () => void;
  configuration: any;
  onSuccess: () => void;
  onError: (message: string) => void;
}

interface PurchaseItem {
  inventory_item_category_id?: number;
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
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [loading, setLoading] = useState(false);
  const [students, setStudents] = useState<any[]>([]);
  const [loadingStudents, setLoadingStudents] = useState(false);

  // Get current session year from configuration service
  const currentSessionYearId = configurationService.getCurrentSessionYearId();

  // Form state
  const [classId, setClassId] = useState<number | null>(null);
  const [studentId, setStudentId] = useState<number | null>(null);
  const [sessionYearId, setSessionYearId] = useState<number>(currentSessionYearId || 4);
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
    { inventory_item_category_id: undefined, inventory_item_type_id: 0, size_type_id: undefined, quantity: 1, unit_price: 0 }
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
    setSessionYearId(currentSessionYearId || 4);
    setPurchaseDate(new Date().toISOString().split('T')[0]);
    setPaymentMethodId(0);
    setPaymentDate(new Date().toISOString().split('T')[0]);
    setTransactionId('');
    setPurchasedBy('');
    setContactNumber('');
    setRemarks('');
    setItems([{ inventory_item_category_id: undefined, inventory_item_type_id: 0, size_type_id: undefined, quantity: 1, unit_price: 0 }]);
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
    setItems([...items, { inventory_item_category_id: undefined, inventory_item_type_id: 0, size_type_id: undefined, quantity: 1, unit_price: 0 }]);
  };

  const handleRemoveItem = (index: number) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const handleItemChange = async (index: number, field: keyof PurchaseItem, value: any) => {
    const newItems = [...items];

    // If category changes, reset the item selection
    if (field === 'inventory_item_category_id') {
      newItems[index] = { ...newItems[index], inventory_item_category_id: value, inventory_item_type_id: 0, size_type_id: undefined, unit_price: 0 };
    } else {
      newItems[index] = { ...newItems[index], [field]: value };
    }

    // Auto-fetch price when item type or size changes
    if (field === 'inventory_item_type_id' || field === 'size_type_id') {
      const item = newItems[index];

      // Only fetch if we have an item type selected
      if (item.inventory_item_type_id && item.inventory_item_type_id !== 0) {
        try {
          // Get the selected item type details to check if it requires a size
          const selectedItemType = configuration?.inventory_item_types?.find(
            (type: any) => type.id === item.inventory_item_type_id
          );

          // Check if item is UNIFORM category (category_id = 1)
          const isUniformCategory = selectedItemType?.inventory_item_category_id === 1;

          // For UNIFORM items, only fetch price if size is also selected
          // For other items (BOOKS, NOTEBOOKS, STATIONERY, ACCESSORY), fetch immediately
          const shouldFetchPrice = !isUniformCategory || (isUniformCategory && item.size_type_id);

          if (shouldFetchPrice) {
            // Fetch pricing based on item type, size, and session year
            const pricingList = await getPricing({
              session_year_id: sessionYearId,
              item_type_id: item.inventory_item_type_id,
              is_active: true
            });

            console.log('Fetching price for:', {
              item_type_id: item.inventory_item_type_id,
              size_type_id: item.size_type_id,
              session_year_id: sessionYearId,
              isUniformCategory,
              pricingList
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
            // This is for items like BOOKS, NOTEBOOKS, STATIONERY that don't have sizes
            if (!matchingPrice) {
              matchingPrice = pricingList.find(
                (p: any) => !p.size_type_id || p.size_type_id === null
              );
            }

            // If we found a matching price, update the unit_price
            if (matchingPrice) {
              console.log('Found matching price:', matchingPrice.unit_price);
              newItems[index].unit_price = Number(matchingPrice.unit_price);
            } else {
              console.log('No matching price found');
              // Reset price to 0 if no matching price found
              newItems[index].unit_price = 0;
            }
          } else {
            // For UNIFORM items without size selected, reset price to 0
            console.log('Waiting for size selection for UNIFORM item');
            newItems[index].unit_price = 0;
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
          New Purchase
        </Typography>
      </DialogTitle>
      <DialogContent sx={{ px: { xs: 2, sm: 3 }, py: { xs: 2, sm: 2 } }}>
        <Box sx={{ mt: { xs: 1, sm: 2 } }}>
          <Grid container spacing={2}>
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

            {/* Class Selection */}
            <Grid size={{ xs: 12, sm: 6 }}>
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
            <Grid size={{ xs: 12, sm: 6 }}>
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

            {/* Items Section */}
            <Grid size={{ xs: 12 }}>
              <Typography
                variant="subtitle1"
                sx={{
                  mb: 1,
                  fontWeight: 600,
                  fontSize: { xs: '0.95rem', sm: '1rem' }
                }}
              >
                Items
              </Typography>
              <TableContainer
                component={Paper}
                variant="outlined"
                sx={{
                  maxHeight: { xs: '300px', sm: '400px' },
                  overflowX: 'auto',
                  overflowY: 'auto',
                  '&::-webkit-scrollbar': {
                    height: '8px',
                  },
                  '&::-webkit-scrollbar-track': {
                    backgroundColor: 'grey.100',
                  },
                  '&::-webkit-scrollbar-thumb': {
                    backgroundColor: 'grey.400',
                    borderRadius: '4px',
                  },
                }}
              >
                <Table size={isMobile ? 'small' : 'small'} stickyHeader sx={{ minWidth: 800 }}>
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'white' }}>
                      <TableCell
                        sx={{
                          fontSize: { xs: '0.75rem', sm: '0.875rem' },
                          py: { xs: 1, sm: 1.5 },
                          width: 140,
                          minWidth: 140
                        }}
                      >
                        Category *
                      </TableCell>
                      <TableCell
                        sx={{
                          fontSize: { xs: '0.75rem', sm: '0.875rem' },
                          py: { xs: 1, sm: 1.5 },
                          width: 220,
                          minWidth: 220
                        }}
                      >
                        Item *
                      </TableCell>
                      <TableCell
                        sx={{
                          fontSize: { xs: '0.75rem', sm: '0.875rem' },
                          py: { xs: 1, sm: 1.5 },
                          width: 110,
                          minWidth: 110
                        }}
                      >
                        Size
                      </TableCell>
                      <TableCell
                        sx={{
                          fontSize: { xs: '0.75rem', sm: '0.875rem' },
                          py: { xs: 1, sm: 1.5 },
                          width: 90,
                          minWidth: 90
                        }}
                      >
                        Qty *
                      </TableCell>
                      <TableCell
                        sx={{
                          fontSize: { xs: '0.75rem', sm: '0.875rem' },
                          py: { xs: 1, sm: 1.5 },
                          width: 110,
                          minWidth: 110
                        }}
                      >
                        Price *
                      </TableCell>
                      <TableCell
                        sx={{
                          fontSize: { xs: '0.75rem', sm: '0.875rem' },
                          py: { xs: 1, sm: 1.5 },
                          width: 110,
                          minWidth: 110
                        }}
                      >
                        Total
                      </TableCell>
                      <TableCell
                        sx={{
                          py: { xs: 1, sm: 1.5 },
                          width: 60,
                          minWidth: 60
                        }}
                      >
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {items.map((item, index) => {
                      // Filter items by selected category
                      const filteredItems = (item.inventory_item_category_id !== null && item.inventory_item_category_id !== undefined)
                        ? configuration?.inventory_item_types?.filter((type: any) => type.inventory_item_category_id === item.inventory_item_category_id) || []
                        : configuration?.inventory_item_types || [];

                      // Check if the selected item needs size (only UNIFORM items need sizes)
                      const selectedItemType = configuration?.inventory_item_types?.find(
                        (type: any) => type.id === item.inventory_item_type_id
                      );
                      const showSize = selectedItemType?.inventory_item_category_id === 1; // UNIFORM category

                      return (
                        <TableRow key={index}>
                          <TableCell sx={{ py: { xs: 0.5, sm: 1 }, width: 140, minWidth: 140 }}>
                            <TextField
                              select
                              fullWidth
                              size="small"
                              placeholder="Category"
                              value={item.inventory_item_category_id ?? ''}
                              onChange={(e) => {
                                const value = e.target.value;
                                handleItemChange(index, 'inventory_item_category_id', value === '' ? undefined : Number(value));
                              }}
                              sx={{
                                '& .MuiInputBase-input': {
                                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                  py: { xs: 0.75, sm: 1 }
                                }
                              }}
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
                          <TableCell sx={{ py: { xs: 0.5, sm: 1 }, width: 220, minWidth: 220 }}>
                            <TextField
                              select
                              fullWidth
                              size="small"
                              value={item.inventory_item_type_id}
                              onChange={(e) => handleItemChange(index, 'inventory_item_type_id', Number(e.target.value))}
                              sx={{
                                '& .MuiInputBase-input': {
                                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                  py: { xs: 0.75, sm: 1 }
                                }
                              }}
                            >
                              <MenuItem value={0}>Select Item</MenuItem>
                              {filteredItems.map((type: any) => (
                                <MenuItem key={type.id} value={type.id}>
                                  {type.description}
                                </MenuItem>
                              ))}
                            </TextField>
                          </TableCell>
                        <TableCell sx={{ py: { xs: 0.5, sm: 1 }, width: 110, minWidth: 110 }}>
                          {showSize ? (
                            <TextField
                              select
                              fullWidth
                              size="small"
                              value={item.size_type_id || ''}
                              onChange={(e) => handleItemChange(index, 'size_type_id', e.target.value ? Number(e.target.value) : undefined)}
                              sx={{
                                '& .MuiInputBase-input': {
                                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                  py: { xs: 0.75, sm: 1 }
                                }
                              }}
                            >
                              <MenuItem value="">Select Size</MenuItem>
                              {configuration?.inventory_size_types?.map((size: any) => (
                                <MenuItem key={size.id} value={size.id}>
                                  {size.description}
                                </MenuItem>
                              ))}
                            </TextField>
                          ) : (
                            <Typography
                              sx={{
                                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                color: 'text.secondary',
                                fontStyle: 'italic',
                                textAlign: 'center'
                              }}
                            >
                              N/A
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell sx={{ py: { xs: 0.5, sm: 1 }, width: 90, minWidth: 90 }}>
                          <TextField
                            type="number"
                            size="small"
                            value={item.quantity}
                            onChange={(e) => handleItemChange(index, 'quantity', Number(e.target.value))}
                            inputProps={{ min: 1 }}
                            sx={{
                              '& .MuiInputBase-input': {
                                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                py: { xs: 0.75, sm: 1 }
                              }
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ py: { xs: 0.5, sm: 1 }, width: 110, minWidth: 110 }}>
                          <TextField
                            type="number"
                            size="small"
                            value={item.unit_price}
                            onChange={(e) => handleItemChange(index, 'unit_price', Number(e.target.value))}
                            inputProps={{ min: 0, step: 0.01 }}
                            sx={{
                              '& .MuiInputBase-input': {
                                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                                py: { xs: 0.75, sm: 1 }
                              }
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{
                          py: { xs: 0.5, sm: 1 },
                          fontSize: { xs: '0.75rem', sm: '0.875rem' },
                          width: 110,
                          minWidth: 110
                        }}>
                          ₹{(item.quantity * item.unit_price).toFixed(2)}
                        </TableCell>
                        <TableCell sx={{ py: { xs: 0.5, sm: 1 }, width: 60, minWidth: 60 }}>
                          <IconButton
                            size="small"
                            onClick={() => handleRemoveItem(index)}
                            disabled={items.length === 1}
                            sx={{
                              p: { xs: 0.5, sm: 1 },
                              minWidth: { xs: 36, sm: 40 },
                              minHeight: { xs: 36, sm: 40 }
                            }}
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
                size={isMobile ? 'small' : 'medium'}
                sx={{
                  mt: 1,
                  fontSize: { xs: '0.8125rem', sm: '0.875rem' }
                }}
              >
                Add Item
              </Button>
            </Grid>

            {/* Total Amount */}
            <Grid size={{ xs: 12 }}>
              <Box sx={{
                display: 'flex',
                justifyContent: 'flex-end',
                p: { xs: 1.5, sm: 2 },
                bgcolor: 'grey.50',
                borderRadius: 1
              }}>
                <Typography
                  variant="h6"
                  sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
                >
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
      <DialogActions sx={{
        px: { xs: 2, sm: 3 },
        py: { xs: 1.5, sm: 2 },
        gap: { xs: 1, sm: 1.5 },
        flexDirection: { xs: 'column-reverse', sm: 'row' }
      }}>
        <Button
          onClick={onClose}
          disabled={loading}
          fullWidth={isMobile}
          size={isMobile ? 'medium' : 'medium'}
          sx={{ fontSize: { xs: '0.875rem', sm: '0.875rem' } }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          fullWidth={isMobile}
          size={isMobile ? 'medium' : 'medium'}
          sx={{ fontSize: { xs: '0.875rem', sm: '0.875rem' } }}
        >
          {loading ? <CircularProgress size={24} /> : 'Create Purchase'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NewPurchaseDialog;

