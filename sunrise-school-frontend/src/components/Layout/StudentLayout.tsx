import React from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  IconButton,
} from '@mui/material';
import {
  Notifications,
  School,
} from '@mui/icons-material';

interface StudentLayoutProps {
  children: React.ReactNode;
}

const StudentLayout: React.FC<StudentLayoutProps> = ({ children }) => {
  return (
    <Box sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      {/* Header */}
      <Paper elevation={1} sx={{ mb: { xs: 2, md: 3 } }}>
        <Container maxWidth="lg" sx={{ px: { xs: 1, sm: 2, md: 3 } }}>
          {/* Top Header Bar */}
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            sx={{
              p: { xs: 1, sm: 2 },
              flexWrap: 'wrap',
              gap: { xs: 1, sm: 0 }
            }}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <School 
                sx={{ 
                  fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
                  color: 'primary.main'
                }} 
              />
              <Typography
                variant="h4"
                fontWeight="bold"
                color="primary"
                sx={{
                  fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' },
                  lineHeight: 1.2
                }}
              >
                Student Portal
              </Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <IconButton
                color="primary"
                size="small"
                sx={{
                  display: { xs: 'flex', sm: 'flex' },
                  p: { xs: 1, sm: 1.5 }
                }}
              >
                <Notifications fontSize="small" />
              </IconButton>
            </Box>
          </Box>
        </Container>
      </Paper>

      {/* Page Content */}
      <Container
        maxWidth="lg"
        sx={{
          px: { xs: 1, sm: 2, md: 3 },
          pb: { xs: 2, sm: 3, md: 4 }
        }}
      >
        {children}
      </Container>
    </Box>
  );
};

export default StudentLayout;
