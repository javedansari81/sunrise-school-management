/**
 * Centralized Error Handling Utility for Frontend
 * 
 * This utility provides standardized error handling for API responses,
 * converting backend error responses into user-friendly messages and
 * providing consistent error display patterns.
 */

export interface ErrorResponse {
  success: boolean;
  message: string;
  error_code: string;
  field_name?: string;
  details?: Record<string, any>;
}

export interface ParsedError {
  message: string;
  severity: 'error' | 'warning' | 'info';
  errorCode?: string;
  fieldName?: string;
  details?: Record<string, any>;
  title?: string;
}

export class ErrorHandler {
  /**
   * Parse API error response into user-friendly format
   */
  static parseApiError(error: any): ParsedError {
    // Default error response
    const defaultError: ParsedError = {
      message: 'An unexpected error occurred. Please try again.',
      severity: 'error' as const,
      errorCode: 'UNKNOWN_ERROR'
    };

    try {
      // Handle network errors
      if (!error.response) {
        if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
          return {
            message: 'Network connection error. Please check your internet connection and try again.',
            severity: 'error',
            errorCode: 'NETWORK_ERROR',
            title: 'Connection Error'
          };
        }
        return {
          ...defaultError,
          message: error.message || defaultError.message
        };
      }

      const { status, data } = error.response;

      // Handle authentication errors
      if (status === 401) {
        return {
          message: 'Your session has expired. Please log in again.',
          severity: 'warning',
          errorCode: 'AUTHENTICATION_EXPIRED',
          title: 'Session Expired'
        };
      }

      // Handle authorization errors
      if (status === 403) {
        return {
          message: 'You do not have permission to perform this action.',
          severity: 'warning',
          errorCode: 'AUTHORIZATION_DENIED',
          title: 'Access Denied'
        };
      }

      // Handle server errors
      if (status >= 500) {
        return {
          message: 'Server error occurred. Please try again later or contact support if the problem persists.',
          severity: 'error',
          errorCode: 'SERVER_ERROR',
          title: 'Server Error'
        };
      }

      // Handle structured error responses from our backend
      if (data && typeof data === 'object') {
        // Check for our standardized error response format
        if (data.success === false && data.message) {
          return {
            message: data.message,
            severity: ErrorHandler.getSeverityFromErrorCode(data.error_code),
            errorCode: data.error_code,
            fieldName: data.field_name,
            details: data.details,
            title: ErrorHandler.getTitleFromErrorCode(data.error_code)
          };
        }

        // Handle FastAPI validation errors (422)
        if (status === 422 && data.detail) {
          return ErrorHandler.parseValidationErrors(data.detail);
        }

        // Handle other structured responses
        if (data.detail) {
          if (typeof data.detail === 'string') {
            return {
              message: data.detail,
              severity: status >= 400 && status < 500 ? 'warning' : 'error',
              errorCode: `HTTP_${status}`
            };
          }

          // Handle array of errors
          if (Array.isArray(data.detail)) {
            const errorMessages = data.detail.map((err: any) => {
              if (typeof err === 'string') return err;
              if (err.msg && err.loc) {
                const field = Array.isArray(err.loc) ? err.loc.join('.') : err.loc;
                return `${field}: ${err.msg}`;
              }
              return err.msg || 'Validation error';
            });
            
            return {
              message: errorMessages.join(', '),
              severity: 'warning',
              errorCode: 'VALIDATION_ERROR',
              title: 'Validation Error'
            };
          }
        }

        // Handle other data formats
        if (data.message) {
          return {
            message: data.message,
            severity: status >= 400 && status < 500 ? 'warning' : 'error',
            errorCode: `HTTP_${status}`
          };
        }
      }

      // Fallback for unstructured responses
      return {
        message: `Request failed with status ${status}. Please try again.`,
        severity: 'error',
        errorCode: `HTTP_${status}`
      };

    } catch (parseError) {
      console.error('Error parsing API error:', parseError);
      return defaultError;
    }
  }

  /**
   * Parse FastAPI validation errors
   */
  private static parseValidationErrors(detail: any): ParsedError {
    if (typeof detail === 'string') {
      return {
        message: detail,
        severity: 'warning',
        errorCode: 'VALIDATION_ERROR',
        title: 'Validation Error'
      };
    }

    if (Array.isArray(detail)) {
      const errorMessages = detail.map((err: any) => {
        if (typeof err === 'string') return err;
        
        if (err.msg && err.loc) {
          const field = Array.isArray(err.loc) ? err.loc.join('.') : err.loc;
          const fieldName = field.replace(/^\d+\./, ''); // Remove array indices
          return `${fieldName}: ${err.msg}`;
        }
        
        return err.msg || 'Validation error';
      });

      return {
        message: errorMessages.join(', '),
        severity: 'warning',
        errorCode: 'VALIDATION_ERROR',
        title: 'Validation Error',
        details: { validationErrors: detail }
      };
    }

    return {
      message: 'Validation failed. Please check your input.',
      severity: 'warning',
      errorCode: 'VALIDATION_ERROR',
      title: 'Validation Error'
    };
  }

  /**
   * Get severity level from error code
   */
  private static getSeverityFromErrorCode(errorCode?: string): 'error' | 'warning' | 'info' {
    if (!errorCode) return 'error';

    const warningCodes = [
      'VALIDATION_ERROR',
      'AUTHENTICATION_EXPIRED',
      'AUTHORIZATION_DENIED',
      'DUPLICATE_ENTRY',
      'UNIQUE_VIOLATION'
    ];

    const infoCodes = [
      'INFO',
      'SUCCESS'
    ];

    if (warningCodes.some(code => errorCode.includes(code))) {
      return 'warning';
    }

    if (infoCodes.some(code => errorCode.includes(code))) {
      return 'info';
    }

    return 'error';
  }

  /**
   * Get appropriate title from error code
   */
  private static getTitleFromErrorCode(errorCode?: string): string | undefined {
    if (!errorCode) return undefined;

    const titleMap: Record<string, string> = {
      'NETWORK_ERROR': 'Connection Error',
      'AUTHENTICATION_EXPIRED': 'Session Expired',
      'AUTHORIZATION_DENIED': 'Access Denied',
      'VALIDATION_ERROR': 'Validation Error',
      'SERVER_ERROR': 'Server Error',
      'UNIQUE_VIOLATION': 'Duplicate Entry',
      'FOREIGN_KEY_VIOLATION': 'Invalid Reference',
      'CHECK_VIOLATION': 'Data Validation Error',
      'NOT_NULL_VIOLATION': 'Required Field Missing'
    };

    // Check for exact matches first
    if (titleMap[errorCode]) {
      return titleMap[errorCode];
    }

    // Check for partial matches
    for (const [key, title] of Object.entries(titleMap)) {
      if (errorCode.includes(key)) {
        return title;
      }
    }

    return undefined;
  }

  /**
   * Create a user-friendly error message for common scenarios
   */
  static getContextualErrorMessage(error: any, context: string): ParsedError {
    const parsedError = ErrorHandler.parseApiError(error);

    // Add context-specific messaging
    const contextMessages: Record<string, string> = {
      'student_creation': 'Failed to create student profile.',
      'teacher_creation': 'Failed to create teacher profile.',
      'fee_payment': 'Failed to process fee payment.',
      'leave_request': 'Failed to submit leave request.',
      'expense_creation': 'Failed to create expense record.',
      'login': 'Login failed.',
      'data_fetch': 'Failed to load data.',
      'data_update': 'Failed to update data.',
      'data_delete': 'Failed to delete data.'
    };

    if (contextMessages[context]) {
      parsedError.message = `${contextMessages[context]} ${parsedError.message}`;
    }

    return parsedError;
  }

  /**
   * Format error for display in snackbar/toast
   */
  static formatForSnackbar(error: any, context?: string): {
    message: string;
    severity: 'error' | 'warning' | 'info' | 'success';
  } {
    const parsedError = context 
      ? ErrorHandler.getContextualErrorMessage(error, context)
      : ErrorHandler.parseApiError(error);

    return {
      message: parsedError.message,
      severity: parsedError.severity
    };
  }

  /**
   * Check if error should trigger a redirect (e.g., authentication errors)
   */
  static shouldRedirect(error: any): { redirect: boolean; path?: string } {
    const parsedError = ErrorHandler.parseApiError(error);
    
    if (parsedError.errorCode === 'AUTHENTICATION_EXPIRED') {
      return { redirect: true, path: '/login' };
    }

    if (parsedError.errorCode === 'AUTHORIZATION_DENIED') {
      return { redirect: true, path: '/unauthorized' };
    }

    return { redirect: false };
  }
}

// Convenience functions for common use cases
export const parseApiError = (error: any) => ErrorHandler.parseApiError(error);
export const getContextualErrorMessage = (error: any, context: string) => 
  ErrorHandler.getContextualErrorMessage(error, context);
export const formatForSnackbar = (error: any, context?: string) => 
  ErrorHandler.formatForSnackbar(error, context);
export const shouldRedirect = (error: any) => ErrorHandler.shouldRedirect(error);
