/**
 * Configuration Loader Component (DEPRECATED)
 *
 * ⚠️ DEPRECATED: This component is deprecated in favor of ServiceConfigurationLoader
 *
 * Use ServiceConfigurationLoader instead for better performance:
 * - 60-80% smaller payload sizes
 * - Faster loading times
 * - Only loads relevant metadata per service
 *
 * Migration:
 * OLD: <ConfigurationLoader><MyComponent /></ConfigurationLoader>
 * NEW: <ServiceConfigurationLoader service="service-name"><MyComponent /></ServiceConfigurationLoader>
 */

import React from 'react';
import {
  Box,
  CircularProgress,
  Typography,
  Alert,
  Button,
  Paper,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { useConfiguration } from '../../contexts/ConfigurationContext';

interface ConfigurationLoaderProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showError?: boolean;
}

const ConfigurationLoader: React.FC<ConfigurationLoaderProps> = ({
  children,
  fallback,
  showError = true,
}) => {
  // Show deprecation warning
  React.useEffect(() => {
    console.warn('⚠️ DEPRECATED: ConfigurationLoader is deprecated. Use ServiceConfigurationLoader instead for better performance.');
  }, []);

  const { isLoading, isLoaded, error, refreshConfiguration, clearError } = useConfiguration();

  // Show loading state
  if (isLoading && !isLoaded) {
    return (
      <>
        {fallback || (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '400px',
              gap: 2,
            }}
          >
            <CircularProgress size={40} />
            <Typography variant="h6" color="text.secondary">
              Loading configuration...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Please wait while we load the application settings
            </Typography>
          </Box>
        )}
      </>
    );
  }

  // Show error state
  if (error && showError) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          gap: 2,
          p: 3,
        }}
      >
        <Paper elevation={3} sx={{ p: 3, maxWidth: 500, textAlign: 'center' }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Configuration Error
            </Typography>
            <Typography variant="body2">
              {error}
            </Typography>
          </Alert>

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={refreshConfiguration}
              disabled={isLoading}
            >
              {isLoading ? 'Retrying...' : 'Retry'}
            </Button>
            <Button
              variant="outlined"
              onClick={clearError}
            >
              Continue Anyway
            </Button>
          </Box>
        </Paper>
      </Box>
    );
  }

  // Show children when loaded successfully
  return <>{children}</>;
};

export default ConfigurationLoader;

// Higher-order component version
export const withConfigurationLoader = <P extends object>(
  Component: React.ComponentType<P>,
  loaderProps?: Omit<ConfigurationLoaderProps, 'children'>
) => {
  return (props: P) => (
    <ConfigurationLoader {...loaderProps}>
      <Component {...props} />
    </ConfigurationLoader>
  );
};

// Hook for conditional rendering based on configuration state
export const useConfigurationState = () => {
  const { isLoading, isLoaded, error } = useConfiguration();
  
  return {
    isLoading: isLoading && !isLoaded,
    isReady: isLoaded && !error,
    hasError: !!error,
    shouldShowLoader: isLoading && !isLoaded,
    shouldShowError: !!error,
    shouldShowContent: isLoaded && !error,
  };
};
