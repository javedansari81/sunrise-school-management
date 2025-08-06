import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Container,
} from '@mui/material';
import {
  School,
  AccountBalance,
  LocalLibrary,
  Science,
  DirectionsBus,
  SportsBasketball,
  Assignment,
  AttachMoney,
} from '@mui/icons-material';
import { enhancedFeesAPI } from '../../services/api';

interface FeeStructureData {
  id: number;
  class_id: number;
  session_year_id: number;
  class_name: string;
  session_year_name: string;
  tuition_fee: number;
  admission_fee: number;
  development_fee: number;
  activity_fee: number;
  transport_fee: number;
  library_fee: number;
  lab_fee: number;
  exam_fee: number;
  other_fee: number;
  total_annual_fee: number;
}

const FeeStructureDisplay: React.FC = () => {
  const [feeStructures, setFeeStructures] = useState<FeeStructureData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Define class order for proper sorting
  const classOrder = [
    'Pre-Kindergarten (PG)',
    'PG',
    'Lower Kindergarten (LKG)', 
    'LKG',
    'Upper Kindergarten (UKG)',
    'UKG',
    'Class 1', 'Class I',
    'Class 2', 'Class II',
    'Class 3', 'Class III',
    'Class 4', 'Class IV',
    'Class 5', 'Class V',
    'Class 6', 'Class VI',
    'Class 7', 'Class VII',
    'Class 8', 'Class VIII'
  ];

  const getClassSortOrder = (className: string): number => {
    const index = classOrder.findIndex(order => 
      className.toLowerCase().includes(order.toLowerCase()) ||
      order.toLowerCase().includes(className.toLowerCase())
    );
    return index === -1 ? 999 : index;
  };

  useEffect(() => {
    const fetchFeeStructures = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await enhancedFeesAPI.getFeeStructure();
        
        // Filter for current session year (2025-26) and sort by class order
        const currentSessionStructures = response.data
          .filter((structure: FeeStructureData) => structure.session_year_name === '2025-26')
          .sort((a: FeeStructureData, b: FeeStructureData) => 
            getClassSortOrder(a.class_name) - getClassSortOrder(b.class_name)
          );
        
        setFeeStructures(currentSessionStructures);
      } catch (error: any) {
        console.error('Error fetching fee structures:', error);
        setError('Failed to load fee structure data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchFeeStructures();
  }, []);

  const formatCurrency = (amount: number): string => {
    return `₹${amount?.toLocaleString() || '0'}`;
  };

  const calculateMonthlyFee = (annualFee: number): string => {
    return formatCurrency(Math.round(annualFee / 12));
  };

  const getFeeComponents = (structure: FeeStructureData) => {
    const components = [
      { name: 'Tuition Fee', amount: structure.tuition_fee, icon: <School /> },
      { name: 'Development Fee', amount: structure.development_fee, icon: <AccountBalance /> },
      { name: 'Activity Fee', amount: structure.activity_fee, icon: <SportsBasketball /> },
      { name: 'Transport Fee', amount: structure.transport_fee, icon: <DirectionsBus /> },
      { name: 'Library Fee', amount: structure.library_fee, icon: <LocalLibrary /> },
      { name: 'Lab Fee', amount: structure.lab_fee, icon: <Science /> },
      { name: 'Exam Fee', amount: structure.exam_fee, icon: <Assignment /> },
      { name: 'Other Fee', amount: structure.other_fee, icon: <AttachMoney /> },
    ];
    
    return components.filter(component => component.amount > 0);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: { xs: 3, sm: 4 }, px: { xs: 2, sm: 3 } }}>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
          <CircularProgress size={48} />
          <Typography
            variant="h6"
            sx={{
              mt: 2,
              color: 'text.secondary',
              fontSize: { xs: '1rem', sm: '1.25rem' },
              textAlign: 'center'
            }}
          >
            Loading Fee Structure Data...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: { xs: 3, sm: 4 }, px: { xs: 2, sm: 3 } }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 3, sm: 4, md: 6 }, px: { xs: 2, sm: 3 } }}>
      {/* Header */}
      <Box textAlign="center" mb={{ xs: 3, sm: 4 }}>
        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          fontWeight="bold"
          color="primary"
          sx={{
            fontSize: { xs: '1.75rem', sm: '2.5rem', md: '3rem' },
            lineHeight: { xs: 1.2, sm: 1.3 },
            mb: { xs: 2, sm: 3 }
          }}
        >
          Fee Structure 2025-26
        </Typography>
        <Typography
          variant="h6"
          color="text.secondary"
          sx={{
            fontSize: { xs: '1rem', sm: '1.25rem' },
            lineHeight: { xs: 1.4, sm: 1.5 },
            px: { xs: 1, sm: 2 }
          }}
        >
          Sunrise National Public School - Comprehensive Fee Breakdown by Class
        </Typography>
      </Box>

      {feeStructures.length === 0 ? (
        <Alert severity="info">
          No fee structure data available for the current academic session (2025-26).
        </Alert>
      ) : (
        <>
          {/* Summary Table */}
          <Paper elevation={3} sx={{ mb: { xs: 3, sm: 4 } }}>
            <Box sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
              <Typography
                variant="h5"
                gutterBottom
                fontWeight="bold"
                color="primary"
                sx={{
                  fontSize: { xs: '1.25rem', sm: '1.5rem', md: '1.5rem' },
                  mb: { xs: 2, sm: 3 }
                }}
              >
                Fee Summary by Class
              </Typography>

              {/* Mobile-friendly fee summary - Cards for mobile, Table for desktop */}
              <Box sx={{ display: { xs: 'block', md: 'none' } }}>
                <Grid container spacing={2}>
                  {feeStructures.map((structure) => (
                    <Grid key={structure.id} size={{ xs: 12, sm: 6 }}>
                      <Card elevation={1} sx={{ p: 2 }}>
                        <Typography variant="h6" fontWeight="bold" color="primary" gutterBottom>
                          {structure.class_name}
                        </Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            Monthly:
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {calculateMonthlyFee(structure.total_annual_fee)}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            Annual:
                          </Typography>
                          <Typography variant="body2" fontWeight="bold" color="primary.main">
                            {formatCurrency(structure.total_annual_fee)}
                          </Typography>
                        </Box>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>

              {/* Desktop Table */}
              <Box sx={{ display: { xs: 'none', md: 'block' } }}>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ backgroundColor: 'primary.main' }}>
                        <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Class/Grade</TableCell>
                        <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Monthly Tuition</TableCell>
                        <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Annual Tuition</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {feeStructures.map((structure) => (
                        <TableRow key={structure.id} hover>
                          <TableCell sx={{ fontWeight: 'medium' }}>
                            {structure.class_name}
                          </TableCell>
                          <TableCell>{calculateMonthlyFee(structure.total_annual_fee)}</TableCell>
                          <TableCell sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                            {formatCurrency(structure.total_annual_fee)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            </Box>
          </Paper>

          {/* Detailed Breakdown Cards */}
          <Typography
            variant="h5"
            gutterBottom
            fontWeight="bold"
            color="primary"
            sx={{
              mb: { xs: 2, sm: 3 },
              fontSize: { xs: '1.25rem', sm: '1.5rem', md: '1.5rem' }
            }}
          >
            Detailed Fee Breakdown by Class
          </Typography>

          <Grid container spacing={{ xs: 2, sm: 3 }}>
            {feeStructures.map((structure) => {
              const feeComponents = getFeeComponents(structure);

              return (
                <Grid key={structure.id} size={{ xs: 12, md: 6, lg: 4 }}>
                  <Card elevation={3} sx={{ height: '100%' }}>
                    <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
                      {/* Class Header */}
                      <Box textAlign="center" mb={{ xs: 1.5, sm: 2 }}>
                        <Typography
                          variant="h6"
                          fontWeight="bold"
                          color="primary"
                          sx={{
                            fontSize: { xs: '1rem', sm: '1.125rem', md: '1.25rem' },
                            mb: { xs: 1, sm: 1.5 }
                          }}
                        >
                          {structure.class_name}
                        </Typography>
                        <Chip
                          label={`Session: ${structure.session_year_name}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{
                            fontSize: { xs: '0.75rem', sm: '0.8125rem' }
                          }}
                        />
                      </Box>

                      <Divider sx={{ mb: { xs: 1.5, sm: 2 } }} />

                      {/* Key Amounts */}
                      <Box mb={{ xs: 1.5, sm: 2 }}>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                          >
                            Monthly Tuition:
                          </Typography>
                          <Typography
                            variant="body2"
                            fontWeight="medium"
                            sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                          >
                            {calculateMonthlyFee(structure.total_annual_fee)}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between" mb={2}>
                          <Typography
                            variant="body1"
                            fontWeight="bold"
                            sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                          >
                            Annual Tuition:
                          </Typography>
                          <Typography
                            variant="body1"
                            fontWeight="bold"
                            color="primary.main"
                            sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                          >
                            {formatCurrency(structure.total_annual_fee)}
                          </Typography>
                        </Box>
                      </Box>

                      {/* Fee Components */}
                      {feeComponents.length > 0 && (
                        <>
                          <Divider sx={{ mb: { xs: 1.5, sm: 2 } }} />
                          <Typography
                            variant="subtitle2"
                            gutterBottom
                            fontWeight="bold"
                            sx={{
                              fontSize: { xs: '0.875rem', sm: '1rem' },
                              mb: { xs: 1, sm: 1.5 }
                            }}
                          >
                            Fee Components:
                          </Typography>
                          <Box>
                            {feeComponents.map((component, index) => (
                              <Box
                                key={index}
                                display="flex"
                                alignItems="center"
                                justifyContent="space-between"
                                mb={1}
                              >
                                <Box display="flex" alignItems="center">
                                  <Box sx={{
                                    color: 'primary.main',
                                    mr: { xs: 0.75, sm: 1 },
                                    fontSize: { xs: '14px', sm: '16px' }
                                  }}>
                                    {component.icon}
                                  </Box>
                                  <Typography
                                    variant="body2"
                                    color="text.secondary"
                                    sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                                  >
                                    {component.name}
                                  </Typography>
                                </Box>
                                <Typography
                                  variant="body2"
                                  fontWeight="medium"
                                  sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                                >
                                  {formatCurrency(component.amount)}
                                </Typography>
                              </Box>
                            ))}
                          </Box>
                        </>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>

          {/* Footer Note */}
          <Alert severity="info" sx={{ mt: { xs: 3, sm: 4 } }}>
            <Typography
              variant="body2"
              sx={{
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                lineHeight: { xs: 1.4, sm: 1.5 }
              }}
            >
              <strong>Note:</strong> Tuition fees shown are for the academic session 2025-26.
              No admission fees, development fees, or other additional fees are currently charged.
              Monthly tuition is calculated by dividing the annual tuition fee by 12 months.
              Additional charges may apply for uniforms, books, transport, and optional services.
            </Typography>
          </Alert>
        </>
      )}
    </Container>
  );
};

export default FeeStructureDisplay;
