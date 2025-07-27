import React from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Paper,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ExpandMore,
  Science,
  Calculate,
  Language,
  Palette,
  SportsBasketball,
  Computer,
  MenuBook,
  Star,
} from '@mui/icons-material';

const Academics: React.FC = () => {
  const programs = [
    {
      title: 'Primary Education (Classes I-V)',
      description: 'Foundation years focusing on basic literacy, numeracy, and social skills',
      subjects: ['English', 'Mathematics', 'Science', 'Social Studies', 'Hindi', 'Art & Craft', 'Physical Education'],
      highlights: ['Play-based learning', 'Individual attention', 'Creative activities', 'Character building']
    },
    {
      title: 'Middle School (Classes VI-VIII)',
      description: 'Developing critical thinking and subject-specific knowledge',
      subjects: ['English', 'Mathematics', 'Science', 'Social Science', 'Hindi', 'Computer Science', 'Art Education'],
      highlights: ['Project-based learning', 'Laboratory experiments', 'Group activities', 'Leadership development']
    },
    {
      title: 'Secondary Education (Classes IX-X)',
      description: 'Comprehensive preparation for board examinations',
      subjects: ['English', 'Mathematics', 'Science', 'Social Science', 'Hindi', 'Computer Applications'],
      highlights: ['Board exam preparation', 'Career guidance', 'Skill development', 'Competitive exam coaching']
    },
    {
      title: 'Senior Secondary (Classes XI-XII)',
      description: 'Specialized streams for higher education preparation',
      subjects: ['Science Stream', 'Commerce Stream', 'Arts Stream'],
      highlights: ['Stream specialization', 'College preparation', 'Entrance exam coaching', 'Research projects']
    }
  ];

  const facilities = [
    { icon: <Science />, title: 'Science Laboratories', description: 'Well-equipped Physics, Chemistry, and Biology labs' },
    { icon: <Computer />, title: 'Computer Lab', description: 'Modern computers with latest software and internet connectivity' },
    { icon: <MenuBook />, title: 'Library', description: 'Extensive collection of books, journals, and digital resources' },
    { icon: <SportsBasketball />, title: 'Sports Complex', description: 'Indoor and outdoor sports facilities for various games' },
    { icon: <Palette />, title: 'Art Studio', description: 'Creative space for art, craft, and design activities' },
    { icon: <Language />, title: 'Language Lab', description: 'Interactive language learning with audio-visual aids' },
  ];

  const achievements = [
    'CBSE Board Toppers for consecutive years',
    '100% Pass Rate in Class X and XII',
    'Excellence in Science Olympiad',
    'Outstanding Performance in Mathematics Competition',
    'Recognition in National Level Debates',
    'Awards in Inter-School Sports Championships'
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" color="primary">
          Academic Excellence
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
          Comprehensive education programs designed to nurture intellectual growth and academic achievement
        </Typography>
      </Box>

      {/* Academic Programs */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Our Academic Programs
        </Typography>
        {programs.map((program, index) => (
          <Accordion key={index} sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6" fontWeight="bold">
                {program.title}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 8 }}>
                  <Typography variant="body1" paragraph>
                    {program.description}
                  </Typography>
                  <Typography variant="h6" gutterBottom>
                    Subjects Offered:
                  </Typography>
                  <Box mb={2}>
                    {program.subjects.map((subject, idx) => (
                      <Chip key={idx} label={subject} sx={{ mr: 1, mb: 1 }} color="primary" variant="outlined" />
                    ))}
                  </Box>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    Key Highlights:
                  </Typography>
                  <List dense>
                    {program.highlights.map((highlight, idx) => (
                      <ListItem key={idx}>
                        <ListItemIcon>
                          <Star color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={highlight} />
                      </ListItem>
                    ))}
                  </List>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>

      {/* Academic Facilities */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Academic Facilities
        </Typography>
        <Grid container spacing={3}>
          {facilities.map((facility, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card elevation={3} sx={{ height: '100%', textAlign: 'center', p: 2 }}>
                <CardContent>
                  <Box color="primary.main" mb={2}>
                    {React.cloneElement(facility.icon, { sx: { fontSize: 48 } })}
                  </Box>
                  <Typography variant="h6" gutterBottom fontWeight="bold">
                    {facility.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {facility.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Academic Achievements */}
      <Grid container spacing={4}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
              Academic Achievements
            </Typography>
            <List>
              {achievements.map((achievement, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Star color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={achievement} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
              Teaching Methodology
            </Typography>
            <Typography variant="body1" paragraph>
              Our teaching approach combines traditional wisdom with modern pedagogical techniques. We believe in:
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <Star color="primary" />
                </ListItemIcon>
                <ListItemText primary="Interactive and engaging classroom sessions" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Star color="primary" />
                </ListItemIcon>
                <ListItemText primary="Technology-integrated learning" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Star color="primary" />
                </ListItemIcon>
                <ListItemText primary="Practical and experiential learning" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Star color="primary" />
                </ListItemIcon>
                <ListItemText primary="Regular assessment and feedback" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Star color="primary" />
                </ListItemIcon>
                <ListItemText primary="Individual attention to each student" />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Academics;
