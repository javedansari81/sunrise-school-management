/**
 * Configuration Service - Singleton Pattern (Service-Aware)
 * Manages service-specific metadata configuration from the backend API
 * Stores configurations in memory for the duration of user session
 * Optimized for reduced payload sizes and faster loading
 */

import api from './api';

// Configuration interfaces
export interface MetadataItem {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface UserType extends MetadataItem {}

export interface SessionYear extends MetadataItem {
  start_date?: string;
  end_date?: string;
  is_current: boolean;
}

export interface Gender extends MetadataItem {}

export interface Class extends MetadataItem {
  sort_order?: number;
}

export interface PaymentType extends MetadataItem {}

export interface PaymentStatus extends MetadataItem {
  color_code?: string;
}

export interface PaymentMethod extends MetadataItem {
  requires_reference: boolean;
}

export interface LeaveType extends MetadataItem {
  max_days_per_year?: number;
  requires_medical_certificate: boolean;
}

export interface LeaveStatus extends MetadataItem {
  color_code?: string;
  is_final: boolean;
}

export interface ExpenseCategory extends MetadataItem {
  budget_limit?: number;
  requires_approval: boolean;
}

export interface ExpenseStatus extends MetadataItem {
  color_code?: string;
  is_final: boolean;
}

export interface EmploymentStatus extends MetadataItem {}

export interface Qualification extends MetadataItem {
  level_order?: number;
}

export interface Department extends MetadataItem {}

export interface Position extends MetadataItem {}

export interface GalleryCategory extends MetadataItem {
  icon?: string;
  display_order?: number;
}

export interface Configuration {
  user_types?: UserType[];
  session_years?: SessionYear[];
  genders?: Gender[];
  classes?: Class[];
  payment_types?: PaymentType[];
  payment_statuses?: PaymentStatus[];
  payment_methods?: PaymentMethod[];
  leave_types?: LeaveType[];
  leave_statuses?: LeaveStatus[];
  expense_categories?: ExpenseCategory[];
  expense_statuses?: ExpenseStatus[];
  employment_statuses?: EmploymentStatus[];
  qualifications?: Qualification[];
  departments?: Department[];
  positions?: Position[];
  gallery_categories?: GalleryCategory[];
  metadata: {
    service?: string;
    last_updated?: string;
    version?: string;
    architecture?: string;
    metadata_types?: string[];
  };
}

// Service-specific configuration interfaces
export interface ServiceConfiguration extends Configuration {
  service: string;
}

// Service type definitions
export type ServiceType =
  | 'fee-management'
  | 'student-management'
  | 'leave-management'
  | 'expense-management'
  | 'teacher-management'
  | 'gallery-management'
  | 'common';

// Dropdown option interface for UI components
export interface DropdownOption {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
}

class ConfigurationService {
  private static instance: ConfigurationService;
  private configuration: Configuration | null = null; // Legacy full configuration
  private serviceConfigurations: Map<ServiceType, Configuration> = new Map(); // Service-specific configurations
  private isLoading = false;
  private serviceLoadingStates: Map<ServiceType, boolean> = new Map();
  private loadPromise: Promise<Configuration> | null = null;
  private serviceLoadPromises: Map<ServiceType, Promise<Configuration>> = new Map();

  private constructor() {}

  /**
   * Get singleton instance
   */
  public static getInstance(): ConfigurationService {
    if (!ConfigurationService.instance) {
      ConfigurationService.instance = new ConfigurationService();
    }
    return ConfigurationService.instance;
  }

  /**
   * Load service-specific configuration from API
   */
  public async loadServiceConfiguration(service: ServiceType): Promise<Configuration> {
    // If already loaded, return cached configuration
    if (this.serviceConfigurations.has(service)) {
      return this.serviceConfigurations.get(service)!;
    }

    // If currently loading, return the existing promise
    if (this.serviceLoadingStates.get(service) && this.serviceLoadPromises.has(service)) {
      return this.serviceLoadPromises.get(service)!;
    }

    // Start loading
    this.serviceLoadingStates.set(service, true);
    const loadPromise = this.fetchServiceConfiguration(service);
    this.serviceLoadPromises.set(service, loadPromise);

    try {
      const configuration = await loadPromise;
      this.serviceConfigurations.set(service, configuration);
      console.log(`✅ ${service} configuration loaded successfully:`, configuration.metadata);
      return configuration;
    } catch (error) {
      console.error(`❌ Failed to load ${service} configuration:`, error);
      throw error;
    } finally {
      this.serviceLoadingStates.set(service, false);
      this.serviceLoadPromises.delete(service);
    }
  }

