import React from 'react';
import Slider from 'react-slick';
import { Box, Typography, Button, Container } from '@mui/material';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';

interface SlideData {
  id: number;
  image: string;
  title: string;
  description: string;
  buttonText?: string;
  buttonLink?: string;
}

const ImageSlider: React.FC = () => {
  const slides: SlideData[] = [
    {
      id: 1,
      image: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80',
      title: 'Welcome to Sunrise National Public School',
      description: 'Nurturing young minds for a brighter tomorrow with excellence in education.',
      buttonText: 'Learn More',
      buttonLink: '/about',
    },
    {
      id: 2,
      image: 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80',
      title: 'Excellence in Education',
      description: 'Providing quality education with modern facilities and experienced faculty.',
      buttonText: 'Our Programs',
      buttonLink: '/academics',
    },
    {
      id: 3,
      image: 'https://images.unsplash.com/photo-1509062522246-3755977927d7?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80',
      title: 'Admissions Open',
      description: 'Join our school community and give your child the best educational foundation.',
      buttonText: 'Apply Now',
      buttonLink: '/admissions',
    },
  ];

  const settings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 5000,
    fade: true,
    cssEase: 'linear',
  };

  return (
    <Box sx={{ position: 'relative', height: '70vh', overflow: 'hidden' }}>
      <Slider {...settings}>
        {slides.map((slide) => (
          <Box key={slide.id} sx={{ position: 'relative', height: '70vh' }}>
            <Box
              sx={{
                backgroundImage: `url(${slide.image})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundColor: 'rgba(0, 0, 0, 0.4)',
                },
              }}
            >
              <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
                <Box
                  sx={{
                    color: 'white',
                    maxWidth: '600px',
                    textAlign: { xs: 'center', md: 'left' },
                  }}
                >
                  <Typography
                    variant="h2"
                    component="h1"
                    gutterBottom
                    sx={{
                      fontWeight: 'bold',
                      fontSize: { xs: '2rem', md: '3.5rem' },
                      textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
                    }}
                  >
                    {slide.title}
                  </Typography>
                  <Typography
                    variant="h5"
                    component="p"
                    gutterBottom
                    sx={{
                      mb: 4,
                      fontSize: { xs: '1.1rem', md: '1.5rem' },
                      textShadow: '1px 1px 2px rgba(0,0,0,0.5)',
                    }}
                  >
                    {slide.description}
                  </Typography>
                  {slide.buttonText && (
                    <Button
                      variant="contained"
                      size="large"
                      sx={{
                        backgroundColor: '#ff6b35',
                        '&:hover': {
                          backgroundColor: '#e55a2b',
                        },
                        px: 4,
                        py: 1.5,
                        fontSize: '1.1rem',
                      }}
                    >
                      {slide.buttonText}
                    </Button>
                  )}
                </Box>
              </Container>
            </Box>
          </Box>
        ))}
      </Slider>
    </Box>
  );
};

export default ImageSlider;
