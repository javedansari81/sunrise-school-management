/**
 * Gallery Component - Sunrise National Public School
 *
 * This component displays school pictures organized by categories.
 * Currently uses static images from Unsplash for demonstration.
 *
 * TODO: Admin Dashboard Integration
 * - Replace static galleryCategories array with API call
 * - Add image upload functionality for admin users
 * - Implement image management (add, edit, delete)
 * - Add image approval workflow
 * - Include metadata fields: uploadDate, category, tags, etc.
 * - Add search and filter functionality
 * - Implement pagination for large image collections
 *
 * API Integration Points:
 * - GET /api/gallery/images - Fetch all images
 * - POST /api/gallery/images - Upload new image (admin only)
 * - PUT /api/gallery/images/:id - Update image details (admin only)
 * - DELETE /api/gallery/images/:id - Delete image (admin only)
 * - GET /api/gallery/categories - Fetch image categories
 */

import React, { useState } from 'react';
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
  Alert,
} from '@mui/material';
import {
  Close,
  School,
  SportsBasketball,
  Celebration,
  Science,
  Palette,
  EmojiEvents,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// Interface for gallery image data - designed for future API integration
interface GalleryImage {
  url: string;
  title: string;
  description: string;
  uploadDate?: string; // Future field for admin dashboard
  category?: string; // Future field for categorization
  tags?: string[]; // Future field for tagging
  id?: number; // Future field for database ID
  approved?: boolean; // Future field for approval workflow
}

interface GalleryCategory {
  label: string;
  icon: React.ReactElement;
  images: GalleryImage[];
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
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Gallery: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [imageLoading, setImageLoading] = useState<{ [key: string]: boolean }>({});
  const [imageErrors, setImageErrors] = useState<{ [key: string]: boolean }>({});

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleImageClick = (imageUrl: string) => {
    setSelectedImage(imageUrl);
  };

  const handleCloseDialog = () => {
    setSelectedImage(null);
  };

  const handleImageLoad = (imageUrl: string) => {
    setImageLoading(prev => ({ ...prev, [imageUrl]: false }));
  };

  const handleImageError = (imageUrl: string) => {
    setImageLoading(prev => ({ ...prev, [imageUrl]: false }));
    setImageErrors(prev => ({ ...prev, [imageUrl]: true }));
  };

  const handleImageLoadStart = (imageUrl: string) => {
    setImageLoading(prev => ({ ...prev, [imageUrl]: true }));
  };

  // Static image data - TODO: Replace with API call from admin dashboard
  // Structure designed for easy integration with dynamic image management
  const galleryCategories: GalleryCategory[] = [
    {
      label: 'Campus Life',
      icon: <School />,
      images: [
        {
          url: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Main Building',
          description: 'Our beautiful main academic building',
          uploadDate: '2024-01-15',
          category: 'campus'
        },
        {
          url: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Library',
          description: 'State-of-the-art library facility',
          uploadDate: '2024-01-16',
          category: 'campus'
        },
        {
          url: 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Playground',
          description: 'Spacious playground for outdoor activities',
          uploadDate: '2024-01-17',
          category: 'campus'
        },
        {
          url: 'https://images.unsplash.com/photo-1562774053-701939374585?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Computer Lab',
          description: 'Modern computer laboratory with latest technology',
          uploadDate: '2024-01-18',
          category: 'campus'
        },
        {
          url: 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Science Lab',
          description: 'Well-equipped science laboratory for experiments',
          uploadDate: '2024-01-19',
          category: 'campus'
        },
        {
          url: 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Cafeteria',
          description: 'Hygienic and spacious cafeteria for students',
          uploadDate: '2024-01-20',
          category: 'campus'
        },
      ]
    },
    {
      label: 'Sports & Activities',
      icon: <SportsBasketball />,
      images: [
        {
          url: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Basketball Court',
          description: 'Students enjoying basketball during sports period',
          uploadDate: '2024-01-21',
          category: 'sports'
        },
        {
          url: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Football Field',
          description: 'Inter-house football competition in progress',
          uploadDate: '2024-01-22',
          category: 'sports'
        },
        {
          url: 'https://images.unsplash.com/photo-1530549387789-4c1017266635?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Swimming Activities',
          description: 'Swimming lessons for primary students',
          uploadDate: '2024-01-23',
          category: 'sports'
        },
        {
          url: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Athletics Track',
          description: 'Annual sports day track events',
          uploadDate: '2024-01-24',
          category: 'sports'
        },
        {
          url: 'https://images.unsplash.com/photo-1571902943202-507ec2618e8f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Gymnasium',
          description: 'Indoor sports and fitness activities',
          uploadDate: '2024-01-25',
          category: 'sports'
        },
        {
          url: 'https://images.unsplash.com/photo-1506629905607-d405b7a30db9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Yoga Session',
          description: 'Morning yoga and meditation for students',
          uploadDate: '2024-01-26',
          category: 'sports'
        },
      ]
    },
    {
      label: 'Events & Celebrations',
      icon: <Celebration />,
      images: [
        {
          url: 'https://images.unsplash.com/photo-1511632765486-a01980e01a18?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Annual Day',
          description: 'Annual day celebration with cultural performances',
          uploadDate: '2024-01-27',
          category: 'events'
        },
        {
          url: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Sports Day',
          description: 'Inter-house sports competition and awards',
          uploadDate: '2024-01-28',
          category: 'events'
        },
        {
          url: 'https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Science Fair',
          description: 'Student science projects and exhibitions',
          uploadDate: '2024-01-29',
          category: 'events'
        },
        {
          url: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Cultural Program',
          description: 'Traditional dance and music performances',
          uploadDate: '2024-01-30',
          category: 'events'
        },
        {
          url: 'https://images.unsplash.com/photo-1559027615-cd4628902d4a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Prize Distribution',
          description: 'Academic achievement awards ceremony',
          uploadDate: '2024-01-31',
          category: 'events'
        },
        {
          url: 'https://images.unsplash.com/photo-1509062522246-3755977927d7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Independence Day',
          description: 'National flag hoisting and patriotic celebration',
          uploadDate: '2024-02-01',
          category: 'events'
        },
      ]
    },
    {
      label: 'Academic Activities',
      icon: <Science />,
      images: [
        {
          url: 'https://images.unsplash.com/photo-1576086213369-97a306d36557?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Science Experiment',
          description: 'Students conducting chemistry experiments in lab',
          uploadDate: '2024-02-02',
          category: 'academics'
        },
        {
          url: 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Math Class',
          description: 'Interactive mathematics learning session',
          uploadDate: '2024-02-03',
          category: 'academics'
        },
        {
          url: 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Art Workshop',
          description: 'Creative art and craft workshop for students',
          uploadDate: '2024-02-04',
          category: 'academics'
        },
        {
          url: 'https://images.unsplash.com/photo-1577896851231-70ef18881754?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Debate Competition',
          description: 'Inter-school debate competition participation',
          uploadDate: '2024-02-05',
          category: 'academics'
        },
        {
          url: 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Field Trip',
          description: 'Educational field trip to science museum',
          uploadDate: '2024-02-06',
          category: 'academics'
        },
        {
          url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Project Presentation',
          description: 'Students presenting their research projects',
          uploadDate: '2024-02-07',
          category: 'academics'
        },
      ]
    },
    {
      label: 'Art & Culture',
      icon: <Palette />,
      images: [
        {
          url: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Art Exhibition',
          description: 'Student artwork and creative displays',
          uploadDate: '2024-02-08',
          category: 'culture'
        },
        {
          url: 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Music Concert',
          description: 'School choir and musical performances',
          uploadDate: '2024-02-09',
          category: 'culture'
        },
        {
          url: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Drama Performance',
          description: 'Annual drama production by students',
          uploadDate: '2024-02-10',
          category: 'culture'
        },
        {
          url: 'https://images.unsplash.com/photo-1571266028243-d220c9c3b2d2?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Dance Festival',
          description: 'Traditional and modern dance performances',
          uploadDate: '2024-02-11',
          category: 'culture'
        },
        {
          url: 'https://images.unsplash.com/photo-1596464716127-f2a82984de30?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Craft Workshop',
          description: 'Handicraft and creative arts session',
          uploadDate: '2024-02-12',
          category: 'culture'
        },
        {
          url: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Poetry Recitation',
          description: 'Poetry competition and literary events',
          uploadDate: '2024-02-13',
          category: 'culture'
        },
      ]
    },
    {
      label: 'Achievements',
      icon: <EmojiEvents />,
      images: [
        {
          url: 'https://images.unsplash.com/photo-1559027615-cd4628902d4a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Academic Toppers',
          description: 'Outstanding academic achievers of 2024',
          uploadDate: '2024-02-14',
          category: 'achievements'
        },
        {
          url: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Sports Champions',
          description: 'District level sports competition winners',
          uploadDate: '2024-02-15',
          category: 'achievements'
        },
        {
          url: 'https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Science Olympiad',
          description: 'National science olympiad medal winners',
          uploadDate: '2024-02-16',
          category: 'achievements'
        },
        {
          url: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Art Competition',
          description: 'State level art competition champions',
          uploadDate: '2024-02-17',
          category: 'achievements'
        },
        {
          url: 'https://images.unsplash.com/photo-1577896851231-70ef18881754?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Quiz Champions',
          description: 'Inter-school quiz competition winners',
          uploadDate: '2024-02-18',
          category: 'achievements'
        },
        {
          url: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
          title: 'Excellence Awards',
          description: 'Overall school excellence recognition ceremony',
          uploadDate: '2024-02-19',
          category: 'achievements'
        },
      ]
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" color="primary">
          School Gallery
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
          Explore the vibrant life at Sunrise National Public School through our photo gallery
        </Typography>
      </Box>

      {/* Gallery Tabs */}
      <Paper elevation={3} sx={{ mb: 4 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          {galleryCategories.map((category, index) => (
            <Tab
              key={index}
              label={category.label}
              icon={category.icon}
              iconPosition="start"
              sx={{ minHeight: 72 }}
            />
          ))}
        </Tabs>

        {/* Gallery Content */}
        {galleryCategories.map((category, index) => (
          <TabPanel key={index} value={tabValue} index={index}>
            <Grid container spacing={3}>
              {category.images.map((image, imgIndex) => (
                <Grid key={imgIndex} size={{ xs: 12, sm: 6, md: 4 }}>
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
                    onClick={() => !imageErrors[image.url] && handleImageClick(image.url)}
                  >
                    <Box sx={{ position: 'relative', height: 200 }}>
                      {imageLoading[image.url] && (
                        <Skeleton
                          variant="rectangular"
                          width="100%"
                          height={200}
                          animation="wave"
                        />
                      )}
                      {imageErrors[image.url] ? (
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
                          image={image.url}
                          alt={image.title}
                          sx={{
                            objectFit: 'cover',
                            display: imageLoading[image.url] ? 'none' : 'block'
                          }}
                          onLoad={() => handleImageLoad(image.url)}
                          onError={() => handleImageError(image.url)}
                          onLoadStart={() => handleImageLoadStart(image.url)}
                        />
                      )}
                    </Box>
                    <CardContent>
                      <Typography variant="h6" gutterBottom fontWeight="bold">
                        {image.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {image.description}
                      </Typography>
                      {/* Future admin dashboard integration point */}
                      {/* <Typography variant="caption" color="text.disabled">
                        Uploaded: {image.uploadDate}
                      </Typography> */}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </TabPanel>
        ))}
      </Paper>

      {/* Future Admin Integration Note */}
      <Alert severity="info" sx={{ mt: 3, mb: 2 }}>
        <Typography variant="body2">
          <strong>Gallery Management:</strong> This gallery is ready for admin dashboard integration.
          Administrators will be able to upload, manage, and organize school pictures through the admin panel.
        </Typography>
      </Alert>

      {/* Image Dialog */}
      <Dialog
        open={!!selectedImage}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogContent sx={{ p: 0, position: 'relative' }}>
          <IconButton
            onClick={handleCloseDialog}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: 'white',
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              zIndex: 1,
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.7)',
              }
            }}
          >
            <Close />
          </IconButton>
          {selectedImage && (
            <img
              src={selectedImage}
              alt="Gallery Image"
              style={{
                width: '100%',
                height: 'auto',
                display: 'block'
              }}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Gallery Stats */}
      <Box textAlign="center" mt={6}>
        <Typography variant="body1" color="text.secondary">
          Capturing memories and celebrating achievements at Sunrise National Public School. 
          Our gallery showcases the vibrant academic and extracurricular life of our students.
        </Typography>
      </Box>
    </Container>
  );
};

export default Gallery;
