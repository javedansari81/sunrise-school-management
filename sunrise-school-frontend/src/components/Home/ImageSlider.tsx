import React from 'react';
import { useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();

  const handleButtonClick = (buttonLink: string) => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => {
      navigate(buttonLink);
    }, 500);
  };

  const slides: SlideData[] = [
    {
      id: 1,
      image: '/images/home-slider/image1_christmas_day.jpeg',
      title: 'Happy to see you!',
      description: 'Nurturing young minds for a brighter tomorrow with excellence in education.',
      buttonText: 'Learn More',
      buttonLink: '/about',
    },
    {
      id: 2,
      image: '/images/home-slider/image2_christmas_day.jpeg',
      title: 'Celebrating Special Moments',
      description: 'Creating memorable experiences and fostering a joyful learning environment.',
      buttonText: 'Our Programs',
      buttonLink: '/academics',
    },
    {
      id: 3,
      image: '/images/home-slider/image3_birthday.jpeg',
      title: 'Building Strong Foundations',
      description: 'Every child is special and deserves the best start in their educational journey.',
      buttonText: 'Learn More',
      buttonLink: '/about',
    },
    {
      id: 4,
      image: '/images/home-slider/image4_indepdence_day.jpeg',
      title: 'Celebrating Our Nation',
      description: 'Instilling values of patriotism and national pride in our students.',
      buttonText: 'Our Values',
      buttonLink: '/about',
    },
    {
      id: 5,
      image: '/images/home-slider/image5_first_day.jpeg',
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
    <Box sx={{
      position: 'relative',
      height: { xs: '50vh', sm: '60vh', md: '70vh' },
      overflow: 'hidden',
      minHeight: { xs: '400px', sm: '500px', md: '600px' }
    }}>
      <Slider {...settings}>
        {slides.map((slide) => (
          <Box key={slide.id} sx={{
            position: 'relative',
            height: { xs: '50vh', sm: '60vh', md: '70vh' },
            minHeight: { xs: '400px', sm: '500px', md: '600px' }
          }}>
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
              <Container maxWidth="lg" sx={{
                position: 'relative',
                zIndex: 1,
                px: { xs: 2, sm: 3, md: 4 }
              }}>
                <Box
                  sx={{
                    color: 'white',
                    maxWidth: { xs: '100%', sm: '80%', md: '600px' },
                    textAlign: { xs: 'center', md: 'left' },
                    mx: { xs: 'auto', md: 0 }
                  }}
                >
                  <Typography
                    variant="h2"
                    component="h1"
                    gutterBottom
                    sx={{
                      fontWeight: 'bold',
                      fontSize: { xs: '1.5rem', sm: '2.5rem', md: '3.5rem' },
                      textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
                      lineHeight: { xs: 1.2, sm: 1.3 },
                      mb: { xs: 2, sm: 3 }
                    }}
                  >
                    {slide.title}
                  </Typography>
                  <Typography
                    variant="h5"
                    component="p"
                    gutterBottom
                    sx={{
                      mb: { xs: 3, sm: 4 },
                      fontSize: { xs: '0.875rem', sm: '1.1rem', md: '1.5rem' },
                      textShadow: '1px 1px 2px rgba(0,0,0,0.5)',
                      lineHeight: { xs: 1.4, sm: 1.5 },
                      px: { xs: 1, sm: 0 }
                    }}
                  >
                    {slide.description}
                  </Typography>
                  {slide.buttonText && slide.buttonLink && (
                    <Button
                      variant="contained"
                      size="large"
                      onClick={() => handleButtonClick(slide.buttonLink!)}
                      sx={{
                        backgroundColor: '#ff6b35',
                        '&:hover': {
                          backgroundColor: '#e55a2b',
                        },
                        px: { xs: 3, sm: 4 },
                        py: { xs: 1.25, sm: 1.5 },
                        fontSize: { xs: '0.875rem', sm: '1rem', md: '1.1rem' },
                        minWidth: { xs: '150px', sm: 'auto' }
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
