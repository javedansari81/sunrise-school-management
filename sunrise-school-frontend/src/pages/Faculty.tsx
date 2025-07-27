import React from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Avatar,
  Paper,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  School,
  EmojiEvents,
  Psychology,
  Science,
  Calculate,
  Language,
  Palette,
  SportsBasketball,
  Computer,
  Star,
} from '@mui/icons-material';

const Faculty: React.FC = () => {
  const facultyMembers = [
    {
      name: 'Dr. Priya Sharma',
      position: 'Principal',
      qualification: 'Ph.D. in Education, M.Ed.',
      experience: '25 years',
      specialization: 'Educational Leadership',
      subjects: ['Educational Administration'],
      avatar: '/api/placeholder/150/150'
    },
    {
      name: 'Mr. Rajesh Kumar',
      position: 'Vice Principal',
      qualification: 'M.Sc. Mathematics, B.Ed.',
      experience: '20 years',
      specialization: 'Mathematics',
      subjects: ['Mathematics', 'Statistics'],
      avatar: '/api/placeholder/150/150'
    },
    {
      name: 'Mrs. Sunita Verma',
      position: 'Head of Science Department',
      qualification: 'M.Sc. Physics, B.Ed.',
      experience: '18 years',
      specialization: 'Physics',
      subjects: ['Physics', 'General Science'],
      avatar: '/api/placeholder/150/150'
    },
    {
      name: 'Dr. Amit Patel',
      position: 'Senior Teacher',
      qualification: 'Ph.D. Chemistry, M.Ed.',
      experience: '15 years',
      specialization: 'Chemistry',
      subjects: ['Chemistry', 'Environmental Science'],
      avatar: '/api/placeholder/150/150'
    },
    {
      name: 'Ms. Kavita Singh',
      position: 'English Teacher',
      qualification: 'M.A. English Literature, B.Ed.',
      experience: '12 years',
      specialization: 'English Literature',
      subjects: ['English', 'Literature'],
      avatar: '/api/placeholder/150/150'
    },
    {
      name: 'Mr. Deepak Gupta',
      position: 'Computer Science Teacher',
      qualification: 'M.Tech Computer Science, B.Ed.',
      experience: '10 years',
      specialization: 'Programming',
      subjects: ['Computer Science', 'Information Technology'],
      avatar: '/api/placeholder/150/150'
    }
  ];

  const departments = [
    {
      name: 'Science Department',
      icon: <Science />,
      subjects: ['Physics', 'Chemistry', 'Biology', 'Mathematics'],
      faculty: 8,
      description: 'Dedicated to fostering scientific thinking and research aptitude'
    },
    {
      name: 'Languages Department',
      icon: <Language />,
      subjects: ['English', 'Hindi', 'Sanskrit'],
      faculty: 6,
      description: 'Developing communication skills and literary appreciation'
    },
    {
      name: 'Social Sciences',
      icon: <Psychology />,
      subjects: ['History', 'Geography', 'Political Science', 'Economics'],
      faculty: 5,
      description: 'Understanding society, culture, and human behavior'
    },
    {
      name: 'Arts & Sports',
      icon: <Palette />,
      subjects: ['Fine Arts', 'Music', 'Dance', 'Physical Education'],
      faculty: 4,
      description: 'Nurturing creativity and physical fitness'
    },
    {
      name: 'Technology',
      icon: <Computer />,
      subjects: ['Computer Science', 'Information Technology'],
      faculty: 3,
      description: 'Preparing students for the digital age'
    }
  ];

  const qualityFeatures = [
    'Highly qualified and experienced faculty',
    'Regular professional development programs',
    'Student-centered teaching approach',
    'Technology-integrated instruction',
    'Continuous assessment and feedback',
    'Research and innovation focus',
    'Collaborative learning environment',
    'Individual attention to students'
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" color="primary">
          Our Distinguished Faculty
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
          Meet our dedicated team of educators who are committed to nurturing young minds and fostering academic excellence
        </Typography>
      </Box>

      {/* Faculty Members */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Leadership Team
        </Typography>
        <Grid container spacing={3}>
          {facultyMembers.map((member, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card elevation={3} sx={{ height: '100%', textAlign: 'center' }}>
                <CardContent sx={{ p: 3 }}>
                  <Avatar
                    sx={{ 
                      width: 100, 
                      height: 100, 
                      mx: 'auto', 
                      mb: 2,
                      bgcolor: 'primary.main',
                      fontSize: '2rem'
                    }}
                  >
                    {member.name.split(' ').map(n => n[0]).join('')}
                  </Avatar>
                  <Typography variant="h6" gutterBottom fontWeight="bold">
                    {member.name}
                  </Typography>
                  <Typography variant="subtitle1" color="primary" gutterBottom>
                    {member.position}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {member.qualification}
                  </Typography>
                  <Box mb={2}>
                    <Chip 
                      label={`${member.experience} Experience`} 
                      color="primary" 
                      variant="outlined" 
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" fontWeight="medium">
                    Specialization: {member.specialization}
                  </Typography>
                  <Box mt={1}>
                    {member.subjects.map((subject, idx) => (
                      <Chip 
                        key={idx} 
                        label={subject} 
                        size="small" 
                        sx={{ mr: 0.5, mb: 0.5 }}
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Departments */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Academic Departments
        </Typography>
        <Grid container spacing={3}>
          {departments.map((dept, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card elevation={3} sx={{ height: '100%', p: 3 }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Box color="primary.main" mr={2}>
                      {React.cloneElement(dept.icon, { sx: { fontSize: 32 } })}
                    </Box>
                    <Typography variant="h6" fontWeight="bold">
                      {dept.name}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {dept.description}
                  </Typography>
                  <Typography variant="body2" fontWeight="medium" gutterBottom>
                    Faculty Members: {dept.faculty}
                  </Typography>
                  <Typography variant="body2" fontWeight="medium" gutterBottom>
                    Subjects:
                  </Typography>
                  <Box>
                    {dept.subjects.map((subject, idx) => (
                      <Chip 
                        key={idx} 
                        label={subject} 
                        size="small" 
                        sx={{ mr: 0.5, mb: 0.5 }}
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Quality Features */}
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom color="primary" fontWeight="bold" textAlign="center">
          What Makes Our Faculty Special
        </Typography>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <List>
              {qualityFeatures.slice(0, 4).map((feature, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Star color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={feature} />
                </ListItem>
              ))}
            </List>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <List>
              {qualityFeatures.slice(4).map((feature, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Star color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={feature} />
                </ListItem>
              ))}
            </List>
          </Grid>
        </Grid>
        <Box textAlign="center" mt={4}>
          <Typography variant="body1" color="text.secondary">
            Our faculty members are not just teachers, but mentors, guides, and inspirers who are dedicated to 
            helping each student reach their full potential. With their expertise, passion, and commitment, 
            they create an environment where learning is both enjoyable and meaningful.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Faculty;