  /**
   * Load configuration from API (DEPRECATED - Use loadServiceConfiguration instead)
   * @deprecated Use loadServiceConfiguration() with specific service names instead
   */
  public async loadConfiguration(): Promise<Configuration> {
    console.warn('⚠️ DEPRECATED: loadConfiguration() is deprecated. Use loadServiceConfiguration() instead.');
    throw new Error('Legacy configuration loading is deprecated. Use service-specific configuration loading instead.');
  }

  /**
   * Utility function to delay execution (for retry backoff)
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Check if an error is retryable
   */
  private isRetryableError(error: any): boolean {
    // Don't retry on client errors (4xx) except for specific cases
    if (error.response?.status >= 400 && error.response?.status < 500) {
      // Don't retry on authentication errors, not found, etc.
      return false;
    }

    // Retry on server errors (5xx)
    if (error.response?.status >= 500) {
      return true;
    }

    // Retry on network errors (no response received)
    if (!error.response && error.message === 'Network Error') {
      return true;
    }

    // Retry on timeout errors
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return true;
    }

    // Don't retry on session expired
    if (error.message === 'Session expired') {
      return false;
    }

    // Default: don't retry
    return false;
  }

  /**
   * Fetch service-specific configuration from API with retry logic
   */
  private async fetchServiceConfiguration(service: ServiceType): Promise<Configuration> {
    const MAX_RETRIES = 3;
    const BASE_DELAY_MS = 1000; // 1 second base delay
    let lastError: any;

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      try {
        console.log(`🔄 Fetching ${service} configuration from /configuration/${service}/ (attempt ${attempt}/${MAX_RETRIES})`);
        const response = await api.get(`/configuration/${service}/`);
        console.log(`✅ ${service} configuration fetched successfully:`, {
          status: response.status,
          dataKeys: Object.keys(response.data),
          metadata: response.data.metadata,
          attempt
        });
        return response.data;
      } catch (error: any) {
        lastError = error;

        console.error(`❌ Error fetching ${service} configuration (attempt ${attempt}/${MAX_RETRIES}):`, {
          error,
          errorMessage: error.message,
          errorName: error.name,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          url: `/configuration/${service}/`,
          hasResponse: !!error.response,
          isAxiosError: error.isAxiosError,
          code: error.code
        });

        // Check if we should retry
        const shouldRetry = this.isRetryableError(error);
        const isLastAttempt = attempt === MAX_RETRIES;

        if (!shouldRetry || isLastAttempt) {
          // Don't retry, throw error immediately
          console.error(`❌ Not retrying ${service} configuration load. shouldRetry: ${shouldRetry}, isLastAttempt: ${isLastAttempt}`);
          break;
        }

        // Calculate exponential backoff delay: 1s, 2s, 4s
        const delayMs = BASE_DELAY_MS * Math.pow(2, attempt - 1);
        console.warn(`⏳ Retrying ${service} configuration load in ${delayMs}ms... (attempt ${attempt + 1}/${MAX_RETRIES})`);
        await this.delay(delayMs);
      }
    }

    // All retries exhausted, throw final error with context
    const attemptText = MAX_RETRIES > 1 ? `after ${MAX_RETRIES} attempts` : '';

