import {
  useState,
  useRef,
  type ChangeEvent,
  type FocusEvent,
  type KeyboardEvent,
} from "react";

interface TimeInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  title?: string;
}

export const TimeInput = ({
  value,
  onChange,
  placeholder = "HH:MM",
  className = "",
  title = "Формат: 00:00 - 23:59",
}: TimeInputProps) => {
  const [localValue, setLocalValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    let input = e.target.value;

    // Remove any non-digit and non-colon characters
    input = input.replace(/[^\d:]/g, "");

    // Auto-add colon after 2 digits
    if (
      input.length === 2 &&
      !input.includes(":") &&
      localValue.length < input.length
    ) {
      input = input + ":";
    }

    // Limit to 5 characters (HH:MM)
    if (input.length > 5) {
      input = input.slice(0, 5);
    }

    setLocalValue(input);
  };

  const handleBlur = (e: FocusEvent<HTMLInputElement>) => {
    const formatted = formatAndValidate(localValue);
    setLocalValue(formatted);
    if (formatted && formatted !== value) {
      onChange(formatted);
    }
  };

  const formatAndValidate = (input: string): string => {
    if (!input) return "";

    const parts = input.split(":");
    if (parts.length !== 2) return "";

    let hours = parseInt(parts[0]) || 0;
    let minutes = parseInt(parts[1]) || 0;

    // Validate ranges
    if (hours > 23) hours = 23;
    if (minutes > 59) minutes = 59;

    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    // Allow: backspace, delete, tab, escape, enter, colon
    const allowedKeys = [8, 9, 27, 13, 46, 186, 191];

    if (allowedKeys.includes(e.keyCode)) return;

    // Allow Ctrl/Cmd shortcuts
    if (e.ctrlKey || e.metaKey) return;

    // Allow arrow keys
    if (e.keyCode >= 35 && e.keyCode <= 39) return;

    // Allow colon
    if (e.key === ":") return;

    // Only allow numbers
    if (e.key < "0" || e.key > "9") {
      e.preventDefault();
    }
  };

  const handleFocus = () => {
    inputRef.current?.select();
  };

  // Sync with external value changes
  if (value !== localValue && !inputRef.current?.matches(":focus")) {
    setLocalValue(value);
  }

  return (
    <input
      ref={inputRef}
      type="text"
      inputMode="numeric"
      pattern="([01]?[0-9]|2[0-3]):[0-5][0-9]"
      placeholder={placeholder}
      title={title}
      value={localValue}
      onChange={handleChange}
      onBlur={handleBlur}
      onFocus={handleFocus}
      onKeyDown={handleKeyDown}
      maxLength={5}
      className={`w-20 px-2 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm text-center ${className}`}
    />
  );
};
