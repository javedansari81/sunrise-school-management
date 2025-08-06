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
          Admissions 2025-26
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
          Join our community of learners and embark on a journey of academic excellence and personal growth
        </Typography>
      </Box>

      {/* Admission Process */}
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
          Admission Process
        </Typography>
        <Paper elevation={3} sx={{ p: { xs: 2.5, sm: 3, md: 4 } }}>
          <Stepper
            orientation="vertical"
            sx={{
              '& .MuiStepLabel-root': {
                py: { xs: 1, sm: 1.5 }
              }
            }}
          >
            {admissionSteps.map((step, index) => (
              <Step key={index} active={true}>
                <StepLabel>
                  <Typography
                    variant="h6"
                    fontWeight="medium"
                    sx={{
                      fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' }
                    }}
                  >
                    {step}
                  </Typography>
                </StepLabel>
              </Step>
            ))}
          </Stepper>
        </Paper>
      </Box>

      {/* Fee Structure */}
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
          Fee Structure
        </Typography>

        {/* Mobile-friendly fee structure - Cards for mobile, Table for desktop */}
        <Box sx={{ display: { xs: 'block', md: 'none' } }}>
          {loading ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <CircularProgress size={24} />
              <Typography variant="body2" sx={{ mt: 1 }}>
                Loading fee structure...
              </Typography>
            </Box>
          ) : (
            <Grid container spacing={2}>
              {feeStructure.map((row, index) => (
                <Grid key={index} size={{ xs: 12, sm: 6 }}>
                  <Card elevation={2} sx={{ p: 2 }}>
                    <Typography variant="h6" fontWeight="bold" color="primary" gutterBottom>
                      {row.class}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Monthly:
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {row.tuitionFee}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        Annual:
                      </Typography>
                      <Typography variant="body2" fontWeight="bold" color="primary.main">
                        {row.totalAnnual}
                      </Typography>
                    </Box>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>

        {/* Desktop Table */}
        <Box sx={{ display: { xs: 'none', md: 'block' } }}>
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
                    <TableCell colSpan={3} sx={{ textAlign: 'center', py: 4 }}>
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
        </Box>

        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography
            variant="body2"
            sx={{
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              lineHeight: { xs: 1.4, sm: 1.5 }
            }}
          >
            * Tuition fees shown are comprehensive and include all academic charges. No additional admission fees are currently charged. Additional charges may apply for transport, uniform, and books.
          </Typography>
        </Alert>
      </Box>

      {/* Important Dates and Documents */}
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
                mb: { xs: 2, sm: 3 }
              }}
            >
              Important Dates
            </Typography>
            <List sx={{ py: 0 }}>
              {importantDates.map((item, index) => (
                <ListItem
                  key={index}
                  sx={{
                    py: { xs: 1, sm: 1.5 },
                    px: { xs: 0, sm: 1 }
                  }}
                >
                  <ListItemIcon sx={{ minWidth: { xs: 40, sm: 56 } }}>
                    <Schedule color="primary" sx={{ fontSize: { xs: 20, sm: 24 } }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={item.event}
                    secondary={item.date}
                    primaryTypographyProps={{
                      fontWeight: 'medium',
                      sx: { fontSize: { xs: '0.875rem', sm: '1rem' } }
                    }}
                    secondaryTypographyProps={{
                      sx: { fontSize: { xs: '0.75rem', sm: '0.875rem' } }
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
              Required Documents
            </Typography>
            <List sx={{ py: 0 }}>
              {requiredDocuments.map((document, index) => (
                <ListItem
                  key={index}
                  sx={{
                    py: { xs: 0.75, sm: 1 },
                    px: { xs: 0, sm: 1 }
                  }}
                >
                  <ListItemIcon sx={{ minWidth: { xs: 40, sm: 56 } }}>
                    <Description color="primary" sx={{ fontSize: { xs: 20, sm: 24 } }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={document}
                    primaryTypographyProps={{
                      sx: { fontSize: { xs: '0.875rem', sm: '1rem' } }
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Contact Information */}
      <Paper elevation={3} sx={{ p: { xs: 2.5, sm: 3, md: 4 } }}>
        <Typography
          variant="h4"
          gutterBottom
          color="primary"
          fontWeight="bold"
          textAlign="center"
          sx={{
            fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2.125rem' },
            mb: { xs: 2, sm: 3 }
          }}
        >
          Admission Enquiry
        </Typography>
        <Grid container spacing={{ xs: 2, sm: 3, md: 4 }}>
          <Grid size={{ xs: 12, md: 4 }}>
            <Card
              elevation={2}
              sx={{
                textAlign: 'center',
                p: { xs: 2, sm: 2.5, md: 3 },
                height: '100%'
              }}
            >
              <Phone
                color="primary"
                sx={{
                  fontSize: { xs: 36, sm: 42, md: 48 },
                  mb: { xs: 1.5, sm: 2 }
                }}
              />
              <Typography
                variant="h6"
                gutterBottom
                sx={{
                  fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
                  mb: { xs: 1, sm: 1.5 }
                }}
              >
                Phone
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  lineHeight: { xs: 1.4, sm: 1.5 }
                }}
              >
                +91 6392171614<br />
                +91 9198627786
              </Typography>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <Card
              elevation={2}
              sx={{
                textAlign: 'center',
                p: { xs: 2, sm: 2.5, md: 3 },
                height: '100%'
              }}
            >
              <Email
                color="primary"
                sx={{
                  fontSize: { xs: 36, sm: 42, md: 48 },
                  mb: { xs: 1.5, sm: 2 }
                }}
              />
              <Typography
                variant="h6"
                gutterBottom
                sx={{
                  fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
                  mb: { xs: 1, sm: 1.5 }
                }}
              >
                Email
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  lineHeight: { xs: 1.4, sm: 1.5 }
                }}
              >
                sunrise.nps008@gmail.com
              </Typography>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <Card
              elevation={2}
              sx={{
                textAlign: 'center',
                p: { xs: 2, sm: 2.5, md: 3 },
                height: '100%'
              }}
            >
              <LocationOn
                color="primary"
                sx={{
                  fontSize: { xs: 36, sm: 42, md: 48 },
                  mb: { xs: 1.5, sm: 2 }
                }}
              />
              <Typography
                variant="h6"
                gutterBottom
                sx={{
                  fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
                  mb: { xs: 1, sm: 1.5 }
                }}
              >
                Visit Us
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  lineHeight: { xs: 1.4, sm: 1.5 }
                }}
              >
                Admission Office<br />
                Mon-Sat: 8:00 AM - 2:30 PM
              </Typography>
            </Card>
          </Grid>
        </Grid>
        <Box
          textAlign="center"
          mt={{ xs: 3, sm: 4 }}
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            gap: { xs: 1.5, sm: 2 },
            justifyContent: 'center',
            alignItems: 'center'
          }}
        >
          <Button
            variant="contained"
            size="large"
            sx={{
              minWidth: { xs: '200px', sm: 'auto' },
              fontSize: { xs: '0.875rem', sm: '1rem' },
              py: { xs: 1.25, sm: 1.5 }
            }}
          >
            Download Application Form
          </Button>
          <Button
            variant="outlined"
            size="large"
            sx={{
              minWidth: { xs: '200px', sm: 'auto' },
              fontSize: { xs: '0.875rem', sm: '1rem' },
              py: { xs: 1.25, sm: 1.5 }
            }}
          >
            Schedule School Visit
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Admissions;
