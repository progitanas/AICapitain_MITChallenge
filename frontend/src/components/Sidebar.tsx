import React from 'react'
import { Link } from 'react-router-dom'
import { X, Ship, BarChart3, Route, Anchor, Settings, LogOut } from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const navItems = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Route Optimization', href: '/optimize', icon: Route },
    { name: 'Vessel Monitoring', href: '/monitoring', icon: Ship },
    { name: 'Analytics', href: '/analytics', icon: Anchor },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <>
      <div
        className={`fixed inset-0 z-40 bg-black/50 transition-opacity lg:hidden ${isOpen ? 'opacity-100' : 'pointer-events-none opacity-0'}`}
        onClick={onToggle}
      />
      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen w-64 flex-col bg-gray-900 text-white transition-transform lg:static lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between border-b border-gray-800 p-4">
          <div className="flex items-center gap-2">
            <Ship className="h-6 w-6 text-blue-400" />
            <span className="text-lg font-bold">AICaptain</span>
          </div>
          <button onClick={onToggle} className="lg:hidden">
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-2 p-4">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.href}
                to={item.href}
                className="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-300 transition-colors hover:bg-gray-800 hover:text-white"
              >
                <Icon className="h-5 w-5" />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>

        <div className="border-t border-gray-800 p-4">
          <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-gray-300 transition-colors hover:bg-gray-800 hover:text-white">
            <LogOut className="h-5 w-5" />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  )
}
