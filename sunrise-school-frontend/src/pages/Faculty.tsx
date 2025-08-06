import React, { useState, useEffect } from 'react';
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
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  Link,
} from '@mui/material';
import {
  Psychology,
  Science,
  Language,
  Palette,
  Computer,
  Star,
  Search,
  Email,
  Phone,
} from '@mui/icons-material';
import { teachersAPI } from '../services/api';

// TypeScript interfaces for teacher data
interface Teacher {
  id: number;
  full_name: string;
  first_name: string;
  last_name: string;
  employee_id: string;
  position: string;
  department?: string;
  subjects: string[];
  experience_years: number;
  qualification_name?: string;
  joining_date?: string;
  email?: string;
  phone?: string;
}

interface Department {
  name: string;
  icon: React.ReactElement;
  subjects: string[];
  faculty: number;
  description: string;
}

const Faculty: React.FC = () => {
  // State management
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [departments, setDepartments] = useState<{ [key: string]: Teacher[] }>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredTeachers, setFilteredTeachers] = useState<Teacher[]>([]);

  // Fetch faculty data on component mount
  useEffect(() => {
    const fetchFacultyData = async () => {
      try {
        setLoading(true);
        setError(null);

        console.log('Fetching faculty data from API...');

        // Try API first, fallback to mock data if API fails
        try {
          const response = await teachersAPI.getPublicFaculty();
          console.log('API Response:', response);

          const { teachers: teacherData, departments: departmentData } = response.data;
          console.log('Teachers data:', teacherData);
          console.log('Departments data:', departmentData);

          setTeachers(teacherData);
          setDepartments(departmentData);
          setFilteredTeachers(teacherData);
        } catch (apiError: any) {
          console.warn('API failed, using mock data:', apiError.message);

          // Mock data based on database content (Amit Kumar - EMP001)
          const mockTeachers: Teacher[] = [
            {
              id: 1,
              full_name: "Amit Kumar",
              first_name: "Amit",
              last_name: "Kumar",
              employee_id: "EMP001",
              position: "Principal",
              department: "Math",
              subjects: ["Mathematics", "Statistics", "Algebra"],
              experience_years: 10,
              qualification_name: "M.Sc. Mathematics, B.Ed.",
              joining_date: "2014-01-15",
              email: "amit.kumar@gmail.com",
              phone: "9876543211"
            },
            {
              id: 2,
              full_name: "Subham Kumar",
              first_name: "Subham",
              last_name: "Kumar",
              employee_id: "EMP002",
              position: "Vice Principal",
              department: "Administration",
              subjects: ["Management", "Administration"],
              experience_years: 0,
              qualification_name: "MBA, B.Ed.",
              joining_date: "2024-01-01",
              email: "subham.kumar@gmail.com",
              phone: "9876543212"
            }
          ];

          const mockDepartments = {
            "Math": [mockTeachers[0]],
            "Administration": [mockTeachers[1]]
          };

          setTeachers(mockTeachers);
          setDepartments(mockDepartments);
          setFilteredTeachers(mockTeachers);
        }
      } catch (error: any) {
        console.error('Error fetching faculty data:', error);
        setError(`Failed to load faculty information. Error: ${error.message || 'Unknown error'}`);
      } finally {
        setLoading(false);
      }
    };

    fetchFacultyData();
  }, []);

  // Search functionality
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredTeachers(teachers);
    } else {
      const filtered = teachers.filter(teacher =>
        teacher.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        teacher.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
        teacher.department?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        teacher.subjects.some(subject =>
          subject.toLowerCase().includes(searchTerm.toLowerCase())
        ) ||
        teacher.employee_id.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredTeachers(filtered);
    }
  }, [searchTerm, teachers]);

  // Helper function to get teacher initials for avatar
  const getInitials = (fullName: string): string => {
    return fullName.split(' ').map(name => name[0]).join('').toUpperCase();
  };

  // Static department information (can be made dynamic later)
  const departmentInfo: Department[] = [
    {
      name: 'Science Department',
      icon: <Science />,
      subjects: ['Physics', 'Chemistry', 'Biology', 'Mathematics'],
      faculty: departments['Science']?.length || 0,
      description: 'Dedicated to fostering scientific thinking and research aptitude'
    },
    {
      name: 'Languages Department',
      icon: <Language />,
      subjects: ['English', 'Hindi', 'Sanskrit'],
      faculty: departments['Languages']?.length || 0,
      description: 'Developing communication skills and literary appreciation'
    },
    {
      name: 'Social Sciences',
      icon: <Psychology />,
      subjects: ['History', 'Geography', 'Political Science', 'Economics'],
      faculty: departments['Social Sciences']?.length || 0,
      description: 'Understanding society, culture, and human behavior'
    },
    {
      name: 'Arts & Sports',
      icon: <Palette />,
      subjects: ['Fine Arts', 'Music', 'Dance', 'Physical Education'],
      faculty: departments['Arts']?.length || departments['Sports']?.length || 0,
      description: 'Nurturing creativity and physical fitness'
    },
    {
      name: 'Technology',
      icon: <Computer />,
      subjects: ['Computer Science', 'Information Technology'],
      faculty: departments['Technology']?.length || departments['Computer Science']?.length || 0,
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

  // Loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
          <CircularProgress size={48} />
          <Typography variant="h6" sx={{ mt: 2, color: 'text.secondary' }}>
            Loading Faculty Information...
          </Typography>
        </Box>
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

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

      {/* Search Section */}
      <Box mb={4}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search faculty by name, position, department, or subject..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search color="action" />
              </InputAdornment>
            ),
          }}
          sx={{ maxWidth: 600, mx: 'auto', display: 'block' }}
        />
      </Box>

      {/* Faculty Summary */}
      <Box mb={4} textAlign="center">
        <Paper elevation={2} sx={{ p: 3, bgcolor: 'primary.50' }}>
          <Typography variant="h5" color="primary" fontWeight="bold" gutterBottom>
            Faculty Overview
          </Typography>
          <Typography variant="body1" color="text.secondary">
            We have <strong>{teachers.length}</strong> dedicated faculty members across various departments,
            committed to providing quality education and nurturing student growth.
          </Typography>
          {searchTerm && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Showing {filteredTeachers.length} results for "{searchTerm}"
            </Typography>
          )}
        </Paper>
      </Box>

      {/* Faculty Members */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Our Faculty Team
        </Typography>
        {filteredTeachers.length === 0 ? (
          <Alert severity="info" sx={{ textAlign: 'center' }}>
            {searchTerm ? 'No faculty members found matching your search.' : 'No faculty information available.'}
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {filteredTeachers.map((teacher) => (
              <Grid key={teacher.id} size={{ xs: 12, sm: 6, md: 4 }}>
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
                      {getInitials(teacher.full_name)}
                    </Avatar>
                    <Typography variant="h6" gutterBottom fontWeight="bold">
                      {teacher.full_name}
                    </Typography>
                    <Typography variant="subtitle1" color="primary" gutterBottom>
                      {teacher.position}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {teacher.qualification_name || 'Qualification not specified'}
                    </Typography>
                    <Box mb={2}>
                      <Chip
                        label={`${teacher.experience_years} ${teacher.experience_years === 1 ? 'Year' : 'Years'} Experience`}
                        color="primary"
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                    {teacher.department && (
                      <Typography variant="body2" fontWeight="medium" gutterBottom>
                        Department: {teacher.department}
                      </Typography>
                    )}
                    <Typography variant="body2" fontWeight="medium" gutterBottom>
                      Employee ID: {teacher.employee_id}
                    </Typography>

                    {/* Contact Information */}
                    <Box mb={2}>
                      {teacher.email && (
                        <Box display="flex" alignItems="center" justifyContent="center" mb={1}>
                          <Email sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                          <Link href={`mailto:${teacher.email}`} variant="body2" color="inherit">
                            {teacher.email}
                          </Link>
                        </Box>
                      )}
                      {teacher.phone && (
                        <Box display="flex" alignItems="center" justifyContent="center">
                          <Phone sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                          <Link href={`tel:${teacher.phone}`} variant="body2" color="inherit">
                            {teacher.phone}
                          </Link>
                        </Box>
                      )}
                    </Box>

                    {/* Subjects */}
                    {teacher.subjects.length > 0 && (
                      <Box mt={2}>
                        <Typography variant="body2" fontWeight="medium" gutterBottom>
                          Subjects:
                        </Typography>
                        <Box>
                          {teacher.subjects.map((subject, idx) => (
                            <Chip
                              key={idx}
                              label={subject}
                              size="small"
                              sx={{ mr: 0.5, mb: 0.5 }}
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      {/* Departments */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Academic Departments
        </Typography>
        <Grid container spacing={3}>
          {departmentInfo.map((dept, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card elevation={3} sx={{ height: '100%', p: 3 }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Box color="primary.main" mr={2} sx={{ fontSize: 32 }}>
                      {dept.icon}
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
