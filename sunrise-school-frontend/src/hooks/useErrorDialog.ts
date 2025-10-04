import { useState, useCallback } from 'react';
import { ErrorHandler, ParsedError } from '../utils/errorHandler';

export interface ErrorDialogState {
  open: boolean;
  title?: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
  errorCode?: string;
  fieldName?: string;
  details?: Record<string, any>;
  showDetails?: boolean;
  actionText?: string;
  onAction?: () => void;
  showCancel?: boolean;
  cancelText?: string;
}

const initialState: ErrorDialogState = {
  open: false,
  message: '',
  severity: 'error'
};

export const useErrorDialog = () => {
  const [errorState, setErrorState] = useState<ErrorDialogState>(initialState);

  /**
   * Show error dialog with parsed error information
   */
  const showError = useCallback((
    error: any, 
    context?: string,
    options?: Partial<ErrorDialogState>
  ) => {
    const parsedError: ParsedError = context 
      ? ErrorHandler.getContextualErrorMessage(error, context)
      : ErrorHandler.parseApiError(error);

    setErrorState({
      ...initialState,
      open: true,
      title: parsedError.title,
      message: parsedError.message,
      severity: parsedError.severity,
      errorCode: parsedError.errorCode,
      fieldName: parsedError.fieldName,
      details: parsedError.details,
      showDetails: !!parsedError.details,
      ...options
    });
  }, []);

  /**
   * Show custom error dialog
   */
  const showCustomError = useCallback((
    message: string,
    options?: Partial<ErrorDialogState>
  ) => {
    setErrorState({
      ...initialState,
      open: true,
      message,
      ...options
    });
  }, []);

  /**
   * Show validation error dialog
   */
  const showValidationError = useCallback((
    message: string,
    fieldName?: string,
    options?: Partial<ErrorDialogState>
  ) => {
    setErrorState({
      ...initialState,
      open: true,
      title: 'Validation Error',
      message,
      severity: 'warning',
      errorCode: 'VALIDATION_ERROR',
      fieldName,
      ...options
    });
  }, []);

  /**
   * Show network error dialog
   */
  const showNetworkError = useCallback((
    options?: Partial<ErrorDialogState>
  ) => {
    setErrorState({
      ...initialState,
      open: true,
      title: 'Connection Error',
      message: 'Network connection error. Please check your internet connection and try again.',
      severity: 'error',
      errorCode: 'NETWORK_ERROR',
      ...options
    });
  }, []);

  /**
   * Show server error dialog
   */
  const showServerError = useCallback((
    options?: Partial<ErrorDialogState>
  ) => {
    setErrorState({
      ...initialState,
      open: true,
      title: 'Server Error',
      message: 'Server error occurred. Please try again later or contact support if the problem persists.',
      severity: 'error',
      errorCode: 'SERVER_ERROR',
      ...options
    });
  }, []);

  /**
   * Show authentication error dialog
   */
  const showAuthError = useCallback((
    options?: Partial<ErrorDialogState>
  ) => {
    setErrorState({
      ...initialState,
      open: true,
      title: 'Session Expired',
      message: 'Your session has expired. Please log in again.',
      severity: 'warning',
      errorCode: 'AUTHENTICATION_EXPIRED',
      actionText: 'Login',
      onAction: () => {
        // Clear any stored auth tokens
        localStorage.removeItem('authToken');
        // Redirect to login
        window.location.href = '/login';
      },
      ...options
    });
  }, []);

  /**
   * Show permission error dialog
   */
  const showPermissionError = useCallback((
    options?: Partial<ErrorDialogState>
  ) => {
    setErrorState({
      ...initialState,
      open: true,
      title: 'Access Denied',
      message: 'You do not have permission to perform this action.',
      severity: 'warning',
      errorCode: 'AUTHORIZATION_DENIED',
      ...options
    });
  }, []);

  /**
   * Show confirmation dialog (using error dialog component)
   */
  const showConfirmation = useCallback((
    message: string,
    onConfirm: () => void,
    options?: Partial<ErrorDialogState>
  ) => {
    setErrorState({
      ...initialState,
      open: true,
      title: 'Confirm Action',
      message,
      severity: 'info',
      actionText: 'Confirm',
      onAction: () => {
        onConfirm();
        closeDialog();
      },
      showCancel: true,
      cancelText: 'Cancel',
      ...options
    });
  }, []);

  /**
   * Show warning dialog
   */
  const showWarning = useCallback((
    message: string,
    options?: Partial<ErrorDialogState>
  ) => {
    setErrorState({
      ...initialState,
      open: true,
      title: 'Warning',
      message,
      severity: 'warning',
      ...options
    });
  }, []);

  /**
   * Show info dialog
   */
  const showInfo = useCallback((
    message: string,
    options?: Partial<ErrorDialogState>
  ) => {
    setErrorState({
      ...initialState,
      open: true,
      title: 'Information',
      message,
      severity: 'info',
      ...options
    });
  }, []);

  /**
   * Close the error dialog
   */
  const closeDialog = useCallback(() => {
    setErrorState(initialState);
  }, []);

  /**
   * Handle API errors with automatic error type detection and appropriate actions
   */
  const handleApiError = useCallback((error: any, context?: string) => {
    // Check if we should redirect
    const redirectInfo = ErrorHandler.shouldRedirect(error);
    if (redirectInfo.redirect && redirectInfo.path) {
      if (redirectInfo.path === '/login') {
        showAuthError();
      } else {
        showPermissionError();
      }
      return;
    }

    // Show appropriate error dialog
    showError(error, context);
  }, [showError, showAuthError, showPermissionError]);

  return {
    // State
    errorState,
    isOpen: errorState.open,
    
    // Actions
    showError,
    showCustomError,
    showValidationError,
    showNetworkError,
    showServerError,
    showAuthError,
    showPermissionError,
    showConfirmation,
    showWarning,
    showInfo,
    closeDialog,
    handleApiError,
    
    // Dialog props (for easy spreading to ErrorDialog component)
    dialogProps: {
      open: errorState.open,
      onClose: closeDialog,
      title: errorState.title,
      message: errorState.message,
      severity: errorState.severity,
      errorCode: errorState.errorCode,
      fieldName: errorState.fieldName,
      details: errorState.details,
      showDetails: errorState.showDetails,
      actionText: errorState.actionText,
      onAction: errorState.onAction,
      showCancel: errorState.showCancel,
      cancelText: errorState.cancelText
    }
  };
};
