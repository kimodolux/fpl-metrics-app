import { useAuthStore } from '../stores/authStore';

export const Dashboard = () => {
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Fantasy Football Analytics
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.username}!
              </span>
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

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Welcome to your Dashboard
              </h2>
              <p className="text-gray-600 mb-6">
                This is where you'll analyze player statistics and manage your fantasy teams.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Player Analytics
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Analyze player performance and statistics
                  </p>
                  <button className="mt-4 bg-primary-600 text-white px-4 py-2 rounded-md text-sm hover:bg-primary-700">
                    Coming Soon
                  </button>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Team Builder
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Create and manage your fantasy teams
                  </p>
                  <button className="mt-4 bg-primary-600 text-white px-4 py-2 rounded-md text-sm hover:bg-primary-700">
                    Coming Soon
                  </button>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Player Comparison
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Compare players side by side
                  </p>
                  <button className="mt-4 bg-primary-600 text-white px-4 py-2 rounded-md text-sm hover:bg-primary-700">
                    Coming Soon
                  </button>
                </div>
              </div>
              
              <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 mb-2">
                  Account Information
                </h4>
                <div className="text-sm text-blue-800">
                  <p>Email: {user?.email}</p>
                  <p>Username: {user?.username}</p>
                  <p>Teams: {user?.teamCount || 0}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};