import React, { useState, useEffect, useCallback } from "react";
import { createPortal } from "react-dom";

interface CenterDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  size?: "xl" | "2xl" | "3xl" | "4xl" | "5xl";
}

export const CenterDetailModal: React.FC<CenterDetailModalProps> = ({
  isOpen,
  onClose,
  children,
  size = "xl",
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [shouldRender, setShouldRender] = useState(false);

  const handleClose = useCallback(() => {
    setIsVisible(false);
    setTimeout(() => onClose(), 300);
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- Required for animation timing
      setShouldRender(true);
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setIsVisible(true);
        });
      });
      document.body.style.overflow = "hidden";
    } else {
      setIsVisible(false);
      const timer = setTimeout(() => {
        setShouldRender(false);
      }, 300);
      document.body.style.overflow = "unset";
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  useEffect(() => {
    return () => {
      document.body.style.overflow = "unset";
    };
  }, []);

  if (!shouldRender) return null;

  const modalContent = (
    <>
      {/* Backdrop with blur */}
      <div
        className={`fixed inset-0 bg-black/40 backdrop-blur-sm transition-opacity duration-300 z-9998 ${
          isVisible ? "opacity-100" : "opacity-0"
        }`}
        onClick={handleClose}
      />

      {/* Panel */}
      <div
        className={`z-9999 fixed top-1/2 left-1/2 -translate-x-1/2 w-[95%] ${{ xl: "max-w-xl", "2xl": "max-w-2xl", "3xl": "max-w-3xl", "4xl": "max-w-4xl", "5xl": "max-w-5xl" }[size]} h-[85vh] bg-white rounded-2xl shadow-[0_25px_60px_-12px_rgba(0,0,0,0.25)] overflow-hidden transition-all duration-300 ease-out ${
          isVisible
            ? "opacity-100 -translate-y-1/2 scale-100"
            : "opacity-0 -translate-y-[45%] scale-[0.97]"
        }`}
      >
        {children}
      </div>
    </>
  );

  return createPortal(modalContent, document.body);
};
