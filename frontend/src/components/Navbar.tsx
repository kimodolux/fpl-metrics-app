import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

export const Navbar = () => {
  const { user, logout } = useAuthStore();
  const location = useLocation();

  const handleLogout = () => {
    logout();
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const linkClass = (path: string) => {
    return isActive(path)
      ? 'text-primary-600 hover:text-primary-700 px-3 py-2 rounded-md text-sm font-medium'
      : 'text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium';
  };

  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-semibold text-gray-900">
              Fantasy Football Analytics
            </h1>
            <div className="flex space-x-4">
              <Link to="/dashboard" className={linkClass('/dashboard')}>
                Dashboard
              </Link>
              <Link to="/teams" className={linkClass('/teams')}>
                Teams
              </Link>
              <Link to="/players" className={linkClass('/players')}>
                Players
              </Link>
              {user?.managerId && (
                <Link to={`/manager/${user.managerId}`} className={linkClass(`/manager/${user.managerId}`)}>
                  Manager
                </Link>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/settings" className="text-sm text-gray-700 hover:text-primary-600">
              {user?.email}
            </Link>
            <button
              onClick={handleLogout}
              className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
