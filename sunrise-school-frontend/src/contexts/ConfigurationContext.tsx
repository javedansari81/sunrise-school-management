/**
 * Configuration Context
 * Provides configuration data to React components
 * Manages loading state and error handling
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { 
  Configuration, 
  DropdownOption, 
  configurationService 
} from '../services/configurationService';

interface ConfigurationContextType {
  // Configuration data
  configuration: Configuration | null;
  
  // Loading states
  isLoading: boolean;
  isLoaded: boolean;
  error: string | null;
  
  // Actions
  loadConfiguration: () => Promise<void>;
  refreshConfiguration: () => Promise<void>;
  clearError: () => void;
  
  // Helper methods for dropdown options
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

  const clearError = () => {
    setError(null);
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
    
    // Actions
    loadConfiguration,
    refreshConfiguration,
    clearError,
    
    // Helper methods
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
 * Hook to use configuration context
 */
export const useConfiguration = (): ConfigurationContextType => {
  const context = useContext(ConfigurationContext);
  if (context === undefined) {
    throw new Error('useConfiguration must be used within a ConfigurationProvider');
  }
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

export default ConfigurationContext;
