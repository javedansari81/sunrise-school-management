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
      title: 'Early Childhood Education (PG, LKG, UKG)',
      description: 'Nurturing foundation years focusing on holistic development through play and exploration',
      subjects: ['Pre-Reading Skills', 'Pre-Math Concepts', 'Creative Arts', 'Music & Movement', 'Nature Study', 'Social Skills'],
      highlights: ['Play-based learning', 'Sensory development', 'Language immersion', 'Creative expression', 'Social interaction']
    },
    {
      title: 'Primary Education (Classes I-V)',
      description: 'Foundation years focusing on basic literacy, numeracy, and social skills',
      subjects: ['English', 'Mathematics', 'Science', 'Social Studies', 'Hindi', 'Art & Craft', 'Physical Education'],
      highlights: ['Interactive learning', 'Individual attention', 'Creative activities', 'Character building']
    },
    {
      title: 'Middle School (Classes VI-VIII)',
      description: 'Developing critical thinking and subject-specific knowledge for comprehensive growth',
      subjects: ['English', 'Mathematics', 'Science', 'Social Science', 'Hindi', 'Computer Science', 'Art Education'],
      highlights: ['Project-based learning', 'Laboratory experiments', 'Group activities', 'Leadership development']
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
    'Excellence in Academic Performance across all grades',
    'Outstanding Results in State-level Assessments',
    'Excellence in Science Olympiad',
    'Outstanding Performance in Mathematics Competition',
    'Recognition in National Level Debates',
    'Awards in Inter-School Sports Championships',
    'Excellence in Creative Arts and Cultural Activities'
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
          Academic Excellence
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
          Comprehensive education programs from Pre-Kindergarten through Grade 8, designed to nurture intellectual growth and foundational learning
        </Typography>
      </Box>

      {/* Academic Programs */}
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
          Our Academic Programs
        </Typography>
        {programs.map((program, index) => (
          <Accordion
            key={index}
            sx={{
              mb: { xs: 1.5, sm: 2 },
              '&:before': { display: 'none' },
              boxShadow: 2
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMore />}
              sx={{
                px: { xs: 2, sm: 3 },
                py: { xs: 1, sm: 1.5 }
              }}
            >
              <Typography
                variant="h6"
                fontWeight="bold"
                sx={{
                  fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
                }}
              >
                {program.title}
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ px: { xs: 2, sm: 3 }, py: { xs: 2, sm: 3 } }}>
              <Grid container spacing={{ xs: 2, sm: 3 }}>
                <Grid size={{ xs: 12, md: 8 }}>
                  <Typography
                    variant="body1"
                    sx={{
                      mb: { xs: 1.5, sm: 2 },
                      fontSize: { xs: '0.875rem', sm: '1rem' },
                      lineHeight: { xs: 1.5, sm: 1.6 }
                    }}
                  >
                    {program.description}
                  </Typography>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
                      mb: { xs: 1, sm: 1.5 }
                    }}
                  >
                    Subjects Offered:
                  </Typography>
                  <Box mb={{ xs: 1.5, sm: 2 }}>
                    {program.subjects.map((subject, idx) => (
                      <Chip
                        key={idx}
                        label={subject}
                        sx={{
                          mr: { xs: 0.5, sm: 1 },
                          mb: { xs: 0.5, sm: 1 },
                          fontSize: { xs: '0.75rem', sm: '0.875rem' }
                        }}
                        color="primary"
                        variant="outlined"
                        size={window.innerWidth < 600 ? "small" : "medium"}
                      />
                    ))}
                  </Box>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
                      mb: { xs: 1, sm: 1.5 }
                    }}
                  >
                    Key Highlights:
                  </Typography>
                  <List dense sx={{ py: 0 }}>
                    {program.highlights.map((highlight, idx) => (
                      <ListItem
                        key={idx}
                        sx={{
                          py: { xs: 0.25, sm: 0.5 },
                          px: 0
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: { xs: 32, sm: 40 } }}>
                          <Star color="primary" sx={{ fontSize: { xs: 16, sm: 20 } }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={highlight}
                          primaryTypographyProps={{
                            sx: { fontSize: { xs: '0.75rem', sm: '0.875rem' } }
                          }}
                        />
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
          Academic Facilities
        </Typography>
        <Grid container spacing={{ xs: 2, sm: 3 }}>
          {facilities.map((facility, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, md: 4 }}>
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
                    {React.cloneElement(facility.icon, {
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
                    {facility.title}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      fontSize: { xs: '0.75rem', sm: '0.875rem' },
                      lineHeight: { xs: 1.4, sm: 1.5 }
                    }}
                  >
                    {facility.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Academic Achievements */}
      <Grid container spacing={{ xs: 2, sm: 3, md: 4 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: { xs: 2.5, sm: 3, md: 4 }, height: '100%' }}>
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
              Academic Achievements
            </Typography>
            <List sx={{ py: 0 }}>
              {achievements.map((achievement, index) => (
                <ListItem
                  key={index}
                  sx={{
                    py: { xs: 0.5, sm: 1 },
                    px: 0
                  }}
                >
                  <ListItemIcon sx={{ minWidth: { xs: 32, sm: 40 } }}>
                    <Star color="primary" sx={{ fontSize: { xs: 18, sm: 24 } }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={achievement}
                    primaryTypographyProps={{
                      sx: { fontSize: { xs: '0.875rem', sm: '1rem' } }
                    }}
                  />
                </ListItem>
              ))}
            </List>
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
                mb: { xs: 2, sm: 3 }
              }}
            >
              Teaching Methodology
            </Typography>
            <Typography
              variant="body1"
              sx={{
                mb: { xs: 1.5, sm: 2 },
                fontSize: { xs: '0.875rem', sm: '1rem' },
                lineHeight: { xs: 1.5, sm: 1.6 }
              }}
            >
              Our teaching approach combines traditional wisdom with modern pedagogical techniques. We believe in:
            </Typography>
            <List sx={{ py: 0 }}>
              <ListItem sx={{ py: { xs: 0.5, sm: 1 }, px: 0 }}>
                <ListItemIcon sx={{ minWidth: { xs: 32, sm: 40 } }}>
                  <Star color="primary" sx={{ fontSize: { xs: 18, sm: 24 } }} />
                </ListItemIcon>
                <ListItemText
                  primary="Interactive and engaging classroom sessions"
                  primaryTypographyProps={{
                    sx: { fontSize: { xs: '0.875rem', sm: '1rem' } }
                  }}
                />
              </ListItem>
              <ListItem sx={{ py: { xs: 0.5, sm: 1 }, px: 0 }}>
                <ListItemIcon sx={{ minWidth: { xs: 32, sm: 40 } }}>
                  <Star color="primary" sx={{ fontSize: { xs: 18, sm: 24 } }} />
                </ListItemIcon>
                <ListItemText
                  primary="Technology-integrated learning"
                  primaryTypographyProps={{
                    sx: { fontSize: { xs: '0.875rem', sm: '1rem' } }
                  }}
                />
              </ListItem>
              <ListItem sx={{ py: { xs: 0.5, sm: 1 }, px: 0 }}>
                <ListItemIcon sx={{ minWidth: { xs: 32, sm: 40 } }}>
                  <Star color="primary" sx={{ fontSize: { xs: 18, sm: 24 } }} />
                </ListItemIcon>
                <ListItemText
                  primary="Practical and experiential learning"
                  primaryTypographyProps={{
                    sx: { fontSize: { xs: '0.875rem', sm: '1rem' } }
                  }}
                />
              </ListItem>
              <ListItem sx={{ py: { xs: 0.5, sm: 1 }, px: 0 }}>
                <ListItemIcon sx={{ minWidth: { xs: 32, sm: 40 } }}>
                  <Star color="primary" sx={{ fontSize: { xs: 18, sm: 24 } }} />
                </ListItemIcon>
                <ListItemText
                  primary="Regular assessment and feedback"
                  primaryTypographyProps={{
                    sx: { fontSize: { xs: '0.875rem', sm: '1rem' } }
                  }}
                />
              </ListItem>
              <ListItem sx={{ py: { xs: 0.5, sm: 1 }, px: 0 }}>
                <ListItemIcon sx={{ minWidth: { xs: 32, sm: 40 } }}>
                  <Star color="primary" sx={{ fontSize: { xs: 18, sm: 24 } }} />
                </ListItemIcon>
                <ListItemText
                  primary="Individual attention to each student"
                  primaryTypographyProps={{
                    sx: { fontSize: { xs: '0.875rem', sm: '1rem' } }
                  }}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Academics;
