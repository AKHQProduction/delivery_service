import React from "react";

interface FormWrapperProps {
  onSubmit: (e: React.FormEvent) => void;
  onClose: () => void;
  submitLabel?: string;
  children: React.ReactNode;
}

export const FormWrapper: React.FC<FormWrapperProps> = ({
  onSubmit,
  onClose,
  submitLabel = "Зберегти",
  children,
}) => {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      {children}
      <div className="flex gap-3 mt-6 sticky bottom-0 bg-white pt-4 pb-4">
        <button
          type="button"
          onClick={onClose}
          className="flex-1 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-colors"
        >
          Скасувати
        </button>
        <button
          type="submit"
          className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl transition-colors"
        >
          {submitLabel}
        </button>
      </div>
    </form>
  );
};
