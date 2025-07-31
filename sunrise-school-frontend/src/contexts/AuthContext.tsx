import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../services/api';
import { configurationService } from '../services/configurationService';

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  user_type: string;
  is_active: boolean;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
  permissions: string[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<LoginResponse>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!localStorage.getItem('authToken');

  // Debug logging
  React.useEffect(() => {
    console.log('Auth state changed:', {
      hasUser: !!user,
      hasToken: !!localStorage.getItem('authToken'),
      isAuthenticated,
      userType: user?.user_type
    });
  }, [user, isAuthenticated]);

  // Helper function to map user_type_id to user_type string (matching backend enum values)
  const mapUserTypeIdToString = (user_type_id: number): string => {
    switch (user_type_id) {
      case 1: return 'ADMIN';    // Backend enum: ADMIN = "ADMIN"
      case 2: return 'TEACHER';  // Backend enum: TEACHER = "TEACHER"
      case 3: return 'STUDENT';  // Backend enum: STUDENT = "STUDENT"
      default: return 'STUDENT';
    }
  };

  const login = async (email: string, password: string): Promise<LoginResponse> => {
    try {
      console.log('Login attempt for:', email);
      const response = await authAPI.login(email, password);
      const { access_token, user, permissions } = response.data;
      console.log('Login successful, token received:', !!access_token);
      console.log('Raw user data from backend:', user);

      localStorage.setItem('authToken', access_token);
      console.log('Token stored in localStorage');

      // Map user_type_id to user_type string for frontend compatibility
      const mappedUser = {
        ...user,
        user_type: user.user_type || mapUserTypeIdToString(user.user_type_id)
      };
      console.log('Mapped user data:', mappedUser);

      // Set user immediately from login response
      setUser(mappedUser);
      localStorage.setItem('userRole', mappedUser.user_type);

      // Return the full response for the caller
      return {
        access_token,
        token_type: 'bearer',
        user: mappedUser,
        permissions: permissions || []
      };
    } catch (error: any) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    setUser(null);
    // Clear configuration cache on logout
    configurationService.clearConfiguration();
  };

  const refreshUser = async () => {
    try {
      const token = localStorage.getItem('authToken');
      console.log('RefreshUser called, token exists:', !!token);
      if (!token) {
        console.log('No token found, setting user to null');
        setUser(null);
        return;
      }

      console.log('Calling getCurrentUser API...');
      const response = await authAPI.getCurrentUser();
      console.log('getCurrentUser response:', response.data);

      // Map user_type_id to user_type string for frontend compatibility
      const mappedUser = {
        ...response.data,
        user_type: response.data.user_type || mapUserTypeIdToString(response.data.user_type_id)
      };
      console.log('Mapped user data from refresh:', mappedUser);

      setUser(mappedUser);

      // Update user role in localStorage
      localStorage.setItem('userRole', mappedUser.user_type);
    } catch (error: any) {
      console.error('Failed to refresh user:', error);
      console.log('Error details:', error.response?.status, error.response?.data);
      logout();
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (token) {
        await refreshUser();
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
