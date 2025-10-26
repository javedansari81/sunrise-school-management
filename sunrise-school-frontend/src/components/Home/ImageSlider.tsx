import React, { useState, useEffect } from 'react';
import Slider from 'react-slick';
import { Box, CircularProgress, Typography } from '@mui/material';
import { ArrowBackIos, ArrowForwardIos } from '@mui/icons-material';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import './ImageSlider.css';
import { galleryAPI, PublicGalleryImage } from '../../services/galleryService';

interface GalleryImageWithCategory extends PublicGalleryImage {
  category?: {
    id: number;
    name: string;
  };
}

// Custom Arrow Components
interface ArrowProps {
  onClick?: () => void;
}

const PrevArrow: React.FC<ArrowProps> = ({ onClick }) => {
  return (
    <Box
      onClick={onClick}
      className="slick-arrow-custom slick-prev-custom"
      sx={{
        position: 'absolute',
        left: 0,
        top: 0,
        bottom: 0,
        width: { xs: '60px', sm: '80px', md: '100px' },
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-start',
        paddingLeft: { xs: '12px', sm: '16px', md: '24px' },
        zIndex: 2,
        cursor: 'pointer',
        background: 'linear-gradient(to right, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0) 100%)',
        opacity: 0,
        transition: 'opacity 0.3s ease',
        '&:hover': {
          opacity: 1,
        },
      }}
    >
      <ArrowBackIos
        sx={{
          fontSize: { xs: 28, sm: 36, md: 44 },
          color: '#fff',
          filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5))',
          transition: 'transform 0.2s ease',
          '&:hover': {
            transform: 'scale(1.2)',
          },
        }}
      />
    </Box>
  );
};

const NextArrow: React.FC<ArrowProps> = ({ onClick }) => {
  return (
    <Box
      onClick={onClick}
      className="slick-arrow-custom slick-next-custom"
      sx={{
        position: 'absolute',
        right: 0,
        top: 0,
        bottom: 0,
        width: { xs: '60px', sm: '80px', md: '100px' },
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        paddingRight: { xs: '12px', sm: '16px', md: '24px' },
        zIndex: 2,
        cursor: 'pointer',
        background: 'linear-gradient(to left, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0) 100%)',
        opacity: 0,
        transition: 'opacity 0.3s ease',
        '&:hover': {
          opacity: 1,
        },
      }}
    >
      <ArrowForwardIos
        sx={{
          fontSize: { xs: 28, sm: 36, md: 44 },
          color: '#fff',
          filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5))',
          transition: 'transform 0.2s ease',
          '&:hover': {
            transform: 'scale(1.2)',
          },
        }}
      />
    </Box>
  );
};

const ImageSlider: React.FC = () => {
  const [images, setImages] = useState<GalleryImageWithCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHomePageImages = async () => {
      try {
        setLoading(true);
        const response = await galleryAPI.getHomePageImages(10);
        setImages(response.data);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching home page images:', err);
        setError('Failed to load images');
        setImages([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHomePageImages();
  }, []);

  // Show loading state
  if (loading) {
    return (
      <Box
        sx={{
          position: 'relative',
          height: { xs: '50vh', sm: '60vh', md: '70vh' },
          minHeight: { xs: '400px', sm: '500px', md: '600px' },
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f5f5f5',
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  // Show welcome image if no images found
  if (!images || images.length === 0) {
    return (
      <Box
        sx={{
          position: 'relative',
          height: { xs: '50vh', sm: '60vh', md: '70vh' },
          minHeight: { xs: '400px', sm: '500px', md: '600px' },
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#1976d2',
          backgroundImage: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
        }}
      >
        <Box
          sx={{
            textAlign: 'center',
            color: 'white',
            px: 3,
          }}
        >
          <Typography
            variant="h2"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 'bold',
              fontSize: { xs: '1.75rem', sm: '2.5rem', md: '3.5rem' },
              textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
              lineHeight: 1.3,
            }}
          >
            Welcome to Sunrise National Public School
          </Typography>
          <Typography
            variant="h5"
            sx={{
              fontSize: { xs: '1rem', sm: '1.25rem', md: '1.5rem' },
              textShadow: '1px 1px 2px rgba(0,0,0,0.3)',
              mt: 2,
            }}
          >
            Nurturing young minds for a brighter tomorrow
          </Typography>
        </Box>
      </Box>
    );
  }

  const settings = {
    dots: true,
    infinite: images.length > 1,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: images.length > 1,
    autoplaySpeed: 5000,
    fade: true,
    cssEase: 'linear',
    arrows: images.length > 1,
    prevArrow: <PrevArrow />,
    nextArrow: <NextArrow />,
  };

  return (
    <Box
      className="slider-container"
      sx={{
        position: 'relative',
        height: { xs: '50vh', sm: '60vh', md: '70vh' },
        overflow: 'hidden',
        minHeight: { xs: '400px', sm: '500px', md: '600px' },
        '&:hover .slick-arrow-custom': {
          opacity: 1,
        },
      }}
    >
      <Slider {...settings}>
        {images.map((image) => (
          <Box
            key={image.id}
            sx={{
              position: 'relative',
              height: { xs: '50vh', sm: '60vh', md: '70vh' },
              minHeight: { xs: '400px', sm: '500px', md: '600px' },
            }}
          >
            <Box
              sx={{
                backgroundImage: `url(${image.cloudinary_url})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                height: '100%',
                width: '100%',
              }}
            />
          </Box>
        ))}
      </Slider>
    </Box>
  );
};

export default ImageSlider;
