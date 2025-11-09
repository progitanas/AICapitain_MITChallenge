import { cn } from '../utils/cn'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  variant?: 'primary' | 'secondary' | 'white'
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
}

const variantClasses = {
  primary: 'border-blue-600 border-t-transparent',
  secondary: 'border-gray-300 border-t-gray-600 dark:border-gray-600 dark:border-t-gray-300',
  white: 'border-white border-t-transparent',
}

export const Spinner = ({ size = 'md', variant = 'primary' }: SpinnerProps) => {
  return (
    <div
      className={cn(
        'animate-spin rounded-full border-4',
        sizeClasses[size],
        variantClasses[variant]
      )}
      role="status"
      aria-label="Loading"
    />
  )
}

interface LoadingSkeletonProps {
  count?: number
  height?: string
}

export const LoadingSkeleton = ({ count = 1, height = 'h-6' }: LoadingSkeletonProps) => (
  <div className="space-y-3">
    {Array.from({ length: count }).map((_, i) => (
      <div
        key={i}
        className={cn('animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700', height)}
      />
    ))}
  </div>
)

interface PageLoadingProps {
  fullScreen?: boolean
}

export const PageLoading = ({ fullScreen = true }: PageLoadingProps) => {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4">
      <Spinner size="lg" variant="primary" />
      <p className="text-gray-600 dark:text-gray-400">Loading...</p>
    </div>
  )

  if (fullScreen) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white dark:bg-gray-900">
        {content}
      </div>
    )
  }

  return content
}
