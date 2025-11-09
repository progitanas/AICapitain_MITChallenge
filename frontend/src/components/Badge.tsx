import React from 'react';
import { cn } from '../utils/cn';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md';
  children: React.ReactNode;
}

const variantClasses = {
  default: 'bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-gray-50',
  primary: 'bg-blue-100 text-blue-900 dark:bg-blue-900/30 dark:text-blue-300',
  success: 'bg-green-100 text-green-900 dark:bg-green-900/30 dark:text-green-300',
  warning: 'bg-yellow-100 text-yellow-900 dark:bg-yellow-900/30 dark:text-yellow-300',
  danger: 'bg-red-100 text-red-900 dark:bg-red-900/30 dark:text-red-300',
};

const sizeClasses = {
  sm: 'px-2 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
};

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', size = 'sm', children, ...props }, ref) => (
    <span
      ref={ref}
      className={cn('inline-flex items-center rounded-full font-medium', variantClasses[variant], sizeClasses[size], className)}
      {...props}
    >
      {children}
    </span>
  )
);

Badge.displayName = 'Badge';

interface AvatarProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src?: string;
  alt: string;
  fallback?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeAvatarClasses = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
};

export const Avatar = React.forwardRef<HTMLDivElement, AvatarProps & { children?: React.ReactNode }>(
  ({ src, alt, fallback, size = 'md', className, children, ...props }, ref) => {
    const [imageError, setImageError] = React.useState(!src);

    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-blue-400 to-blue-600 font-semibold text-white',
          sizeAvatarClasses[size],
          className
        )}
        {...(props as React.HTMLAttributes<HTMLDivElement>)}
      >
        {!imageError && src ? (
          <img
            src={src}
            alt={alt}
            className="h-full w-full object-cover"
            onError={() => setImageError(true)}
          />
        ) : (
          children || fallback || alt.charAt(0).toUpperCase()
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';
