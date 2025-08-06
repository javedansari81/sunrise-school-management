import React, { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { sessionService } from '../services/sessionService';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole
}) => {
  const { user, isAuthenticated, isLoading, handleSessionExpired, setShowLoginPopup } = useAuth();

  // Debug logging
  console.log('ProtectedRoute check:', {
    isLoading,
    isAuthenticated,
    hasUser: !!user,
    userType: user?.user_type,
    requiredRole,
    hasToken: !!localStorage.getItem('authToken'),
    sessionValid: sessionService.isSessionValid()
  });

  // Check for session expiration on route access
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token && sessionService.isTokenExpired(token)) {
      console.log('ProtectedRoute: Token expired on route access');
      handleSessionExpired();
    }
  }, [handleSessionExpired]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    console.log('ProtectedRoute: Showing loading spinner');
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  // Check if user is authenticated and session is valid
  if (!isAuthenticated || !sessionService.isSessionValid()) {
    console.log('ProtectedRoute: Not authenticated or session invalid, redirecting to home');

    // Trigger login popup if not already shown
    setTimeout(() => {
      setShowLoginPopup(true);
    }, 100);

    return <Navigate to="/" replace />;
  }

  // Check if user has required role (case-insensitive, comparing with backend enum values)
  if (requiredRole && user?.user_type?.toUpperCase() !== requiredRole.toUpperCase()) {
    console.log('ProtectedRoute: Insufficient role, redirecting to home');
    return <Navigate to="/" replace />;
  }

  console.log('ProtectedRoute: Access granted');
  return <>{children}</>;
};

export default ProtectedRoute;
