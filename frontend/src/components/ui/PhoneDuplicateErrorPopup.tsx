// components/DuplicatePhoneToast.tsx
interface ExistingClient {
  id: string;
  full_name: string;
}

interface DuplicatePhone {
  phone_number: string;
  existing_clients: ExistingClient[];
}

interface DuplicatePhoneToastProps {
  duplicates: DuplicatePhone[];
  onConfirm: () => void;
  onCancel: () => void;
}

export const DuplicatePhoneToast = ({
  duplicates,
  onConfirm,
  onCancel,
}: DuplicatePhoneToastProps) => {
  return (
    <div className="fixed inset-0 z-[10000] flex items-end justify-center bg-slate-950/45 px-0 sm:items-center sm:px-4">
      <div className="w-full rounded-t-lg border border-slate-200 bg-white shadow-2xl sm:max-w-md sm:rounded-lg">
        <div className="flex justify-center pt-3 sm:hidden">
          <span className="h-1 w-10 rounded-full bg-slate-300" />
        </div>
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-5">
          <div className="flex min-w-0 items-start gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-amber-100 text-amber-600">
              <WarningIcon className="h-5 w-5" />
            </span>
            <div>
              <h3 className="font-semibold text-slate-950">Знайдено дублікати телефонів</h3>
              <p className="mt-1 text-sm leading-5 text-slate-600">
                Перевірте збіги перед створенням клієнта.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onCancel}
            className="-mr-2 -mt-2 flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-700"
            aria-label="Закрити"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="max-h-[50vh] space-y-3 overflow-y-auto px-5 py-5">
          {duplicates.map((duplicate, idx) => (
            <div key={idx} className="rounded-md border border-amber-200 bg-amber-50 p-3">
              <p className="mb-2 font-semibold text-slate-950">{duplicate.phone_number}</p>

              <p className="mb-1 text-sm text-slate-600">Існуючі клієнти:</p>

              <ul className="space-y-1 text-sm text-slate-700">
                {duplicate.existing_clients.map((client) => (
                  <li key={client.id} className="pl-2">
                    • {client.full_name}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-3 border-t border-slate-200 px-5 py-5 sm:grid-cols-2">
          <button
            type="button"
            onClick={onCancel}
            className="h-11 rounded-md bg-slate-100 px-4 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200"
          >
            Скасувати
          </button>

          <button
            type="button"
            onClick={onConfirm}
            className="h-11 rounded-md bg-blue-600 px-4 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            Продовжити
          </button>
        </div>
      </div>
    </div>
  );
};

const WarningIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 9v4m0 4h.01M10.3 4.5 2.9 17.25A1.5 1.5 0 0 0 4.2 19.5h15.6a1.5 1.5 0 0 0 1.3-2.25L13.7 4.5a1.5 1.5 0 0 0-2.6 0Z"
    />
  </svg>
);
