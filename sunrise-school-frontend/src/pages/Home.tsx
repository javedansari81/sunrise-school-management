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
      <Container maxWidth="lg" sx={{ py: { xs: 4, sm: 6, md: 8 }, px: { xs: 2, sm: 3 } }}>
        <Box textAlign="center" mb={{ xs: 4, sm: 5, md: 6 }}>
          <Typography
            variant="h3"
            component="h2"
            gutterBottom
            fontWeight="bold"
            sx={{
              fontSize: { xs: '1.5rem', sm: '2rem', md: '3rem' },
              lineHeight: { xs: 1.2, sm: 1.3 },
              mb: { xs: 2, sm: 3 }
            }}
          >
            About Sunrise National Public School
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{
              maxWidth: "800px",
              mx: "auto",
              fontSize: { xs: '0.875rem', sm: '1rem', md: '1.25rem' },
              lineHeight: { xs: 1.4, sm: 1.5 },
              px: { xs: 1, sm: 2 }
            }}
          >
            Established with a vision to provide quality education, we are committed to nurturing
            young minds and preparing them for a successful future. Our school offers education
            from Pre-Primary to Class 8 with a focus on academic excellence and character building.
          </Typography>
        </Box>

        {/* Features Grid */}
        <Box sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(4, 1fr)'
          },
          gap: { xs: 2, sm: 3, md: 4 },
          mb: { xs: 6, sm: 7, md: 8 }
        }}>
          {features.map((feature, index) => (
            <Paper
              key={index}
              elevation={3}
              sx={{
                p: { xs: 2, sm: 2.5, md: 3 },
                textAlign: 'center',
                height: '100%',
                transition: 'transform 0.3s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-5px)',
                },
              }}
            >
              <Box sx={{ color: 'primary.main', mb: { xs: 1.5, sm: 2 } }}>
                {feature.icon}
              </Box>
              <Typography
                variant="h6"
                gutterBottom
                fontWeight="bold"
                sx={{
                  fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
                  mb: { xs: 1, sm: 1.5 }
                }}
              >
                {feature.title}
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  lineHeight: { xs: 1.4, sm: 1.5 }
                }}
              >
                {feature.description}
              </Typography>
            </Paper>
          ))}
        </Box>

        {/* Achievements Section */}
        <Box textAlign="center" mb={{ xs: 4, sm: 5, md: 6 }}>
          <Typography
            variant="h4"
            component="h2"
            gutterBottom
            fontWeight="bold"
            sx={{
              fontSize: { xs: '1.25rem', sm: '1.75rem', md: '2.125rem' },
              mb: { xs: 1.5, sm: 2 }
            }}
          >
            Our Achievements
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{
              fontSize: { xs: '0.875rem', sm: '1rem', md: '1.25rem' },
              px: { xs: 1, sm: 2 }
            }}
          >
            Celebrating excellence in academics, sports, and cultural activities
          </Typography>
        </Box>

        <Box sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(3, 1fr)'
          },
          gap: { xs: 2, sm: 3, md: 4 },
          mb: { xs: 6, sm: 7, md: 8 }
        }}>
          {achievements.map((achievement, index) => (
            <Card
              key={index}
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
                image={achievement.image}
                alt={achievement.title}
                sx={{
                  height: { xs: 150, sm: 180, md: 200 },
                  objectFit: 'cover'
                }}
              />
              <CardContent sx={{ p: { xs: 1.5, sm: 2 } }}>
                <Typography
                  variant="h6"
                  gutterBottom
                  fontWeight="bold"
                  sx={{
                    fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
                    mb: { xs: 1, sm: 1.5 }
                  }}
                >
                  {achievement.title}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    lineHeight: { xs: 1.4, sm: 1.5 }
                  }}
                >
                  {achievement.description}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Call to Action */}
        <Box
          textAlign="center"
          sx={{
            backgroundColor: 'primary.main',
            color: 'white',
            p: { xs: 3, sm: 4, md: 6 },
            borderRadius: 2,
            mx: { xs: 1, sm: 0 }
          }}
        >
          <Typography
            variant="h4"
            gutterBottom
            fontWeight="bold"
            sx={{
              fontSize: { xs: '1.25rem', sm: '1.75rem', md: '2.125rem' },
              mb: { xs: 2, sm: 2.5, md: 3 }
            }}
          >
            Ready to Join Our School Community?
          </Typography>
          <Typography
            variant="h6"
            sx={{
              mb: { xs: 2.5, sm: 3 },
              fontSize: { xs: '0.875rem', sm: '1rem', md: '1.25rem' },
              px: { xs: 1, sm: 2 }
            }}
          >
            Give your child the best educational foundation for a bright future
          </Typography>
          <Box sx={{
            display: 'flex',
            gap: { xs: 1.5, sm: 2 },
            justifyContent: 'center',
            flexWrap: 'wrap',
            flexDirection: { xs: 'column', sm: 'row' },
            alignItems: 'center'
          }}>
            <Button
              variant="contained"
              size="large"
              sx={{
                backgroundColor: 'white',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: '#f5f5f5',
                },
                px: { xs: 3, sm: 4 },
                py: { xs: 1.25, sm: 1.5 },
                fontSize: { xs: '0.875rem', sm: '1rem' },
                minWidth: { xs: '200px', sm: 'auto' }
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
                px: { xs: 3, sm: 4 },
                py: { xs: 1.25, sm: 1.5 },
                fontSize: { xs: '0.875rem', sm: '1rem' },
                minWidth: { xs: '200px', sm: 'auto' }
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
