import React from 'react';
import { cn } from '../utils/cn';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
};

export const Modal = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  size = 'md',
}: ModalProps) => {
  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/50 transition-opacity" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className={cn('w-full rounded-lg bg-white p-6 shadow-2xl dark:bg-gray-800', sizeClasses[size])}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-50">{title}</h2>
            {description && <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{description}</p>}
          </div>

          {children && <div className="mb-6 text-gray-700 dark:text-gray-300">{children}</div>}

          {footer && <div className="border-t border-gray-200 pt-4 dark:border-gray-700">{footer}</div>}
        </div>
      </div>
    </>
  );
};

export const useModal = (initialState = false) => {
  const [isOpen, setIsOpen] = React.useState(initialState);

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen((prev) => !prev),
  };
};
