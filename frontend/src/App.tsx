import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import AdminDashboard from './pages/AdminDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import StudentDashboard from './pages/StudentDashboard';
import ParentDashboard from './pages/ParentDashboard';
import AttendancePage from './pages/AttendancePage';
import MarkAttendancePage from './pages/MarkAttendancePage';
import LeavePage from './pages/LeavePage';
import NotificationsPage from './pages/NotificationsPage';
import ReportsPage from './pages/ReportsPage';
import UserManagementPage from './pages/admin/UserManagementPage';
import CourseManagementPage from './pages/admin/CourseManagementPage';
import DepartmentPage from './pages/admin/DepartmentPage';

function DashboardRouter() {
  const { user } = useAuth();
  if (!user) return null;
  if (user.role === 'admin') return <AdminDashboard />;
  if (user.role === 'teacher') return <TeacherDashboard />;
  if (user.role === 'student') return <StudentDashboard />;
  if (user.role === 'parent') return <ParentDashboard />;
  return null;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/dashboard" element={<DashboardRouter />} />
                <Route path="/attendance" element={<AttendancePage />} />
                <Route
                  path="/mark-attendance"
                  element={
                    <ProtectedRoute roles={['admin', 'teacher']}>
                      <MarkAttendancePage />
                    </ProtectedRoute>
                  }
                />
                <Route path="/leaves" element={<LeavePage />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route
                  path="/reports"
                  element={
                    <ProtectedRoute roles={['admin', 'teacher']}>
                      <ReportsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/users"
                  element={
                    <ProtectedRoute roles={['admin']}>
                      <UserManagementPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/courses"
                  element={
                    <ProtectedRoute roles={['admin']}>
                      <CourseManagementPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/departments"
                  element={
                    <ProtectedRoute roles={['admin']}>
                      <DepartmentPage />
                    </ProtectedRoute>
                  }
                />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" />
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
