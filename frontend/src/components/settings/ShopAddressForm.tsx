import React, { useState } from "react";
import { MapPicker } from "../shared/MapPicker";
import { MapButton } from "../shared/MapButton";
import { useMapPicker } from "../../hooks/useMapPicker";
import {
  useShopSettings,
  type ShopAddress,
} from "../../hooks/settings/useShopSettings";
import { useUserShopStore } from "../../context/useUserShopStore";

interface ShopAddressFormProps {
  onSuccess?: () => void;
}

type AddressError =
  | "not_found"
  | "needs_verification"
  | "missing_fields"
  | null;

export const ShopAddressForm: React.FC<ShopAddressFormProps> = ({
  onSuccess,
}) => {
  const shop = useUserShopStore((state) => state.shop);
  const { loading, error, saveShopAddress } = useShopSettings();

  const [shopAddress, setShopAddress] = useState<ShopAddress>({
    street: shop?.street ?? "",
    house: shop?.house ?? "",
    city: shop?.city ?? "Київ",
    coordinates: null,
  });

  const [addressError, setAddressError] = useState<AddressError>(null);
  const [pendingCoordinates, setPendingCoordinates] = useState<{
    lat: number;
    lng: number;
  } | null>(null);

  const {
    isMapOpen,
    isLoading,
    openMap,
    closeMap,
    reverseGeocode,
    forwardGeocode,
  } = useMapPicker();

  const handleAddressChange = (field: keyof ShopAddress, value: string) => {
    setShopAddress((prev) => ({
      ...prev,
      [field]: value,
      ...(field === "street" || field === "house" ? { coordinates: null } : {}),
    }));
    setAddressError(null);
    setPendingCoordinates(null);
  };

  const handleSave = async () => {
    if (!shopAddress.city.trim() || !shopAddress.street.trim()) {
      setAddressError("missing_fields");
      return;
    }

    if (shopAddress.coordinates) {
      setAddressError(null);
      const success = await saveShopAddress(shopAddress);
      if (success) {
        onSuccess?.();
      }
      return;
    }

    const coords = await forwardGeocode(
      shopAddress.street,
      shopAddress.house,
      shopAddress.city,
    );

    if (coords) {
      setPendingCoordinates(coords);
      setAddressError("needs_verification");
    } else {
      setAddressError("not_found");
    }
  };

  const handleMapConfirm = async (coordinates: {
    lat: number;
    lng: number;
  }) => {
    const result = await reverseGeocode(coordinates);

    if (result) {
      setShopAddress({
        street: result.street,
        house: result.house,
        city: result.city,
        coordinates: {
          latitude: coordinates.lat,
          longitude: coordinates.lng,
        },
      });
      setAddressError(null);
      setPendingCoordinates(null);
      closeMap();
    }
  };

  const getInputClassName = (field: "city" | "street") => {
    const baseClass =
      "w-full px-4 py-3 border-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent";
    const isEmpty = !shopAddress[field].trim();
    const hasError = addressError === "missing_fields" && isEmpty;
    return `${baseClass} ${hasError ? "border-red-300 bg-red-50" : "border-gray-200"}`;
  };

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Адреса магазину
          </h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Місто *
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={shopAddress.city}
                onChange={(e) => handleAddressChange("city", e.target.value)}
                className={`flex-1 ${getInputClassName("city").replace("w-full ", "")}`}
                placeholder="Київ"
                required
              />
              <MapButton onClick={openMap} />
            </div>
            {shopAddress.coordinates ? (
              <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Координати збережено
              </p>
            ) : (
              <p className="text-xs text-gray-500 mt-1">
                Виберіть точку на карті, щоб автоматично заповнити адресу та
                зберегти координати
              </p>
            )}

            {addressError === "not_found" && (
              <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <svg
                  className="w-5 h-5 text-red-500 shrink-0 mt-0.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <div>
                  <p className="text-sm font-medium text-red-800">
                    Адресу не знайдено
                  </p>
                  <p className="text-xs text-red-600 mt-0.5">
                    Перевірте правильність адреси або виберіть місцезнаходження
                    на карті
                  </p>
                  <button
                    type="button"
                    onClick={openMap}
                    className="mt-2 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    Відкрити карту
                  </button>
                </div>
              </div>
            )}

            {addressError === "needs_verification" && pendingCoordinates && (
              <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2">
                <svg
                  className="w-5 h-5 text-amber-500 shrink-0 mt-0.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div>
                  <p className="text-sm font-medium text-amber-800">
                    Підтвердіть місцезнаходження
                  </p>
                  <p className="text-xs text-amber-700 mt-0.5">
                    Адресу знайдено. Будь ласка, перевірте на карті, що мітка
                    встановлена правильно
                  </p>
                  <button
                    type="button"
                    onClick={openMap}
                    className="mt-2 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    Перевірити на карті
                  </button>
                </div>
              </div>
            )}

            {addressError === "missing_fields" && (
              <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <svg
                  className="w-5 h-5 text-red-500 shrink-0 mt-0.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <div>
                  <p className="text-sm font-medium text-red-800">
                    Заповніть поля
                  </p>
                  <p className="text-xs text-red-600 mt-0.5">
                    Місто та вулиця є обов'язковими полями
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-start gap-2">
            <div className="grid grid-cols-2 gap-4 flex-1">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Вулиця *
                </label>
                <input
                  type="text"
                  value={shopAddress.street}
                  onChange={(e) =>
                    handleAddressChange("street", e.target.value)
                  }
                  className={getInputClassName("street")}
                  placeholder="Хрещатик"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Будинок
                </label>
                <input
                  type="text"
                  value={shopAddress.house}
                  onChange={(e) => handleAddressChange("house", e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="1"
                />
              </div>
            </div>
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            onClick={handleSave}
            disabled={loading || isLoading}
            className="w-full px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading
              ? "Зберігаємо..."
              : isLoading
                ? "Перевіряємо адресу..."
                : "Зберегти адресу"}
          </button>
        </div>
      </div>

      {isMapOpen && (
        <MapPicker
          isOpen={isMapOpen}
          onClose={closeMap}
          onConfirm={handleMapConfirm}
          isLoading={isLoading}
          initialStreet={shopAddress.street}
          initialHouse={shopAddress.house}
          city={shopAddress.city}
          onGeocode={forwardGeocode}
          defaultCenter={pendingCoordinates ?? undefined}
        />
      )}
    </>
  );
};
