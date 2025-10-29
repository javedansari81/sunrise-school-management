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

  // Check for session expiration on route access
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token && sessionService.isTokenExpired(token)) {
      handleSessionExpired();
    }
  }, [handleSessionExpired]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  // Check if user is authenticated and session is valid
  if (!isAuthenticated || !sessionService.isSessionValid()) {
    // Trigger login popup if not already shown
    setTimeout(() => {
      setShowLoginPopup(true);
    }, 100);

    return <Navigate to="/" replace />;
  }

  // Check if user has required role (case-insensitive, comparing with backend enum values)
  if (requiredRole && user?.user_type?.toUpperCase() !== requiredRole.toUpperCase()) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
