import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '../AuthContext';
import * as api from '../../services/api';

// Mock the API
jest.mock('../../services/api', () => ({
  authAPI: {
    login: jest.fn(),
    getCurrentUser: jest.fn(),
    logout: jest.fn(),
  }
}));

const mockedApi = api as jest.Mocked<typeof api>;

// Test component that uses the auth context
const TestComponent: React.FC = () => {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
      </div>
      {user && (
        <div data-testid="user-info">
          {user.first_name} {user.last_name} ({user.email})
        </div>
      )}
      <button
        data-testid="login-button"
        onClick={() => login('test@example.com', 'password')}
      >
        Login
      </button>
      <button data-testid="logout-button" onClick={logout}>
        Logout
      </button>
    </div>
  );
};

const renderWithAuthProvider = (component: React.ReactElement) => {
  return render(<AuthProvider>{component}</AuthProvider>);
};

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('should render loading state initially', () => {
    renderWithAuthProvider(<TestComponent />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should show not authenticated when no token', async () => {
    renderWithAuthProvider(<TestComponent />);
    
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
    });
  });

  it('should handle successful login', async () => {

    const mockLoginResponse = {
      data: {
        access_token: 'mock-token',
        token_type: 'bearer'
      }
    };
    const mockUserResponse = {
      data: {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        email: 'test@example.com',
        user_type: 'admin',
        is_active: true
      }
    };

    (mockedApi.authAPI.login as jest.Mock).mockResolvedValue(mockLoginResponse);
    (mockedApi.authAPI.getCurrentUser as jest.Mock).mockResolvedValue(mockUserResponse);

    renderWithAuthProvider(<TestComponent />);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
    });

    await userEvent.click(screen.getByTestId('login-button'));

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('user-info')).toHaveTextContent('John Doe (test@example.com)');
    });

    expect(localStorage.getItem('authToken')).toBe('mock-token');
    expect(localStorage.getItem('userRole')).toBe('admin');
  });

  it('should handle login failure', async () => {
    const mockError = new Error('Invalid credentials');

    (mockedApi.authAPI.login as jest.Mock).mockRejectedValue(mockError);

    renderWithAuthProvider(<TestComponent />);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
    });

    await expect(async () => {
      await userEvent.click(screen.getByTestId('login-button'));
    }).rejects.toThrow('Invalid credentials');

    expect(localStorage.getItem('authToken')).toBeNull();
  });

  it('should handle logout', async () => {

    
    // Set up initial authenticated state
    localStorage.setItem('authToken', 'mock-token');
    localStorage.setItem('userRole', 'admin');

    const mockUserResponse = {
      data: {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        email: 'test@example.com',
        user_type: 'admin',
        is_active: true
      }
    };

    (mockedApi.authAPI.getCurrentUser as jest.Mock).mockResolvedValue(mockUserResponse);

    renderWithAuthProvider(<TestComponent />);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
    });

    await userEvent.click(screen.getByTestId('logout-button'));

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
    });

    expect(localStorage.getItem('authToken')).toBeNull();
    expect(localStorage.getItem('userRole')).toBeNull();
  });

  it('should restore authentication state from localStorage', async () => {
    localStorage.setItem('authToken', 'existing-token');
    
    const mockUserResponse = {
      data: {
        id: 1,
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane@example.com',
        user_type: 'user',
        is_active: true
      }
    };

    (mockedApi.authAPI.getCurrentUser as jest.Mock).mockResolvedValue(mockUserResponse);

    renderWithAuthProvider(<TestComponent />);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('user-info')).toHaveTextContent('Jane Smith (jane@example.com)');
    });

    expect(localStorage.getItem('userRole')).toBe('user');
  });

  it('should handle API error during token refresh', async () => {
    localStorage.setItem('authToken', 'invalid-token');
    
    (mockedApi.authAPI.getCurrentUser as jest.Mock).mockRejectedValue(new Error('Unauthorized'));

    renderWithAuthProvider(<TestComponent />);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
    });

    // Token should be removed after failed refresh
    expect(localStorage.getItem('authToken')).toBeNull();
  });
});
