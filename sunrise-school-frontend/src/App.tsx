import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Typography } from '@mui/material';
import { SearchOff as NotFoundIcon } from '@mui/icons-material';
import theme, { brand } from './theme';
import MainLayout from './components/Layout/MainLayout';
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
import TransportManagement from './pages/admin/TransportManagement';
import GalleryManagement from './pages/admin/GalleryManagement';
import InventoryManagement from './pages/admin/InventoryManagement';
import StockProcurementManagement from './pages/admin/StockProcurementManagement';
import PricingManagement from './pages/admin/PricingManagement';
import StockLevelsManagement from './pages/admin/StockLevelsManagement';
import AttendanceManagement from './pages/admin/AttendanceManagement';
import StudentProfiles from './pages/admin/StudentProfiles';
import TeacherProfiles from './pages/admin/TeacherProfiles';
import StudentUDISEReport from './pages/admin/StudentUDISEReport';
import FeeTrackingReport from './pages/admin/FeeTrackingReport';
import DailyCollectionReport from './pages/admin/DailyCollectionReport';
import SessionProgression from './pages/admin/SessionProgression';
import TeacherDashboard from './pages/teacher/TeacherDashboard';
import TeacherLeaveManagementPage from './pages/teacher/TeacherLeaveManagementPage';
import TeacherStudentProfilesPage from './pages/teacher/TeacherStudentProfilesPage';
import TeacherAttendancePage from './pages/teacher/TeacherAttendancePage';
import StudentDashboard from './pages/student/StudentDashboard';
import StudentLeaveManagementPage from './pages/student/StudentLeaveManagementPage';
import StudentFeeManagementPage from './pages/student/StudentFeeManagementPage';
import StudentAttendancePage from './pages/student/StudentAttendancePage';
import ProfilePage from './pages/ProfilePage';
import AlertsPage from './pages/AlertsPage';
import PlatformLogin from './pages/platform/PlatformLogin';
import PlatformSchools from './pages/platform/PlatformSchools';

import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { ConfigurationProvider } from './contexts/ConfigurationContext';
import { SchoolProvider, useSchool } from './contexts/SchoolContext';

/** Shown instead of the school's site when its address belongs to no school, or the school is suspended. */
const SchoolProblem: React.FC<{ message: string }> = ({ message }) => (
  <Box
    sx={{
      minHeight: '100vh',
      display: 'grid',
      placeItems: 'center',
      p: 3,
      color: '#fff',
      textAlign: 'center',
      background: `linear-gradient(135deg, ${brand.navTop}, ${brand.navBottom})`,
    }}
  >
    <Box className="fade-up" sx={{ maxWidth: 460 }}>
      <NotFoundIcon sx={{ fontSize: 72, opacity: 0.85 }} />
      <Typography sx={{ mt: 1, fontSize: '1.6rem', fontWeight: 800 }}>{message}</Typography>
      <Typography sx={{ mt: 1, opacity: 0.75 }}>
        Check the web address, or ask your school office for the right link.
      </Typography>
    </Box>
  </Box>
);

