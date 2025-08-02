/**
 * Configuration Context (Service-Aware)
 * Provides service-specific configuration data to React components
 * Manages loading state and error handling for multiple services
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import {
  Configuration,
  DropdownOption,
  ServiceType,
  configurationService
} from '../services/configurationService';

interface ConfigurationContextType {
  // Configuration data
  configuration: Configuration | null; // Legacy full configuration

  // Loading states
  isLoading: boolean;
  isLoaded: boolean;
  error: string | null;

  // Service-specific states
  serviceLoadingStates: Map<ServiceType, boolean>;
  serviceErrors: Map<ServiceType, string | null>;

  // Actions
  loadConfiguration: () => Promise<void>; // Legacy method
  loadServiceConfiguration: (service: ServiceType) => Promise<void>;
  refreshConfiguration: () => Promise<void>; // Legacy method
  refreshServiceConfiguration: (service: ServiceType) => Promise<void>;
  clearError: () => void;
  clearServiceError: (service: ServiceType) => void;

  // Service state helpers
  isServiceLoaded: (service: ServiceType) => boolean;
  isServiceLoading: (service: ServiceType) => boolean;
  getServiceError: (service: ServiceType) => string | null;
  getServiceConfiguration: (service: ServiceType) => Configuration | null;

  // Helper methods for dropdown options (service-aware)
  getUserTypes: () => DropdownOption[];
  getSessionYears: () => DropdownOption[];
  getCurrentSessionYear: () => any;
  getGenders: () => DropdownOption[];
  getClasses: () => DropdownOption[];
  getPaymentTypes: () => DropdownOption[];
  getPaymentStatuses: () => DropdownOption[];
  getPaymentMethods: () => DropdownOption[];
  getLeaveTypes: () => DropdownOption[];
  getLeaveStatuses: () => DropdownOption[];
  getExpenseCategories: () => DropdownOption[];
  getExpenseStatuses: () => DropdownOption[];
  getEmploymentStatuses: () => DropdownOption[];
  getQualifications: () => DropdownOption[];
}

const ConfigurationContext = createContext<ConfigurationContextType | undefined>(undefined);

interface ConfigurationProviderProps {
  children: ReactNode;
  autoLoad?: boolean; // Whether to automatically load configuration on mount
}

export const ConfigurationProvider: React.FC<ConfigurationProviderProps> = ({
  children,
  autoLoad = true
}) => {
  const [configuration, setConfiguration] = useState<Configuration | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Service-specific states
  const [serviceLoadingStates] = useState<Map<ServiceType, boolean>>(new Map());
  const [serviceErrors] = useState<Map<ServiceType, string | null>>(new Map());

  const loadConfiguration = async () => {
    if (isLoading) return; // Prevent multiple simultaneous loads

    setIsLoading(true);
    setError(null);

    try {
      const config = await configurationService.loadConfiguration();
      setConfiguration(config);
      console.log('✅ Configuration loaded in context');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load configuration';
      setError(errorMessage);
      console.error('❌ Configuration loading failed:', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const loadServiceConfiguration = async (service: ServiceType) => {
    if (serviceLoadingStates.get(service)) return; // Prevent multiple simultaneous loads

    console.log(`🔄 Starting ${service} configuration load in context`);
    serviceLoadingStates.set(service, true);
    serviceErrors.set(service, null);

    try {
      // Add timeout to prevent hanging
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error(`Configuration loading timeout for ${service}`)), 30000);
      });

      const configPromise = configurationService.loadServiceConfiguration(service);
      await Promise.race([configPromise, timeoutPromise]);

      console.log(`✅ ${service} configuration loaded in context`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to load ${service} configuration`;
      serviceErrors.set(service, errorMessage);
      console.error(`❌ ${service} configuration loading failed:`, {
        service,
        error: errorMessage,
        timestamp: new Date().toISOString()
      });
    } finally {
      serviceLoadingStates.set(service, false);
    }
  };

  const refreshConfiguration = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const config = await configurationService.refreshConfiguration();
      setConfiguration(config);
      console.log('✅ Configuration refreshed');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to refresh configuration';
      setError(errorMessage);
      console.error('❌ Configuration refresh failed:', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshServiceConfiguration = async (service: ServiceType) => {
    serviceLoadingStates.set(service, true);
    serviceErrors.set(service, null);

    try {
      await configurationService.refreshServiceConfiguration(service);
      console.log(`✅ ${service} configuration refreshed`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to refresh ${service} configuration`;
      serviceErrors.set(service, errorMessage);
      console.error(`❌ ${service} configuration refresh failed:`, errorMessage);
    } finally {
      serviceLoadingStates.set(service, false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const clearServiceError = (service: ServiceType) => {
    serviceErrors.set(service, null);
  };

  // Service state helpers
  const isServiceLoaded = (service: ServiceType) => {
    return configurationService.isServiceConfigurationLoaded(service);
  };

  const isServiceLoading = (service: ServiceType) => {
    return serviceLoadingStates.get(service) || false;
  };

  const getServiceError = (service: ServiceType) => {
    return serviceErrors.get(service) || null;
  };

  const getServiceConfiguration = (service: ServiceType) => {
    return configurationService.getServiceConfiguration(service);
  };

  // Helper methods that delegate to the service
  const getUserTypes = () => configurationService.getUserTypes();
  const getSessionYears = () => configurationService.getSessionYears();
  const getCurrentSessionYear = () => configurationService.getCurrentSessionYear();
  const getGenders = () => configurationService.getGenders();
  const getClasses = () => configurationService.getClasses();
  const getPaymentTypes = () => configurationService.getPaymentTypes();
  const getPaymentStatuses = () => configurationService.getPaymentStatuses();
  const getPaymentMethods = () => configurationService.getPaymentMethods();
  const getLeaveTypes = () => configurationService.getLeaveTypes();
  const getLeaveStatuses = () => configurationService.getLeaveStatuses();
  const getExpenseCategories = () => configurationService.getExpenseCategories();
  const getExpenseStatuses = () => configurationService.getExpenseStatuses();
  const getEmploymentStatuses = () => configurationService.getEmploymentStatuses();
  const getQualifications = () => configurationService.getQualifications();

  // Auto-load configuration on mount
  useEffect(() => {
    if (autoLoad) {
      loadConfiguration();
    }
  }, [autoLoad]);

  const contextValue: ConfigurationContextType = {
    // Configuration data
    configuration,

    // Loading states
    isLoading,
    isLoaded: configuration !== null,
    error,

    // Service-specific states
    serviceLoadingStates,
    serviceErrors,

    // Actions
    loadConfiguration,
    loadServiceConfiguration,
    refreshConfiguration,
    refreshServiceConfiguration,
    clearError,
    clearServiceError,

    // Service state helpers
    isServiceLoaded,
    isServiceLoading,
    getServiceError,
    getServiceConfiguration,

    // Helper methods (service-aware)
    getUserTypes,
    getSessionYears,
    getCurrentSessionYear,
    getGenders,
    getClasses,
    getPaymentTypes,
    getPaymentStatuses,
    getPaymentMethods,
    getLeaveTypes,
    getLeaveStatuses,
    getExpenseCategories,
    getExpenseStatuses,
    getEmploymentStatuses,
    getQualifications,
  };

  return (
    <ConfigurationContext.Provider value={contextValue}>
      {children}
    </ConfigurationContext.Provider>
  );
};

/**
 * Hook to use configuration context (DEPRECATED)
 *
 * ⚠️ DEPRECATED: This hook is deprecated in favor of useServiceConfiguration
 *
 * Use useServiceConfiguration instead for better performance:
 * - 60-80% smaller payload sizes
 * - Faster loading times
 * - Only loads relevant metadata per service
 *
 * @deprecated Use useServiceConfiguration(service) instead
 */