    // Provide more specific error messages
    if (lastError.response?.status === 404) {
      throw new Error(`${service} configuration endpoint not found. Please check if the service is properly configured.`);
    } else if (lastError.response?.status === 401) {
      throw new Error(`Authentication required to load ${service} configuration. Please login again.`);
    } else if (lastError.response?.status >= 500) {
      throw new Error(`Server error while loading ${service} configuration ${attemptText}. Please try again later.`);
    } else if (lastError.message === 'Session expired') {
      throw new Error(`Your session has expired. Please login again.`);
    } else if (lastError.code === 'ECONNABORTED' || lastError.message.includes('timeout')) {
      throw new Error(`Request timeout while loading ${service} configuration ${attemptText}. Please check your connection and try again.`);
    } else if (!lastError.response && lastError.message === 'Network Error') {
      throw new Error(`Network error while loading ${service} configuration ${attemptText}. Please check your internet connection and ensure the backend server is running.`);
    } else {
      throw new Error(`Failed to load ${service} configuration ${attemptText}: ${lastError.message}`);
    }
  }

  /**
   * Fetch configuration from API (DEPRECATED)
   * @deprecated This method is deprecated and will be removed
   */
  private async fetchConfiguration(): Promise<Configuration> {
    throw new Error('Legacy configuration fetching is deprecated. Use service-specific endpoints instead.');
  }

  /**
   * Get cached service configuration (returns null if not loaded)
   */
  public getServiceConfiguration(service: ServiceType): Configuration | null {
    return this.serviceConfigurations.get(service) || null;
  }

  /**
   * Get cached configuration (DEPRECATED - Use getServiceConfiguration instead)
   * @deprecated Use getServiceConfiguration() with specific service names instead
   */
  public getConfiguration(): Configuration | null {
    console.warn('⚠️ DEPRECATED: getConfiguration() is deprecated. Use getServiceConfiguration() instead.');
    return null;
  }

  /**
   * Force refresh service-specific configuration from API
   */
  public async refreshServiceConfiguration(service: ServiceType): Promise<Configuration> {
    this.serviceConfigurations.delete(service);
    return this.loadServiceConfiguration(service);
  }

  /**
   * Force refresh configuration from API (DEPRECATED - Use refreshServiceConfiguration instead)
   * @deprecated Use refreshServiceConfiguration() with specific service names instead
   */
  public async refreshConfiguration(): Promise<Configuration> {
    console.warn('⚠️ DEPRECATED: refreshConfiguration() is deprecated. Use refreshServiceConfiguration() instead.');
    throw new Error('Legacy configuration refresh is deprecated. Use service-specific configuration refresh instead.');
  }

  /**
   * Clear cached configurations (useful for logout)
   */
  public clearConfiguration(): void {
    this.configuration = null;
    this.serviceConfigurations.clear();
    this.serviceLoadingStates.clear();
    this.serviceLoadPromises.clear();
  }

  /**
   * Clear specific service configuration
   */
  public clearServiceConfiguration(service: ServiceType): void {
    this.serviceConfigurations.delete(service);
    this.serviceLoadingStates.delete(service);
    this.serviceLoadPromises.delete(service);
  }

  /**
   * Check if service configuration is loaded
   */
  public isServiceConfigurationLoaded(service: ServiceType): boolean {
    return this.serviceConfigurations.has(service);
  }

  /**
   * Check if service configuration is currently loading
   */
  public isServiceConfigurationLoading(service: ServiceType): boolean {
    return this.serviceLoadingStates.get(service) || false;
  }

  // Service-aware helper methods for getting specific metadata as dropdown options

  /**
   * Get metadata from service configurations or fallback to legacy
   */
  private getMetadataFromServices<T extends MetadataItem>(
    metadataKey: keyof Configuration
  ): T[] {
    // Try to get from any loaded service configuration
    const configs = Array.from(this.serviceConfigurations.values());
    for (const config of configs) {
      const metadata = config[metadataKey] as T[] | undefined;
      if (metadata && metadata.length > 0) {
        return metadata;
      }
    }

    // Fallback to legacy configuration
    return (this.configuration?.[metadataKey] as T[]) || [];
  }

  /**
   * Get user types as dropdown options (service-aware)
   */
  public getUserTypes(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<UserType>('user_types'));
  }

  /**
   * Get session years as dropdown options (service-aware)
   */
  public getSessionYears(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<SessionYear>('session_years'));
  }

  /**
   * Get current session year (service-aware)
   */
  public getCurrentSessionYear(): SessionYear | null {
    // Try to get from any loaded service configuration that has session_years
    const configs = Array.from(this.serviceConfigurations.values());
    for (const config of configs) {
      if (config.session_years) {
        const current = config.session_years.find((sy: SessionYear) => sy.is_current);
        if (current) return current;
      }
    }

    // Fallback to legacy configuration
    return this.configuration?.session_years?.find((sy: SessionYear) => sy.is_current) || null;
  }

  /**
   * Get genders as dropdown options (service-aware)
   */
  public getGenders(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<Gender>('genders'));
  }

  /**
   * Get classes as dropdown options (service-aware)
   */
  public getClasses(): DropdownOption[] {
    const classes = this.getMetadataFromServices<Class>('classes');
    return classes
      .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
      .map(cls => ({
        id: cls.id,
        name: cls.name,
        description: cls.description || cls.name,
        is_active: cls.is_active
      }));
  }

  /**
   * Get payment types as dropdown options (service-aware)
   */
  public getPaymentTypes(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<PaymentType>('payment_types'));
  }

  /**
   * Get payment statuses as dropdown options (service-aware)
   */
  public getPaymentStatuses(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<PaymentStatus>('payment_statuses'));
  }

  /**
   * Get payment methods as dropdown options (service-aware)
   */
  public getPaymentMethods(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<PaymentMethod>('payment_methods'));
  }

  /**
   * Get leave types as dropdown options
   */
  public getLeaveTypes(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<LeaveType>('leave_types'));
  }

  /**
   * Get leave statuses as dropdown options
   */
  public getLeaveStatuses(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<LeaveStatus>('leave_statuses'));
  }

  /**
   * Get expense categories as dropdown options
   */
  public getExpenseCategories(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<ExpenseCategory>('expense_categories'));
  }

  /**
   * Get expense statuses as dropdown options (service-aware)
   */
  public getExpenseStatuses(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<ExpenseStatus>('expense_statuses'));
  }

  /**
   * Get employment statuses as dropdown options (service-aware)
   */
  public getEmploymentStatuses(): DropdownOption[] {
    return this.getDropdownOptions(this.getMetadataFromServices<EmploymentStatus>('employment_statuses'));
  }

  /**
   * Get qualifications as dropdown options (service-aware)
   */
  public getQualifications(): DropdownOption[] {
    const qualifications = this.getMetadataFromServices<Qualification>('qualifications');
    return qualifications
      .sort((a, b) => (a.level_order || 0) - (b.level_order || 0))
      .map(qual => ({
        id: qual.id,
        name: qual.name,
        display_name: qual.name,
        is_active: qual.is_active
      }));
  }

  /**
   * Get gallery categories as dropdown options (service-aware)
   */
  public getGalleryCategories(): DropdownOption[] {
    const categories = this.getMetadataFromServices<GalleryCategory>('gallery_categories');
    return categories
      .sort((a, b) => (a.display_order || 0) - (b.display_order || 0))
      .map(cat => ({
        id: cat.id,
        name: cat.name,
        description: cat.description,
        display_name: cat.description || cat.name,
        is_active: cat.is_active
      }));
  }

  /**
   * Convert metadata items to dropdown options
   */
  private getDropdownOptions(items: MetadataItem[]): DropdownOption[] {
    return items
      .filter(item => item.is_active)
      .map(item => ({
        id: item.id,
        name: item.name,
        display_name: item.name,
        is_active: item.is_active
      }));
  }

  /**
   * Get metadata item by ID
   */
  public getMetadataById(type: keyof Configuration, id: number): MetadataItem | null {
    if (!this.configuration || !this.configuration[type]) {
      return null;
    }
    
    const items = this.configuration[type] as MetadataItem[];
    return items.find(item => item.id === id) || null;
  }

  /**
   * Check if configuration is loaded
   */
  public isConfigurationLoaded(): boolean {
    return this.configuration !== null;
  }
}

