interface Address {
  street: string;
  house: string;
  apartment?: string;
  entrance?: string;
  floor?: string;
  intercom?: string;
  is_primary: boolean;
  comment?: string;
}

interface AddressInputListProps {
  addresses: Address[];
  onSetPrimary: (index: number) => void;
  onAddressChange: (index: number, field: keyof Address, value: string) => void;
  onRemove: (index: number) => void;
  onAdd: () => void;
}

export const AddressInputList: React.FC<AddressInputListProps> = ({
  addresses,
  onSetPrimary,
  onAddressChange,
  onRemove,
  onAdd,
}) => {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">Адреси</label>
      {addresses.map((address, index) => (
        <div
          key={index}
          className="p-4 border-2 border-gray-200 rounded-xl space-y-3"
        >
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-gray-600">
              Адреса #{index + 1}
            </label>
            <div className="flex items-center gap-2">
              {!address.is_primary && addresses.length > 1 && (
                <button
                  type="button"
                  onClick={() => onSetPrimary(index)}
                  className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                >
                  Зробити основною
                </button>
              )}
              {address.is_primary && (
                <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full font-medium">
                  Основна
                </span>
              )}
              {addresses.length > 1 && (
                <button
                  type="button"
                  onClick={() => onRemove(index)}
                  className="text-red-600 hover:bg-red-50 p-1 rounded"
                >
                  ✕
                </button>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={address.street}
                onChange={(e) =>
                  onAddressChange(index, "street", e.target.value)
                }
                placeholder="Вулиця *"
                required
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="text"
                value={address.house}
                onChange={(e) =>
                  onAddressChange(index, "house", e.target.value)
                }
                placeholder="Будинок *"
                required
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={address.apartment || ""}
                onChange={(e) =>
                  onAddressChange(index, "apartment", e.target.value)
                }
                placeholder="Квартира"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="text"
                value={address.entrance || ""}
                onChange={(e) =>
                  onAddressChange(index, "entrance", e.target.value)
                }
                placeholder="Під'їзд"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="text"
                value={address.floor || ""}
                onChange={(e) =>
                  onAddressChange(index, "floor", e.target.value)
                }
                placeholder="Поверх"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="text"
                value={address.intercom || ""}
                onChange={(e) =>
                  onAddressChange(index, "intercom", e.target.value)
                }
                placeholder="Домофон"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="pt-2">
              <label className="flex items-center gap-2 text-xs font-medium text-gray-600 mb-2">
                <svg
                  className="w-4 h-4 text-gray-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                  />
                </svg>
                Примітки до адреси
              </label>
              <div className="relative">
                <textarea
                  value={address.comment || ""}
                  onChange={(e) =>
                    onAddressChange(index, "comment", e.target.value)
                  }
                  placeholder="Додайте важливі деталі для доставки..."
                  rows={3}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-gray-900 resize-none bg-gradient-to-br from-white to-gray-50 placeholder:text-gray-400"
                />
              </div>
            </div>
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={onAdd}
        className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
      >
        + Додати адресу
      </button>
    </div>
  );
};
