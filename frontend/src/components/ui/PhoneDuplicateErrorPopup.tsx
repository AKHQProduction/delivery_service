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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg border border-indigo-600 p-4 mx-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full flex items-center justify-center">
              <span className="text-white text-lg">⚠️</span>
            </div>
            <h3 className="font-semibold text-gray-900">Знайдено дублікати телефонів</h3>
          </div>

          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
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

        {/* Content */}
        <div className="mb-4 space-y-3">
          {duplicates.map((duplicate, idx) => (
            <div key={idx} className="bg-indigo-50 rounded p-3">
              <p className="font-medium mb-2">{duplicate.phone_number}</p>

              <p className="text-sm mb-1">Існуючі клієнти:</p>

              <ul className="text-sm text-gray-700 space-y-1">
                {duplicate.existing_clients.map((client) => (
                  <li key={client.id} className="pl-2">
                    • {client.full_name}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
          >
            Скасувати
          </button>

          <button
            onClick={onConfirm}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            Продовжити
          </button>
        </div>
      </div>
    </div>
  );
};
