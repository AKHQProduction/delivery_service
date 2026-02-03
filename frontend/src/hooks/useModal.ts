import { useState, useEffect } from "react";

interface UseModalOptions {
  initialOpen?: boolean;
  onOpen?: () => void;
  onClose?: () => void;
  animationDelay?: number;
}

interface UseModalReturn {
  isOpen: boolean;
  isVisible: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
}

export const useModal = (options: UseModalOptions = {}): UseModalReturn => {
  const {
    initialOpen = false,
    onOpen,
    onClose,
    animationDelay = 300,
  } = options;

  const [isOpen, setIsOpen] = useState(initialOpen);
  const [isVisible, setIsVisible] = useState(false);

  // Handle body scroll lock when modal is open
  useEffect(() => {
    if (isOpen) {
      setIsVisible(true);
      document.body.style.overflow = "hidden";
      onOpen?.();
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onOpen]);

  const open = () => {
    setIsOpen(true);
  };

  const close = () => {
    setIsVisible(false);
    setTimeout(() => {
      setIsOpen(false);
      onClose?.();
    }, animationDelay);
  };

  const toggle = () => {
    if (isOpen) {
      close();
    } else {
      open();
    }
  };

  return {
    isOpen,
    isVisible,
    open,
    close,
    toggle,
  };
};
