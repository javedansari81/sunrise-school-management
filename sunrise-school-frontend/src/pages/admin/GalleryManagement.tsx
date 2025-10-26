import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  Chip,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Snackbar,
  Alert,
  Pagination,
  Tooltip,
  Stack,
  Tabs,
  Tab,
  FormControlLabel,
  Checkbox,
  CardMedia,
} from '@mui/material';
import { DEFAULT_PAGE_SIZE } from '../../config/pagination';
import AdminLayout from '../../components/Layout/AdminLayout';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  PhotoLibrary,
  Image as ImageIcon,
  Category,
  TrendingUp,
  Home as HomeIcon,
  Search,
  CloudUpload,
  FilterList,
} from '@mui/icons-material';
import { useServiceConfiguration, useConfiguration } from '../../contexts/ConfigurationContext';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';
import { galleryAPI } from '../../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`gallery-tabpanel-${index}`}
      aria-labelledby={`gallery-tab-${index}`}
      {...other}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

interface GalleryFilters {
  category_id: string;
  is_active: string;
  search_title: string;
}

interface GalleryImageFormData {
  category_id: string;
  title: string;
  description: string;
  display_order: string;
  is_visible_on_home_page: boolean;
  file?: File | null;
}

const GalleryManagement: React.FC = () => {
  const { isLoading: configLoading, isLoaded: configLoaded, error: configError } = useServiceConfiguration('gallery-management');
  const { getServiceConfiguration, getGalleryCategories } = useConfiguration();

  // Get the service configuration
  const configuration = getServiceConfiguration('gallery-management');

  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [images, setImages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedImage, setSelectedImage] = useState<any>(null);
  const [dialogMode, setDialogMode] = useState<'add' | 'edit' | 'view'>('add');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [statistics, setStatistics] = useState<any>({});
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalImages, setTotalImages] = useState(0);
  const perPage = DEFAULT_PAGE_SIZE;

  // Filters
  const [filters, setFilters] = useState<GalleryFilters>({
    category_id: '',
    is_active: 'true',
    search_title: '',
  });

  // Form data
  const [imageForm, setImageForm] = useState<GalleryImageFormData>({
    category_id: '',
    title: '',
    description: '',
    display_order: '0',
    is_visible_on_home_page: false,
    file: null,
  });

  // Get gallery categories from configuration
  const galleryCategories = getGalleryCategories();

  // Fetch images when filters or page changes
  useEffect(() => {
    fetchImages();
  }, [filters, page, activeTab]);

  // Fetch statistics
  useEffect(() => {
    fetchStatistics();
  }, []);

  // API Functions
  const fetchImages = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      
      // Add filters based on active tab
      if (activeTab === 1) {
        // Home Page Featured tab
        params.append('is_visible_on_home_page', 'true');
      }

      // Add other filters
      if (filters.category_id) {
        params.append('category_id', filters.category_id);
      }
      if (filters.is_active) {
        params.append('is_active', filters.is_active);
      }

      const response = await galleryAPI.getImages(params);
      
      // Filter by title search on client side (backend doesn't support title search yet)
      let filteredImages = response;
      if (filters.search_title) {
        filteredImages = response.filter((img: any) =>
          img.title.toLowerCase().includes(filters.search_title.toLowerCase())
        );
      }

      setImages(filteredImages);
      setTotalImages(filteredImages.length);
      setTotalPages(Math.ceil(filteredImages.length / perPage));
    } catch (error: any) {
      console.error('Error fetching images:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Error fetching images',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const stats = await galleryAPI.getStatistics();
      setStatistics(stats);
    } catch (error: any) {
      console.error('Error fetching statistics:', error);
    }
  };

  const handleOpenDialog = (image?: any, mode: 'add' | 'edit' | 'view' = 'add') => {
    setDialogMode(mode);
    if (image) {
      setImageForm({
        category_id: image.category_id?.toString() || '',
        title: image.title || '',
        description: image.description || '',
        display_order: image.display_order?.toString() || '0',
        is_visible_on_home_page: image.is_visible_on_home_page || false,
        file: null,
      });
      setSelectedImage(image);
      setImagePreview(image.cloudinary_thumbnail_url || image.cloudinary_url);
    } else {
      // Reset form for new image
      setImageForm({
        category_id: '',
        title: '',
        description: '',
        display_order: '0',
        is_visible_on_home_page: false,
        file: null,
      });
      setSelectedImage(null);
      setImagePreview(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedImage(null);
    setImagePreview(null);
    setImageForm({
      category_id: '',
      title: '',
      description: '',
      display_order: '0',
      is_visible_on_home_page: false,
      file: null,
    });
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setImageForm(prev => ({ ...prev, [name]: checked }));
    } else {
      setImageForm(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (Cloudinary free tier limit: 10MB)
      const maxSizeInBytes = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSizeInBytes) {
        setSnackbar({
          open: true,
          message: `File size exceeds 10MB limit. Please select a smaller image. Current size: ${(file.size / (1024 * 1024)).toFixed(2)}MB`,
          severity: 'error'
        });
        // Reset file input
        e.target.value = '';
        return;
      }

      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        setSnackbar({
          open: true,
          message: 'Invalid file type. Please select a JPEG, PNG, GIF, or WebP image.',
          severity: 'error'
        });
        // Reset file input
        e.target.value = '';
        return;
      }

      setImageForm(prev => ({ ...prev, file }));
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

      if (selectedImage) {
        // Update existing image
        const updateData = {
          category_id: parseInt(imageForm.category_id),
          title: imageForm.title,
          description: imageForm.description || null,
          display_order: parseInt(imageForm.display_order),
          is_visible_on_home_page: imageForm.is_visible_on_home_page,
        };

        await galleryAPI.updateImage(selectedImage.id, updateData);
        setSnackbar({ open: true, message: 'Image updated successfully', severity: 'success' });
      } else {
        // Upload new image
        if (!imageForm.file) {
          setSnackbar({ open: true, message: 'Please select an image file', severity: 'error' });
          return;
        }

        const formData = new FormData();
        formData.append('file', imageForm.file);
        formData.append('category_id', imageForm.category_id);
        formData.append('title', imageForm.title);
        if (imageForm.description) {
          formData.append('description', imageForm.description);
        }
        formData.append('display_order', imageForm.display_order);
        formData.append('is_visible_on_home_page', imageForm.is_visible_on_home_page.toString());

        await galleryAPI.uploadImage(formData);
        setSnackbar({ open: true, message: 'Image uploaded successfully', severity: 'success' });
      }

      handleCloseDialog();
      fetchImages();
      fetchStatistics();
    } catch (error: any) {
      console.error('Error saving image:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Error saving image',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (imageId: number) => {
    if (!window.confirm('Are you sure you want to delete this image? This will also remove it from Cloudinary.')) {
      return;
    }

    try {
      await galleryAPI.deleteImage(imageId);
      setSnackbar({ open: true, message: 'Image deleted successfully', severity: 'success' });
      fetchImages();
      fetchStatistics();
    } catch (error: any) {
      console.error('Error deleting image:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Error deleting image',
        severity: 'error'
      });
    }
  };



  const handleFilterChange = (field: keyof GalleryFilters, value: any) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPage(1); // Reset to first page when filtering
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    setPage(1);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  // Computed values
  const imageStats = [
    {
      title: 'Total Images',
      value: statistics.total_images || 0,
      icon: <PhotoLibrary />,
      color: 'primary',
    },
    {
      title: 'Active Images',
      value: statistics.active_images || 0,
      icon: <ImageIcon />,
      color: 'success',
    },
    {
      title: 'Home Page Featured',
      value: statistics.home_page_images || 0,
      icon: <HomeIcon />,
      color: 'warning',
    },
    {
      title: 'Categories',
      value: statistics.total_categories || 0,
      icon: <Category />,
      color: 'info',
    },
  ];

  // Paginate images
  const paginatedImages = images.slice((page - 1) * perPage, page * perPage);

  return (
    <AdminLayout>
      <Box sx={{ p: 3 }}>
        <ServiceConfigurationLoader service="gallery-management">
          {/* Filters Section - Above Tabs */}
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            {/* Header with Filters Label and Upload Button */}
            <Box sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 2,
              flexWrap: 'wrap',
              gap: 2
            }}>
              {/* Filters Label */}
              <Typography variant="h6" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
                <FilterList sx={{ mr: 1 }} />
                Filters
              </Typography>

              {/* Upload Image Button - Right Side */}
              <Button
                variant="contained"
                startIcon={<CloudUpload />}
                onClick={() => handleOpenDialog()}
                sx={{
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  padding: { xs: '6px 12px', sm: '8px 16px' },
                  whiteSpace: 'nowrap'
                }}
              >
                Upload New Image
              </Button>
            </Box>

            {/* Filter Controls */}
            <Box sx={{
              display: 'flex',
              gap: { xs: 1.5, sm: 2 },
              alignItems: { xs: 'stretch', sm: 'center' },
              flexWrap: 'wrap',
              flexDirection: { xs: 'column', sm: 'row' }
            }}>
              {/* Category Filter */}
              <FormControl
                size="small"
                sx={{
                  flex: { xs: '1 1 100%', sm: '1 1 auto' },
                  minWidth: { xs: '100%', sm: 'auto' }
                }}
              >
                <InputLabel>Category</InputLabel>
                <Select
                  value={filters.category_id}
                  label="Category"
                  onChange={(e) => handleFilterChange('category_id', e.target.value)}
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {galleryCategories.filter((cat: any) => cat.is_active).map((category: any) => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.description || category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Status Filter */}
              <FormControl
                size="small"
                sx={{
                  flex: { xs: '1 1 100%', sm: '1 1 auto' },
                  minWidth: { xs: '100%', sm: 'auto' }
                }}
              >
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.is_active}
                  label="Status"
                  onChange={(e) => handleFilterChange('is_active', e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="true">Active</MenuItem>
                  <MenuItem value="false">Inactive</MenuItem>
                </Select>
              </FormControl>

              {/* Search by Title */}
              <TextField
                size="small"
                label="Search by Title"
                placeholder="Enter image title..."
                value={filters.search_title}
                onChange={(e) => handleFilterChange('search_title', e.target.value)}
                sx={{
                  flex: { xs: '1 1 100%', sm: '1 1 auto' },
                  minWidth: { xs: '100%', sm: 'auto' }
                }}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Box>
          </Paper>

          {/* Tabs */}
          <Paper sx={{ width: '100%' }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                borderBottom: 1,
                borderColor: 'divider',
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontWeight: 500,
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  minHeight: { xs: 48, sm: 56 },
                }
              }}
            >
              <Tab
                label="All Images"
                icon={<PhotoLibrary />}
                iconPosition="start"
              />
              <Tab
                label="Home Page Featured"
                icon={<HomeIcon />}
                iconPosition="start"
              />
              <Tab
                label="Statistics"
                icon={<TrendingUp />}
                iconPosition="start"
              />
            </Tabs>

            {/* All Images Tab */}
            <TabPanel value={activeTab} index={0}>
              <Box sx={{ p: 3 }}>
                {loading ? (
                  <Box display="flex" justifyContent="center" p={4}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Thumbnail</TableCell>
                            <TableCell>Title</TableCell>
                            <TableCell>Category</TableCell>
                            <TableCell>Upload Date</TableCell>
                            <TableCell>Uploaded By</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Home Page</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {paginatedImages.length === 0 ? (
                            <TableRow>
                              <TableCell colSpan={8} align="center">
                                <Typography variant="body2" color="text.secondary">
                                  No images found
                                </Typography>
                              </TableCell>
                            </TableRow>
                          ) : (
                            paginatedImages.map((image) => (
                              <TableRow key={image.id}>
                                <TableCell>
                                  <CardMedia
                                    component="img"
                                    sx={{ width: 80, height: 60, objectFit: 'cover', borderRadius: 1 }}
                                    image={image.cloudinary_thumbnail_url || image.cloudinary_url}
                                    alt={image.title}
                                  />
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                                    {image.title}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Chip
                                    label={image.category_name || 'Unknown'}
                                    size="small"
                                    color="primary"
                                    variant="outlined"
                                  />
                                </TableCell>
                                <TableCell>
                                  {new Date(image.upload_date).toLocaleDateString()}
                                </TableCell>
                                <TableCell>
                                  {image.uploaded_by_name || '-'}
                                </TableCell>
                                <TableCell>
                                  <Chip
                                    label={image.is_active ? 'Active' : 'Inactive'}
                                    size="small"
                                    color={image.is_active ? 'success' : 'default'}
                                  />
                                </TableCell>
                                <TableCell>
                                  <Chip
                                    label={image.is_visible_on_home_page ? 'Yes' : 'No'}
                                    size="small"
                                    color={image.is_visible_on_home_page ? 'warning' : 'default'}
                                    icon={image.is_visible_on_home_page ? <HomeIcon /> : undefined}
                                  />
                                </TableCell>
                                <TableCell>
                                  <Stack direction="row" spacing={1}>
                                    <Tooltip title="View Details">
                                      <IconButton
                                        size="small"
                                        color="primary"
                                        onClick={() => handleOpenDialog(image, 'view')}
                                      >
                                        <Visibility />
                                      </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Edit">
                                      <IconButton
                                        size="small"
                                        color="secondary"
                                        onClick={() => handleOpenDialog(image, 'edit')}
                                      >
                                        <Edit />
                                      </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Delete">
                                      <IconButton
                                        size="small"
                                        color="error"
                                        onClick={() => handleDelete(image.id)}
                                      >
                                        <Delete />
                                      </IconButton>
                                    </Tooltip>
                                  </Stack>
                                </TableCell>
                              </TableRow>
                            ))
                          )}
                        </TableBody>
                      </Table>
                    </TableContainer>

                    {/* Pagination */}
                    {totalPages > 1 && (
                      <Box display="flex" justifyContent="center" mt={3}>
                        <Pagination
                          count={totalPages}
                          page={page}
                          onChange={handlePageChange}
                          color="primary"
                          showFirstButton
                          showLastButton
                        />
                      </Box>
                    )}
                  </>
                )}
              </Box>
            </TabPanel>

            {/* Home Page Featured Tab */}
            <TabPanel value={activeTab} index={1}>
              <Box sx={{ p: 3 }}>
                {loading ? (
                  <Box display="flex" justifyContent="center" p={4}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Thumbnail</TableCell>
                            <TableCell>Title</TableCell>
                            <TableCell>Category</TableCell>
                            <TableCell>Display Order</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {paginatedImages.length === 0 ? (
                            <TableRow>
                              <TableCell colSpan={5} align="center">
                                <Typography variant="body2" color="text.secondary">
                                  No featured images found
                                </Typography>
                              </TableCell>
                            </TableRow>
                          ) : (
                            paginatedImages.map((image) => (
                              <TableRow key={image.id}>
                                <TableCell>
                                  <CardMedia
                                    component="img"
                                    sx={{ width: 80, height: 60, objectFit: 'cover', borderRadius: 1 }}
                                    image={image.cloudinary_thumbnail_url || image.cloudinary_url}
                                    alt={image.title}
                                  />
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2">
                                    {image.title}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Chip
                                    label={image.category_name || 'Unknown'}
                                    size="small"
                                    color="primary"
                                    variant="outlined"
                                  />
                                </TableCell>
                                <TableCell>{image.display_order}</TableCell>
                                <TableCell>
                                  <Stack direction="row" spacing={1}>
                                    <Tooltip title="View Details">
                                      <IconButton
                                        size="small"
                                        color="primary"
                                        onClick={() => handleOpenDialog(image, 'view')}
                                      >
                                        <Visibility />
                                      </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Edit">
                                      <IconButton
                                        size="small"
                                        color="secondary"
                                        onClick={() => handleOpenDialog(image, 'edit')}
                                      >
                                        <Edit />
                                      </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Delete">
                                      <IconButton
                                        size="small"
                                        color="error"
                                        onClick={() => handleDelete(image.id)}
                                      >
                                        <Delete />
                                      </IconButton>
                                    </Tooltip>
                                  </Stack>
                                </TableCell>
                              </TableRow>
                            ))
                          )}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                )}
              </Box>
            </TabPanel>

            {/* Statistics Tab */}
            <TabPanel value={activeTab} index={2}>
              <Box sx={{ p: 3 }}>
                {/* Statistics Cards */}
                <Grid container spacing={3}>
                  {imageStats.map((stat, index) => (
                    <Grid key={index} size={{ xs: 12, sm: 6, md: 3 }}>
                      <Card elevation={3}>
                        <CardContent>
                          <Box display="flex" alignItems="center" justifyContent="space-between">
                            <Box>
                              <Typography variant="h5" fontWeight="bold" color={`${stat.color}.main`}>
                                {stat.value}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {stat.title}
                              </Typography>
                            </Box>
                            <Box
                              sx={{
                                backgroundColor: `${stat.color}.light`,
                                borderRadius: '50%',
                                p: 1.5,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}
                            >
                              {React.cloneElement(stat.icon, {
                                sx: { fontSize: 32, color: `${stat.color}.main` }
                              })}
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            </TabPanel>
          </Paper>

          {/* Upload/Edit Image Dialog */}
          <Dialog
            open={openDialog}
            onClose={handleCloseDialog}
            maxWidth="md"
            fullWidth
          >
            <DialogTitle sx={{ backgroundColor: 'white', borderBottom: '1px solid rgba(0, 0, 0, 0.12)' }}>
              {dialogMode === 'view' ? 'View Image' : dialogMode === 'edit' ? 'Edit Image' : 'Upload New Image'}
            </DialogTitle>
            <DialogContent sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                {/* Image Preview */}
                {imagePreview && (
                  <Grid size={{ xs: 12 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                      <CardMedia
                        component="img"
                        sx={{ maxWidth: '100%', maxHeight: 300, objectFit: 'contain', borderRadius: 1 }}
                        image={imagePreview}
                        alt="Preview"
                      />
                    </Box>
                  </Grid>
                )}

                {/* File Upload (only for new images) */}
                {dialogMode === 'add' && (
                  <Grid size={{ xs: 12 }}>
                    <Button
                      variant="outlined"
                      component="label"
                      fullWidth
                      startIcon={<CloudUpload />}
                    >
                      Select Image File
                      <input
                        type="file"
                        hidden
                        accept="image/*"
                        onChange={handleFileChange}
                      />
                    </Button>
                    {imageForm.file && (
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        Selected: {imageForm.file.name}
                      </Typography>
                    )}
                  </Grid>
                )}

                {/* Category */}
                <Grid size={{ xs: 12, sm: 6 }}>
                  <FormControl fullWidth required>
                    <InputLabel>Category</InputLabel>
                    <Select
                      name="category_id"
                      value={imageForm.category_id}
                      label="Category"
                      onChange={(e) => setImageForm(prev => ({ ...prev, category_id: e.target.value }))}
                      disabled={dialogMode === 'view'}
                    >
                      {galleryCategories.filter((cat: any) => cat.is_active).map((category: any) => (
                        <MenuItem key={category.id} value={category.id}>
                          {category.description || category.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                {/* Display Order */}
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Display Order"
                    name="display_order"
                    type="number"
                    value={imageForm.display_order}
                    onChange={handleFormChange}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>

                {/* Title */}
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    required
                    label="Title"
                    name="title"
                    value={imageForm.title}
                    onChange={handleFormChange}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>

                {/* Description */}
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Description"
                    name="description"
                    multiline
                    rows={3}
                    value={imageForm.description}
                    onChange={handleFormChange}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>

                {/* Is Visible on Home Page */}
                <Grid size={{ xs: 12 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        name="is_visible_on_home_page"
                        checked={imageForm.is_visible_on_home_page}
                        onChange={handleFormChange}
                        disabled={dialogMode === 'view'}
                      />
                    }
                    label="Show on Home Page Carousel"
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>
                {dialogMode === 'view' ? 'Close' : 'Cancel'}
              </Button>
              {dialogMode !== 'view' && (
                <Button
                  onClick={handleSubmit}
                  variant="contained"
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={20} /> :
                   (selectedImage ? 'Update' : 'Upload') + ' Image'}
                </Button>
              )}
            </DialogActions>
          </Dialog>

          {/* Snackbar for notifications */}
          <Snackbar
            open={snackbar.open}
            autoHideDuration={6000}
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            <Alert
              onClose={() => setSnackbar({ ...snackbar, open: false })}
              severity={snackbar.severity}
              sx={{ width: '100%' }}
            >
              {snackbar.message}
            </Alert>
          </Snackbar>
        </ServiceConfigurationLoader>
      </Box>
    </AdminLayout>
  );
};

export default GalleryManagement;

