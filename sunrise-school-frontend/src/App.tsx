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
import Profile from './pages/Profile';
// import ConfigurationTest from './components/common/ConfigurationTest';

import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { ConfigurationProvider } from './contexts/ConfigurationContext';

// Create a custom theme
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
    },
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 600,
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

                {/* Teacher Routes - Redirect to home */}
                <Route path="/teacher/dashboard" element={
                  <ProtectedRoute>
                    <Home />
                  </ProtectedRoute>
                } />

                {/* Student Routes - Redirect to home */}
                <Route path="/student/dashboard" element={
                  <ProtectedRoute>
                    <Home />
                  </ProtectedRoute>
                } />

                {/* Profile Route */}
                <Route path="/profile" element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                } />
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
