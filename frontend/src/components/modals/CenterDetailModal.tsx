import React, { useState, useEffect, useCallback } from "react";
import { createPortal } from "react-dom";

interface CenterDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export const CenterDetailModal: React.FC<CenterDetailModalProps> = ({ isOpen, onClose, children }) => {
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

  // ESC key to close
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, handleClose]);

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
        className={`z-9999 fixed top-1/2 left-1/2 -translate-x-1/2 w-[95%] max-w-xl h-[85vh] bg-white rounded-2xl shadow-[0_25px_60px_-12px_rgba(0,0,0,0.25)] overflow-hidden transition-all duration-300 ease-out ${
          isVisible
            ? "opacity-100 -translate-y-1/2 scale-100"
            : "opacity-0 -translate-y-[45%] scale-[0.97]"
        }`}
      >
        {/* Close button overlaid on top-right */}
        <button
          type="button"
          onClick={handleClose}
          className="absolute top-4 right-4 z-10 w-9 h-9 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/40 transition-colors cursor-pointer"
          aria-label="Close"
        >
          <svg
            className="w-5 h-5 text-white drop-shadow-sm"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            strokeWidth={2.5}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {children}
      </div>
    </>
  );

  return createPortal(modalContent, document.body);
};