export const useConfiguration = (): ConfigurationContextType => {
  const context = useContext(ConfigurationContext);
  if (context === undefined) {
    throw new Error('useConfiguration must be used within a ConfigurationProvider');
  }

  // Show deprecation warning (only once per component)
  React.useEffect(() => {
    console.warn('⚠️ DEPRECATED: useConfiguration() is deprecated. Use useServiceConfiguration(service) instead for better performance.');
  }, []);

  return context;
};

/**
 * Hook to get dropdown options for a specific metadata type
 */
export const useDropdownOptions = (type: 'userTypes' | 'sessionYears' | 'genders' | 'classes' | 'paymentTypes' | 'paymentStatuses' | 'paymentMethods' | 'leaveTypes' | 'leaveStatuses' | 'expenseCategories' | 'expenseStatuses' | 'employmentStatuses' | 'qualifications'): DropdownOption[] => {
  const config = useConfiguration();
  
  switch (type) {
    case 'userTypes': return config.getUserTypes();
    case 'sessionYears': return config.getSessionYears();
    case 'genders': return config.getGenders();
    case 'classes': return config.getClasses();
    case 'paymentTypes': return config.getPaymentTypes();
    case 'paymentStatuses': return config.getPaymentStatuses();
    case 'paymentMethods': return config.getPaymentMethods();
    case 'leaveTypes': return config.getLeaveTypes();
    case 'leaveStatuses': return config.getLeaveStatuses();
    case 'expenseCategories': return config.getExpenseCategories();
    case 'expenseStatuses': return config.getExpenseStatuses();
    case 'employmentStatuses': return config.getEmploymentStatuses();
    case 'qualifications': return config.getQualifications();
    default: return [];
  }
};

/**
 * Hook to check if configuration is ready
 */
export const useConfigurationReady = (): boolean => {
  const { isLoaded, error } = useConfiguration();
  return isLoaded && !error;
};

/**
 * Hook to load and use service-specific configuration
 */
export const useServiceConfiguration = (service: ServiceType) => {
  const context = useConfiguration();

  useEffect(() => {
    if (!context.isServiceLoaded(service) && !context.isServiceLoading(service)) {
      context.loadServiceConfiguration(service);
    }
  }, [service, context]);

  return {
    isLoaded: context.isServiceLoaded(service),
    isLoading: context.isServiceLoading(service),
    error: context.getServiceError(service),
    refresh: () => context.refreshServiceConfiguration(service),
    clearError: () => context.clearServiceError(service),
  };
};

/**
 * Hook to check if service configuration is ready
 */
export const useServiceConfigurationReady = (service: ServiceType): boolean => {
  const { isLoaded, error } = useServiceConfiguration(service);
  return isLoaded && !error;
};

// Re-export ServiceType for convenience
export type { ServiceType };

export default ConfigurationContext;
