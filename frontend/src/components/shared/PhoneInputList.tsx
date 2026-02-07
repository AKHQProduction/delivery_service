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
  errors?: Record<string, string>; // phone number -> error message
}

export const PhoneInputList: React.FC<PhoneInputListProps> = ({
  phones,
  onPhoneChange,
  onSetPrimary,
  onRemove,
  onAdd,
  errors = {},
}) => {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Телефони <span className="text-red-500">*</span>
      </label>
      {phones.map((phone, index) => {
        const phoneError = errors[phone.number];
        const hasError = !!phoneError;

        return (
          <div
            key={index}
            className={`p-4 border-2 rounded-xl space-y-3 ${
              hasError ? "border-red-400 bg-red-50" : "border-gray-200"
            }`}
          >
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-gray-600">Телефон #{index + 1}</label>
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
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 ${
                hasError
                  ? "border-red-400 focus:ring-red-500"
                  : "border-gray-300 focus:ring-indigo-500"
              }`}
            />
            {hasError && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                {phoneError}
              </p>
            )}
          </div>
        );
      })}
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
