import '@/styles/globals.css'
import '@/styles/animations.css'
import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { AppLayout } from '@/layouts/AppLayout'
import { Dashboard } from '@/pages/Dashboard'
import { RouteOptimization } from '@/pages/RouteOptimization'
import { VesselMonitoring } from '@/pages/VesselMonitoring'
import { Analytics } from '@/pages/Analytics'
import { Settings } from '@/pages/Settings'

const LayoutWrapper = () => (
  <AppLayout>
    <Outlet />
  </AppLayout>
)

export function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route element={<LayoutWrapper />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/optimize" element={<RouteOptimization />} />
            <Route path="/monitoring" element={<VesselMonitoring />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </Router>
    </ErrorBoundary>
  )
}
