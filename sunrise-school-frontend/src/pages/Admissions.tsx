import React from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Assignment,
  Schedule,
  Payment,
  CheckCircle,
  Description,
  Phone,
  Email,
  LocationOn,
} from '@mui/icons-material';

const Admissions: React.FC = () => {
  const admissionSteps = [
    'Application Form Submission',
    'Document Verification',
    'Entrance Test/Interview',
    'Fee Payment',
    'Admission Confirmation'
  ];

  const feeStructure = [
    { class: 'Nursery - UKG', admissionFee: '₹5,000', tuitionFee: '₹3,000/month', totalAnnual: '₹41,000' },
    { class: 'Class I - V', admissionFee: '₹7,000', tuitionFee: '₹4,000/month', totalAnnual: '₹55,000' },
    { class: 'Class VI - VIII', admissionFee: '₹8,000', tuitionFee: '₹5,000/month', totalAnnual: '₹68,000' },
    { class: 'Class IX - X', admissionFee: '₹10,000', tuitionFee: '₹6,000/month', totalAnnual: '₹82,000' },
    { class: 'Class XI - XII', admissionFee: '₹12,000', tuitionFee: '₹7,000/month', totalAnnual: '₹96,000' },
  ];

  const requiredDocuments = [
    'Birth Certificate (Original + 2 copies)',
    'Transfer Certificate from previous school',
    'Academic records/Report cards',
    'Passport size photographs (6 copies)',
    'Address proof (Ration card/Voter ID/Passport)',
    'Caste certificate (if applicable)',
    'Medical fitness certificate',
    'Parent\'s ID proof (Aadhar/PAN/Passport)'
  ];

  const importantDates = [
    { event: 'Application Form Release', date: 'January 15, 2024' },
    { event: 'Last Date for Application', date: 'March 31, 2024' },
    { event: 'Entrance Test', date: 'April 15-20, 2024' },
    { event: 'Result Declaration', date: 'April 25, 2024' },
    { event: 'Admission Confirmation', date: 'May 1-15, 2024' },
    { event: 'Academic Session Begins', date: 'June 1, 2024' }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" color="primary">
          Admissions 2024-25
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
          Join our community of learners and embark on a journey of academic excellence and personal growth
        </Typography>
      </Box>

      {/* Admission Process */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Admission Process
        </Typography>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Stepper orientation="vertical">
            {admissionSteps.map((step, index) => (
              <Step key={index} active={true}>
                <StepLabel>
                  <Typography variant="h6" fontWeight="medium">
                    {step}
                  </Typography>
                </StepLabel>
              </Step>
            ))}
          </Stepper>
        </Paper>
      </Box>

      {/* Fee Structure */}
      <Box mb={6}>
        <Typography variant="h4" gutterBottom textAlign="center" color="primary" fontWeight="bold">
          Fee Structure
        </Typography>
        <TableContainer component={Paper} elevation={3}>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'primary.main' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Class</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Admission Fee</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Monthly Tuition</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Total Annual Fee</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {feeStructure.map((row, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row" sx={{ fontWeight: 'medium' }}>
                    {row.class}
                  </TableCell>
                  <TableCell>{row.admissionFee}</TableCell>
                  <TableCell>{row.tuitionFee}</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {row.totalAnnual}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            * Fees include tuition, library, sports, and examination charges. Additional charges may apply for transport, uniform, and books.
          </Typography>
        </Alert>
      </Box>

      {/* Important Dates and Documents */}
      <Grid container spacing={4} mb={6}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
              Important Dates
            </Typography>
            <List>
              {importantDates.map((item, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Schedule color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.event}
                    secondary={item.date}
                    primaryTypographyProps={{ fontWeight: 'medium' }}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
              Required Documents
            </Typography>
            <List>
              {requiredDocuments.map((document, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Description color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={document} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Contact Information */}
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom color="primary" fontWeight="bold" textAlign="center">
          Admission Enquiry
        </Typography>
        <Grid container spacing={4}>
          <Grid size={{ xs: 12, md: 4 }}>
            <Card elevation={2} sx={{ textAlign: 'center', p: 3 }}>
              <Phone color="primary" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Phone
              </Typography>
              <Typography variant="body1">
                +91 98765 43210<br />
                +91 87654 32109
              </Typography>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <Card elevation={2} sx={{ textAlign: 'center', p: 3 }}>
              <Email color="primary" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Email
              </Typography>
              <Typography variant="body1">
                admissions@sunriseschool.edu<br />
                info@sunriseschool.edu
              </Typography>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <Card elevation={2} sx={{ textAlign: 'center', p: 3 }}>
              <LocationOn color="primary" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Visit Us
              </Typography>
              <Typography variant="body1">
                Admission Office<br />
                Mon-Fri: 9:00 AM - 4:00 PM<br />
                Sat: 9:00 AM - 1:00 PM
              </Typography>
            </Card>
          </Grid>
        </Grid>
        <Box textAlign="center" mt={4}>
          <Button variant="contained" size="large" sx={{ mr: 2 }}>
            Download Application Form
          </Button>
          <Button variant="outlined" size="large">
            Schedule School Visit
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Admissions;
