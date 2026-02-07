import React, { useState, useEffect, useRef } from "react";
import { MapPicker } from "./MapPicker";
import { MapButton } from "./MapButton";
import { Toast } from "../ui/Toast";
import { useMapPicker } from "../../hooks/useMapPicker";
import { useUserShopStore } from "../../context/useUserShopStore";
import { useToast } from "../../hooks/useToast";
import { type Address, type AddressCoordinates } from "../../types/entities/Client";

export interface District {
  district_id: string;
  name: string;
}

interface AddressInputListProps {
  addresses: Address[];
  onSetPrimary: (index: number) => void;
  onAddressChange: (index: number, field: keyof Address, value: string) => void;
  onCoordinatesChange: (index: number, coordinates: AddressCoordinates | null) => void;
  onRemove: (index: number) => void;
  onAdd: () => void;
  districts?: District[];
}

export const AddressInputList: React.FC<AddressInputListProps> = ({
  addresses,
  onSetPrimary,
  onAddressChange,
  onCoordinatesChange,
  onRemove,
  onAdd,
  districts = [],
}) => {
  const shop = useUserShopStore((state) => state.shop);
  const { toast, showToast, hideToast } = useToast();
  const { isMapOpen, isLoading, openMap, closeMap, reverseGeocode, forwardGeocode } =
    useMapPicker();

  const [currentEditingIndex, setCurrentEditingIndex] = useState<number | null>(null);
  const [addressStatus, setAddressStatus] = useState<Record<number, "found" | "not_found" | null>>(
    {},
  );
  const debounceTimers = useRef<Record<number, ReturnType<typeof setTimeout>>>({});

  // Cleanup timers on unmount
  useEffect(() => {
    const timers = debounceTimers.current;
    return () => {
      Object.values(timers).forEach(clearTimeout);
    };
  }, []);

  const checkAddress = async (index: number, street: string, house: string) => {
    if (!street.trim()) {
      setAddressStatus((prev) => ({ ...prev, [index]: null }));
      onCoordinatesChange(index, null);
      return;
    }

    const city = shop?.city ?? undefined;
    const coords = await forwardGeocode(street, house || undefined, city);

    if (coords) {
      setAddressStatus((prev) => ({ ...prev, [index]: "found" }));
      onCoordinatesChange(index, {
        latitude: coords.lat,
        longitude: coords.lng,
      });
      showToast(
        `Адресу "${street}${house ? `, ${house}` : ""}" знайдено${city ? ` в м. ${city}` : ""}`,
        "success",
      );
    } else {
      setAddressStatus((prev) => ({ ...prev, [index]: "not_found" }));
      onCoordinatesChange(index, null);
      showToast(
        `Адресу "${street}${house ? `, ${house}` : ""}" не знайдено. Спробуйте вибрати на карті`,
        "warning",
      );
    }
  };

  const handleAddressFieldChange = (index: number, field: keyof Address, value: string) => {
    onAddressChange(index, field, value);

    // Only trigger geocode check for street or house changes
    if (field === "street" || field === "house") {
      // Clear previous status
      setAddressStatus((prev) => ({ ...prev, [index]: null }));

      // Clear previous timer for this index
      if (debounceTimers.current[index]) {
        clearTimeout(debounceTimers.current[index]);
      }

      // Get current values (with the new value applied)
      const currentAddress = addresses[index];
      const street = field === "street" ? value : currentAddress.street;
      const house = field === "house" ? value : currentAddress.house;

      // Debounce the geocode check
      if (street.trim()) {
        debounceTimers.current[index] = setTimeout(() => {
          checkAddress(index, street, house);
        }, 1000);
      }
    }
  };

  const handleOpenMap = (index: number) => {
    setCurrentEditingIndex(index);
    openMap();
  };

  const handleMapConfirm = async (coordinates: { lat: number; lng: number }) => {
    if (currentEditingIndex === null) return;

    const result = await reverseGeocode(coordinates);

    if (result) {
      onAddressChange(currentEditingIndex, "street", result.street);
      onAddressChange(currentEditingIndex, "house", result.house);
      onCoordinatesChange(currentEditingIndex, {
        latitude: coordinates.lat,
        longitude: coordinates.lng,
      });
      setAddressStatus((prev) => ({ ...prev, [currentEditingIndex]: "found" }));
      showToast("Адресу вибрано з карти", "success");
      closeMap();
      setCurrentEditingIndex(null);
    }
  };

  const getInputBorderClass = (index: number) => {
    const status = addressStatus[index];
    if (status === "found") return "border-green-300 bg-green-50";
    if (status === "not_found") return "border-amber-300 bg-amber-50";
    return "border-gray-300";
  };

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">Адреси</label>
      {addresses.map((address, index) => (
        <div key={index} className="p-4 border-2 border-gray-200 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-gray-600">Адреса #{index + 1}</label>
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
              <MapButton onClick={() => handleOpenMap(index)} />
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
            <div className="flex items-start gap-2">
              <div className="grid grid-cols-2 gap-2 flex-1">
                <div className="relative">
                  <input
                    type="text"
                    value={address.street}
                    onChange={(e) => handleAddressFieldChange(index, "street", e.target.value)}
                    placeholder="Вулиця *"
                    required
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${getInputBorderClass(index)}`}
                  />
                </div>

                <input
                  type="text"
                  value={address.house}
                  onChange={(e) => handleAddressFieldChange(index, "house", e.target.value)}
                  placeholder="Будинок *"
                  required
                  className={`px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${getInputBorderClass(index)}`}
                />
              </div>
            </div>

            {addressStatus[index] === "not_found" && (
              <p className="text-xs text-amber-600 flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01"
                  />
                </svg>
                Адресу не знайдено. Виберіть на карті для точного розташування
              </p>
            )}

            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={address.apartment || ""}
                onChange={(e) => onAddressChange(index, "apartment", e.target.value)}
                placeholder="Квартира"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="text"
                value={address.entrance || ""}
                onChange={(e) => onAddressChange(index, "entrance", e.target.value)}
                placeholder="Під'їзд"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="text"
                value={address.floor || ""}
                onChange={(e) => onAddressChange(index, "floor", e.target.value)}
                placeholder="Поверх"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="text"
                value={address.intercom || ""}
                onChange={(e) => onAddressChange(index, "intercom", e.target.value)}
                placeholder="Домофон"
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            {districts.length > 0 && (
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Район</label>
                <select
                  value={address.district_id || ""}
                  onChange={(e) => onAddressChange(index, "district_id", e.target.value || "")}
                  title="Район доставки"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                >
                  <option value="">Не вказано</option>
                  {districts.map((district) => (
                    <option key={district.district_id} value={district.district_id}>
                      {district.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

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
                  onChange={(e) => onAddressChange(index, "comment", e.target.value)}
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

      <MapPicker
        isOpen={isMapOpen}
        onClose={closeMap}
        onConfirm={handleMapConfirm}
        isLoading={isLoading}
        initialStreet={currentEditingIndex !== null ? addresses[currentEditingIndex]?.street : ""}
        initialHouse={currentEditingIndex !== null ? addresses[currentEditingIndex]?.house : ""}
        city={shop?.city ?? undefined}
        onGeocode={forwardGeocode}
      />

      {toast.isVisible && <Toast message={toast.message} type={toast.type} onClose={hideToast} />}
    </div>
  );
};
