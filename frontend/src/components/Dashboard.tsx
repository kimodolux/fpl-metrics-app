import { useAuthStore } from '../stores/authStore';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const { user } = useAuthStore();

  return (
    <>
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
                    Teams
                  </h3>
                  <p className="text-gray-600 text-sm">
                    View all Premier League teams and their statistics
                  </p>
                  <Link
                    to="/teams"
                    className="mt-4 inline-block bg-primary-600 text-white px-4 py-2 rounded-md text-sm hover:bg-primary-700"
                  >
                    View Teams
                  </Link>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Player Analytics
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Analyse player performance and statistics
                  </p>
                  <Link
                    to="/players"
                    className="mt-4 inline-block bg-primary-600 text-white px-4 py-2 rounded-md text-sm hover:bg-primary-700"
                  >
                    View Players
                  </Link>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Team Planner
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Create teams and plan for future weeks
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
                  <p>Manager ID: {user?.managerId}</p>
                  <p>Teams: {user?.teamCount || 0}</p>
                </div>
              </div>
            </div>
          </div>
    </>
  );
};