import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout/Layout';
import Home from './pages/Home';
import About from './pages/About';
import Academics from './pages/Academics';
import Admissions from './pages/Admissions';
import Faculty from './pages/Faculty';
import Gallery from './pages/Gallery';
import Contact from './pages/Contact';

import AdminDashboard from './pages/admin/AdminDashboard';
import FeesManagement from './pages/admin/FeesManagement';
import LeaveManagement from './pages/admin/LeaveManagement';
import ExpenseManagement from './pages/admin/ExpenseManagement';
import StudentProfiles from './pages/admin/StudentProfiles';
import TeacherProfiles from './pages/admin/TeacherProfiles';
import TeacherDashboard from './pages/teacher/TeacherDashboard';
import StudentDashboard from './pages/student/StudentDashboard';
import Profile from './pages/Profile';
// import ConfigurationTest from './components/common/ConfigurationTest';

import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { ConfigurationProvider } from './contexts/ConfigurationContext';

// Test utilities (only in development)
if (process.env.NODE_ENV === 'development') {
  import('./utils/testSessionInvalidation');
}

// Create a custom theme with mobile responsiveness
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#ff6b35',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      '@media (max-width:600px)': {
        fontSize: '2rem',
      },
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
      '@media (max-width:600px)': {
        fontSize: '1.75rem',
      },
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
      '@media (max-width:600px)': {
        fontSize: '1.5rem',
      },
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      '@media (max-width:600px)': {
        fontSize: '1.25rem',
      },
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.25rem',
      '@media (max-width:600px)': {
        fontSize: '1.125rem',
      },
    },
    h6: {
      fontWeight: 500,
      fontSize: '1.125rem',
      '@media (max-width:600px)': {
        fontSize: '1rem',
      },
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
  components: {
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingLeft: '8px',
          paddingRight: '8px',
          '@media (min-width: 600px)': {
            paddingLeft: '16px',
            paddingRight: '16px',
          },
          '@media (min-width: 900px)': {
            paddingLeft: '24px',
            paddingRight: '24px',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          '@media (max-width:600px)': {
            borderRadius: '8px',
            margin: '8px 0',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
          '@media (max-width:600px)': {
            fontSize: '0.875rem',
            padding: '8px 16px',
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          '@media (max-width:600px)': {
            margin: '8px',
            width: 'calc(100% - 16px)',
            maxHeight: 'calc(100% - 16px)',
            borderRadius: '12px',
          },
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          '@media (max-width:600px)': {
            fontSize: '1.125rem',
            padding: '12px 16px',
          },
        },
      },
    },
    MuiDialogContent: {
      styleOverrides: {
        root: {
          '@media (max-width:600px)': {
            padding: '8px 16px',
          },
        },
      },
    },
    MuiDialogActions: {
      styleOverrides: {
        root: {
          '@media (max-width:600px)': {
            padding: '8px 16px 16px',
            gap: '8px',
            '& .MuiButton-root': {
              fontSize: '0.875rem',
              padding: '6px 12px',
            },
          },
        },
      },
    },
    MuiTable: {
      styleOverrides: {
        root: {
          '@media (max-width:600px)': {
            fontSize: '0.75rem',
          },
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <ConfigurationProvider autoLoad={true}>
          <Router>
          <Routes>
          {/* All login is now handled via popup - no separate login routes needed */}

          {/* Routes with Layout */}
          <Route path="/*" element={
            <Layout>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/about" element={<About />} />
                <Route path="/academics" element={<Academics />} />
                <Route path="/admissions" element={<Admissions />} />
                <Route path="/faculty" element={<Faculty />} />
                <Route path="/gallery" element={<Gallery />} />
                <Route path="/contact" element={<Contact />} />
                {/* <Route path="/config-test" element={<ConfigurationTest />} /> */}
                <Route path="/admin" element={<div>Please use /admin/login to access admin panel</div>} />

                {/* Protected Admin Routes */}
                <Route path="/admin/dashboard" element={
                  <ProtectedRoute requiredRole="ADMIN">
                    <AdminDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/admin/fees" element={
                  <ProtectedRoute requiredRole="ADMIN">
                    <FeesManagement />
                  </ProtectedRoute>
                } />
                <Route path="/admin/leaves" element={
                  <ProtectedRoute requiredRole="ADMIN">
                    <LeaveManagement />
                  </ProtectedRoute>
                } />
                <Route path="/admin/expenses" element={
                  <ProtectedRoute requiredRole="ADMIN">
                    <ExpenseManagement />
                  </ProtectedRoute>
                } />
                <Route path="/admin/students" element={
                  <ProtectedRoute requiredRole="ADMIN">
                    <StudentProfiles />
                  </ProtectedRoute>
                } />
                <Route path="/admin/teachers" element={
                  <ProtectedRoute requiredRole="ADMIN">
                    <TeacherProfiles />
                  </ProtectedRoute>
                } />

                {/* Teacher Routes */}
                <Route path="/teacher/dashboard" element={
                  <ProtectedRoute requiredRole="TEACHER">
                    <TeacherDashboard />
                  </ProtectedRoute>
                } />

                {/* Student Routes */}
                <Route path="/student/dashboard" element={
                  <ProtectedRoute requiredRole="STUDENT">
                    <StudentDashboard />
                  </ProtectedRoute>
                } />

                {/* Profile Route */}
                <Route path="/profile" element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                } />

                {/* Catch-all route for authenticated users */}
                <Route path="*" element={<Home />} />
              </Routes>
            </Layout>
          } />
          </Routes>
        </Router>
        </ConfigurationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
