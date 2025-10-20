import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { api } from '../lib/api';
import type { ManagerHistoryResponse, GameweekHistory } from '../types/manager';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export const Manager = () => {
  const { managerId } = useParams<{ managerId: string }>();
  const { user, logout } = useAuthStore();
  const [managerData, setManagerData] = useState<GameweekHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchManagerData = async () => {
      if (!managerId) return;

      try {
        setLoading(true);
        const response = await api.get<ManagerHistoryResponse>(`/manager/${managerId}`);
        setManagerData(response.data.data.current);
        setError(null);
      } catch (err) {
        console.error('Error fetching manager data:', err);
        setError('Failed to load manager data');
      } finally {
        setLoading(false);
      }
    };

    fetchManagerData();
  }, [managerId]);

  const handleLogout = () => {
    logout();
  };

  // Transform data for the chart (invert overall_rank for better visualization)
  const chartData = managerData.map((gw) => ({
    gameweek: `GW${gw.event}`,
    rank: gw.overall_rank,
    points: gw.points,
    gwRank: gw.rank,
  }));

  // Find best and worst ranks
  const bestRank = managerData.length > 0
    ? Math.min(...managerData.map(gw => gw.overall_rank))
    : 0;
  const worstRank = managerData.length > 0
    ? Math.max(...managerData.map(gw => gw.overall_rank))
    : 0;
  const latestGW = managerData.length > 0
    ? managerData[managerData.length - 1]
    : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-semibold text-gray-900">
                Fantasy Football Analytics
              </h1>
              <div className="flex space-x-4">
                <Link
                  to="/dashboard"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Dashboard
                </Link>
                <Link
                  to="/teams"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Teams
                </Link>
              </div>
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
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Manager Stats - ID: {managerId}
            </h2>
            <p className="text-gray-600 mt-1">
              Overall rank progression and gameweek performance
            </p>
          </div>

          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p className="mt-4 text-gray-600">Loading manager data...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {!loading && !error && managerData.length > 0 && (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
                    Current Rank
                  </h3>
                  <p className="mt-2 text-3xl font-bold text-gray-900">
                    {latestGW?.overall_rank.toLocaleString()}
                  </p>
                  <p className="mt-1 text-sm text-gray-600">
                    Top {latestGW?.percentile_rank}%
                  </p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
                    Total Points
                  </h3>
                  <p className="mt-2 text-3xl font-bold text-gray-900">
                    {latestGW?.total_points.toLocaleString()}
                  </p>
                  <p className="mt-1 text-sm text-gray-600">
                    {managerData.length} gameweeks
                  </p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
                    Best Rank
                  </h3>
                  <p className="mt-2 text-3xl font-bold text-green-600">
                    {bestRank.toLocaleString()}
                  </p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
                    Worst Rank
                  </h3>
                  <p className="mt-2 text-3xl font-bold text-red-600">
                    {worstRank.toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Rank Progression Chart */}
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Overall Rank Progression
                </h3>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="gameweek" />
                    <YAxis
                      reversed
                      label={{ value: 'Overall Rank', angle: -90, position: 'insideLeft' }}
                      tickFormatter={(value) => value.toLocaleString()}
                    />
                    <Tooltip
                      formatter={(value: number) => value.toLocaleString()}
                      labelStyle={{ color: '#111827' }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="rank"
                      stroke="#2563eb"
                      strokeWidth={2}
                      name="Overall Rank"
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Lower is better - Y-axis is reversed
                </p>
              </div>

              {/* Gameweek Details Table */}
              <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg font-medium text-gray-900">
                    Gameweek Details
                  </h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Gameweek
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          GW Points
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Total Points
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          GW Rank
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Overall Rank
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Team Value
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Transfers
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Bench Points
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {managerData.map((gw) => (
                        <tr key={gw.event} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {gw.event}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {gw.points}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {gw.total_points.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {gw.rank.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {gw.overall_rank.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            £{(gw.value / 10).toFixed(1)}m
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {gw.event_transfers > 0 && (
                              <span className={gw.event_transfers_cost > 0 ? 'text-red-600' : ''}>
                                {gw.event_transfers} {gw.event_transfers_cost > 0 ? `(-${gw.event_transfers_cost})` : ''}
                              </span>
                            )}
                            {gw.event_transfers === 0 && '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {gw.points_on_bench}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {!loading && !error && managerData.length === 0 && (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-600">No manager data found</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
