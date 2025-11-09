import React from 'react'

interface TopbarProps {
  onMenuClick?: () => void
  onSidebarToggle?: () => void
}

export const Topbar: React.FC<TopbarProps> = ({ onMenuClick, onSidebarToggle }) => {
  const handleToggle = onMenuClick || onSidebarToggle

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6 dark:border-gray-700 dark:bg-gray-800">
      <button onClick={handleToggle} className="lg:hidden">
        <svg
          className="h-6 w-6 text-gray-600 dark:text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>

      <div className="flex items-center gap-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500 text-white font-semibold text-sm">
          CS
        </div>
        <div>
          <p className="text-sm font-medium text-gray-900 dark:text-gray-50">Captain Smith</p>
          <p className="text-xs text-gray-600 dark:text-gray-400">Fleet Manager</p>
        </div>
      </div>
    </header>
  )
}
