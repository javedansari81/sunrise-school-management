/**
 * Gallery Component - Sunrise National Public School
 * Public-facing gallery page that displays school photos organized by categories
 * Features lazy loading, category filtering, and lightbox view
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Tabs,
  Tab,
  Dialog,
  DialogContent,
  IconButton,
  Paper,
  Skeleton,
  CircularProgress,
  Alert,
  Chip,
  Menu,
  MenuItem as MuiMenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Close,
  School,
  SportsBasketball,
  Celebration,
  Science,
  Palette,
  EmojiEvents,
  Flag,
  CalendarToday,
  TheaterComedy,
  EmojiFlags,
  MusicNote,
  MenuBook,
  Person,
  PhotoLibrary,
  MoreHoriz,
} from '@mui/icons-material';
import { galleryAPI, PublicGalleryCategory, PublicGalleryImage } from '../services/galleryService';

// Icon mapping for category icons
const iconMap: { [key: string]: React.ReactElement } = {
  Flag: <Flag />,
  School: <School />,
  CalendarToday: <CalendarToday />,
  SportsBasketball: <SportsBasketball />,
  TheaterComedy: <TheaterComedy />,
  EmojiFlags: <EmojiFlags />,
  Science: <Science />,
  MusicNote: <MusicNote />,
  MenuBook: <MenuBook />,
  Person: <Person />,
  Celebration: <Celebration />,
  Palette: <Palette />,
  EmojiEvents: <EmojiEvents />,
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`gallery-tabpanel-${index}`}
      aria-labelledby={`gallery-tab-${index}`}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

const Gallery: React.FC = () => {
  // State management
  const [categories, setCategories] = useState<PublicGalleryCategory[]>([]);
  const [allCategories, setAllCategories] = useState<PublicGalleryCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [selectedImage, setSelectedImage] = useState<PublicGalleryImage | null>(null);
  const [imageLoading, setImageLoading] = useState<{ [key: number]: boolean }>({});
  const [imageErrors, setImageErrors] = useState<{ [key: number]: boolean }>({});
  const [moreMenuAnchor, setMoreMenuAnchor] = useState<null | HTMLElement>(null);
  const moreMenuOpen = Boolean(moreMenuAnchor);

  // Initial load - fetch first 3 categories
  useEffect(() => {
    const fetchInitialCategories = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await galleryAPI.getPublicGalleryGrouped(3);
        setCategories(response.data);

        // Also fetch all categories for the dropdown
        const allResponse = await galleryAPI.getPublicGalleryGrouped();
        setAllCategories(allResponse.data);
      } catch (err: any) {
        console.error('Error fetching gallery:', err);
        setError(err.response?.data?.detail || 'Failed to load gallery. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchInitialCategories();
  }, []);

  // Handle tab change
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    // Don't change tab if "More" tab is clicked (it opens menu instead)
    if (newValue !== categories.length) {
      setTabValue(newValue);
    }
  };

  // Handle More menu open
  const handleMoreMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMoreMenuAnchor(event.currentTarget);
  };

  // Handle More menu close
  const handleMoreMenuClose = () => {
    setMoreMenuAnchor(null);
  };

  // Handle category selection from More menu
  const handleCategorySelect = async (categoryId: number) => {
    handleMoreMenuClose();

    const existingCategory = categories.find(cat => cat.id === categoryId);

    if (!existingCategory) {
      // Lazy load this category
      try {
        const response = await galleryAPI.getImagesByCategory(categoryId);
        const categoryInfo = allCategories.find(cat => cat.id === categoryId);

        if (categoryInfo) {
          const newCategory: PublicGalleryCategory = {
            ...categoryInfo,
            images: response.data.map((img: any) => ({
              id: img.id,
              title: img.title,
              description: img.description,
              cloudinary_url: img.cloudinary_url,
              cloudinary_thumbnail_url: img.cloudinary_thumbnail_url,
              display_order: img.display_order,
              upload_date: img.upload_date,
            }))
          };

          setCategories(prev => [...prev, newCategory]);
          setTabValue(categories.length);
        }
      } catch (err: any) {
        console.error('Error loading category:', err);
        setError('Failed to load category');
      }
    } else {
      // Switch to existing category tab
      const index = categories.findIndex(cat => cat.id === categoryId);
      setTabValue(index);
    }
  };

  // Handle image click (open lightbox)
  const handleImageClick = (image: PublicGalleryImage) => {
    setSelectedImage(image);
  };

  // Handle close lightbox
  const handleCloseDialog = () => {
    setSelectedImage(null);
  };

  // Handle image load
  const handleImageLoad = (imageId: number) => {
    setImageLoading(prev => ({ ...prev, [imageId]: false }));
  };

  // Handle image error
  const handleImageError = (imageId: number) => {
    setImageErrors(prev => ({ ...prev, [imageId]: true }));
    setImageLoading(prev => ({ ...prev, [imageId]: false }));
  };

  // Handle image load start
  const handleImageLoadStart = (imageId: number) => {
    setImageLoading(prev => ({ ...prev, [imageId]: true }));
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading gallery...
        </Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  // No data found
  if (!loading && categories.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Hero Section */}
        <Box textAlign="center" mb={4}>
          <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" color="primary">
            School Gallery
          </Typography>
          <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
            Explore the vibrant life at Sunrise National Public School through our photo gallery
          </Typography>
        </Box>

        {/* No Data Message */}
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <PhotoLibrary sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h5" color="text.secondary" gutterBottom>
            No Gallery Images Available
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gallery images will appear here once they are uploaded by the administrator.
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={4}>
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" color="primary">
          School Gallery
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
          Explore the vibrant life at Sunrise National Public School through our photo gallery
        </Typography>
      </Box>

      {/* Category Tabs with More Menu */}
      <Paper elevation={2} sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': {
              minHeight: 64,
              textTransform: 'none',
              fontSize: '1rem',
            },
          }}
        >
          {categories.map((category, index) => (
            <Tab
              key={category.id}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {category.icon && iconMap[category.icon]}
                  <span>{category.name}</span>
                  <Chip label={category.images.length} size="small" color="primary" />
                </Box>
              }
              id={`gallery-tab-${index}`}
              aria-controls={`gallery-tabpanel-${index}`}
            />
          ))}

          {/* More Tab */}
          {allCategories.length > categories.length && (
            <Tab
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <MoreHoriz />
                  <span>More</span>
                </Box>
              }
              onClick={handleMoreMenuOpen}
              sx={{
                minWidth: 'auto',
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            />
          )}
        </Tabs>

        {/* More Categories Menu */}
        <Menu
          anchorEl={moreMenuAnchor}
          open={moreMenuOpen}
          onClose={handleMoreMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          {allCategories
            .filter(cat => !categories.find(c => c.id === cat.id))
            .map((category) => (
              <MuiMenuItem
                key={category.id}
                onClick={() => handleCategorySelect(category.id)}
              >
                <ListItemIcon>
                  {category.icon && iconMap[category.icon]}
                </ListItemIcon>
                <ListItemText primary={category.name} />
              </MuiMenuItem>
            ))}
        </Menu>

        {/* Gallery Content */}
        {categories.map((category, index) => (
          <TabPanel key={category.id} value={tabValue} index={index}>
            {category.images.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary">
                  No images available in this category yet.
                </Typography>
              </Box>
            ) : (
              <Grid container spacing={3}>
                {category.images.map((image) => (
                  <Grid key={image.id} size={{ xs: 12, sm: 6, md: 4 }}>
                    <Card
                      elevation={2}
                      sx={{
                        cursor: 'pointer',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        '&:hover': {
                          transform: 'scale(1.02)',
                          boxShadow: 4
                        }
                      }}
                      onClick={() => !imageErrors[image.id] && handleImageClick(image)}
                    >
                      <Box sx={{ position: 'relative', height: 200 }}>
                        {imageLoading[image.id] && (
                          <Skeleton
                            variant="rectangular"
                            width="100%"
                            height={200}
                            animation="wave"
                          />
                        )}
                        {imageErrors[image.id] ? (
                          <Box
                            sx={{
                              height: 200,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              backgroundColor: 'grey.100',
                              color: 'text.secondary'
                            }}
                          >
                            <Typography variant="body2">
                              Image unavailable
                            </Typography>
                          </Box>
                        ) : (
                          <CardMedia
                            component="img"
                            height="200"
                            image={image.cloudinary_thumbnail_url || image.cloudinary_url}
                            alt={image.title}
                            sx={{
                              objectFit: 'cover',
                              display: imageLoading[image.id] ? 'none' : 'block'
                            }}
                            onLoad={() => handleImageLoad(image.id)}
                            onError={() => handleImageError(image.id)}
                            onLoadStart={() => handleImageLoadStart(image.id)}
                          />
                        )}
                      </Box>
                      <CardContent>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                          {image.title}
                        </Typography>
                        {image.description && (
                          <Typography variant="body2" color="text.secondary">
                            {image.description}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </TabPanel>
        ))}
      </Paper>

      {/* Lightbox Dialog */}
      <Dialog
        open={!!selectedImage}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
        slotProps={{
          paper: {
            sx: {
              backgroundColor: 'rgba(0, 0, 0, 0.9)',
            }
          }
        }}
      >
        <IconButton
          onClick={handleCloseDialog}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: 'white',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
            },
            zIndex: 1,
          }}
        >
          <Close />
        </IconButton>
        <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {selectedImage && (
            <>
              <Box
                component="img"
                src={selectedImage.cloudinary_url}
                alt={selectedImage.title}
                sx={{
                  width: '100%',
                  height: 'auto',
                  maxHeight: '80vh',
                  objectFit: 'contain',
                }}
              />
              <Box sx={{ p: 3, color: 'white', textAlign: 'center' }}>
                <Typography variant="h5" gutterBottom>
                  {selectedImage.title}
                </Typography>
                {selectedImage.description && (
                  <Typography variant="body1" color="rgba(255, 255, 255, 0.7)">
                    {selectedImage.description}
                  </Typography>
                )}
              </Box>
            </>
          )}
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default Gallery;