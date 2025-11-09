import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/Card';

export const Analytics: React.FC = () => {
  const stats = [
    { label: 'Total Distance Optimized', value: '45,230', unit: 'NM', change: '+15%' },
    { label: 'Fuel Cost Savings', value: '285,450', unit: 'USD', change: '+23%' },
    { label: 'Carbon Emissions Reduced', value: '1,245', unit: 'tons CO2', change: '+18%' },
    { label: 'Routes Analyzed', value: '892', unit: 'routes', change: '+42%' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50">Analytics</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">Performance metrics and historical trends.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
              <div className="mt-2 flex items-baseline gap-2">
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-50">{stat.value}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">{stat.unit}</p>
              </div>
              <p className="mt-2 text-xs font-semibold text-green-600 dark:text-green-400">{stat.change} this month</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Monthly Trends</CardTitle>
            <CardDescription>Optimization metrics over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700">
              <p className="text-gray-600 dark:text-gray-400">Chart placeholder - Recharts integration</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Routes</CardTitle>
            <CardDescription>Most optimized routes this month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {['Singapore → Rotterdam', 'Shanghai → Los Angeles', 'Rotterdam → Singapore'].map((route, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-50">{route}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{45 - i * 5} times</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Analytics;
