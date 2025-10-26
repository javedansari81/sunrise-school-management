/**
 * Configuration Context (Service-Aware)
 * Provides service-specific configuration data to React components
 * Manages loading state and error handling for multiple services
 */

import React, { createContext, useContext, useEffect, useState, ReactNode, useMemo, useCallback } from 'react';
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
  serviceLoadingStates: Record<ServiceType, boolean>;
  serviceErrors: Record<ServiceType, string | null>;

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
  getGalleryCategories: () => DropdownOption[];
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

  // Service-specific states - use objects instead of Maps for better React integration
  const [serviceLoadingStates, setServiceLoadingStates] = useState<Record<ServiceType, boolean>>({
    'fee-management': false,
    'student-management': false,
    'leave-management': false,
    'expense-management': false,
    'teacher-management': false,
    'gallery-management': false,
    'common': false,
  });
  const [serviceErrors, setServiceErrors] = useState<Record<ServiceType, string | null>>({
    'fee-management': null,
    'student-management': null,
    'leave-management': null,
    'expense-management': null,
    'teacher-management': null,
    'gallery-management': null,
    'common': null,
  });

  const loadConfiguration = useCallback(async () => {
    if (isLoading) return; // Prevent multiple simultaneous loads

    setIsLoading(true);
    setError(null);

    try {
      // DEPRECATED: Legacy configuration loading is no longer supported
      // Service-specific configuration loading should be used instead
      console.warn('⚠️ DEPRECATED: loadConfiguration() is deprecated. Use loadServiceConfiguration() instead.');
      throw new Error('Legacy configuration loading is deprecated. Use service-specific configuration loading instead.');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load configuration';
      setError(errorMessage);
      console.error('❌ Configuration loading failed:', errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const loadServiceConfiguration = useCallback(async (service: ServiceType) => {
    if (serviceLoadingStates[service]) return; // Prevent multiple simultaneous loads

    console.log(`🔄 Starting ${service} configuration load in context`);
    setServiceLoadingStates(prev => ({ ...prev, [service]: true }));
    setServiceErrors(prev => ({ ...prev, [service]: null }));

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
      setServiceErrors(prev => ({ ...prev, [service]: errorMessage }));
      console.error(`❌ ${service} configuration loading failed:`, {
        service,
        error: errorMessage,
        timestamp: new Date().toISOString()
      });
    } finally {
      setServiceLoadingStates(prev => ({ ...prev, [service]: false }));
    }
  }, [serviceLoadingStates]);

  const refreshConfiguration = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // DEPRECATED: Legacy configuration refresh is no longer supported
      // Service-specific configuration refresh should be used instead
      console.warn('⚠️ DEPRECATED: refreshConfiguration() is deprecated. Use refreshServiceConfiguration() instead.');
      throw new Error('Legacy configuration refresh is deprecated. Use service-specific configuration refresh instead.');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to refresh configuration';
      setError(errorMessage);
      console.error('❌ Configuration refresh failed:', errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshServiceConfiguration = useCallback(async (service: ServiceType) => {
    setServiceLoadingStates(prev => ({ ...prev, [service]: true }));
    setServiceErrors(prev => ({ ...prev, [service]: null }));

    try {
      await configurationService.refreshServiceConfiguration(service);
      console.log(`✅ ${service} configuration refreshed`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to refresh ${service} configuration`;
      setServiceErrors(prev => ({ ...prev, [service]: errorMessage }));
      console.error(`❌ ${service} configuration refresh failed:`, errorMessage);
    } finally {
      setServiceLoadingStates(prev => ({ ...prev, [service]: false }));
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearServiceError = useCallback((service: ServiceType) => {
    setServiceErrors(prev => ({ ...prev, [service]: null }));
  }, []);

  // Service state helpers
  const isServiceLoaded = useCallback((service: ServiceType) => {
    return configurationService.isServiceConfigurationLoaded(service);
  }, []);

  const isServiceLoading = useCallback((service: ServiceType) => {
    return serviceLoadingStates[service] || false;
  }, [serviceLoadingStates]);

  const getServiceError = useCallback((service: ServiceType) => {
    return serviceErrors[service] || null;
  }, [serviceErrors]);

  const getServiceConfiguration = useCallback((service: ServiceType) => {
    return configurationService.getServiceConfiguration(service);
  }, []);

  // Helper methods that delegate to the service
  const getUserTypes = useCallback(() => configurationService.getUserTypes(), []);
  const getSessionYears = useCallback(() => configurationService.getSessionYears(), []);
  const getCurrentSessionYear = useCallback(() => configurationService.getCurrentSessionYear(), []);
  const getGenders = useCallback(() => configurationService.getGenders(), []);
  const getClasses = useCallback(() => configurationService.getClasses(), []);
  const getPaymentTypes = useCallback(() => configurationService.getPaymentTypes(), []);
  const getPaymentStatuses = useCallback(() => configurationService.getPaymentStatuses(), []);
  const getPaymentMethods = useCallback(() => configurationService.getPaymentMethods(), []);
  const getLeaveTypes = useCallback(() => configurationService.getLeaveTypes(), []);
  const getLeaveStatuses = useCallback(() => configurationService.getLeaveStatuses(), []);
  const getExpenseCategories = useCallback(() => configurationService.getExpenseCategories(), []);
  const getExpenseStatuses = useCallback(() => configurationService.getExpenseStatuses(), []);
  const getEmploymentStatuses = useCallback(() => configurationService.getEmploymentStatuses(), []);
  const getQualifications = useCallback(() => configurationService.getQualifications(), []);
  const getGalleryCategories = useCallback(() => configurationService.getGalleryCategories(), []);

  // Auto-load configuration on mount (DISABLED - Use service-specific loading instead)
  useEffect(() => {
    if (autoLoad) {
      // DEPRECATED: Auto-loading legacy configuration is disabled
      // Service-specific configurations are loaded on-demand by individual components
      console.log('ℹ️ Auto-load configuration disabled. Use service-specific configuration loading instead.');
    }
  }, [autoLoad]);

  const contextValue: ConfigurationContextType = useMemo(() => ({
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
    getGalleryCategories,
  }), [
    configuration,
    isLoading,
    error,
    serviceLoadingStates,
    serviceErrors,
    loadConfiguration,
    loadServiceConfiguration,
    refreshConfiguration,
    refreshServiceConfiguration,
    clearError,
    clearServiceError,
    isServiceLoaded,
    isServiceLoading,
    getServiceError,
    getServiceConfiguration,
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
    getGalleryCategories,
  ]);

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
 * @deprecated This hook is deprecated. Use service-specific configuration loading instead.
 */
export const useDropdownOptions = (type: 'userTypes' | 'sessionYears' | 'genders' | 'classes' | 'paymentTypes' | 'paymentStatuses' | 'paymentMethods' | 'leaveTypes' | 'leaveStatuses' | 'expenseCategories' | 'expenseStatuses' | 'employmentStatuses' | 'qualifications'): DropdownOption[] => {
  console.warn('⚠️ DEPRECATED: useDropdownOptions() is deprecated. Use service-specific configuration loading instead.');

  // Return empty array to avoid breaking existing components
  return [];
};

/**
 * Hook to check if configuration is ready
 * @deprecated This hook is deprecated. Use useServiceConfigurationReady() instead.
 */
export const useConfigurationReady = (): boolean => {
  console.warn('⚠️ DEPRECATED: useConfigurationReady() is deprecated. Use useServiceConfigurationReady() instead.');
  return false;
};

/**
 * Hook to load and use service-specific configuration
 */
export const useServiceConfiguration = (service: ServiceType) => {
  const context = useContext(ConfigurationContext);
  if (context === undefined) {
    throw new Error('useServiceConfiguration must be used within a ConfigurationProvider');
  }

  // Extract the functions we need directly from context (avoid deprecated useConfiguration)
  const {
    isServiceLoaded,
    isServiceLoading,
    getServiceError,
    loadServiceConfiguration,
    refreshServiceConfiguration,
    clearServiceError
  } = context;

  useEffect(() => {
    console.log(`🔧 useServiceConfiguration [${service}] effect running:`, {
      isLoaded: isServiceLoaded(service),
      isLoading: isServiceLoading(service),
      timestamp: new Date().toISOString()
    });

    if (!isServiceLoaded(service) && !isServiceLoading(service)) {
      console.log(`🚀 Triggering load for ${service}`);
      loadServiceConfiguration(service);
    }
  }, [service, isServiceLoaded, isServiceLoading, loadServiceConfiguration]);

  return {
    isLoaded: isServiceLoaded(service),
    isLoading: isServiceLoading(service),
    error: getServiceError(service),
    refresh: () => refreshServiceConfiguration(service),
    clearError: () => clearServiceError(service),
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
