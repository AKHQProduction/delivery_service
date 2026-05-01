interface DeleteConfirmationProps {
  title: string;
  onCancel: () => void;
  onConfirm: () => void;
}

export const DeleteConfirmation = ({ title, onCancel, onConfirm }: DeleteConfirmationProps) => (
  <div className="rounded-md border border-red-200 bg-red-50 p-3">
    <p className="text-sm font-semibold text-red-700">{title}</p>
    <p className="mt-1 text-sm text-red-700">Дію не можна буде скасувати.</p>
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
