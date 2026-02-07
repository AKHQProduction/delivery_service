import React from "react";
import { PageHeader } from "../components/ui/PageHeader";
import { Toast } from "../components/ui/Toast";
import { ShopAddressForm } from "../components/settings/ShopAddressForm";
import { DistrictsComponent } from "../components/settings/DistrictsComponent";
import { TimeSlotsComponent } from "../components/settings/TimeSlotsComponent";
import { useToast } from "../hooks/useToast";

export const ShopSettingsPage: React.FC = () => {
  const { toast, showToast, hideToast } = useToast();

  const handleAddressSaveSuccess = () => {
    showToast("Адресу збережено", "success");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 pb-32 lg:from-white lg:to-white lg:pb-8">
      <PageHeader title="Налаштування магазину" />

      <div className="px-4 sm:px-6 py-6 space-y-6 lg:px-8">
        <ShopAddressForm onSuccess={handleAddressSaveSuccess} />

        <DistrictsComponent />

        <TimeSlotsComponent />
      </div>

      {toast.isVisible && <Toast message={toast.message} type={toast.type} onClose={hideToast} />}
    </div>
  );
};
