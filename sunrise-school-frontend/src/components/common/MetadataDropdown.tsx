/**
 * Metadata Dropdown Components
 * Reusable dropdown components that use configuration service
 */

import React from 'react';
import {
  TextField,
  MenuItem,
} from '@mui/material';
import { useDropdownOptions, useConfiguration } from '../../contexts/ConfigurationContext';

// Base props for all metadata dropdowns
interface BaseDropdownProps {
  value: string | number;
  onChange: (value: string | number) => void;
  label: string;
  required?: boolean;
  disabled?: boolean;
  error?: boolean;
  helperText?: string;
  fullWidth?: boolean;
  size?: 'small' | 'medium';
  variant?: 'outlined' | 'filled' | 'standard';
  includeAll?: boolean; // Whether to include "All" option
  allLabel?: string; // Label for "All" option
}

// Generic metadata dropdown component
interface MetadataDropdownProps extends BaseDropdownProps {
  metadataType: 'userTypes' | 'sessionYears' | 'genders' | 'classes' | 'paymentTypes' | 'paymentStatuses' | 'paymentMethods' | 'leaveTypes' | 'leaveStatuses' | 'expenseCategories' | 'expenseStatuses' | 'employmentStatuses' | 'qualifications';
}

export const MetadataDropdown: React.FC<MetadataDropdownProps> = ({
  metadataType,
  value,
  onChange,
  label,
  required = false,
  disabled = false,
  error = false,
  helperText,
  fullWidth = true,
  size = 'medium',
  variant = 'outlined',
  includeAll = false,
  allLabel = 'All',
}) => {
  const options = useDropdownOptions(metadataType);
  const { isLoading } = useConfiguration();

  const handleChange = (event: any) => {
    onChange(event.target.value);
  };

  return (
    <TextField
      select
      label={label}
      value={value}
      onChange={handleChange}
      required={required}
      disabled={disabled || isLoading}
      error={error}
      helperText={helperText}
      fullWidth={fullWidth}
      size={size}
      variant={variant}
    >
      {includeAll && (
        <MenuItem value="all">
          {allLabel}
        </MenuItem>
      )}
      {options.map((option) => (
        <MenuItem key={option.id} value={option.id}>
          {option.display_name || option.name}
        </MenuItem>
      ))}
    </TextField>
  );
};

// Specific dropdown components for better type safety and convenience

export const UserTypeDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'User Type',
  ...props
}) => (
  <MetadataDropdown metadataType="userTypes" label={label} {...props} />
);

export const SessionYearDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Session Year',
  ...props
}) => (
  <MetadataDropdown metadataType="sessionYears" label={label} {...props} />
);

export const GenderDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Gender',
  ...props
}) => (
  <MetadataDropdown metadataType="genders" label={label} {...props} />
);

export const ClassDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Class',
  ...props
}) => (
  <MetadataDropdown metadataType="classes" label={label} {...props} />
);

export const PaymentTypeDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Payment Type',
  ...props
}) => (
  <MetadataDropdown metadataType="paymentTypes" label={label} {...props} />
);

export const PaymentStatusDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Payment Status',
  ...props
}) => (
  <MetadataDropdown metadataType="paymentStatuses" label={label} {...props} />
);

export const PaymentMethodDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Payment Method',
  ...props
}) => (
  <MetadataDropdown metadataType="paymentMethods" label={label} {...props} />
);

export const LeaveTypeDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Leave Type',
  ...props
}) => (
  <MetadataDropdown metadataType="leaveTypes" label={label} {...props} />
);

export const LeaveStatusDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Leave Status',
  ...props
}) => (
  <MetadataDropdown metadataType="leaveStatuses" label={label} {...props} />
);

export const ExpenseCategoryDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Expense Category',
  ...props
}) => (
  <MetadataDropdown metadataType="expenseCategories" label={label} {...props} />
);

export const ExpenseStatusDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Expense Status',
  ...props
}) => (
  <MetadataDropdown metadataType="expenseStatuses" label={label} {...props} />
);

export const EmploymentStatusDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Employment Status',
  ...props
}) => (
  <MetadataDropdown metadataType="employmentStatuses" label={label} {...props} />
);

export const QualificationDropdown: React.FC<Omit<BaseDropdownProps, 'label'> & { label?: string }> = ({
  label = 'Qualification',
  ...props
}) => (
  <MetadataDropdown metadataType="qualifications" label={label} {...props} />
);

// Filter dropdown component (includes "All" option by default)
interface FilterDropdownProps extends Omit<BaseDropdownProps, 'includeAll' | 'allLabel'> {
  metadataType: 'userTypes' | 'sessionYears' | 'genders' | 'classes' | 'paymentTypes' | 'paymentStatuses' | 'paymentMethods' | 'leaveTypes' | 'leaveStatuses' | 'expenseCategories' | 'expenseStatuses' | 'employmentStatuses' | 'qualifications';
  allLabel?: string;
}

export const FilterDropdown: React.FC<FilterDropdownProps> = ({
  allLabel = 'All',
  ...props
}) => (
  <MetadataDropdown includeAll={true} allLabel={allLabel} {...props} />
);

// Specific filter components
export const ClassFilter: React.FC<Omit<FilterDropdownProps, 'metadataType' | 'label'> & { label?: string }> = ({
  label = 'Class',
  allLabel = 'All Classes',
  ...props
}) => (
  <FilterDropdown metadataType="classes" label={label} allLabel={allLabel} {...props} />
);

export const GenderFilter: React.FC<Omit<FilterDropdownProps, 'metadataType' | 'label'> & { label?: string }> = ({
  label = 'Gender',
  allLabel = 'All Genders',
  ...props
}) => (
  <FilterDropdown metadataType="genders" label={label} allLabel={allLabel} {...props} />
);

export const PaymentStatusFilter: React.FC<Omit<FilterDropdownProps, 'metadataType' | 'label'> & { label?: string }> = ({
  label = 'Payment Status',
  allLabel = 'All Statuses',
  ...props
}) => (
  <FilterDropdown metadataType="paymentStatuses" label={label} allLabel={allLabel} {...props} />
);

export default MetadataDropdown;
