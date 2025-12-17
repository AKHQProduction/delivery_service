import React from "react";

interface Phone {
  number: string;
  is_primary: boolean;
}

interface PhoneInputListProps {
  phones: Phone[];
  onPhoneChange: (index: number, value: string) => void;
  onSetPrimary: (index: number) => void;
  onRemove: (index: number) => void;
  onAdd: () => void;
  predefinedNumbers?: string;
}

export const PhoneInputList: React.FC<PhoneInputListProps> = ({
  phones,
  onPhoneChange,
  onSetPrimary,
  onRemove,
  onAdd,
}) => {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Телефони <span className="text-red-500">*</span>
      </label>
      {phones.map((phone, index) => (
        <div
          key={index}
          className="p-4 border-2 border-gray-200 rounded-xl space-y-3"
        >
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-gray-600">
              Телефон #{index + 1}
            </label>
            <div className="flex items-center gap-2">
              {!phone.is_primary && phones.length > 1 && (
                <button
                  type="button"
                  onClick={() => onSetPrimary(index)}
                  className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                >
                  Зробити основним
                </button>
              )}
              {phone.is_primary && (
                <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full font-medium">
                  Основний
                </span>
              )}
              {phones.length > 1 && (
                <button
                  type="button"
                  onClick={() => onRemove(index)}
                  className="text-red-600 hover:bg-red-50 p-1 rounded transition-colors"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
          <input
            type="tel"
            value={phone.number}
            onChange={(e) => onPhoneChange(index, e.target.value)}
            placeholder="+380..."
            required={index === 0}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      ))}
      <button
        type="button"
        onClick={onAdd}
        className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
      >
        + Додати телефон
      </button>
    </div>
  );
};
