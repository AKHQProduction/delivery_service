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
    <form onSubmit={onSubmit} className="flex min-h-full flex-col">
      <div className="space-y-4">{children}</div>
      <div className="mt-auto flex gap-3 bg-white pt-8">
        <button
          type="button"
          onClick={onClose}
          className="flex-1 rounded-md bg-slate-100 py-3 font-medium text-slate-700 transition-colors hover:bg-slate-200"
        >
          Скасувати
        </button>
        <button
          type="submit"
          className="flex-1 rounded-md bg-blue-600 py-3 font-medium text-white transition-colors hover:bg-blue-700"
        >
          {submitLabel}
        </button>
      </div>
    </form>
  );
};
