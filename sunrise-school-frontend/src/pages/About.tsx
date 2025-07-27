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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" color="primary">
          About Sunrise National Public School
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
          Nurturing young minds for a brighter tomorrow through quality education and holistic development
        </Typography>
      </Box>

      {/* Mission & Vision */}
      <Grid container spacing={4} mb={6}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
              Our Mission
            </Typography>
            <Typography variant="body1" paragraph>
              To provide quality education that empowers students to become confident, creative, and responsible global citizens.
              We strive to create an environment where every child can discover their potential and develop the skills needed
              for success in the 21st century.
            </Typography>
            <Typography variant="body1">
              Our mission is to foster a love for learning, encourage critical thinking, and instill values that will guide
              our students throughout their lives.
            </Typography>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
              Our Vision
            </Typography>
            <Typography variant="body1" paragraph>
              To be a leading educational institution that shapes future leaders and innovators. We envision a school where 
              academic excellence meets character development, creating well-rounded individuals who contribute positively 
              to society.
            </Typography>
            <Typography variant="body1">
              We aim to be recognized for our commitment to educational excellence, innovation in teaching, and the 
              holistic development of our students.
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Our Values */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Our Core Values
        </Typography>
        <Paper elevation={2} sx={{ p: 3 }}>
          <List>
            {values.map((value, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <CheckCircle color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary={value}
                  primaryTypographyProps={{ variant: 'h6', fontWeight: 'medium' }}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Box>

      {/* Key Achievements */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Why Choose Sunrise?
        </Typography>
        <Grid container spacing={3}>
          {achievements.map((achievement, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, md: 3 }}>
              <Card elevation={3} sx={{ height: '100%', textAlign: 'center', p: 2 }}>
                <CardContent>
                  <Box color="primary.main" mb={2}>
                    {React.cloneElement(achievement.icon, { sx: { fontSize: 48 } })}
                  </Box>
                  <Typography variant="h6" gutterBottom fontWeight="bold">
                    {achievement.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {achievement.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* History Section */}
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
          Our History
        </Typography>
        <Typography variant="body1" paragraph>
          Established in 1995, Sunrise National Public School has been a beacon of educational excellence for over 
          two decades. What started as a small institution with a vision to provide quality education has grown into 
          one of the most respected schools in the region.
        </Typography>
        <Typography variant="body1" paragraph>
          Over the years, we have continuously evolved our teaching methodologies, infrastructure, and programs to 
          meet the changing needs of education. Our commitment to excellence has earned us recognition from various 
          educational boards and organizations.
        </Typography>
        <Typography variant="body1">
          Today, we are proud to have educated thousands of students who have gone on to achieve success in various 
          fields, from academics and research to business and public service. Our alumni are our greatest testament 
          to the quality of education we provide.
        </Typography>
      </Paper>
    </Container>
  );
};

export default About;
