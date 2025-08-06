import React, { useState, useEffect } from 'react';
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
  CircularProgress,
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
import { enhancedFeesAPI } from '../services/api';

const Admissions: React.FC = () => {
  const [feeStructure, setFeeStructure] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const admissionSteps = [
    'Application Form Submission',
    'Document Verification',
    'Entrance Test/Interview',
    'Fee Payment',
    'Admission Confirmation'
  ];

  // Fetch fee structure data on component mount
  useEffect(() => {
    const fetchFeeStructure = async () => {
      try {
        setLoading(true);
        const response = await enhancedFeesAPI.getFeeStructure();

        // Filter for current session year (2025-26) and format data for display
        const currentSessionStructures = response.data
          .filter((structure: any) => structure.session_year_name === '2025-26')
          .map((structure: any) => ({
            class: structure.class_name,
            admissionFee: `₹${structure.admission_fee?.toLocaleString() || '0'}`,
            tuitionFee: `₹${Math.round(structure.total_annual_fee / 12)?.toLocaleString() || '0'}/month`,
            totalAnnual: `₹${structure.total_annual_fee?.toLocaleString() || '0'}`
          }));

        setFeeStructure(currentSessionStructures);
      } catch (error) {
        console.error('Error fetching fee structure:', error);
        // Fallback to current database structure if API fails
        setFeeStructure([
          { class: 'PG', admissionFee: '₹0', tuitionFee: '₹640/month', totalAnnual: '₹7,680' },
          { class: 'LKG', admissionFee: '₹0', tuitionFee: '₹680/month', totalAnnual: '₹8,160' },
          { class: 'UKG', admissionFee: '₹0', tuitionFee: '₹720/month', totalAnnual: '₹8,640' },
          { class: 'Class 1', admissionFee: '₹0', tuitionFee: '₹800/month', totalAnnual: '₹9,600' },
          { class: 'Class 2', admissionFee: '₹0', tuitionFee: '₹840/month', totalAnnual: '₹10,080' },
          { class: 'Class 3', admissionFee: '₹0', tuitionFee: '₹880/month', totalAnnual: '₹10,560' },
          { class: 'Class 4', admissionFee: '₹0', tuitionFee: '₹920/month', totalAnnual: '₹11,040' },
          { class: 'Class 5', admissionFee: '₹0', tuitionFee: '₹960/month', totalAnnual: '₹11,520' },
          { class: 'Class 6', admissionFee: '₹0', tuitionFee: '₹1,000/month', totalAnnual: '₹12,000' },
          { class: 'Class 7', admissionFee: '₹0', tuitionFee: '₹1,040/month', totalAnnual: '₹12,480' },
          { class: 'Class 8', admissionFee: '₹0', tuitionFee: '₹1,080/month', totalAnnual: '₹12,960' },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchFeeStructure();
  }, []);

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
    { event: 'Application Form Release', date: 'January 15, 2025' },
    { event: 'Last Date for Application', date: 'March 31, 2025' },
    { event: 'Entrance Test', date: 'April 15-20, 2025' },
    { event: 'Result Declaration', date: 'April 25, 2025' },
    { event: 'Admission Confirmation', date: 'May 1-15, 2025' },
    { event: 'Academic Session Begins', date: 'June 1, 2025' }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" color="primary">
          Admissions 2025-26
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
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Monthly Tuition</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Annual Tuition</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={4} sx={{ textAlign: 'center', py: 4 }}>
                    <CircularProgress size={24} />
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Loading fee structure...
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                feeStructure.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell component="th" scope="row" sx={{ fontWeight: 'medium' }}>
                      {row.class}
                    </TableCell>
                    <TableCell>{row.tuitionFee}</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      {row.totalAnnual}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            * Tuition fees shown are comprehensive and include all academic charges. No additional admission fees are currently charged. Additional charges may apply for transport, uniform, and books.
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
                +91 6392171614<br />
                +91 9198627786
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
                sunrise.nps008@gmail.com
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
                Mon-Sat: 8:00 AM - 2:30 PM
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
