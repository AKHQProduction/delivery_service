// context/ErrorContext.tsx
import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useRef,
} from "react";
import { createPortal } from "react-dom";
import { setApiErrorHandler } from "../config/api.config";

interface ErrorContextType {
  showError: (message: string, details?: string) => void;
  showSuccess: (message: string) => void;
  showWarning: (message: string) => void;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

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

export const ErrorProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback(
    (type: Toast["type"], message: string, details?: string) => {
      const id = Math.random().toString(36).substring(2, 9);
      console.log('Adding toast:', { type, message, details });
      setToasts((prev) => [...prev, { id, type, message, details }]);

      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
      }, 5000);
    },
    [],
  );

  const showError = useCallback(
    (message: string, details?: string) => {
      console.log('showError called:', { message, details });
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

  // Use ref to keep the latest showError function
  const showErrorRef = useRef(showError);
  
  useEffect(() => {
    showErrorRef.current = showError;
  }, [showError]);

  // Connect API error handler on mount only once
  useEffect(() => {
    console.log('Setting up API error handler');
    setApiErrorHandler((message: string, details?: string) => {
      console.log('API error handler called:', { message, details });
      showErrorRef.current(message, details);
    });
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

// Toast Component - now using Portal
interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

const ToastContainer: React.FC<ToastContainerProps> = ({
  toasts,
  onRemove,
}) => {
  if (toasts.length === 0) return null;

  // Render toasts in a portal attached to document.body
  return createPortal(
    <div
      style={{
        position: 'fixed',
        top: '16px',
        right: '16px',
        zIndex: 999999, // Very high z-index
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        maxWidth: '400px',
        pointerEvents: 'none', // Allow clicks through container
      }}
    >
      {toasts.map((toast) => {
        const bgColor = 
          toast.type === 'error' ? '#ef4444' :
          toast.type === 'success' ? '#22c55e' :
          '#eab308';

        return (
          <div
            key={toast.id}
            style={{
              backgroundColor: bgColor,
              color: 'white',
              padding: '16px',
              borderRadius: '8px',
              boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
              minWidth: '300px',
              animation: 'slideIn 0.3s ease-out',
              pointerEvents: 'auto', // Re-enable clicks on toast itself
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <p style={{ fontWeight: 600, wordBreak: 'break-word', margin: 0 }}>
                    {toast.message}
                  </p>
                </div>
                {toast.details && (
                  <p style={{ 
                    fontSize: '14px', 
                    marginTop: '8px', 
                    marginBottom: 0,
                    marginLeft: '28px',
                    opacity: 0.9,
                    wordBreak: 'break-word',
                  }}>
                    {toast.details}
                  </p>
                )}
              </div>
              <button
                onClick={() => onRemove(toast.id)}
                style={{
                  color: 'white',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  fontSize: '20px',
                  lineHeight: '1',
                  opacity: 1,
                  transition: 'opacity 0.2s',
                }}
                onMouseEnter={(e) => e.currentTarget.style.opacity = '0.75'}
                onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                aria-label="Close"
              >
                ✕
              </button>
            </div>
          </div>
        );
      })}
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>,
    document.body // Render directly to body
  );
};