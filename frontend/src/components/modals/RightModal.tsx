import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";

interface RightModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export const RightModal: React.FC<RightModalProps> = ({ isOpen, onClose, children }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [shouldRender, setShouldRender] = useState(false);

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

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => onClose(), 300);
  };

  if (!shouldRender) return null;

  const modalContent = (
    <>
      <div
        className={`fixed inset-0 bg-black transition-opacity duration-300 z-9998 ${
          isVisible ? "opacity-50" : "opacity-0"
        }`}
        onClick={handleClose}
      />

      <div
        className={`z-9999 fixed top-0 right-0 h-full w-full max-w-lg bg-white shadow-2xl transition-transform duration-300 ease-in-out ${
          isVisible ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {children}
      </div>
    </>
  );

  return createPortal(modalContent, document.body);
};
