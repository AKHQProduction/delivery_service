import React, { useMemo, useState } from "react";
import { Toast } from "../components/ui/Toast";
import { ShopAddressForm } from "../components/settings/ShopAddressForm";
import { DistrictsComponent } from "../components/settings/DistrictsComponent";
import { TimeSlotsComponent } from "../components/settings/TimeSlotsComponent";
import { PaymentMethodsComponent } from "../components/settings/PaymentMethodsComponent";
import { useToast } from "../hooks/useToast";

export const ShopSettingsPage: React.FC = () => {
  const { toast, showToast, hideToast } = useToast();
  const [activeSection, setActiveSection] = useState<SettingsSectionKey>("address");

  const handleAddressSaveSuccess = () => {
    showToast("Адресу збережено", "success");
  };

  const activeSettingsSection = useMemo(
    () =>
      SETTINGS_SECTIONS.find((section) => section.key === activeSection) ?? SETTINGS_SECTIONS[0],
    [activeSection],
  );

  return (
    <div className="min-h-screen bg-slate-50 px-4 pb-28 pt-6 sm:px-6 md:px-8 md:pb-10">
      <div>
        <h1 className="text-2xl font-semibold leading-8 text-slate-950">Налаштування магазину</h1>
        <p className="mt-1 text-sm text-slate-500">
          Адреса, райони, часові проміжки та способи оплати
        </p>
      </div>

      <div className="-mx-4 mt-4 overflow-x-auto px-4 md:hidden">
        <div className="flex gap-2">
          {SETTINGS_SECTIONS.map((section) => (
            <button
              key={section.key}
              type="button"
              onClick={() => setActiveSection(section.key)}
              className={`h-10 shrink-0 rounded-md px-3 text-sm font-medium transition-colors ${
                activeSection === section.key
                  ? "bg-blue-600 text-white"
                  : "border border-slate-200 bg-white text-slate-700"
              }`}
            >
              {section.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-[17rem_minmax(0,1fr)]">
        <aside className="hidden rounded-lg border border-slate-200 bg-white p-3 md:block">
          <nav className="space-y-1">
            {SETTINGS_SECTIONS.map((section) => (
              <button
                key={section.key}
                type="button"
                onClick={() => setActiveSection(section.key)}
                className={`w-full rounded-md px-3 py-3 text-left transition-colors ${
                  activeSection === section.key
                    ? "bg-blue-50 text-blue-700"
                    : "text-slate-700 hover:bg-slate-100 hover:text-slate-950"
                }`}
              >
                <span className="block text-sm font-semibold">{section.label}</span>
                <span className="mt-0.5 block text-xs text-slate-500">{section.description}</span>
              </button>
            ))}
          </nav>
        </aside>

        <section>
          {activeSettingsSection.key === "address" && (
            <ShopAddressForm onSuccess={handleAddressSaveSuccess} />
          )}
          {activeSettingsSection.key === "districts" && <DistrictsComponent />}
          {activeSettingsSection.key === "timeSlots" && <TimeSlotsComponent />}
          {activeSettingsSection.key === "paymentMethods" && <PaymentMethodsComponent />}
        </section>
      </div>

      {toast.isVisible && <Toast message={toast.message} type={toast.type} onClose={hideToast} />}
    </div>
  );
};

type SettingsSectionKey = "address" | "districts" | "timeSlots" | "paymentMethods";

const SETTINGS_SECTIONS: Array<{
  key: SettingsSectionKey;
  label: string;
  description: string;
}> = [
  { key: "address", label: "Адреса", description: "Адреса магазину і координати" },
  { key: "districts", label: "Райони", description: "Зони доставки" },
  { key: "timeSlots", label: "Часові проміжки", description: "Вікна доставки" },
  { key: "paymentMethods", label: "Оплата", description: "Способи оплати" },
];
