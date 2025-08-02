/**
 * Service Configuration Test Component
 * Tests and validates service-specific configuration loading
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  ExpandMore,
  Refresh,
  CheckCircle,
  Error,
  Info,
} from '@mui/icons-material';
import {
  ServiceType,
  useServiceConfiguration,
  useConfiguration,
} from '../../contexts/ConfigurationContext';

const SERVICE_TYPES: ServiceType[] = [
  'fee-management',
  'student-management',
  'leave-management',
  'expense-management',
  'teacher-management',
  'common',
];

const ServiceConfigurationTest: React.FC = () => {
  const [selectedService, setSelectedService] = useState<ServiceType>('fee-management');
  const legacyConfig = useConfiguration();

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Service Configuration Test
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        Test and validate service-specific configuration loading performance
      </Typography>

      {/* Legacy Configuration Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Legacy Configuration Status
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            {legacyConfig.isLoaded ? (
              <Chip icon={<CheckCircle />} label="Loaded" color="success" />
            ) : legacyConfig.isLoading ? (
              <Chip icon={<CircularProgress size={16} />} label="Loading" color="warning" />
            ) : (
              <Chip icon={<Error />} label="Not Loaded" color="error" />
            )}
            <Button
              size="small"
              startIcon={<Refresh />}
              onClick={legacyConfig.refreshConfiguration}
              disabled={legacyConfig.isLoading}
            >
              Refresh Legacy
            </Button>
          </Box>
          {legacyConfig.configuration && (
            <Typography variant="body2" color="textSecondary">
              Total metadata types: {Object.keys(legacyConfig.configuration).filter(k => k !== 'metadata').length}
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Service Selection */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Test Service-Specific Configuration
          </Typography>
          <Grid container spacing={1}>
            {SERVICE_TYPES.map((service) => (
              <Grid size="auto" key={service}>
                <Button
                  variant={selectedService === service ? 'contained' : 'outlined'}
                  onClick={() => setSelectedService(service)}
                  size="small"
                >
                  {service.replace('-', ' ')}
                </Button>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Service Configuration Details */}
      <ServiceConfigurationDetails service={selectedService} />

      {/* Performance Comparison */}
      <PerformanceComparison />
    </Box>
  );
};

interface ServiceConfigurationDetailsProps {
  service: ServiceType;
}

const ServiceConfigurationDetails: React.FC<ServiceConfigurationDetailsProps> = ({ service }) => {
  const { isLoaded, isLoading, error, refresh } = useServiceConfiguration(service);
  const config = useConfiguration();
  const serviceConfig = config.getServiceConfiguration(service);

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            {service.replace('-', ' ')} Configuration
          </Typography>
          <Button
            size="small"
            startIcon={<Refresh />}
            onClick={refresh}
            disabled={isLoading}
          >
            Refresh
          </Button>
        </Box>

        {/* Status */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          {isLoaded ? (
            <Chip icon={<CheckCircle />} label="Loaded" color="success" />
          ) : isLoading ? (
            <Chip icon={<CircularProgress size={16} />} label="Loading" color="warning" />
          ) : (
            <Chip icon={<Error />} label="Not Loaded" color="error" />
          )}
        </Box>

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Configuration Details */}
        {serviceConfig && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Configuration Details</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Metadata Type</TableCell>
                      <TableCell align="right">Count</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(serviceConfig)
                      .filter(([key]) => key !== 'metadata')
                      .map(([key, value]) => (
                        <TableRow key={key}>
                          <TableCell>{key}</TableCell>
                          <TableCell align="right">
                            {Array.isArray(value) ? value.length : 'N/A'}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              {serviceConfig.metadata && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Metadata Info:
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Service: {serviceConfig.metadata.service}<br />
                    Version: {serviceConfig.metadata.version}<br />
                    Architecture: {serviceConfig.metadata.architecture}<br />
                    Types: {serviceConfig.metadata.metadata_types?.join(', ')}
                  </Typography>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        )}
      </CardContent>
    </Card>
  );
};

const PerformanceComparison: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Performance Comparison
        </Typography>
        
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="subtitle2">Expected Performance Improvements:</Typography>
          <Typography variant="body2">
            • Payload Size: 60-80% reduction<br />
            • Load Time: 50-70% faster<br />
            • Memory Usage: Service-specific caching<br />
            • Network Efficiency: Only required metadata loaded
          </Typography>
        </Alert>

        <Typography variant="body2" color="textSecondary">
          Open browser DevTools → Network tab to see actual payload sizes and load times.
          Service-specific endpoints should show significantly smaller response sizes compared to the legacy /configuration/ endpoint.
        </Typography>
      </CardContent>
    </Card>
  );
};

export default ServiceConfigurationTest;
