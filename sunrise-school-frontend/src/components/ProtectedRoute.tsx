import React, { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { sessionService } from '../services/sessionService';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

/**
 * Check if user role satisfies the required role.
 * SUPER_ADMIN is treated as having ADMIN privileges.
 */
const hasRequiredRole = (userRole: string | undefined, requiredRole: string): boolean => {
  if (!userRole) return false;

  const userRoleUpper = userRole.toUpperCase();
  const requiredRoleUpper = requiredRole.toUpperCase();

  // Direct match
  if (userRoleUpper === requiredRoleUpper) return true;

  // SUPER_ADMIN has all ADMIN privileges
  if (userRoleUpper === 'SUPER_ADMIN' && requiredRoleUpper === 'ADMIN') return true;

  return false;
};

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

  // Check if user has required role (case-insensitive, SUPER_ADMIN has ADMIN privileges)
  if (requiredRole && !hasRequiredRole(user?.user_type, requiredRole)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
