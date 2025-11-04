import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Box,
  Typography,
  IconButton,
  Avatar,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Close as CloseIcon, CloudUpload as UploadIcon } from '@mui/icons-material';
import { createPricing, updatePricing, uploadItemTypeImage, InventoryPricing } from '../../../services/inventoryService';

interface PricingDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  pricing?: InventoryPricing | null;
  configuration: any;
}

const PricingDialog: React.FC<PricingDialogProps> = ({
  open,
  onClose,
  onSuccess,
  pricing,
  configuration,
}) => {
  const [formData, setFormData] = useState({
    inventory_item_type_id: '',
    size_type_id: '',
    class_id: '',
    session_year_id: '',
    unit_price: '',
    description: '',
    effective_from: '',
    effective_to: '',
    is_active: true,
  });

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditMode = !!pricing;

  useEffect(() => {
    if (pricing) {
      setFormData({
        inventory_item_type_id: pricing.inventory_item_type_id.toString(),
        size_type_id: pricing.size_type_id?.toString() || '',
        class_id: pricing.class_id?.toString() || '',
        session_year_id: pricing.session_year_id.toString(),
        unit_price: pricing.unit_price.toString(),
        description: pricing.description || '',
        effective_from: pricing.effective_from || '',
        effective_to: pricing.effective_to || '',
        is_active: pricing.is_active,
      });
      if (pricing.item_image_url) {
        setImagePreview(pricing.item_image_url);
      }
    } else {
      // Reset form for new pricing
      const today = new Date().toISOString().split('T')[0];
      setFormData({
        inventory_item_type_id: '',
        size_type_id: '',
        class_id: '',
        session_year_id: '',
        unit_price: '',
        description: '',
        effective_from: today,
        effective_to: '',
        is_active: true,
      });
      setImageFile(null);
      setImagePreview(null);
    }
    setError(null);
  }, [pricing, open]);

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (10MB limit)
      const maxSizeInBytes = 10 * 1024 * 1024;
      if (file.size > maxSizeInBytes) {
        setError(`File size exceeds 10MB limit. Current size: ${(file.size / (1024 * 1024)).toFixed(2)}MB`);
        e.target.value = '';
        return;
      }

      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        setError('Invalid file type. Please select a JPEG, PNG, GIF, or WebP image.');
        e.target.value = '';
        return;
      }

      setImageFile(file);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      // Validate required fields
      if (!formData.inventory_item_type_id || !formData.session_year_id || !formData.unit_price || !formData.effective_from) {
        setError('Please fill in all required fields');
        setLoading(false);
        return;
      }

      const pricingData = {
        inventory_item_type_id: parseInt(formData.inventory_item_type_id),
        size_type_id: formData.size_type_id ? parseInt(formData.size_type_id) : undefined,
        class_id: formData.class_id ? parseInt(formData.class_id) : undefined,
        session_year_id: parseInt(formData.session_year_id),
        unit_price: parseFloat(formData.unit_price),
        description: formData.description || undefined,
        effective_from: formData.effective_from,
        effective_to: formData.effective_to || undefined,
        is_active: formData.is_active,
      };

      if (isEditMode && pricing) {
        // Update existing pricing
        await updatePricing(pricing.id, {
          unit_price: pricingData.unit_price,
          description: pricingData.description,
          effective_to: pricingData.effective_to,
          is_active: pricingData.is_active,
        });
      } else {
        // Create new pricing
        await createPricing(pricingData);
      }

      // Upload image if selected
      if (imageFile && formData.inventory_item_type_id) {
        setUploadingImage(true);
        await uploadItemTypeImage(parseInt(formData.inventory_item_type_id), imageFile);
        setUploadingImage(false);
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error saving pricing:', err);
      setError(err.response?.data?.detail || 'Failed to save pricing');
    } finally {
      setLoading(false);
      setUploadingImage(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ bgcolor: 'white', borderBottom: 1, borderColor: 'divider' }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">{isEditMode ? 'Edit Pricing' : 'Add New Pricing'}</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ mt: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2}>
          {/* Item Type */}
          <Grid size={{ xs: 12, sm: 6 }}>
            <FormControl fullWidth required disabled={isEditMode}>
              <InputLabel>Item Type</InputLabel>
              <Select
                value={formData.inventory_item_type_id}
                onChange={(e) => handleChange('inventory_item_type_id', e.target.value)}
                label="Item Type"
              >
                {configuration?.inventory_item_types?.map((item: any) => (
                  <MenuItem key={item.id} value={item.id}>
                    {item.description}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Size Type */}
          <Grid size={{ xs: 12, sm: 6 }}>
            <FormControl fullWidth disabled={isEditMode}>
              <InputLabel>Size (Optional)</InputLabel>
              <Select
                value={formData.size_type_id}
                onChange={(e) => handleChange('size_type_id', e.target.value)}
                label="Size (Optional)"
              >
                <MenuItem value="">
                  <em>All Sizes</em>
                </MenuItem>
                {configuration?.inventory_size_types?.map((size: any) => (
                  <MenuItem key={size.id} value={size.id}>
                    {size.description}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Class */}
          <Grid size={{ xs: 12, sm: 6 }}>
            <FormControl fullWidth disabled={isEditMode}>
              <InputLabel>Class (Optional)</InputLabel>
              <Select
                value={formData.class_id}
                onChange={(e) => handleChange('class_id', e.target.value)}
                label="Class (Optional)"
              >
                <MenuItem value="">
                  <em>All Classes</em>
                </MenuItem>
                {configuration?.classes?.map((cls: any) => (
                  <MenuItem key={cls.id} value={cls.id}>
                    {cls.description}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Session Year */}
          <Grid size={{ xs: 12, sm: 6 }}>
            <FormControl fullWidth required disabled={isEditMode}>
              <InputLabel>Session Year</InputLabel>
              <Select
                value={formData.session_year_id}
                onChange={(e) => handleChange('session_year_id', e.target.value)}
                label="Session Year"
              >
                {configuration?.session_years?.map((year: any) => (
                  <MenuItem key={year.id} value={year.id}>
                    {year.description}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Unit Price */}
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              required
              label="Unit Price (₹)"
              type="number"
              value={formData.unit_price}
              onChange={(e) => handleChange('unit_price', e.target.value)}
              inputProps={{ min: 0, step: 0.01 }}
            />
          </Grid>

          {/* Effective From */}
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              required
              label="Effective From"
              type="date"
              value={formData.effective_from}
              onChange={(e) => handleChange('effective_from', e.target.value)}
              InputLabelProps={{ shrink: true }}
              disabled={isEditMode}
            />
          </Grid>

          {/* Effective To */}
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Effective To (Optional)"
              type="date"
              value={formData.effective_to}
              onChange={(e) => handleChange('effective_to', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          {/* Description */}
          <Grid size={{ xs: 12 }}>
            <TextField
              fullWidth
              label="Description (Optional)"
              multiline
              rows={2}
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
            />
          </Grid>

          {/* Image Upload */}
          <Grid size={{ xs: 12 }}>
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Item Image {!isEditMode && '(Optional)'}
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                {imagePreview && (
                  <Avatar
                    src={imagePreview}
                    variant="rounded"
                    sx={{ width: 100, height: 100 }}
                  />
                )}
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={uploadingImage ? <CircularProgress size={20} /> : <UploadIcon />}
                  disabled={uploadingImage || !formData.inventory_item_type_id}
                >
                  {imagePreview ? 'Change Image' : 'Upload Image'}
                  <input
                    type="file"
                    hidden
                    accept="image/*"
                    onChange={handleImageChange}
                  />
                </Button>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Max size: 10MB. Formats: JPEG, PNG, GIF, WebP
              </Typography>
            </Box>
          </Grid>

          {/* Is Active */}
          <Grid size={{ xs: 12 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_active}
                  onChange={(e) => handleChange('is_active', e.target.checked)}
                />
              }
              label="Active"
            />
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} disabled={loading || uploadingImage}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || uploadingImage}
          startIcon={loading || uploadingImage ? <CircularProgress size={20} /> : null}
        >
          {loading || uploadingImage ? 'Saving...' : isEditMode ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PricingDialog;

