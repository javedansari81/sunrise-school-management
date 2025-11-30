import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../services/api';
import { configurationService } from '../services/configurationService';
import { sessionService } from '../services/sessionService';

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  user_type: string;
  is_active: boolean;
  profile_picture_url?: string | null;
  phone?: string;
  teacher_profile?: {
    id: number;
    class_teacher_of_id?: number;
    class_teacher_of_name?: string;
    [key: string]: any;
  };
  student_profile?: {
    id: number;
    class_id?: number;
    [key: string]: any;
  };
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
  handleSessionExpired: () => void;
  showLoginPopup: boolean;
  setShowLoginPopup: (show: boolean) => void;
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
  const [showLoginPopup, setShowLoginPopup] = useState(false);

  const isAuthenticated = !!user && !!localStorage.getItem('authToken') && sessionService.isSessionValid();



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
      const response = await authAPI.login(email, password);
      const { access_token, user, permissions } = response.data;

      localStorage.setItem('authToken', access_token);

      // Map user_type_id to user_type string for frontend compatibility
      const mappedUser = {
        ...user,
        user_type: user.user_type || mapUserTypeIdToString(user.user_type_id)
      };

      // Set user immediately from login response
      setUser(mappedUser);
      localStorage.setItem('userRole', mappedUser.user_type);

      // Hide login popup on successful login
      setShowLoginPopup(false);

      // Start session monitoring
      sessionService.startSessionMonitoring();

      // Fetch full profile data (including profile picture) in the background
      // This will update the user state with profile picture
      refreshUser().catch(err => {
        console.error('Failed to fetch profile picture after login:', err);
      });

      // Return the full response for the caller
      return {
        access_token,
        token_type: 'bearer',
        user: mappedUser,
        permissions: permissions || []
      };
    } catch (error: any) {
      throw error;
    }
  };

  const logout = () => {
    sessionService.clearSession();
    setUser(null);
    setShowLoginPopup(false);
    // Clear configuration cache on logout
    configurationService.clearConfiguration();
    // Stop session monitoring
    sessionService.stopSessionMonitoring();
  };

  const handleSessionExpired = () => {
    setUser(null);
    setShowLoginPopup(true);
    // Clear configuration cache
    configurationService.clearConfiguration();

    // Navigate to home page if not already there
    const currentPath = window.location.pathname;
    if (currentPath !== '/') {
      window.location.href = '/';
    }
  };

  const refreshUser = async () => {
    try {
      const token = localStorage.getItem('authToken');

      if (!token) {
        setUser(null);
        return;
      }

      // Check if token is expired before making API call
      if (sessionService.isTokenExpired(token)) {
        handleSessionExpired();
        return;
      }

      const response = await authAPI.getProfile();
      const profileData = response.data;

      // Extract profile picture URL from student_profile or teacher_profile
      let profilePictureUrl = null;
      if (profileData.student_profile?.profile_picture_url) {
        profilePictureUrl = profileData.student_profile.profile_picture_url;
      } else if (profileData.teacher_profile?.profile_picture_url) {
        profilePictureUrl = profileData.teacher_profile.profile_picture_url;
      } else if (profileData.admin_profile?.profile_picture_url) {
        profilePictureUrl = profileData.admin_profile.profile_picture_url;
      }

      // Map user_type_id to user_type string for frontend compatibility
      const mappedUser = {
        ...profileData.user_info,
        user_type: profileData.user_info.user_type || mapUserTypeIdToString(profileData.user_info.user_type_id),
        profile_picture_url: profilePictureUrl,
        teacher_profile: profileData.teacher_profile,
        student_profile: profileData.student_profile
      };

      setUser(mappedUser);

      // Update user role in localStorage
      localStorage.setItem('userRole', mappedUser.user_type);
    } catch (error: any) {
      // If it's a 401 error, handle as session expiration
      if (error.response?.status === 401) {
        handleSessionExpired();
      }
      // For other errors, don't immediately logout - keep the token and user state
      // This prevents losing session on temporary network issues
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

    // Set up session service callbacks
    sessionService.setCallbacks({
      onSessionExpired: handleSessionExpired,
      onSessionInvalid: handleSessionExpired,
      onSessionCleared: () => {}
    });

    initAuth();

    // Start session monitoring if user is authenticated
    const token = localStorage.getItem('authToken');
    if (token && sessionService.isSessionValid()) {
      sessionService.startSessionMonitoring();
    }

    // Cleanup on unmount
    return () => {
      sessionService.stopSessionMonitoring();
    };
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshUser,
    handleSessionExpired,
    showLoginPopup,
    setShowLoginPopup,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
