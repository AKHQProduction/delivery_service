import { createPortal } from "react-dom";

interface ConfirmDeleteModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  warning?: string;
  confirmLabel: string;
  onCancel: () => void;
  onConfirm: () => void;
}

export const ConfirmDeleteModal = ({
  isOpen,
  title,
  message,
  warning,
  confirmLabel,
  onCancel,
  onConfirm,
}: ConfirmDeleteModalProps) => {
  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-[10000] flex items-end justify-center bg-slate-950/45 px-0 sm:items-center sm:px-4">
      <div className="w-full rounded-t-lg bg-white shadow-2xl sm:max-w-md sm:rounded-lg">
        <div className="flex justify-center pt-3 sm:hidden">
          <span className="h-1 w-10 rounded-full bg-slate-300" />
        </div>
        <div className="flex items-start gap-4 border-b border-slate-200 px-5 py-5 sm:px-6">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-red-50 text-red-600">
            <TrashIcon className="h-5 w-5" />
          </span>
          <div className="min-w-0 flex-1">
            <h2 className="text-lg font-semibold leading-6 text-slate-950">{title}</h2>
            <p className="mt-1 text-sm leading-5 text-slate-600">{message}</p>
          </div>
          <button
            type="button"
            onClick={onCancel}
            className="-mr-2 -mt-2 flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-700"
            aria-label="Закрити"
          >
            <CloseIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="px-5 py-5 sm:px-6">
          {warning && (
            <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium leading-5 text-red-700">
              {warning}
            </div>
          )}
        </div>
        <div className="grid grid-cols-1 gap-3 border-t border-slate-200 px-5 py-5 sm:grid-cols-2 sm:px-6">
          <button
            type="button"
            onClick={onCancel}
            className="h-11 rounded-md bg-slate-100 px-4 text-sm font-medium text-slate-700 hover:bg-slate-200"
          >
            Скасувати
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="h-11 rounded-md bg-red-600 px-4 text-sm font-medium text-white hover:bg-red-700"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
};

const TrashIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M6 7.5h12m-10.5 0 .7 11.2A2.25 2.25 0 0 0 10.45 21h3.1a2.25 2.25 0 0 0 2.25-2.3l.7-11.2M9.75 7.5V5.25A2.25 2.25 0 0 1 12 3h0a2.25 2.25 0 0 1 2.25 2.25V7.5"
    />
  </svg>
);

const CloseIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18 18 6M6 6l12 12" />
  </svg>
);
