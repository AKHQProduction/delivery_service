import { useState } from "react";
import { useUserShopStore } from "../../context/useUserShopStore";
import { useShopSettings } from "../../hooks/settings/useShopSettings";
import type { RepeatOrderMode } from "../../types/entities/user";

const DEFAULT_REPEAT_ORDER_MODE: RepeatOrderMode = "CONFIRMATION_REQUIRED";

const REPEAT_ORDER_OPTIONS: Array<{
  value: RepeatOrderMode;
  title: string;
  description: string;
}> = [
  {
    value: "CONFIRMATION_REQUIRED",
    title: "Показувати підтвердження",
    description: "Менеджер бачить підказку з останнім замовленням клієнта і сам застосовує її.",
  },
  {
    value: "CREATE_REGULAR_ORDER",
    title: "Створювати регулярне замовлення",
    description: "Підказка повторення не відкривається під час створення нового замовлення.",
  },
];

export const OrderSettingsComponent = () => {
  const shopRepeatOrderMode =
    useUserShopStore((state) => state.shop?.repeat_order_mode) ?? DEFAULT_REPEAT_ORDER_MODE;
  const { loading, error, saveRepeatOrderMode } = useShopSettings();
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  const handleModeChange = async (mode: RepeatOrderMode) => {
    if (mode === shopRepeatOrderMode || loading) return;

    setSavedMessage(null);
    const success = await saveRepeatOrderMode(mode);
    if (success) {
      setSavedMessage("Налаштування замовлень збережено");
    }
  };

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-slate-950">Замовлення</h2>
        <p className="mt-1 text-sm text-slate-500">
          Оберіть, як працює повторення останнього замовлення клієнта.
        </p>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        {REPEAT_ORDER_OPTIONS.map((option) => {
          const isSelected = option.value === shopRepeatOrderMode;

          return (
            <button
              key={option.value}
              type="button"
              onClick={() => handleModeChange(option.value)}
              disabled={loading}
              className={`rounded-md border p-4 text-left transition-colors ${
                isSelected
                  ? "border-blue-600 bg-blue-50"
                  : "border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50"
              } ${loading ? "cursor-wait opacity-75" : ""}`}
              aria-pressed={isSelected}
            >
              <span className="flex items-start gap-3">
                <span
                  className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border ${
                    isSelected ? "border-blue-600 bg-blue-600" : "border-slate-300 bg-white"
                  }`}
                >
                  {isSelected && <span className="h-2 w-2 rounded-full bg-white" />}
                </span>
                <span>
                  <span className="block text-sm font-semibold text-slate-950">
                    {option.title}
                  </span>
                  <span className="mt-1 block text-sm leading-5 text-slate-500">
                    {option.description}
                  </span>
                </span>
              </span>
            </button>
          );
        })}
      </div>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      {savedMessage && !error && <p className="mt-3 text-sm text-emerald-600">{savedMessage}</p>}
    </div>
  );
};
