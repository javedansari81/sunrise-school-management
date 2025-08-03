/**
 * Debug component to investigate Fee Management configuration loading issue
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { configurationAPI } from '../../services/configurationService';

const FeeManagementDebug: React.FC = () => {
  const { isLoading, isLoaded, error, refresh, clearError } = useServiceConfiguration('fee-management');
  const [debugInfo, setDebugInfo] = useState<any[]>([]);
  const [apiTestResult, setApiTestResult] = useState<string>('');

  // Track state changes
  useEffect(() => {
    const timestamp = new Date().toISOString();
    const newEntry = {
      timestamp,
      isLoading,
      isLoaded,
      error,
      action: 'State Change'
    };
    
    setDebugInfo(prev => [...prev, newEntry]);
    
    console.log('🔍 Fee Management Debug State:', newEntry);
  }, [isLoading, isLoaded, error]);

  // Test direct API call
  const testDirectAPI = async () => {
    setApiTestResult('Testing...');
    try {
      const response = await configurationAPI.getFeeManagementConfiguration();
      setApiTestResult(`✅ Success: ${JSON.stringify(response.data).substring(0, 100)}...`);
    } catch (err: any) {
      setApiTestResult(`❌ Error: ${err.message}`);
    }
  };

  // Clear debug log
  const clearDebugLog = () => {
    setDebugInfo([]);
  };

  const getStatusColor = (isLoading: boolean, isLoaded: boolean, error: string | null) => {
    if (error) return 'error';
    if (isLoading) return 'warning';
    if (isLoaded) return 'success';
    return 'default';
  };

  const getStatusText = (isLoading: boolean, isLoaded: boolean, error: string | null) => {
    if (error) return `Error: ${error}`;
    if (isLoading) return 'Loading';
    if (isLoaded) return 'Loaded';
    return 'Not Started';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Fee Management Configuration Debug
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        This debug component helps investigate the configuration loading issue.
        Status: Loading={isLoading ? 'Yes' : 'No'}, Loaded={isLoaded ? 'Yes' : 'No'}, Error={error ? 'Yes' : 'No'}
      </Alert>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button variant="contained" onClick={refresh} startIcon={<Refresh />}>
          Refresh Configuration
        </Button>
        <Button variant="outlined" onClick={testDirectAPI}>
          Test Direct API Call
        </Button>
        <Button variant="outlined" onClick={clearDebugLog}>
          Clear Debug Log
        </Button>
        {error && (
          <Button variant="outlined" color="error" onClick={clearError}>
            Clear Error
          </Button>
        )}
      </Box>

      {apiTestResult && (
        <Alert severity={apiTestResult.includes('✅') ? 'success' : 'error'} sx={{ mb: 3 }}>
          <Typography variant="subtitle2">Direct API Test Result:</Typography>
          <Typography variant="body2">{apiTestResult}</Typography>
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current State
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip 
              label={`Loading: ${isLoading ? 'Yes' : 'No'}`}
              color={isLoading ? 'warning' : 'default'}
            />
            <Chip 
              label={`Loaded: ${isLoaded ? 'Yes' : 'No'}`}
              color={isLoaded ? 'success' : 'default'}
            />
            <Chip 
              label={`Error: ${error ? 'Yes' : 'No'}`}
              color={error ? 'error' : 'default'}
            />
          </Box>
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            State Change Log ({debugInfo.length} entries)
          </Typography>
          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Loading</TableCell>
                  <TableCell>Loaded</TableCell>
                  <TableCell>Error</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {debugInfo.slice(-20).reverse().map((entry, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={entry.isLoading ? 'Yes' : 'No'}
                        size="small"
                        color={entry.isLoading ? 'warning' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={entry.isLoaded ? 'Yes' : 'No'}
                        size="small"
                        color={entry.isLoaded ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={entry.error ? 'Yes' : 'No'}
                        size="small"
                        color={entry.error ? 'error' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={getStatusText(entry.isLoading, entry.isLoaded, entry.error)}
                        size="small"
                        color={getStatusColor(entry.isLoading, entry.isLoaded, entry.error)}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default FeeManagementDebug;
