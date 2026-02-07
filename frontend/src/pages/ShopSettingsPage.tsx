import React from "react";
import { PageHeader } from "../components/ui/PageHeader";
import { Toast } from "../components/ui/Toast";
import { ShopAddressForm } from "../components/settings/ShopAddressForm";
import { DistrictsComponent } from "../components/settings/DistrictsComponent";
import { useToast } from "../hooks/useToast";

export const ShopSettingsPage: React.FC = () => {
  const { toast, showToast, hideToast } = useToast();

  const handleAddressSaveSuccess = () => {
    showToast("Адресу збережено", "success");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 pb-32">
      <PageHeader title="Налаштування магазину" />

      <div className="px-4 sm:px-6 py-6 space-y-6">
        <ShopAddressForm onSuccess={handleAddressSaveSuccess} />

        <DistrictsComponent />
      </div>

      {toast.isVisible && <Toast message={toast.message} type={toast.type} onClose={hideToast} />}
    </div>
  );
};
