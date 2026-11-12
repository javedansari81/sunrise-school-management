import React from 'react';
import { Box, Container, Typography } from '@mui/material';
import { Email, LocationOn, Phone } from '@mui/icons-material';
import { useSchool } from '../../contexts/SchoolContext';
import SchoolLogo from '../common/SchoolLogo';
import { brand } from '../../theme';

/** Footer of the public site, with the school's own name and contact details. */
const Footer: React.FC = () => {
  const { school } = useSchool();
  const contact = [
    { icon: <LocationOn fontSize="small" />, text: school.address },
    { icon: <Phone fontSize="small" />, text: school.phone, href: school.phone ? `tel:${school.phone}` : undefined },
    { icon: <Email fontSize="small" />, text: school.email, href: school.email ? `mailto:${school.email}` : undefined },
  ].filter((item) => item.text);

  return (
    <Box
      component="footer"
      sx={{
        position: 'relative',
        overflow: 'hidden',
        mt: 'auto',
        py: 6,
        color: '#fff',
        background: `linear-gradient(135deg, ${brand.navTop} 0%, ${brand.navMid} 55%, ${brand.navBottom} 100%)`,
        '&::before': {
          content: '""',
          position: 'absolute',
          width: 380,
          height: 380,
          top: -200,
          right: -80,
          borderRadius: '50%',
          filter: 'blur(80px)',
          background: 'rgba(59,130,246,0.35)',
        },
      }}
    >
      <Container maxWidth="lg" sx={{ position: 'relative' }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4, justifyContent: 'space-between' }}>
          <Box sx={{ flex: '1 1 320px', maxWidth: 520 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
              <SchoolLogo size={48} ring />
              <Typography variant="h6" sx={{ fontWeight: 800 }}>
                {school.name}
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Nurturing young minds for a brighter tomorrow.
            </Typography>
          </Box>

          {contact.length > 0 && (
            <Box sx={{ flex: '1 1 280px', maxWidth: 420 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>
                Contact
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.25 }}>
                {contact.map((item) => (
                  <Box key={item.text} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, opacity: 0.9 }}>
                    <Box sx={{ mt: 0.25, color: '#93c5fd' }}>{item.icon}</Box>
                    <Typography
                      variant="body2"
                      component={item.href ? 'a' : 'span'}
                      href={item.href}
                      sx={{ color: 'inherit', textDecoration: 'none', '&:hover': item.href ? { textDecoration: 'underline' } : undefined }}
                    >
                      {item.text}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          )}
        </Box>

        <Box sx={{ borderTop: '1px solid rgba(255,255,255,0.14)', mt: 4, pt: 2, textAlign: 'center' }}>
          <Typography variant="body2" sx={{ opacity: 0.75 }}>
            © {new Date().getFullYear()} {school.name}. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
