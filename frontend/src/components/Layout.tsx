import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNotifications } from '../hooks/useNotifications';
import type { ReactNode } from 'react';

const roleLinks: Record<string, { to: string; label: string }[]> = {
  admin: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/attendance', label: 'Attendance' },
    { to: '/leaves', label: 'Leaves' },
    { to: '/reports', label: 'Reports' },
    { to: '/notifications', label: 'Notifications' },
    { to: '/admin/users', label: 'Users' },
    { to: '/admin/courses', label: 'Courses' },
    { to: '/admin/departments', label: 'Departments' },
  ],
  teacher: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/attendance', label: 'Attendance' },
    { to: '/mark-attendance', label: 'Mark Attendance' },
    { to: '/leaves', label: 'Leaves' },
    { to: '/reports', label: 'Reports' },
    { to: '/notifications', label: 'Notifications' },
  ],
  student: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/leaves', label: 'My Leaves' },
    { to: '/notifications', label: 'Notifications' },
  ],
  parent: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/notifications', label: 'Notifications' },
  ],
};

export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { unreadCount } = useNotifications();

  const links = roleLinks[user?.role ?? 'student'] ?? [];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <span className="text-sm font-bold text-blue-700 tracking-wide uppercase">Attendance</span>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/dashboard'}
              className={({ isActive }) =>
                `block px-3 py-2 rounded text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
          <span className="text-sm font-medium text-gray-700">
            {user?.name} &nbsp;
            <span className="text-xs text-gray-400 capitalize">({user?.role})</span>
          </span>
          <NavLink
            to="/notifications"
            className="relative text-gray-500 hover:text-blue-700 text-sm px-2 py-1 rounded"
          >
            🔔
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </NavLink>
        </header>

        {/* Content */}
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
