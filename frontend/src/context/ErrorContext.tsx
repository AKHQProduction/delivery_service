import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { setApiErrorHandler } from "../config/api.config";

interface ErrorContextType {
  showError: (message: string, details?: string) => void;
  showSuccess: (message: string) => void;
  showWarning: (message: string) => void;
}

interface ApiErrorHandler {
  (message: string, details?: string): void;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

// eslint-disable-next-line react-refresh/only-export-components
export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error("useError must be used within ErrorProvider");
  }
  return context;
};

interface Toast {
  id: string;
  type: "error" | "success" | "warning";
  message: string;
  details?: string;
}

export const ErrorProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((type: Toast["type"], message: string, details?: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, message, details }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, 5000);
  }, []);

  const showError = useCallback(
    (message: string, details?: string) => {
      addToast("error", message, details);
    },
    [addToast],
  );

  const showSuccess = useCallback(
    (message: string) => {
      addToast("success", message);
    },
    [addToast],
  );

  const showWarning = useCallback(
    (message: string) => {
      addToast("warning", message);
    },
    [addToast],
  );

  const showErrorRef = useRef(showError);

  useEffect(() => {
    showErrorRef.current = showError;
  }, [showError]);

  useEffect(() => {
    const handler: ApiErrorHandler = (message: string, details?: string) => {
      showErrorRef.current(message, details);
    };
    setApiErrorHandler(handler);
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return (
    <ErrorContext.Provider value={{ showError, showSuccess, showWarning }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ErrorContext.Provider>
  );
};

interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

const toastStyles: Record<
  Toast["type"],
  { shell: string; icon: string; Icon: React.FC<{ className?: string }> }
> = {
  success: {
    shell: "border-green-200 bg-green-50",
    icon: "bg-green-100 text-green-600",
    Icon: SuccessIcon,
  },
  error: {
    shell: "border-red-200 bg-red-50",
    icon: "bg-red-100 text-red-600",
    Icon: ErrorIcon,
  },
  warning: {
    shell: "border-amber-200 bg-amber-50",
    icon: "bg-amber-100 text-amber-600",
    Icon: WarningIcon,
  },
};

const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onRemove }) => {
  if (toasts.length === 0) return null;

  return createPortal(
    <div className="pointer-events-none fixed inset-x-4 top-4 z-[99999] flex flex-col gap-3 sm:left-auto sm:right-4 sm:w-[380px]">
      {toasts.map((toast) => {
        const style = toastStyles[toast.type];
        const Icon = style.Icon;

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto animate-slide-in rounded-lg border px-4 py-3 shadow-lg shadow-slate-900/10 ${style.shell}`}
          >
            <div className="flex gap-3">
              <span
                className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${style.icon}`}
              >
                <Icon className="h-4 w-4" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="break-words text-sm font-semibold leading-5 text-slate-950">
                  {toast.message}
                </p>
                {toast.details && (
                  <p className="mt-1 break-words text-sm leading-5 text-slate-600">
                    {toast.details}
                  </p>
                )}
              </div>
              <button
                type="button"
                onClick={() => onRemove(toast.id)}
                className="-mr-1 -mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-slate-500 hover:bg-white/70 hover:text-slate-700"
                aria-label="Закрити повідомлення"
              >
                <CloseIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>,
    document.body,
  );
};

function SuccessIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="m4.5 12.75 6 6 9-13.5"
      />
    </svg>
  );
}

function ErrorIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18 18 6M6 6l12 12" />
    </svg>
  );
}

function WarningIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 9v4m0 4h.01M10.3 4.5 2.9 17.25A1.5 1.5 0 0 0 4.2 19.5h15.6a1.5 1.5 0 0 0 1.3-2.25L13.7 4.5a1.5 1.5 0 0 0-2.6 0Z"
      />
    </svg>
  );
}

function CloseIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18 18 6M6 6l12 12" />
    </svg>
  );
}
