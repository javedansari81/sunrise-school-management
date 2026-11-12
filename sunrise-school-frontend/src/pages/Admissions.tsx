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
  Chip,
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
import { publicAPI } from '../services/api';

interface KeyDate {
  key: string;
  label: string;
  date: string;
  end_date: string | null;
}

const longDate = (iso: string, withYear = true) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', ...(withYear ? { year: 'numeric' } : {}) });

/** "15 November 2026", or "15–20 February 2027" for a range within one month */
const dateRange = (item: KeyDate) => {
  if (!item.end_date) return longDate(item.date);
  const start = new Date(`${item.date}T00:00:00`);
  const end = new Date(`${item.end_date}T00:00:00`);
  if (start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear()) {
    return `${start.getDate()}–${longDate(item.end_date)}`;
  }
  return `${longDate(item.date, false)} – ${longDate(item.end_date)}`;
};

const Admissions: React.FC = () => {
  const [feeStructure, setFeeStructure] = useState<any[]>([]);
  const [feeSession, setFeeSession] = useState<string>('');
  const [admissionSession, setAdmissionSession] = useState<string>('');
  const [keyDates, setKeyDates] = useState<KeyDate[]>([]);
  const [loading, setLoading] = useState(true);

  const admissionSteps = [
    'Application Form Submission',
    'Document Verification',
    'Entrance Test/Interview',
    'Fee Payment',
    'Admission Confirmation'
  ];

  // The session families apply for now, its key dates and its fees, all from the school's data
  useEffect(() => {
    const rupees = (value: string) => `₹${Number(value).toLocaleString('en-IN')}`;
    publicAPI
      .getAdmissions()
      .then((response) => {
        setAdmissionSession(response.data.session?.name || '');
        setKeyDates(response.data.dates || []);
        setFeeSession(response.data.fees?.session_year || '');
        setFeeStructure(
          (response.data.fees?.classes || []).map((row: any) => ({
            class: row.class_name,
            tuitionFee: Number(row.monthly) > 0 ? `${rupees(row.monthly)}/month` : '—',
            oneTime: Number(row.one_time) > 0 ? rupees(row.one_time) : '—',
            totalAnnual: rupees(row.first_year_total),
          }))
        );
      })
      .catch(() => setFeeStructure([]))
      .finally(() => setLoading(false));
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

  const today = new Date().toISOString().slice(0, 10);
  // The first date that has not fully passed yet
  const nextKey = keyDates.find((item) => (item.end_date || item.date) >= today)?.key;

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
          {admissionSession ? `Admissions ${admissionSession}` : 'Admissions'}
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
          Fee Structure{feeSession ? ` ${feeSession}` : ''}
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
                        First year in all:
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
                <TableRow sx={{ background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)', '& .MuiTableCell-head': { backgroundColor: 'transparent', color: 'white' } }}>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Class</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Monthly fees</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>One-time, at admission</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>First year in all</TableCell>
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
                      <TableCell>{row.oneTime}</TableCell>
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
            {feeStructure.length === 0 && !loading
              ? 'The fee structure is not published yet. Please contact the school office for fee details.'
              : `${admissionSession && feeSession && feeSession !== admissionSession ? `Fees for ${admissionSession} are not announced yet; these are the ${feeSession} fees. ` : ''}* Fees for a new student. The first-year figure adds up every fee billed in the year. Transport, uniform and books are charged separately.`}
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
            {loading ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <CircularProgress size={24} />
              </Box>
            ) : (
              <Box sx={{ position: 'relative' }}>
                {keyDates.map((item, index) => {
                  const past = (item.end_date || item.date) < today;
                  const next = item.key === nextKey;
                  return (
                    <Box
                      key={item.key}
                      sx={{
                        position: 'relative',
                        display: 'flex',
                        gap: 2,
                        pb: index === keyDates.length - 1 ? 0 : 2.5,
                        opacity: past ? 0.55 : 1,
                        animation: 'fadeUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) both',
                        animationDelay: `${index * 60}ms`,
                      }}
                    >
                      {/* Line joining the dates */}
                      {index < keyDates.length - 1 && (
                        <Box
                          sx={{
                            position: 'absolute',
                            left: 17,
                            top: 38,
                            bottom: 4,
                            width: 2,
                            borderRadius: 2,
                            background: past ? 'rgba(15,23,42,0.12)' : 'linear-gradient(180deg, #2563eb, rgba(124,58,237,0.3))',
                          }}
                        />
                      )}
                      <Box
                        sx={{
                          flexShrink: 0,
                          display: 'grid',
                          placeItems: 'center',
                          width: 36,
                          height: 36,
                          borderRadius: '50%',
                          color: past ? 'text.secondary' : '#fff',
                          background: past ? 'rgba(15,23,42,0.08)' : 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                          animation: next ? 'pulseRing 2.4s ease-out infinite' : 'none',
                        }}
                      >
                        {past ? <CheckCircle sx={{ fontSize: 20 }} /> : <Schedule sx={{ fontSize: 20 }} />}
                      </Box>
                      <Box sx={{ pt: 0.25 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                          <Typography sx={{ fontWeight: 600, fontSize: { xs: '0.9rem', sm: '1rem' } }}>{item.label}</Typography>
                          {next && <Chip size="small" color="primary" label="Next" sx={{ height: 20, fontSize: '0.7rem' }} />}
                        </Box>
                        <Typography
                          color={next ? 'primary.main' : 'text.secondary'}
                          sx={{ fontSize: { xs: '0.8rem', sm: '0.9rem' }, fontWeight: next ? 700 : 400 }}
                        >
                          {dateRange(item)}
                        </Typography>
                      </Box>
                    </Box>
                  );
                })}
              </Box>
            )}
            {!loading && keyDates.length > 0 && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2.5 }}>
                Dates may change. Please confirm with the school office.
              </Typography>
            )}
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
