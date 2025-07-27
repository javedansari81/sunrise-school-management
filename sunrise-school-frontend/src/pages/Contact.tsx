import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Phone,
  Email,
  LocationOn,
  Schedule,
  Send,
  Person,
  Subject,
  Message,
} from '@mui/icons-material';

const Contact: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });
  const [showSuccess, setShowSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would typically send the form data to your backend
    console.log('Form submitted:', formData);
    setShowSuccess(true);
    setFormData({
      name: '',
      email: '',
      phone: '',
      subject: '',
      message: ''
    });
  };

  const contactInfo = [
    {
      icon: <Phone />,
      title: 'Phone Numbers',
      details: [
        'Main Office: +91 98765 43210',
        'Admissions: +91 87654 32109',
        'Principal: +91 76543 21098'
      ]
    },
    {
      icon: <Email />,
      title: 'Email Addresses',
      details: [
        'General: info@sunriseschool.edu',
        'Admissions: admissions@sunriseschool.edu',
        'Principal: principal@sunriseschool.edu'
      ]
    },
    {
      icon: <LocationOn />,
      title: 'Address',
      details: [
        'Sunrise National Public School',
        '123 Education Street, Knowledge City',
        'Academic District, State - 123456'
      ]
    },
    {
      icon: <Schedule />,
      title: 'Office Hours',
      details: [
        'Monday - Friday: 8:00 AM - 5:00 PM',
        'Saturday: 9:00 AM - 2:00 PM',
        'Sunday: Closed'
      ]
    }
  ];

  const departments = [
    { name: 'Principal Office', extension: 'Ext. 101', email: 'principal@sunriseschool.edu' },
    { name: 'Admissions Office', extension: 'Ext. 102', email: 'admissions@sunriseschool.edu' },
    { name: 'Academic Office', extension: 'Ext. 103', email: 'academics@sunriseschool.edu' },
    { name: 'Finance Office', extension: 'Ext. 104', email: 'finance@sunriseschool.edu' },
    { name: 'Transport Office', extension: 'Ext. 105', email: 'transport@sunriseschool.edu' },
    { name: 'Sports Department', extension: 'Ext. 106', email: 'sports@sunriseschool.edu' }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" color="primary">
          Contact Us
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
          Get in touch with us for admissions, inquiries, or any assistance you need
        </Typography>
      </Box>

      {/* Contact Information Cards */}
      <Grid container spacing={3} mb={6}>
        {contactInfo.map((info, index) => (
          <Grid key={index} size={{ xs: 12, sm: 6, md: 3 }}>
            <Card elevation={3} sx={{ height: '100%', textAlign: 'center' }}>
              <CardContent sx={{ p: 3 }}>
                <Box color="primary.main" mb={2}>
                  {React.cloneElement(info.icon, { sx: { fontSize: 48 } })}
                </Box>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  {info.title}
                </Typography>
                {info.details.map((detail, idx) => (
                  <Typography key={idx} variant="body2" color="text.secondary" paragraph>
                    {detail}
                  </Typography>
                ))}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Contact Form and Map */}
      <Grid container spacing={4} mb={6}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
              Send us a Message
            </Typography>
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Full Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                margin="normal"
                InputProps={{
                  startAdornment: <Person sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
              <TextField
                fullWidth
                label="Email Address"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                margin="normal"
                InputProps={{
                  startAdornment: <Email sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
              <TextField
                fullWidth
                label="Phone Number"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                margin="normal"
                InputProps={{
                  startAdornment: <Phone sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
              <TextField
                fullWidth
                label="Subject"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                required
                margin="normal"
                InputProps={{
                  startAdornment: <Subject sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
              <TextField
                fullWidth
                label="Message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                required
                multiline
                rows={4}
                margin="normal"
                InputProps={{
                  startAdornment: <Message sx={{ mr: 1, color: 'text.secondary', alignSelf: 'flex-start', mt: 1 }} />
                }}
              />
              <Button
                type="submit"
                variant="contained"
                size="large"
                startIcon={<Send />}
                sx={{ mt: 3, mb: 2 }}
                fullWidth
              >
                Send Message
              </Button>
            </Box>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
              Visit Our Campus
            </Typography>
            <Typography variant="body1" paragraph>
              We welcome you to visit our beautiful campus and experience the learning environment firsthand. 
              Schedule a visit to see our facilities, meet our faculty, and learn more about our programs.
            </Typography>
            
            {/* Map Placeholder */}
            <Box
              sx={{
                height: 250,
                backgroundColor: 'grey.200',
                borderRadius: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3
              }}
            >
              <Typography variant="h6" color="text.secondary">
                Interactive Map Coming Soon
              </Typography>
            </Box>
            
            <Button variant="outlined" size="large" fullWidth>
              Get Directions
            </Button>
          </Paper>
        </Grid>
      </Grid>

      {/* Department Contacts */}
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom color="primary" fontWeight="bold" textAlign="center">
          Department Contacts
        </Typography>
        <Grid container spacing={2}>
          {departments.map((dept, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card elevation={1} sx={{ p: 2 }}>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  {dept.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {dept.extension}
                </Typography>
                <Typography variant="body2" color="primary">
                  {dept.email}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Success Snackbar */}
      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={() => setShowSuccess(false)}
      >
        <Alert onClose={() => setShowSuccess(false)} severity="success" sx={{ width: '100%' }}>
          Thank you for your message! We will get back to you soon.
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Contact;
