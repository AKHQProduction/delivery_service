import { useState, useCallback } from "react";
import type { ToastType } from "../components/ui/Toast";

interface ToastState {
  message: string;
  type: ToastType;
  isVisible: boolean;
}

export const useToast = () => {
  const [toast, setToast] = useState<ToastState>({
    message: "",
    type: "success",
    isVisible: false,
  });

  const showToast = useCallback((message: string, type: ToastType = "success") => {
    setToast({ message, type, isVisible: true });
  }, []);

  const hideToast = useCallback(() => {
    setToast((prev) => ({ ...prev, isVisible: false }));
  }, []);

  return {
    toast,
    showToast,
    hideToast,
  };
};
