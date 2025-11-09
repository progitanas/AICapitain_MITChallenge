import React from 'react'
import { Card, CardContent } from '../components/Card'
import { Button } from '../components/Button'
import { Alert, AlertTitle, AlertDescription } from '../components/Alert'
import { Badge } from '../components/Badge'

export const VesselMonitoring: React.FC = () => {
  const vessels = [
    {
      id: 'vessel1',
      name: 'Maritime Explorer',
      mmsi: '636016829',
      status: 'sailing',
      position: { lat: 1.3521, lng: 103.8198 },
      speed: 18.5,
      course: 245,
      destination: 'Rotterdam',
      eta: '2025-11-22',
    },
    {
      id: 'vessel2',
      name: 'Ocean Navigator',
      mmsi: '636016830',
      status: 'anchored',
      position: { lat: 51.4769, lng: 3.6172 },
      speed: 0,
      course: 0,
      destination: 'Port of Rotterdam',
      eta: '2025-11-20',
    },
    {
      id: 'vessel3',
      name: 'Global Carrier',
      mmsi: '636016831',
      status: 'sailing',
      position: { lat: 31.387, lng: 30.1675 },
      speed: 16.2,
      course: 330,
      destination: 'Singapore',
      eta: '2025-12-05',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50">Vessel Monitoring</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Real-time tracking and monitoring of your fleet.
        </p>
      </div>

      <Alert variant="info">
        <AlertTitle>Live AIS Feed Active</AlertTitle>
        <AlertDescription>
          All vessels are being tracked in real-time. Updates every 30 seconds.
        </AlertDescription>
      </Alert>

      <div className="grid gap-4">
        {vessels.map((vessel) => (
          <Card key={vessel.id}>
            <CardContent className="pt-6">
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-gray-50">
                        {vessel.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        MMSI: {vessel.mmsi}
                      </p>
                    </div>
                    <Badge variant={vessel.status === 'sailing' ? 'success' : 'warning'}>
                      {vessel.status === 'sailing' ? 'Sailing' : 'Anchored'}
                    </Badge>
                  </div>

                  <div className="mt-3 grid gap-2 text-sm sm:grid-cols-2 md:grid-cols-4">
                    <div>
                      <p className="text-gray-600 dark:text-gray-400">Position</p>
                      <p className="font-medium text-gray-900 dark:text-gray-50">
                        {vessel.position.lat.toFixed(2)}, {vessel.position.lng.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600 dark:text-gray-400">Speed</p>
                      <p className="font-medium text-gray-900 dark:text-gray-50">
                        {vessel.speed} knots
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600 dark:text-gray-400">Course</p>
                      <p className="font-medium text-gray-900 dark:text-gray-50">
                        {vessel.course}°
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600 dark:text-gray-400">ETA</p>
                      <p className="font-medium text-gray-900 dark:text-gray-50">{vessel.eta}</p>
                    </div>
                  </div>

                  <div className="mt-3">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Destination:{' '}
                      <span className="font-medium text-gray-900 dark:text-gray-50">
                        {vessel.destination}
                      </span>
                    </p>
                  </div>
                </div>

                <div className="flex gap-2 md:flex-col">
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                  <Button variant="primary" size="sm">
                    Optimize Route
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default VesselMonitoring
