interface DeleteConfirmationProps {
  title: string;
  onCancel: () => void;
  onConfirm: () => void;
}

export const DeleteConfirmation = ({ title, onCancel, onConfirm }: DeleteConfirmationProps) => (
  <div className="rounded-lg border border-red-200 bg-red-50 p-4">
    <div className="flex gap-3">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600">
        <TrashIcon className="h-4 w-4" />
      </span>
      <div>
        <p className="text-sm font-semibold text-slate-950">{title}</p>
        <p className="mt-1 text-sm leading-5 text-red-700">Цю дію не можна скасувати.</p>
      </div>
    </div>
    <div className="mt-3 grid grid-cols-2 gap-2">
      <button
        type="button"
        onClick={onCancel}
        className="h-10 rounded-md bg-white text-sm font-medium text-slate-700 hover:bg-red-100"
      >
        Скасувати
      </button>
      <button
        type="button"
        onClick={onConfirm}
        className="h-10 rounded-md bg-red-600 text-sm font-medium text-white hover:bg-red-700"
      >
        Видалити
      </button>
    </div>
  </div>
);

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