/** The school's own site: public pages and the admin, teacher and student portals. */
const SchoolSite: React.FC = () => {
  const { problem } = useSchool();
  if (problem) return <SchoolProblem message={problem} />;

  return (
    <AuthProvider>
      <ConfigurationProvider autoLoad={true}>
        <Routes>
          {/* All login is handled by a popup; there are no separate login routes */}

          {/* Public pages, with the public menu and footer */}
          <Route path="/*" element={
            <MainLayout>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/about" element={<About />} />
                <Route path="/academics" element={<Academics />} />
                <Route path="/admissions" element={<Admissions />} />
                <Route path="/faculty" element={<Faculty />} />
                <Route path="/gallery" element={<Gallery />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="*" element={<Home />} />
              </Routes>
            </MainLayout>
          } />

          {/* Student portal */}
          <Route path="/student/dashboard" element={<ProtectedRoute requiredRole="STUDENT"><StudentDashboard /></ProtectedRoute>} />
          <Route path="/student/leaves" element={<ProtectedRoute requiredRole="STUDENT"><StudentLeaveManagementPage /></ProtectedRoute>} />
          <Route path="/student/fees" element={<ProtectedRoute requiredRole="STUDENT"><StudentFeeManagementPage /></ProtectedRoute>} />
          <Route path="/student/attendance" element={<ProtectedRoute requiredRole="STUDENT"><StudentAttendancePage /></ProtectedRoute>} />
          <Route path="/student/alerts" element={<ProtectedRoute requiredRole="STUDENT"><AlertsPage /></ProtectedRoute>} />

          {/* Teacher portal */}
          <Route path="/teacher/dashboard" element={<ProtectedRoute requiredRole="TEACHER"><TeacherDashboard /></ProtectedRoute>} />
          <Route path="/teacher/leaves" element={<ProtectedRoute requiredRole="TEACHER"><TeacherLeaveManagementPage /></ProtectedRoute>} />
          <Route path="/teacher/students" element={<ProtectedRoute requiredRole="TEACHER"><TeacherStudentProfilesPage /></ProtectedRoute>} />
          <Route path="/teacher/attendance" element={<ProtectedRoute requiredRole="TEACHER"><TeacherAttendancePage /></ProtectedRoute>} />
          <Route path="/teacher/alerts" element={<ProtectedRoute requiredRole="TEACHER"><AlertsPage /></ProtectedRoute>} />

          {/* For every logged-in user, inside their own portal */}
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="/alerts" element={<ProtectedRoute><AlertsPage /></ProtectedRoute>} />

          {/* Admin portal */}
          <Route path="/admin/dashboard" element={<ProtectedRoute requiredRole="ADMIN"><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/fees" element={<ProtectedRoute requiredRole="ADMIN"><FeesManagement /></ProtectedRoute>} />
          <Route path="/admin/transport" element={<ProtectedRoute requiredRole="ADMIN"><TransportManagement /></ProtectedRoute>} />
          <Route path="/admin/expenses" element={<ProtectedRoute requiredRole="ADMIN"><ExpenseManagement /></ProtectedRoute>} />
          <Route path="/admin/leaves" element={<ProtectedRoute requiredRole="ADMIN"><LeaveManagement /></ProtectedRoute>} />
          <Route path="/admin/shop-sales" element={<ProtectedRoute requiredRole="ADMIN"><InventoryManagement /></ProtectedRoute>} />
          <Route path="/admin/stock-procurement" element={<ProtectedRoute requiredRole="ADMIN"><StockProcurementManagement /></ProtectedRoute>} />
          <Route path="/admin/pricing" element={<ProtectedRoute requiredRole="ADMIN"><PricingManagement /></ProtectedRoute>} />
          <Route path="/admin/stock-levels" element={<ProtectedRoute requiredRole="ADMIN"><StockLevelsManagement /></ProtectedRoute>} />
          <Route path="/admin/attendance" element={<ProtectedRoute requiredRole="ADMIN"><AttendanceManagement /></ProtectedRoute>} />
          <Route path="/admin/gallery-management" element={<ProtectedRoute requiredRole="ADMIN"><GalleryManagement /></ProtectedRoute>} />
          <Route path="/admin/students" element={<ProtectedRoute requiredRole="ADMIN"><StudentProfiles /></ProtectedRoute>} />
          <Route path="/admin/teachers" element={<ProtectedRoute requiredRole="ADMIN"><TeacherProfiles /></ProtectedRoute>} />
          <Route path="/admin/alerts" element={<ProtectedRoute requiredRole="ADMIN"><AlertsPage /></ProtectedRoute>} />
          <Route path="/admin/reports/student-udise" element={<ProtectedRoute requiredRole="ADMIN"><StudentUDISEReport /></ProtectedRoute>} />
          <Route path="/admin/reports/fee-tracking" element={<ProtectedRoute requiredRole="ADMIN"><FeeTrackingReport /></ProtectedRoute>} />
          <Route path="/admin/reports/daily-collection" element={<ProtectedRoute requiredRole="ADMIN"><DailyCollectionReport /></ProtectedRoute>} />
          {/* SUPER_ADMIN only */}
          <Route path="/admin/session-progression" element={<ProtectedRoute requiredRole="SUPER_ADMIN" exactRoleMatch={true}><SessionProgression /></ProtectedRoute>} />
        </Routes>
      </ConfigurationProvider>
    </AuthProvider>
  );
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          {/* Platform admin: belongs to no school, with its own login */}
          <Route path="/platform/login" element={<PlatformLogin />} />
          <Route path="/platform/*" element={<PlatformSchools />} />

          <Route path="/*" element={<SchoolProvider><SchoolSite /></SchoolProvider>} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
