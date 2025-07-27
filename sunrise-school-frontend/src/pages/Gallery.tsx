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

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleImageClick = (imageUrl: string) => {
    setSelectedImage(imageUrl);
  };

  const handleCloseDialog = () => {
    setSelectedImage(null);
  };

  // Mock image data - in a real app, these would come from an API
  const galleryCategories = [
    {
      label: 'Campus Life',
      icon: <School />,
      images: [
        { url: '/api/placeholder/400/300', title: 'Main Building', description: 'Our beautiful main academic building' },
        { url: '/api/placeholder/400/300', title: 'Library', description: 'State-of-the-art library facility' },
        { url: '/api/placeholder/400/300', title: 'Playground', description: 'Spacious playground for outdoor activities' },
        { url: '/api/placeholder/400/300', title: 'Computer Lab', description: 'Modern computer laboratory' },
        { url: '/api/placeholder/400/300', title: 'Science Lab', description: 'Well-equipped science laboratory' },
        { url: '/api/placeholder/400/300', title: 'Cafeteria', description: 'Hygienic and spacious cafeteria' },
      ]
    },
    {
      label: 'Sports & Activities',
      icon: <SportsBasketball />,
      images: [
        { url: '/api/placeholder/400/300', title: 'Basketball Court', description: 'Indoor basketball court' },
        { url: '/api/placeholder/400/300', title: 'Football Field', description: 'Large football ground' },
        { url: '/api/placeholder/400/300', title: 'Swimming Pool', description: 'Olympic size swimming pool' },
        { url: '/api/placeholder/400/300', title: 'Athletics Track', description: '400m athletics track' },
        { url: '/api/placeholder/400/300', title: 'Gymnasium', description: 'Fully equipped gymnasium' },
        { url: '/api/placeholder/400/300', title: 'Yoga Hall', description: 'Peaceful yoga and meditation hall' },
      ]
    },
    {
      label: 'Events & Celebrations',
      icon: <Celebration />,
      images: [
        { url: '/api/placeholder/400/300', title: 'Annual Day', description: 'Annual day celebration 2023' },
        { url: '/api/placeholder/400/300', title: 'Sports Day', description: 'Inter-house sports competition' },
        { url: '/api/placeholder/400/300', title: 'Science Fair', description: 'Student science exhibition' },
        { url: '/api/placeholder/400/300', title: 'Cultural Program', description: 'Traditional dance performance' },
        { url: '/api/placeholder/400/300', title: 'Prize Distribution', description: 'Academic achievement awards' },
        { url: '/api/placeholder/400/300', title: 'Independence Day', description: 'National flag hoisting ceremony' },
      ]
    },
    {
      label: 'Academic Activities',
      icon: <Science />,
      images: [
        { url: '/api/placeholder/400/300', title: 'Chemistry Experiment', description: 'Students conducting experiments' },
        { url: '/api/placeholder/400/300', title: 'Math Class', description: 'Interactive mathematics session' },
        { url: '/api/placeholder/400/300', title: 'Art Workshop', description: 'Creative art and craft workshop' },
        { url: '/api/placeholder/400/300', title: 'Debate Competition', description: 'Inter-school debate competition' },
        { url: '/api/placeholder/400/300', title: 'Field Trip', description: 'Educational field trip to museum' },
        { url: '/api/placeholder/400/300', title: 'Project Presentation', description: 'Student project presentations' },
      ]
    },
    {
      label: 'Art & Culture',
      icon: <Palette />,
      images: [
        { url: '/api/placeholder/400/300', title: 'Art Exhibition', description: 'Student artwork display' },
        { url: '/api/placeholder/400/300', title: 'Music Concert', description: 'School choir performance' },
        { url: '/api/placeholder/400/300', title: 'Drama Performance', description: 'Annual drama production' },
        { url: '/api/placeholder/400/300', title: 'Dance Festival', description: 'Traditional dance festival' },
        { url: '/api/placeholder/400/300', title: 'Craft Workshop', description: 'Handicraft making session' },
        { url: '/api/placeholder/400/300', title: 'Poetry Recitation', description: 'Poetry competition event' },
      ]
    },
    {
      label: 'Achievements',
      icon: <EmojiEvents />,
      images: [
        { url: '/api/placeholder/400/300', title: 'Academic Toppers', description: 'Board exam toppers 2023' },
        { url: '/api/placeholder/400/300', title: 'Sports Champions', description: 'District level sports winners' },
        { url: '/api/placeholder/400/300', title: 'Science Olympiad', description: 'National science olympiad winners' },
        { url: '/api/placeholder/400/300', title: 'Art Competition', description: 'State level art competition winners' },
        { url: '/api/placeholder/400/300', title: 'Quiz Champions', description: 'Inter-school quiz competition' },
        { url: '/api/placeholder/400/300', title: 'Excellence Awards', description: 'Overall excellence recognition' },
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
                      transition: 'transform 0.2s',
                      '&:hover': {
                        transform: 'scale(1.02)',
                        elevation: 4
                      }
                    }}
                    onClick={() => handleImageClick(image.url)}
                  >
                    <CardMedia
                      component="img"
                      height="200"
                      image={image.url}
                      alt={image.title}
                      sx={{ objectFit: 'cover' }}
                    />
                    <CardContent>
                      <Typography variant="h6" gutterBottom fontWeight="bold">
                        {image.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {image.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </TabPanel>
        ))}
      </Paper>

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
