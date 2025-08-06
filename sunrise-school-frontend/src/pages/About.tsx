import React from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  School,
  EmojiEvents,
  Groups,
  Psychology,
  CheckCircle,
} from '@mui/icons-material';

const About: React.FC = () => {
  const values = [
    'Excellence in Education',
    'Character Development',
    'Innovation and Creativity',
    'Inclusive Learning Environment',
    'Community Engagement',
    'Global Citizenship',
  ];

  const achievements = [
    { icon: <EmojiEvents />, title: 'Academic Excellence', description: 'Consistently high performance in board examinations' },
    { icon: <Groups />, title: 'Holistic Development', description: 'Focus on overall personality development' },
    { icon: <Psychology />, title: 'Modern Teaching', description: 'Innovative teaching methodologies and technology integration' },
    { icon: <School />, title: 'Experienced Faculty', description: 'Highly qualified and dedicated teaching staff' },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 3, sm: 4, md: 6 }, px: { xs: 2, sm: 3 } }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={{ xs: 4, sm: 5, md: 6 }}>
        <Typography
          variant="h2"
          component="h1"
          gutterBottom
          fontWeight="bold"
          color="primary"
          sx={{
            fontSize: { xs: '1.75rem', sm: '2.5rem', md: '3.75rem' },
            lineHeight: { xs: 1.2, sm: 1.3 },
            mb: { xs: 2, sm: 3 }
          }}
        >
          About Sunrise National Public School
        </Typography>
        <Typography
          variant="h5"
          color="text.secondary"
          sx={{
            maxWidth: 800,
            mx: 'auto',
            fontSize: { xs: '1rem', sm: '1.25rem', md: '1.5rem' },
            lineHeight: { xs: 1.4, sm: 1.5 },
            px: { xs: 1, sm: 2 }
          }}
        >
          Nurturing young minds for a brighter tomorrow through quality education and holistic development
        </Typography>
      </Box>

      {/* Mission & Vision */}
      <Grid container spacing={{ xs: 2, sm: 3, md: 4 }} mb={{ xs: 4, sm: 5, md: 6 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: { xs: 2.5, sm: 3, md: 4 }, height: '100%' }}>
            <Typography
              variant="h4"
              gutterBottom
              color="primary"
              fontWeight="bold"
              sx={{
                fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2.125rem' },
                mb: { xs: 1.5, sm: 2 }
              }}
            >
              Our Mission
            </Typography>
            <Typography
              variant="body1"
              sx={{
                mb: { xs: 1.5, sm: 2 },
                fontSize: { xs: '0.875rem', sm: '1rem' },
                lineHeight: { xs: 1.5, sm: 1.6 }
              }}
            >
              To provide quality education that empowers students to become confident, creative, and responsible global citizens.
              We strive to create an environment where every child can discover their potential and develop the skills needed
              for success in the 21st century.
            </Typography>
            <Typography
              variant="body1"
              sx={{
                fontSize: { xs: '0.875rem', sm: '1rem' },
                lineHeight: { xs: 1.5, sm: 1.6 }
              }}
            >
              Our mission is to foster a love for learning, encourage critical thinking, and instill values that will guide
              our students throughout their lives.
            </Typography>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: { xs: 2.5, sm: 3, md: 4 }, height: '100%' }}>
            <Typography
              variant="h4"
              gutterBottom
              color="primary"
              fontWeight="bold"
              sx={{
                fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2.125rem' },
                mb: { xs: 1.5, sm: 2 }
              }}
            >
              Our Vision
            </Typography>
            <Typography
              variant="body1"
              sx={{
                mb: { xs: 1.5, sm: 2 },
                fontSize: { xs: '0.875rem', sm: '1rem' },
                lineHeight: { xs: 1.5, sm: 1.6 }
              }}
            >
              To be a leading educational institution that shapes future leaders and innovators. We envision a school where
              academic excellence meets character development, creating well-rounded individuals who contribute positively
              to society.
            </Typography>
            <Typography
              variant="body1"
              sx={{
                fontSize: { xs: '0.875rem', sm: '1rem' },
                lineHeight: { xs: 1.5, sm: 1.6 }
              }}
            >
              We aim to be recognized for our commitment to educational excellence, innovation in teaching, and the
              holistic development of our students.
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Our Values */}
      <Box mb={{ xs: 4, sm: 5, md: 6 }}>
        <Typography
          variant="h4"
          gutterBottom
          textAlign="center"
          color="primary"
          fontWeight="bold"
          sx={{
            fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2.125rem' },
            mb: { xs: 2, sm: 3 }
          }}
        >
          Our Core Values
        </Typography>
        <Paper elevation={2} sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
          <List sx={{ py: 0 }}>
            {values.map((value, index) => (
              <ListItem
                key={index}
                sx={{
                  py: { xs: 1, sm: 1.5 },
                  px: { xs: 1, sm: 2 }
                }}
              >
                <ListItemIcon sx={{ minWidth: { xs: 40, sm: 56 } }}>
                  <CheckCircle color="primary" sx={{ fontSize: { xs: 20, sm: 24 } }} />
                </ListItemIcon>
                <ListItemText
                  primary={value}
                  primaryTypographyProps={{
                    variant: 'h6',
                    fontWeight: 'medium',
                    sx: { fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' } }
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Box>

      {/* Key Achievements */}
      <Box mb={{ xs: 4, sm: 5, md: 6 }}>
        <Typography
          variant="h4"
          gutterBottom
          textAlign="center"
          color="primary"
          fontWeight="bold"
          sx={{
            fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2.125rem' },
            mb: { xs: 2, sm: 3 }
          }}
        >
          Why Choose Sunrise?
        </Typography>
        <Grid container spacing={{ xs: 2, sm: 3 }}>
          {achievements.map((achievement, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, md: 3 }}>
              <Card
                elevation={3}
                sx={{
                  height: '100%',
                  textAlign: 'center',
                  p: { xs: 1.5, sm: 2 },
                  transition: 'transform 0.3s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  }
                }}
              >
                <CardContent sx={{ p: { xs: 1.5, sm: 2 } }}>
                  <Box color="primary.main" mb={{ xs: 1.5, sm: 2 }}>
                    {React.cloneElement(achievement.icon, {
                      sx: { fontSize: { xs: 36, sm: 42, md: 48 } }
                    })}
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
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* History Section */}
      <Paper elevation={3} sx={{ p: { xs: 2.5, sm: 3, md: 4 } }}>
        <Typography
          variant="h4"
          gutterBottom
          color="primary"
          fontWeight="bold"
          sx={{
            fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2.125rem' },
            mb: { xs: 2, sm: 3 }
          }}
        >
          Our History
        </Typography>
        <Typography
          variant="body1"
          sx={{
            mb: { xs: 1.5, sm: 2 },
            fontSize: { xs: '0.875rem', sm: '1rem' },
            lineHeight: { xs: 1.5, sm: 1.6 }
          }}
        >
          Established in 2024, Sunrise National Public School represents a new era of educational excellence.
          What started as a vision to provide quality education has quickly grown into one of the most promising
          educational institutions in the region.
        </Typography>
        <Typography
          variant="body1"
          sx={{
            mb: { xs: 1.5, sm: 2 },
            fontSize: { xs: '0.875rem', sm: '1rem' },
            lineHeight: { xs: 1.5, sm: 1.6 }
          }}
        >
          From our inception, we have embraced modern teaching methodologies, state-of-the-art infrastructure, and
          innovative programs designed to meet the evolving needs of 21st-century education. Our commitment to
          excellence has already begun earning recognition from educational boards and organizations.
        </Typography>
        <Typography
          variant="body1"
          sx={{
            fontSize: { xs: '0.875rem', sm: '1rem' },
            lineHeight: { xs: 1.5, sm: 1.6 }
          }}
        >
          As a newly established institution, we are building a strong foundation for future generations of students
          who will go on to achieve success in various fields, from academics and research to business and public
          service. Our growing community of students and families is testament to the quality of education we provide.
        </Typography>
      </Paper>
    </Container>
  );
};

export default About;
