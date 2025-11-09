import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/Card';
import { Spinner } from '../components/Spinner';
import { Alert, AlertTitle, AlertDescription } from '../components/Alert';

export const Dashboard: React.FC = () => {
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    // Simulate data loading
    setLoading(true);
    const timer = setTimeout(() => setLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const stats = [
    { label: 'Active Vessels', value: '24', change: '+3' },
    { label: 'Routes Optimized', value: '156', change: '+12' },
    { label: 'Distance Saved', value: '4,250 NM', change: '+450' },
    { label: 'Fuel Saved', value: '185 tons', change: '+23' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50">Dashboard</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">Welcome back. Here is your fleet overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                <p className="mt-2 text-2xl font-bold text-gray-900 dark:text-gray-50">{stat.value}</p>
              </div>
              <div className="text-right">
                <span className="inline-block rounded-lg bg-green-100 px-3 py-1 text-sm font-semibold text-green-700 dark:bg-green-900/30 dark:text-green-300">
                  {stat.change}
                </span>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Optimizations</CardTitle>
              <CardDescription>Latest route optimization results</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-8">
                  <Spinner />
                </div>
              ) : (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center justify-between border-b border-gray-200 pb-4 last:border-0 dark:border-gray-700">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-50">Route {i}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Optimized 2 hours ago</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-blue-600">+12.5% efficient</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">450 NM saved</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert variant="success">
                <AlertTitle>All Systems Operational</AlertTitle>
                <AlertDescription>No alerts or warnings</AlertDescription>
              </Alert>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">API</span>
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Database</span>
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">AIS Feed</span>
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
