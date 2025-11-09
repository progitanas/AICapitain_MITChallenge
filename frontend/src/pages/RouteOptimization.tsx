import React from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/Card'
import { Button } from '../components/Button'
import { Input, Select } from '../components/Input'
import { Spinner } from '../components/Spinner'
import { Alert, AlertTitle, AlertDescription } from '../components/Alert'
import { optimizeRoute, getWaypoints, Waypoint, parseApiError } from '../services/api'

export const RouteOptimization: React.FC = () => {
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [result, setResult] = React.useState<any>(null)
  const [waypoints, setWaypoints] = React.useState<Waypoint[]>([])

  const [formData, setFormData] = React.useState({
    vessel_name: 'Maritime Explorer',
    mmsi: '636016829',
    imo: '9123456',
    call_sign: 'CALL1',
    length_m: '190',
    beam_m: '32',
    draught_m: '11',
    depth_m: '18',
    type_code: '70',
    latitude: '1.3521',
    longitude: '103.8198',
    sog_knots: '15',
    cog_degrees: '90',
    heading_degrees: '88',
    nav_status: '0',
    start_port: '',
    end_port: '',
    fuel_price: '500',
    weight_time: '1',
    weight_cost: '1',
    weight_risk: '1',
  })

  // Load waypoints on mount
  React.useEffect(() => {
    const loadWaypoints = async () => {
      try {
        const data = await getWaypoints()
        setWaypoints(data)
        if (data.length > 0) {
          setFormData((prev) => ({
            ...prev,
            start_port: data[0].id,
            end_port: data[Math.min(1, data.length - 1)].id,
          }))
        }
      } catch (err) {
        console.error('Error loading waypoints:', err)
      }
    }
    loadWaypoints()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await optimizeRoute({
        vessel: {
          mmsi: formData.mmsi,
          imo: formData.imo,
          name: formData.vessel_name,
          call_sign: formData.call_sign,
          dimensions: {
            length_m: parseFloat(formData.length_m),
            beam_m: parseFloat(formData.beam_m),
            draught_m: parseFloat(formData.draught_m),
            depth_m: parseFloat(formData.depth_m),
          },
          type_code: parseInt(formData.type_code),
          latitude: parseFloat(formData.latitude),
          longitude: parseFloat(formData.longitude),
          sog_knots: parseFloat(formData.sog_knots),
          cog_degrees: parseFloat(formData.cog_degrees),
          heading_degrees: parseFloat(formData.heading_degrees),
          nav_status: parseInt(formData.nav_status),
        },
        start_port_id: formData.start_port,
        end_port_id: formData.end_port,
        weight_time: parseFloat(formData.weight_time),
        weight_cost: parseFloat(formData.weight_cost),
        weight_risk: parseFloat(formData.weight_risk),
        fuel_price_per_ton: parseFloat(formData.fuel_price),
      })

      setResult(response)
    } catch (err: any) {
      const apiError = parseApiError(err)
      setError(apiError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50">Route Optimization</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Calculate optimal maritime routes with advanced algorithms.
        </p>
      </div>

      {error && (
        <Alert variant="error" onClose={() => setError(null)}>
          <AlertTitle>Erreur d'optimisation</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Form */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Route Parameters</CardTitle>
              <CardDescription>Enter vessel and route details</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Vessel Info */}
                <div className="space-y-3 border-b pb-4">
                  <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Vessel Information
                  </p>
                  <Input
                    label="Vessel Name"
                    value={formData.vessel_name}
                    onChange={(e) => setFormData({ ...formData, vessel_name: e.target.value })}
                  />
                  <Input
                    label="MMSI"
                    value={formData.mmsi}
                    onChange={(e) => setFormData({ ...formData, mmsi: e.target.value })}
                  />
                  <Input
                    label="Length (m)"
                    type="number"
                    value={formData.length_m}
                    onChange={(e) => setFormData({ ...formData, length_m: e.target.value })}
                  />
                  <Input
                    label="Beam (m)"
                    type="number"
                    value={formData.beam_m}
                    onChange={(e) => setFormData({ ...formData, beam_m: e.target.value })}
                  />
                </div>

                {/* Route Info */}
                <div className="space-y-3 border-b pb-4">
                  <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">Route</p>
                  <Select
                    label="Start Port"
                    options={waypoints.map((wp) => ({ value: wp.id, label: wp.name }))}
                    value={formData.start_port}
                    onChange={(e) => setFormData({ ...formData, start_port: e.target.value })}
                  />
                  <Select
                    label="End Port"
                    options={waypoints.map((wp) => ({ value: wp.id, label: wp.name }))}
                    value={formData.end_port}
                    onChange={(e) => setFormData({ ...formData, end_port: e.target.value })}
                  />
                </div>

                {/* Optimization */}
                <div className="space-y-3">
                  <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Optimization Weights
                  </p>

                  {/* Weight Time */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm text-gray-600 dark:text-gray-400">
                        Time: {formData.weight_time}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        value={formData.weight_time}
                        onChange={(e) => setFormData({ ...formData, weight_time: e.target.value })}
                        className="w-24"
                      />
                    </div>
                  </div>

                  {/* Weight Cost */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm text-gray-600 dark:text-gray-400">
                        Cost: {formData.weight_cost}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        value={formData.weight_cost}
                        onChange={(e) => setFormData({ ...formData, weight_cost: e.target.value })}
                        className="w-24"
                      />
                    </div>
                  </div>

                  {/* Weight Risk */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm text-gray-600 dark:text-gray-400">
                        Risk: {formData.weight_risk}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        value={formData.weight_risk}
                        onChange={(e) => setFormData({ ...formData, weight_risk: e.target.value })}
                        className="w-24"
                      />
                    </div>
                  </div>

                  <Input
                    label="Fuel Price ($/ton)"
                    type="number"
                    step="0.1"
                    value={formData.fuel_price}
                    onChange={(e) => setFormData({ ...formData, fuel_price: e.target.value })}
                  />
                </div>

                <Button type="submit" className="w-full" isLoading={loading}>
                  {loading ? 'Calculating...' : 'Calculate Route'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Results */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Optimization Results</CardTitle>
              <CardDescription>Recommended route with detailed metrics</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-12">
                  <Spinner size="lg" />
                </div>
              ) : result ? (
                <div className="space-y-6">
                  {/* Waypoints */}
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-gray-50 mb-3">
                      Route Waypoints
                    </h3>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {result.waypoints.map((wp: any, idx: number) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between rounded-lg bg-gray-50 p-2 dark:bg-gray-800"
                        >
                          <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                              {idx + 1}. {wp.name}
                            </p>
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                              {wp.lat.toFixed(4)}, {wp.lon.toFixed(4)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Distance</p>
                      <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-gray-50">
                        {result.metrics.distance_nm.toFixed(0)} NM
                      </p>
                    </div>
                    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Time</p>
                      <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-gray-50">
                        {(result.metrics.time_hours / 24).toFixed(1)} days
                      </p>
                    </div>
                    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Fuel Cost</p>
                      <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-gray-50">
                        USD {result.metrics.cost_usd.toFixed(0)}
                      </p>
                    </div>
                    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Risk Score</p>
                      <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-gray-50">
                        {result.metrics.risk_score.toFixed(2)}
                      </p>
                    </div>
                  </div>

                  {/* Blockages */}
                  {result.blockages && result.blockages.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-gray-50 mb-3">
                        Chokepoint Risks
                      </h3>
                      <div className="space-y-2">
                        {result.blockages.map((block: any, idx: number) => (
                          <Alert key={idx} variant="warning">
                            <AlertTitle>{block.chokepoint}</AlertTitle>
                            <AlertDescription>{block.recommendation}</AlertDescription>
                          </Alert>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <Button variant="primary" className="flex-1">
                      Deploy Route
                    </Button>
                    <Button variant="secondary" className="flex-1">
                      Compare Alternatives
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center">
                  <p className="text-gray-600 dark:text-gray-400">
                    Submit a form to calculate optimized routes
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default RouteOptimization
