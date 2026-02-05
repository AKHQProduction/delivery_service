import React, { useState } from "react";
import { PageHeader } from "../components/ui/PageHeader";
import { Toast } from "../components/ui/Toast";
import { ShopAddressForm } from "../components/settings/ShopAddressForm";
import { useToast } from "../hooks/useToast";

interface DeliveryDistrict {
  id: string;
  name: string;
}

export const ShopSettingsPage: React.FC = () => {
  const { toast, showToast, hideToast } = useToast();

  const [districts, setDistricts] = useState<DeliveryDistrict[]>([]);
  const [showAddDistrict, setShowAddDistrict] = useState(false);
  const [newDistrict, setNewDistrict] = useState<Omit<DeliveryDistrict, "id">>({
    name: "",
  });

  const handleAddDistrict = () => {
    if (!newDistrict.name.trim()) return;

    const district: DeliveryDistrict = {
      id: Date.now().toString(),
      ...newDistrict,
    };

    setDistricts((prev) => [...prev, district]);
    setNewDistrict({ name: "" });
    setShowAddDistrict(false);
  };

  const handleDeleteDistrict = (id: string) => {
    setDistricts((prev) => prev.filter((d) => d.id !== id));
  };

  const handleAddressSaveSuccess = () => {
    showToast("Адресу збережено", "success");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 pb-32">
      <PageHeader title="Налаштування магазину" />

      <div className="px-4 sm:px-6 py-6 space-y-6">
        <ShopAddressForm onSuccess={handleAddressSaveSuccess} />

        {/* Delivery Districts Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Райони доставки
            </h2>
            <button
              onClick={() => setShowAddDistrict(!showAddDistrict)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors text-sm"
            >
              {showAddDistrict ? "Скасувати" : "+ Додати район"}
            </button>
          </div>

          {/* Add District Form */}
          {showAddDistrict && (
            <div className="mb-6 p-4 bg-gray-50 rounded-xl space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Назва району *
                </label>
                <input
                  type="text"
                  value={newDistrict.name}
                  onChange={(e) =>
                    setNewDistrict((prev) => ({
                      ...prev,
                      name: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="Печерський район"
                />
              </div>

              <button
                onClick={handleAddDistrict}
                disabled={!newDistrict.name.trim()}
                className="w-full px-6 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Додати район
              </button>
            </div>
          )}

          {/* Districts List */}
          <div className="space-y-3">
            {districts.length === 0 && !showAddDistrict ? (
              <div className="text-center py-8 text-gray-500">
                <p>Райони доставки не додані</p>
                <p className="text-sm mt-1">
                  Натисніть "+ Додати район" щоб створити новий
                </p>
              </div>
            ) : (
              districts.map((district) => (
                <div
                  key={district.id}
                  className="p-4 border-2 border-gray-200 rounded-xl hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">
                          {district.name}
                        </h3>
                      </div>
                    </div>
                    <button
                      type="button"
                      title="deleteDistrict"
                      onClick={() => handleDeleteDistrict(district.id)}
                      className="text-red-600 hover:bg-red-50 p-2 rounded-lg transition-colors"
                    >
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {toast.isVisible && (
        <Toast message={toast.message} type={toast.type} onClose={hideToast} />
      )}
    </div>
  );
};
