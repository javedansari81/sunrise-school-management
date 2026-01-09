import React, { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { sessionService } from '../services/sessionService';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
  /** If true, requires exact role match (e.g., SUPER_ADMIN only, not ADMIN) */
  exactRoleMatch?: boolean;
}

/**
 * Check if user role satisfies the required role.
 * SUPER_ADMIN is treated as having ADMIN privileges (unless exact match is required).
 *
 * @param userRole - The user's current role
 * @param requiredRole - The required role to access the route
 * @param exactMatch - If true, requires exact role match (default: false)
 */
const hasRequiredRole = (
  userRole: string | undefined,
  requiredRole: string,
  exactMatch: boolean = false
): boolean => {
  if (!userRole) return false;

  const userRoleUpper = userRole.toUpperCase();
  const requiredRoleUpper = requiredRole.toUpperCase();

  // Direct match
  if (userRoleUpper === requiredRoleUpper) return true;

  // If exact match is required, don't allow role escalation
  if (exactMatch) return false;

  // SUPER_ADMIN has all ADMIN privileges (when exact match not required)
  if (userRoleUpper === 'SUPER_ADMIN' && requiredRoleUpper === 'ADMIN') return true;

  return false;
};

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  exactRoleMatch = false
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

  // Check if user has required role (case-insensitive, SUPER_ADMIN has ADMIN privileges unless exactRoleMatch)
  if (requiredRole && !hasRequiredRole(user?.user_type, requiredRole, exactRoleMatch)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
