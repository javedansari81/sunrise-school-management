import React from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Button,
  Paper,
} from '@mui/material';
import {
  School,
  Groups,
  Science,
  SportsBasketball,
  Login,
} from '@mui/icons-material';
import ImageSlider from '../components/Home/ImageSlider';

const Home: React.FC = () => {
  const features = [
    {
      icon: <School fontSize="large" />,
      title: 'Quality Education',
      description: 'Comprehensive curriculum designed to nurture academic excellence and character development.',
    },
    {
      icon: <Groups fontSize="large" />,
      title: 'Experienced Faculty',
      description: 'Dedicated and qualified teachers committed to student success and holistic development.',
    },
    {
      icon: <Science fontSize="large" />,
      title: 'Modern Facilities',
      description: 'State-of-the-art laboratories, library, and technology-enabled classrooms.',
    },
    {
      icon: <SportsBasketball fontSize="large" />,
      title: 'Sports & Activities',
      description: 'Wide range of sports and extracurricular activities for overall personality development.',
    },
  ];

  const achievements = [
    {
      title: 'Academic Excellence',
      description: '95% pass rate in board examinations',
      image: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    },
    {
      title: 'Sports Champions',
      description: 'District level winners in multiple sports',
      image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    },
    {
      title: 'Cultural Programs',
      description: 'Award-winning cultural and arts programs',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    },
  ];

  return (
    <Box>
      {/* Hero Section with Image Slider */}
      <ImageSlider />

      {/* About Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Box textAlign="center" mb={6}>
          <Typography variant="h3" component="h2" gutterBottom fontWeight="bold">
            About Sunrise National Public School
          </Typography>
          <Typography variant="h6" color="text.secondary" maxWidth="800px" mx="auto">
            Established with a vision to provide quality education, we are committed to nurturing
            young minds and preparing them for a successful future. Our school offers education
            from Pre-Primary to Class 8 with a focus on academic excellence and character building.
          </Typography>
        </Box>

        {/* Features Grid */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4, mb: 8 }}>
          {features.map((feature, index) => (
            <Box key={index} sx={{ flex: '1 1 250px', minWidth: 250 }}>
              <Paper
                elevation={3}
                sx={{
                  p: 3,
                  textAlign: 'center',
                  height: '100%',
                  transition: 'transform 0.3s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                  },
                }}
              >
                <Box sx={{ color: 'primary.main', mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </Paper>
            </Box>
          ))}
        </Box>

        {/* Achievements Section */}
        <Box textAlign="center" mb={6}>
          <Typography variant="h4" component="h2" gutterBottom fontWeight="bold">
            Our Achievements
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Celebrating excellence in academics, sports, and cultural activities
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4, mb: 8 }}>
          {achievements.map((achievement, index) => (
            <Box key={index} sx={{ flex: '1 1 300px', minWidth: 300 }}>
              <Card
                sx={{
                  height: '100%',
                  transition: 'transform 0.3s ease-in-out',
                  '&:hover': {
                    transform: 'scale(1.02)',
                  },
                }}
              >
                <CardMedia
                  component="img"
                  height="200"
                  image={achievement.image}
                  alt={achievement.title}
                />
                <CardContent>
                  <Typography variant="h6" gutterBottom fontWeight="bold">
                    {achievement.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {achievement.description}
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          ))}
        </Box>

        {/* Call to Action */}
        <Box
          textAlign="center"
          sx={{
            backgroundColor: 'primary.main',
            color: 'white',
            p: 6,
            borderRadius: 2,
          }}
        >
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Ready to Join Our School Community?
          </Typography>
          <Typography variant="h6" mb={3}>
            Give your child the best educational foundation for a bright future
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              sx={{
                backgroundColor: 'white',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: '#f5f5f5',
                },
                px: 4,
                py: 1.5,
              }}
            >
              Apply for Admission
            </Button>
            <Button
              component={Link}
              to="/login"
              variant="outlined"
              size="large"
              startIcon={<Login />}
              sx={{
                borderColor: 'white',
                color: 'white',
                '&:hover': {
                  borderColor: 'white',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
                px: 4,
                py: 1.5,
              }}
            >
              Login Portal
            </Button>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Home;
