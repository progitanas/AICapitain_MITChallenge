import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/Card';
import { Button } from '../components/Button';
import { Input, Select } from '../components/Input';
import { Badge } from '../components/Badge';

export const Settings: React.FC = () => {
  const [saved, setSaved] = React.useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50">Settings</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">Manage your account and preferences.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          {/* Account Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Account Settings</CardTitle>
              <CardDescription>Manage your account information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input label="Full Name" defaultValue="Captain John Smith" />
              <Input label="Email" type="email" defaultValue="john.smith@aicaptain.com" />
              <Input label="Phone" type="tel" defaultValue="+1 (555) 000-0000" />
            </CardContent>
            <CardFooter>
              <Button onClick={handleSave}>{saved ? 'Saved!' : 'Save Changes'}</Button>
            </CardFooter>
          </Card>

          {/* Preferences */}
          <Card>
            <CardHeader>
              <CardTitle>Preferences</CardTitle>
              <CardDescription>Customize your experience</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select
                label="Optimization Mode"
                options={[
                  { value: 'balanced', label: 'Balanced (Default)' },
                  { value: 'fastest', label: 'Fastest Routes' },
                  { value: 'economical', label: 'Most Economical' },
                  { value: 'eco', label: 'Eco-Friendly' },
                ]}
                defaultValue="balanced"
              />
              <Select
                label="Distance Units"
                options={[
                  { value: 'nm', label: 'Nautical Miles' },
                  { value: 'km', label: 'Kilometers' },
                  { value: 'miles', label: 'Miles' },
                ]}
                defaultValue="nm"
              />
              <Select
                label="Speed Units"
                options={[
                  { value: 'knots', label: 'Knots' },
                  { value: 'kmh', label: 'Kilometers per Hour' },
                  { value: 'mph', label: 'Miles per Hour' },
                ]}
                defaultValue="knots"
              />
            </CardContent>
            <CardFooter>
              <Button onClick={handleSave}>{saved ? 'Saved!' : 'Save Preferences'}</Button>
            </CardFooter>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <CardTitle>Notifications</CardTitle>
              <CardDescription>Control how you receive alerts</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { label: 'Route Optimization Complete', enabled: true },
                { label: 'Vessel Alerts', enabled: true },
                { label: 'Weather Warnings', enabled: true },
                { label: 'Forecast Updates', enabled: false },
              ].map((notif) => (
                <label key={notif.label} className="flex items-center gap-3">
                  <input type="checkbox" defaultChecked={notif.enabled} className="h-4 w-4 rounded" />
                  <span className="text-sm text-gray-900 dark:text-gray-50">{notif.label}</span>
                </label>
              ))}
            </CardContent>
            <CardFooter>
              <Button onClick={handleSave}>{saved ? 'Saved!' : 'Save Notifications'}</Button>
            </CardFooter>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* API Keys */}
          <Card>
            <CardHeader>
              <CardTitle>API Keys</CardTitle>
              <CardDescription>Manage integrations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between rounded-lg bg-gray-100 p-2 dark:bg-gray-700">
                  <code className="text-xs text-gray-600 dark:text-gray-400">sk_live_4nJ9xK2...</code>
                  <Badge variant="success" size="sm">
                    Active
                  </Badge>
                </div>
              </div>
              <Button variant="outline" size="sm" className="mt-3 w-full">
                Generate New Key
              </Button>
            </CardContent>
          </Card>

          {/* Subscription */}
          <Card>
            <CardHeader>
              <CardTitle>Subscription</CardTitle>
              <CardDescription>Current plan</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">Plan</p>
                <p className="font-semibold text-gray-900 dark:text-gray-50">Professional</p>
                <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">Next billing</p>
                <p className="font-semibold text-gray-900 dark:text-gray-50">December 9, 2025</p>
              </div>
              <Button variant="outline" size="sm" className="mt-4 w-full">
                Manage Billing
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Settings;
