import React from 'react';
import {
  Box,
  Container,
  Typography,
  IconButton,
} from '@mui/material';
import {
  Facebook,
  Twitter,
  Instagram,
  LinkedIn,
  Phone,
  Email,
  LocationOn,
} from '@mui/icons-material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: '#2c3e50',
        color: 'white',
        py: 6,
        mt: 'auto',
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4, justifyContent: 'center' }}>
          <Box sx={{ flex: '1 1 400px', minWidth: 300, maxWidth: 500 }}>
            <Typography variant="h6" gutterBottom>
              Sunrise National Public School
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              Nurturing young minds for a brighter tomorrow. Excellence in education
              since our establishment.
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton color="inherit" size="small">
                <Facebook />
              </IconButton>
              <IconButton color="inherit" size="small">
                <Twitter />
              </IconButton>
              <IconButton color="inherit" size="small">
                <Instagram />
              </IconButton>
              <IconButton color="inherit" size="small">
                <LinkedIn />
              </IconButton>
            </Box>
          </Box>

          <Box sx={{ flex: '1 1 400px', minWidth: 300, maxWidth: 500 }}>
            <Typography variant="h6" gutterBottom>
              Contact Info
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                <LocationOn fontSize="small" sx={{ mt: 0.5 }} />
                <Typography variant="body2">
                  Sena road, Farsauliyana, Rath, Hamirpur, 210431
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Phone fontSize="small" />
                <Typography variant="body2">6392171614</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Email fontSize="small" />
                <Typography variant="body2">sunrise.nps008@gmail.com</Typography>
              </Box>
            </Box>
          </Box>
        </Box>
        
        <Box
          sx={{
            borderTop: '1px solid rgba(255,255,255,0.1)',
            mt: 4,
            pt: 2,
            textAlign: 'center',
          }}
        >
          <Typography variant="body2">
            © 2024 Sunrise National Public School. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
