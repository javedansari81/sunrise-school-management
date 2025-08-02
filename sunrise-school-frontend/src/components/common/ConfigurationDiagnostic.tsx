/**
 * Configuration Diagnostic Component
 * Helps debug configuration loading issues
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  Chip,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { ServiceType, useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { configurationAPI } from '../../services/configurationService';

interface ConfigurationDiagnosticProps {
  service: ServiceType;
}

const ConfigurationDiagnostic: React.FC<ConfigurationDiagnosticProps> = ({ service }) => {
  const { isLoading, isLoaded, error, refresh } = useServiceConfiguration(service);
  const [testResult, setTestResult] = useState<string>('');

  const testDirectAPI = async () => {
    setTestResult('Testing...');

    try {
      console.log(`🧪 Testing direct API call to /configuration/${service}/`);

      let response;
      switch (service) {
        case 'leave-management':
          response = await configurationAPI.getLeaveManagementConfiguration();
          break;
        case 'fee-management':
          response = await configurationAPI.getFeeManagementConfiguration();
          break;
        case 'student-management':
          response = await configurationAPI.getStudentManagementConfiguration();
          break;
        case 'expense-management':
          response = await configurationAPI.getExpenseManagementConfiguration();
          break;
        case 'teacher-management':
          response = await configurationAPI.getTeacherManagementConfiguration();
          break;
        case 'common':
          response = await configurationAPI.getCommonConfiguration();
          break;
        default:
          setTestResult(`Unknown service: ${service}`);
          return;
      }

      setTestResult(`✅ API Success: ${Object.keys(response.data).length} keys loaded`);
      console.log(`✅ Direct API test successful:`, response.data);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Unknown error';
      setTestResult(`❌ API Error: ${errorMsg}`);
      console.error(`❌ Direct API test failed:`, err);
    }
  };

  return (
    <Card sx={{ mb: 2, border: '2px solid #ff9800' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom color="warning.main">
          🔧 Configuration Diagnostic: {service}
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Service Configuration Hook Status:
          </Typography>
          <Chip
            label={
              isLoading ? 'Loading...' :
              error ? `Error: ${error}` :
              isLoaded ? 'Loaded Successfully' : 'Not Loaded'
            }
            color={
              isLoading ? 'info' :
              error ? 'error' :
              isLoaded ? 'success' : 'warning'
            }
            sx={{ mr: 1 }}
          />
          <Button
            size="small"
            onClick={refresh}
            startIcon={<Refresh />}
            disabled={isLoading}
            variant="outlined"
          >
            Retry Hook
          </Button>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Direct API Test:
          </Typography>
          <Button
            size="small"
            onClick={testDirectAPI}
            startIcon={<Refresh />}
            variant="outlined"
            sx={{ mr: 1 }}
          >
            Test API Directly
          </Button>
          {testResult && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              {testResult}
            </Typography>
          )}
        </Box>

        <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
          <Typography variant="body2">
            <strong>Debug Info:</strong> Loading={isLoading ? 'Yes' : 'No'},
            Loaded={isLoaded ? 'Yes' : 'No'},
            Error={error ? 'Yes' : 'No'}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            If the direct API test works but the hook fails, there's a React context issue.
            If both fail, there's a backend or network issue.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );
};

export default ConfigurationDiagnostic;
