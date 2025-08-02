/**
 * Service Configuration Loader Component
 * Loads service-specific configuration and provides loading states
 */

import React, { ReactNode } from 'react';
import {
  Box,
  CircularProgress,
  Typography,
  Alert,
  Button,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { ServiceType, useServiceConfiguration } from '../../contexts/ConfigurationContext';

interface ServiceConfigurationLoaderProps {
  service: ServiceType;
  children: ReactNode;
  fallback?: ReactNode;
  showError?: boolean;
}

const ServiceConfigurationLoader: React.FC<ServiceConfigurationLoaderProps> = ({
  service,
  children,
  fallback,
  showError = true,
}) => {
  const { isLoading, isLoaded, error, refresh, clearError } = useServiceConfiguration(service);

  // Debug logging
  React.useEffect(() => {
    console.log(`🔧 ServiceConfigurationLoader [${service}]:`, {
      isLoading,
      isLoaded,
      error,
      timestamp: new Date().toISOString()
    });

    // Log the decision path
    if (isLoading) {
      console.log(`⏳ [${service}] Showing loading state`);
    } else if (error) {
      console.log(`❌ [${service}] Showing error state: ${error}`);
    } else if (isLoaded) {
      console.log(`✅ [${service}] Showing loaded content`);
    } else {
      console.log(`⚠️ [${service}] Showing fallback state (not loading, not loaded, no error)`);
    }
  }, [service, isLoading, isLoaded, error]);

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
              minHeight: '200px',
              gap: 2,
            }}
          >
            <CircularProgress size={40} />
            <Typography variant="h6" color="text.secondary">
              Loading {service.replace('-', ' ')} configuration...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Please wait while we load the required settings
            </Typography>
          </Box>
        )}
      </>
    );
  }

  // Show error state
  if (error && showError) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert 
          severity="error" 
          action={
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                color="inherit"
                size="small"
                onClick={clearError}
              >
                Dismiss
              </Button>
              <Button
                color="inherit"
                size="small"
                onClick={refresh}
                startIcon={<Refresh />}
              >
                Retry
              </Button>
            </Box>
          }
        >
          <Typography variant="subtitle2">
            Failed to load {service.replace('-', ' ')} configuration
          </Typography>
          <Typography variant="body2">
            {error}
          </Typography>
        </Alert>
      </Box>
    );
  }

  // Show content when loaded successfully
  if (isLoaded) {
    return <>{children}</>;
  }

  // Fallback state - this should rarely happen
  return (
    <Box sx={{ p: 2 }}>
      <Alert severity="warning" sx={{ mb: 2 }}>
        <Typography variant="subtitle2">
          Configuration Loading Issue
        </Typography>
        <Typography variant="body2">
          The {service.replace('-', ' ')} configuration is not loading properly.
        </Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          Status: Loading={isLoading ? 'Yes' : 'No'}, Loaded={isLoaded ? 'Yes' : 'No'}, Error={error ? 'Yes' : 'No'}
        </Typography>
      </Alert>
      <Button
        variant="outlined"
        onClick={refresh}
        startIcon={<Refresh />}
        size="small"
      >
        Try Loading Again
      </Button>
    </Box>
  );
};

// Hook for conditional rendering based on service configuration state
export const useServiceConfigurationState = (service: ServiceType) => {
  const { isLoading, isLoaded, error } = useServiceConfiguration(service);
  
  return {
    isLoading: isLoading && !isLoaded,
    isReady: isLoaded && !error,
    hasError: !!error,
    shouldShowLoader: isLoading && !isLoaded,
    shouldShowError: !!error,
    shouldShowContent: isLoaded && !error,
  };
};

export default ServiceConfigurationLoader;
