/**
 * Configuration Service - Singleton Pattern
 * Manages metadata configuration from the backend API
 * Stores configuration in memory for the duration of user session
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
  display_name?: string;
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

export interface Configuration {
  user_types: UserType[];
  session_years: SessionYear[];
  genders: Gender[];
  classes: Class[];
  payment_types: PaymentType[];
  payment_statuses: PaymentStatus[];
  payment_methods: PaymentMethod[];
  leave_types: LeaveType[];
  leave_statuses: LeaveStatus[];
  expense_categories: ExpenseCategory[];
  expense_statuses: ExpenseStatus[];
  employment_statuses: EmploymentStatus[];
  qualifications: Qualification[];
  metadata: {
    last_updated?: string;
    version?: string;
    architecture?: string;
  };
}

// Dropdown option interface for UI components
export interface DropdownOption {
  id: number;
  name: string;
  display_name?: string;
  is_active: boolean;
}

class ConfigurationService {
  private static instance: ConfigurationService;
  private configuration: Configuration | null = null;
  private isLoading = false;
  private loadPromise: Promise<Configuration> | null = null;

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
   * Load configuration from API
   */
  public async loadConfiguration(): Promise<Configuration> {
    // If already loaded, return cached configuration
    if (this.configuration) {
      return this.configuration;
    }

    // If currently loading, return the existing promise
    if (this.isLoading && this.loadPromise) {
      return this.loadPromise;
    }

    // Start loading
    this.isLoading = true;
    this.loadPromise = this.fetchConfiguration();

    try {
      this.configuration = await this.loadPromise;
      console.log('✅ Configuration loaded successfully:', this.configuration.metadata);
      return this.configuration;
    } catch (error) {
      console.error('❌ Failed to load configuration:', error);
      throw error;
    } finally {
      this.isLoading = false;
      this.loadPromise = null;
    }
  }

  /**
   * Fetch configuration from API
   */
  private async fetchConfiguration(): Promise<Configuration> {
    try {
      const response = await api.get('/configuration/');
      return response.data;
    } catch (error) {
      console.error('Error fetching configuration:', error);
      throw new Error('Failed to load application configuration');
    }
  }

  /**
   * Get cached configuration (returns null if not loaded)
   */
  public getConfiguration(): Configuration | null {
    return this.configuration;
  }

  /**
   * Force refresh configuration from API
   */
  public async refreshConfiguration(): Promise<Configuration> {
    this.configuration = null;
    return this.loadConfiguration();
  }

  /**
   * Clear cached configuration (useful for logout)
   */
  public clearConfiguration(): void {
    this.configuration = null;
  }

  // Helper methods for getting specific metadata as dropdown options

  /**
   * Get user types as dropdown options
   */
  public getUserTypes(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.user_types || []);
  }

  /**
   * Get session years as dropdown options
   */
  public getSessionYears(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.session_years || []);
  }

  /**
   * Get current session year
   */
  public getCurrentSessionYear(): SessionYear | null {
    return this.configuration?.session_years.find(sy => sy.is_current) || null;
  }

  /**
   * Get genders as dropdown options
   */
  public getGenders(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.genders || []);
  }

  /**
   * Get classes as dropdown options
   */
  public getClasses(): DropdownOption[] {
    const classes = this.configuration?.classes || [];
    return classes
      .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
      .map(cls => ({
        id: cls.id,
        name: cls.name,
        display_name: cls.display_name || cls.name,
        is_active: cls.is_active
      }));
  }

  /**
   * Get payment types as dropdown options
   */
  public getPaymentTypes(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.payment_types || []);
  }

  /**
   * Get payment statuses as dropdown options
   */
  public getPaymentStatuses(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.payment_statuses || []);
  }

  /**
   * Get payment methods as dropdown options
   */
  public getPaymentMethods(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.payment_methods || []);
  }

  /**
   * Get leave types as dropdown options
   */
  public getLeaveTypes(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.leave_types || []);
  }

  /**
   * Get leave statuses as dropdown options
   */
  public getLeaveStatuses(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.leave_statuses || []);
  }

  /**
   * Get expense categories as dropdown options
   */
  public getExpenseCategories(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.expense_categories || []);
  }

  /**
   * Get expense statuses as dropdown options
   */
  public getExpenseStatuses(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.expense_statuses || []);
  }

  /**
   * Get employment statuses as dropdown options
   */
  public getEmploymentStatuses(): DropdownOption[] {
    return this.getDropdownOptions(this.configuration?.employment_statuses || []);
  }

  /**
   * Get qualifications as dropdown options
   */
  public getQualifications(): DropdownOption[] {
    const qualifications = this.configuration?.qualifications || [];
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

// Export API function for configuration endpoint
export const configurationAPI = {
  getConfiguration: () => api.get('/configuration/'),
  refreshConfiguration: () => api.post('/configuration/refresh'),
};

export default configurationService;
