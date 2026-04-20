import { useState } from "react";
import { usePaymentMethodsSettings } from "../../hooks/settings/usePaymentMethodsSettings";
import { isBalancePaymentMethodName } from "../../shared/paymentMethod";
import { SettingsItemSkeleton } from "../ui/Skeleton";

interface PaymentMethod {
  payment_method_id: string;
  name: string;
}

interface NewMethod {
  id: string;
  name: string;
}

export const PaymentMethodsComponent = () => {
  const {
    paymentMethods,
    updatePaymentMethodById,
    addPaymentMethod,
    deletePaymentMethodById,
    isLoading,
  } = usePaymentMethodsSettings();
  const [editedMethods, setEditedMethods] = useState<Record<string, Partial<PaymentMethod>>>({});
  const [newMethods, setNewMethods] = useState<NewMethod[]>([]);

  const handleFieldChange = (methodId: string, value: string) => {
    setEditedMethods((prev) => {
      const original = paymentMethods?.find((m) => m?.payment_method_id === methodId);
      return {
        ...prev,
        [methodId]: {
          ...original,
          ...prev[methodId],
          name: value,
        },
      };
    });
  };

  const handleNewMethodChange = (tempId: string, value: string) => {
    setNewMethods((prev) =>
      prev.map((method) => (method.id === tempId ? { ...method, name: value } : method)),
    );
  };

  const handleSaveExisting = async (methodId: string) => {
    try {
      const changes = editedMethods[methodId];
      if (changes?.name) {
        await updatePaymentMethodById(methodId, changes.name);
        setEditedMethods((prev) => {
          const updated = { ...prev };
          delete updated[methodId];
          return updated;
        });
      }
    } catch (error) {
      console.error("Error saving changes:", error);
    }
  };

  const handleSaveNew = async (tempId: string) => {
    try {
      const newMethod = newMethods.find((m) => m.id === tempId);
      if (newMethod && newMethod.name.trim()) {
        await addPaymentMethod(newMethod.name.trim());
        setNewMethods((prev) => prev.filter((m) => m.id !== tempId));
      }
    } catch (error) {
      console.error("Error creating payment method:", error);
    }
  };

  const handleDeleteNew = (tempId: string) => {
    setNewMethods((prev) => prev.filter((m) => m.id !== tempId));
  };

  const handleAddNew = () => {
    const tempId = `temp-${Date.now()}`;
    setNewMethods((prev) => [...prev, { id: tempId, name: "" }]);
  };

  const getMethodName = (method: PaymentMethod): string => {
    const edited = editedMethods[method.payment_method_id];
    if (edited?.name !== undefined) return edited.name;
    return method.name;
  };

  const isProtectedMethod = (method: PaymentMethod) => isBalancePaymentMethodName(method.name);

  const isMethodEdited = (methodId: string) => {
    const edited = editedMethods[methodId];
    if (!edited) return false;
    const original = paymentMethods?.find((m) => m?.payment_method_id === methodId);
    if (!original) return false;
    return (edited.name ?? original.name) !== original.name;
  };

  const validMethods = (paymentMethods || []).filter(
    (m): m is PaymentMethod => m !== null && m !== undefined && m.payment_method_id !== null,
  );

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Способи оплати</h2>
      </div>

      <div className="space-y-3">
        {isLoading && validMethods.length === 0 && (
          <>
            {Array.from({ length: 3 }).map((_, i) => (
              <SettingsItemSkeleton key={i} />
            ))}
          </>
        )}

        {validMethods.map((method) => (
          <div key={method.payment_method_id} className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Назва"
              value={getMethodName(method)}
              onChange={(e) => handleFieldChange(method.payment_method_id, e.target.value)}
              disabled={isProtectedMethod(method)}
              readOnly={isProtectedMethod(method)}
              className="flex-1 min-w-0 px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed"
            />

            {isMethodEdited(method.payment_method_id) ? (
              <button
                onClick={() => handleSaveExisting(method.payment_method_id)}
                className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl bg-green-500 hover:bg-green-600 text-white transition-colors"
                aria-label="Зберегти"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </button>
            ) : !isProtectedMethod(method) ? (
              <button
                onClick={async () => {
                  try {
                    await deletePaymentMethodById(method.payment_method_id);
                  } catch (error) {
                    console.error("Error deleting payment method:", error);
                  }
                }}
                className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl hover:bg-red-50 text-red-500 transition-colors"
                aria-label="Видалити"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            ) : null}
          </div>
        ))}

        {newMethods.map((method) => (
          <div
            key={method.id}
            className="flex items-center gap-2 border-2 border-dashed border-gray-200 rounded-xl p-3"
          >
            <input
              type="text"
              placeholder="Назва способу оплати"
              value={method.name}
              onChange={(e) => handleNewMethodChange(method.id, e.target.value)}
              className="flex-1 min-w-0 px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <button
              onClick={() => handleSaveNew(method.id)}
              disabled={!method.name.trim()}
              className={`w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl transition-colors ${
                method.name.trim()
                  ? "bg-green-500 hover:bg-green-600 text-white"
                  : "bg-gray-200 text-gray-400 cursor-not-allowed"
              }`}
              aria-label="Зберегти"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </button>
            <button
              onClick={() => handleDeleteNew(method.id)}
              className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl hover:bg-red-200 bg-red-100 text-red-500 transition-colors"
              aria-label="Скасувати"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        ))}

        {validMethods.length === 0 && newMethods.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>Способи оплати не додані</p>
            <p className="text-sm mt-1">Натисніть "+ Додати спосіб оплати" щоб створити новий</p>
          </div>
        )}

        <button
          onClick={handleAddNew}
          className="text-indigo-600 hover:text-indigo-700 text-sm font-medium transition-colors"
        >
          + Додати спосіб оплати
        </button>
      </div>
    </div>
  );
};
