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
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
          <CircularProgress size={48} />
          <Typography variant="h6" sx={{ mt: 2, color: 'text.secondary' }}>
            Loading Fee Structure Data...
          </Typography>
        </Box>
      </Container>
    );
  }

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
      {/* Header */}
      <Box textAlign="center" mb={4}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold" color="primary">
          Fee Structure 2025-26
        </Typography>
        <Typography variant="h6" color="text.secondary">
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
          <Paper elevation={3} sx={{ mb: 4 }}>
            <Box sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom fontWeight="bold" color="primary">
                Fee Summary by Class
              </Typography>
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
          </Paper>

          {/* Detailed Breakdown Cards */}
          <Typography variant="h5" gutterBottom fontWeight="bold" color="primary" sx={{ mb: 3 }}>
            Detailed Fee Breakdown by Class
          </Typography>
          
          <Grid container spacing={3}>
            {feeStructures.map((structure) => {
              const feeComponents = getFeeComponents(structure);
              
              return (
                <Grid key={structure.id} size={{ xs: 12, md: 6, lg: 4 }}>
                  <Card elevation={3} sx={{ height: '100%' }}>
                    <CardContent sx={{ p: 3 }}>
                      {/* Class Header */}
                      <Box textAlign="center" mb={2}>
                        <Typography variant="h6" fontWeight="bold" color="primary">
                          {structure.class_name}
                        </Typography>
                        <Chip 
                          label={`Session: ${structure.session_year_name}`} 
                          size="small" 
                          color="primary" 
                          variant="outlined" 
                        />
                      </Box>

                      <Divider sx={{ mb: 2 }} />

                      {/* Key Amounts */}
                      <Box mb={2}>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="body2" color="text.secondary">
                            Monthly Tuition:
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {calculateMonthlyFee(structure.total_annual_fee)}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between" mb={2}>
                          <Typography variant="body1" fontWeight="bold">
                            Annual Tuition:
                          </Typography>
                          <Typography variant="body1" fontWeight="bold" color="primary.main">
                            {formatCurrency(structure.total_annual_fee)}
                          </Typography>
                        </Box>
                      </Box>

                      {/* Fee Components */}
                      {feeComponents.length > 0 && (
                        <>
                          <Divider sx={{ mb: 2 }} />
                          <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                            Fee Components:
                          </Typography>
                          <Box>
                            {feeComponents.map((component, index) => (
                              <Box key={index} display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                                <Box display="flex" alignItems="center">
                                  <Box sx={{ color: 'primary.main', mr: 1, fontSize: '16px' }}>
                                    {component.icon}
                                  </Box>
                                  <Typography variant="body2" color="text.secondary">
                                    {component.name}
                                  </Typography>
                                </Box>
                                <Typography variant="body2" fontWeight="medium">
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
          <Alert severity="info" sx={{ mt: 4 }}>
            <Typography variant="body2">
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