// Export singleton instance
export const configurationService = ConfigurationService.getInstance();

// Export API functions for configuration endpoints
export const configurationAPI = {
  // Service-specific endpoints (RECOMMENDED)
  getFeeManagementConfiguration: () => api.get('/configuration/fee-management/'),
  getStudentManagementConfiguration: () => api.get('/configuration/student-management/'),
  getLeaveManagementConfiguration: () => api.get('/configuration/leave-management/'),
  getExpenseManagementConfiguration: () => api.get('/configuration/expense-management/'),
  getTeacherManagementConfiguration: () => api.get('/configuration/teacher-management/'),
  getGalleryManagementConfiguration: () => api.get('/configuration/gallery-management/'),
  getCommonConfiguration: () => api.get('/configuration/common/'),

  // Service-specific refresh
  refreshServiceConfiguration: (service?: string) =>
    api.post('/configuration/refresh', null, { params: { service } }),

  // Get available services
  getAvailableServices: () => api.get('/configuration/services/'),

  // DEPRECATED: Legacy endpoints (will be removed)
  getConfiguration: () => {
    console.warn('⚠️ DEPRECATED: getConfiguration() is deprecated. Use service-specific endpoints instead.');
    return Promise.reject(new Error('This endpoint has been deprecated. Use service-specific configuration endpoints.'));
  },
  refreshConfiguration: () => {
    console.warn('⚠️ DEPRECATED: refreshConfiguration() is deprecated. Use refreshServiceConfiguration() instead.');
    return api.post('/configuration/refresh');
  },
};

export default configurationService;
