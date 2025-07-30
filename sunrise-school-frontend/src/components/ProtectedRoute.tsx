import React from 'react';
import { Navigate } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  // Debug logging
  console.log('ProtectedRoute check:', {
    isLoading,
    isAuthenticated,
    hasUser: !!user,
    userType: user?.user_type,
    requiredRole,
    hasToken: !!localStorage.getItem('authToken')
  });

  // Show loading spinner while checking authentication
  if (isLoading) {
    console.log('ProtectedRoute: Showing loading spinner');
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  // Check if user is authenticated
  if (!isAuthenticated) {
    console.log('ProtectedRoute: Not authenticated, redirecting to home');
    return <Navigate to="/" replace />;
  }

  // Check if user has required role (case-insensitive)
  if (requiredRole && user?.user_type?.toLowerCase() !== requiredRole.toLowerCase()) {
    console.log('ProtectedRoute: Insufficient role, redirecting to home');
    return <Navigate to="/" replace />;
  }

  console.log('ProtectedRoute: Access granted');
  return <>{children}</>;
};

export default ProtectedRoute;
