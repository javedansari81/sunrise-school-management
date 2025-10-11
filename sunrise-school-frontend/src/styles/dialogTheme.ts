/**
 * Standardized Dialog Design System for Sunrise School
 * 
 * This file defines consistent styling patterns for all dialog components
 * across the application to ensure professional and uniform appearance.
 */

export const dialogStyles = {
  // Standard dialog container styles
  paper: {
    borderRadius: 3,
    boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
    background: '#ffffff',
    maxHeight: { xs: '95vh', sm: '90vh' },
    margin: { xs: 1, sm: 2 },
    overflow: 'hidden',
  },

  // Professional header styling with gradient
  title: {
    background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
    color: 'white',
    padding: { xs: 2, sm: 3 },
    position: 'relative' as const,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 64,
  },

  // Title text styling
  titleText: {
    fontWeight: 600,
    fontSize: { xs: '1.25rem', sm: '1.5rem' },
    display: 'flex',
    alignItems: 'center',
    gap: 1,
  },

  // Close button styling
  closeButton: {
    color: 'white',
    '&:hover': {
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
    },
  },

  // Content area styling
  content: {
    padding: { xs: 2, sm: 3 },
    backgroundColor: '#fafafa',
    '&.MuiDialogContent-dividers': {
      borderTop: '1px solid #e0e0e0',
      borderBottom: '1px solid #e0e0e0',
    },
  },

  // Actions area styling
  actions: {
    padding: { xs: 2, sm: 3 },
    backgroundColor: '#ffffff',
    borderTop: '1px solid #e0e0e0',
    gap: 1,
    justifyContent: 'flex-end',
  },

  // Primary button styling
  primaryButton: {
    borderRadius: 2,
    textTransform: 'none' as const,
    fontWeight: 600,
    padding: { xs: '8px 16px', sm: '10px 20px' },
    fontSize: { xs: '0.875rem', sm: '1rem' },
    minWidth: 100,
    background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
    '&:hover': {
      background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
    },
  },

  // Secondary button styling
  secondaryButton: {
    borderRadius: 2,
    textTransform: 'none' as const,
    fontWeight: 500,
    padding: { xs: '8px 16px', sm: '10px 20px' },
    fontSize: { xs: '0.875rem', sm: '1rem' },
    minWidth: 100,
    borderColor: '#1976d2',
    color: '#1976d2',
    '&:hover': {
      borderColor: '#1565c0',
      backgroundColor: 'rgba(25, 118, 210, 0.04)',
    },
  },

  // Alert/message styling
  alert: {
    borderRadius: 2,
    marginBottom: 2,
    '&.MuiAlert-standardInfo': {
      backgroundColor: '#e3f2fd',
      color: '#0d47a1',
    },
    '&.MuiAlert-standardError': {
      backgroundColor: '#ffebee',
      color: '#c62828',
    },
    '&.MuiAlert-standardWarning': {
      backgroundColor: '#fff3e0',
      color: '#ef6c00',
    },
    '&.MuiAlert-standardSuccess': {
      backgroundColor: '#e8f5e8',
      color: '#2e7d32',
    },
  },

  // Form field styling
  textField: {
    '& .MuiOutlinedInput-root': {
      borderRadius: 2,
      '&:hover .MuiOutlinedInput-notchedOutline': {
        borderColor: '#1976d2',
      },
      '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
        borderColor: '#1976d2',
      },
    },
    '& .MuiInputLabel-root': {
      '&.Mui-focused': {
        color: '#1976d2',
      },
    },
  },

  // Info section styling (for displaying user info, etc.)
  infoSection: {
    padding: 2,
    backgroundColor: '#f5f5f5',
    borderRadius: 2,
    marginBottom: 2,
    border: '1px solid #e0e0e0',
  },

  // Loading state styling
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: 200,
    backgroundColor: '#fafafa',
  },
};

/**
 * Color palette for consistent theming
 */
export const dialogColors = {
  primary: '#1976d2',
  primaryDark: '#1565c0',
  primaryLight: '#42a5f5',
  secondary: '#ff6b35',
  success: '#2e7d32',
  warning: '#ef6c00',
  error: '#c62828',
  info: '#0288d1',
  background: '#ffffff',
  surface: '#fafafa',
  border: '#e0e0e0',
  text: {
    primary: '#212121',
    secondary: '#757575',
    disabled: '#bdbdbd',
  },
};

/**
 * Typography variants for dialogs
 */
export const dialogTypography = {
  title: {
    fontWeight: 600,
    fontSize: { xs: '1.25rem', sm: '1.5rem' },
    lineHeight: 1.2,
  },
  subtitle: {
    fontWeight: 500,
    fontSize: { xs: '1rem', sm: '1.125rem' },
    lineHeight: 1.3,
  },
  body: {
    fontWeight: 400,
    fontSize: { xs: '0.875rem', sm: '1rem' },
    lineHeight: 1.5,
  },
  caption: {
    fontWeight: 400,
    fontSize: { xs: '0.75rem', sm: '0.875rem' },
    lineHeight: 1.4,
  },
};

/**
 * Responsive breakpoints for dialogs
 */
export const dialogBreakpoints = {
  mobile: 'xs',
  tablet: 'sm',
  desktop: 'md',
  large: 'lg',
};

/**
 * Standard dialog sizes
 */
export const dialogSizes = {
  small: 'xs',
  medium: 'sm',
  large: 'md',
  extraLarge: 'lg',
};

/**
 * Animation settings for dialogs
 */
export const dialogAnimations = {
  transition: {
    duration: 300,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
};
