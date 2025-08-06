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
  Link,
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
        '+91 6392171614',
        '+91 9198627786'
      ]
    },
    {
      icon: <Email />,
      title: 'Email Address',
      details: [
        'sunrise.nps008@gmail.com'
      ]
    },
    {
      icon: <LocationOn />,
      title: 'Address',
      details: [
        'Sunrise National Public School',
        'Sena road, Farsauliyana',
        'Rath, Hamirpur, UP - 210431'
      ]
    },
    {
      icon: <Schedule />,
      title: 'Office Hours',
      details: [
        'Mon-Sat: 8:00 AM - 2:30 PM',
        'Sunday: Closed'
      ]
    }
  ];

  const departments = [
    { name: 'Principal Office', phone: '+91 6392171614', email: 'sunrise.nps008@gmail.com' },
    { name: 'Admissions Office', phone: '+91 9198627786', email: 'sunrise.nps008@gmail.com' },
    { name: 'Academic Office', phone: '+91 6392171614', email: 'sunrise.nps008@gmail.com' },
    { name: 'Finance Office', phone: '+91 9198627786', email: 'sunrise.nps008@gmail.com' },
    { name: 'Transport Office', phone: '+91 6392171614', email: 'sunrise.nps008@gmail.com' },
    { name: 'Sports Department', phone: '+91 9198627786', email: 'sunrise.nps008@gmail.com' }
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
                    {info.title === 'Phone Numbers' ? (
                      <Link href={`tel:${detail}`} color="inherit" underline="hover">
                        {detail}
                      </Link>
                    ) : info.title === 'Email Address' ? (
                      <Link href={`mailto:${detail}`} color="inherit" underline="hover">
                        {detail}
                      </Link>
                    ) : (
                      detail
                    )}
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

            {/* Google Maps Embed */}
            <Box
              sx={{
                height: 250,
                borderRadius: 2,
                overflow: 'hidden',
                mb: 3,
                border: '1px solid',
                borderColor: 'grey.300'
              }}
            >
              <iframe
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3603.8234567890123!2d79.6234567!3d25.4567890!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2sRath%2C%20Hamirpur%2C%20Uttar%20Pradesh%20210431!5e0!3m2!1sen!2sin!4v1234567890123!5m2!1sen!2sin"
                width="100%"
                height="100%"
                style={{ border: 0 }}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                title="Sunrise National Public School Location"
              />
            </Box>

            <Button
              variant="outlined"
              size="large"
              fullWidth
              onClick={() => window.open('https://maps.google.com/?q=Sunrise+National+Public+School+Rath+Hamirpur+UP', '_blank')}
            >
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
                <Typography variant="body2" color="text.secondary" paragraph>
                  <Link href={`tel:${dept.phone}`} color="inherit" underline="hover">
                    {dept.phone}
                  </Link>
                </Typography>
                <Typography variant="body2" color="primary">
                  <Link href={`mailto:${dept.email}`} color="inherit" underline="hover">
                    {dept.email}
                  </Link>
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
