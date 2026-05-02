import { useEffect, useState } from "react";

interface FloatingAddButtonProps {
  label: string;
  onClick: () => void;
  threshold?: number;
}

export const FloatingAddButton = ({
  label,
  onClick,
  threshold = 240,
}: FloatingAddButtonProps) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const updateVisibility = () => {
      setIsVisible(window.scrollY > threshold);
    };

    updateVisibility();
    window.addEventListener("scroll", updateVisibility, { passive: true });
    return () => window.removeEventListener("scroll", updateVisibility);
  }, [threshold]);

  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className={`fixed right-5 bottom-[calc(env(safe-area-inset-bottom)+5.75rem)] z-30 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg shadow-blue-600/25 transition-all duration-200 hover:bg-blue-700 active:scale-95 md:hidden ${
        isVisible
          ? "pointer-events-auto translate-y-0 opacity-100"
          : "pointer-events-none translate-y-3 opacity-0"
      }`}
    >
      <PlusIcon className="h-7 w-7" />
    </button>
  );
};

const PlusIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4.5v15m7.5-7.5h-15" />
  </svg>
);
