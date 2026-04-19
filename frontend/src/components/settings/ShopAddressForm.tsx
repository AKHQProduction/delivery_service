import React, { useEffect, useRef, useState } from "react";
import { MapPicker, type MapConfirmData } from "../shared/MapPicker";
import { MapButton } from "../shared/MapButton";
import { useMapPicker } from "../../hooks/useMapPicker";
import { useAddressSuggestions } from "../../hooks/useAddressSuggestions";
import { useShopSettings, type ShopAddress } from "../../hooks/settings/useShopSettings";
import { useUserShopStore } from "../../context/useUserShopStore";
import { type AddressSuggestion } from "../../services/api/geocodingApi";
import { hasDigit } from "../../utils/addressValidation";

interface ShopAddressFormProps {
  onSuccess?: () => void;
}

type AddressError = "not_found" | "needs_verification" | "missing_fields" | null;

const MIN_STREET_LENGTH_FOR_HOUSE_SUGGESTIONS = 5;

const buildSuggestionQuery = (street: string, house: string) => {
  const normalizedStreet = street.trim();
  const normalizedHouse = house.trim();

  if (!normalizedStreet) {
    return "";
  }

  if (
    normalizedStreet.length < MIN_STREET_LENGTH_FOR_HOUSE_SUGGESTIONS ||
    !hasDigit(normalizedHouse)
  ) {
    return normalizedStreet;
  }

  return `${normalizedStreet} ${normalizedHouse}`.trim();
};

const buildSuggestionTitle = (suggestion: AddressSuggestion) =>
  [suggestion.street, suggestion.house].filter(Boolean).join(", ");

const buildSuggestionSubtitle = (suggestion: AddressSuggestion) =>
  [suggestion.district, suggestion.city].filter(Boolean).join(", ");

export const ShopAddressForm: React.FC<ShopAddressFormProps> = ({ onSuccess }) => {
  const shop = useUserShopStore((state) => state.shop);
  const { loading, error, saveShopAddress } = useShopSettings();
  const suggestionDropdownRef = useRef<HTMLDivElement>(null);

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

  const { isMapOpen, isLoading, openMap, closeMap, reverseGeocode, forwardGeocode } =
    useMapPicker();
  const suggestionQuery = buildSuggestionQuery(shopAddress.street, shopAddress.house);
  const {
    items: suggestionItems,
    isLoading: isSuggestionsLoading,
    isOpen: isSuggestionsOpen,
    error: suggestionsError,
    open: openSuggestions,
    close: closeSuggestions,
    clear: clearSuggestions,
  } = useAddressSuggestions(suggestionQuery, {
    city: shopAddress.city,
    enabled: shopAddress.city.trim().length > 0,
    limit: 5,
    debounceMs: 300,
  });

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionDropdownRef.current &&
        !suggestionDropdownRef.current.contains(event.target as Node)
      ) {
        closeSuggestions();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [closeSuggestions]);

  useEffect(() => {
    if (!suggestionQuery || !shopAddress.city.trim()) {
      clearSuggestions();
    }
  }, [clearSuggestions, shopAddress.city, suggestionQuery]);

  const handleAddressChange = (field: keyof ShopAddress, value: string) => {
    setShopAddress((prev) => ({
      ...prev,
      [field]: value,
      ...(field === "street" || field === "house" || field === "city"
        ? { coordinates: null }
        : {}),
    }));
    setAddressError(null);
    setPendingCoordinates(null);
  };

  const handleStreetHouseChange = (field: "street" | "house", value: string) => {
    handleAddressChange(field, value);

    if (shopAddress.city.trim()) {
      openSuggestions();
      return;
    }

    closeSuggestions();
  };

  const handleSuggestionSelect = (suggestion: AddressSuggestion) => {
    const nextCity = suggestion.city.trim() || shopAddress.city;
    const nextPendingCoordinates = suggestion.coordinates
      ? {
          lat: suggestion.coordinates.latitude,
          lng: suggestion.coordinates.longitude,
        }
      : null;

    setShopAddress((prev) => ({
      ...prev,
      street: suggestion.street || prev.street,
      house: suggestion.house || prev.house,
      city: nextCity,
      coordinates: suggestion.coordinates
        ? {
            latitude: suggestion.coordinates.latitude,
            longitude: suggestion.coordinates.longitude,
          }
        : null,
    }));
    setPendingCoordinates(nextPendingCoordinates);
    setAddressError(nextPendingCoordinates ? "needs_verification" : null);
    closeSuggestions();
    openMap();
  };

  const handleSave = async () => {
    if (!shopAddress.city.trim() || !shopAddress.street.trim()) {
      setAddressError("missing_fields");
      return;
    }

    // Forward geocode to place marker, then open map for verification
    const coords = await forwardGeocode(shopAddress.street, shopAddress.house, shopAddress.city);
    if (!coords) {
      setPendingCoordinates(null);
      setAddressError("not_found");
      return;
    }

    setPendingCoordinates(coords);
    setAddressError("needs_verification");
    openMap();
  };

  const handleMapConfirm = async (data: MapConfirmData) => {
    let street = data.street;
    let house = data.house || shopAddress.house;
    let city = data.city || shopAddress.city;

    if (!street) {
      const result = await reverseGeocode({ lat: data.lat, lng: data.lng });
      if (result) {
        street = result.street || result.fullAddress;
        house = result.house || shopAddress.house;
        city = result.city || shopAddress.city;
      }
    }

    if (!street) return;

    const updatedAddress: ShopAddress = {
      street,
      house,
      city,
      coordinates: { latitude: data.lat, longitude: data.lng },
    };
    setShopAddress(updatedAddress);
    setAddressError(null);
    setPendingCoordinates(null);
    closeMap();

    if (updatedAddress.street.trim()) {
      const success = await saveShopAddress(updatedAddress);
      if (success) {
        onSuccess?.();
      }
    }
  };

  const getInputClassName = (field: "city" | "street") => {
    const baseClass =
      "w-full px-4 py-3 border-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent";
    const isEmpty = !shopAddress[field].trim();
    const hasError = addressError === "missing_fields" && isEmpty;
    return `${baseClass} ${hasError ? "border-red-300 bg-red-50" : "border-gray-200"}`;
  };

  const showSuggestions = isSuggestionsOpen && suggestionQuery.length > 0;
  const hasConfirmedCoordinates = Boolean(shopAddress.coordinates) && !pendingCoordinates;

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Адреса магазину</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Місто *</label>
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
            {hasConfirmedCoordinates ? (
              <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Координати збережено
              </p>
            ) : pendingCoordinates ? (
              <p className="text-xs text-amber-600 mt-1">
                Координати знайдено. Підтвердіть адресу на карті, щоб зберегти її
              </p>
            ) : (
              <p className="text-xs text-gray-500 mt-1">
                Виберіть точку на карті, щоб автоматично заповнити адресу та зберегти координати
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
                  <p className="text-sm font-medium text-red-800">Адресу не знайдено</p>
                  <p className="text-xs text-red-600 mt-0.5">
                    Перевірте правильність адреси або виберіть місцезнаходження на карті
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
                  <p className="text-sm font-medium text-amber-800">Підтвердіть місцезнаходження</p>
                  <p className="text-xs text-amber-700 mt-0.5">
                    Адресу знайдено. Будь ласка, перевірте на карті, що мітка встановлена правильно
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
                  <p className="text-sm font-medium text-red-800">Заповніть поля</p>
                  <p className="text-xs text-red-600 mt-0.5">
                    Місто та вулиця є обов'язковими полями
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-start gap-2">
            <div className="relative flex-1" ref={suggestionDropdownRef}>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Вулиця *</label>
                  <input
                    type="text"
                    value={shopAddress.street}
                    onChange={(e) => handleStreetHouseChange("street", e.target.value)}
                    onFocus={openSuggestions}
                    className={getInputClassName("street")}
                    placeholder="Хрещатик"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Будинок</label>
                  <input
                    type="text"
                    value={shopAddress.house}
                    onChange={(e) => handleStreetHouseChange("house", e.target.value)}
                    onFocus={openSuggestions}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="1"
                  />
                </div>
              </div>

              {showSuggestions && (
                <div className="absolute z-50 mt-2 w-full rounded-xl border border-gray-200 bg-white shadow-lg overflow-hidden">
                  {isSuggestionsLoading && (
                    <div className="px-4 py-3 text-sm text-gray-500">Пошук адрес...</div>
                  )}

                  {!isSuggestionsLoading && suggestionsError && (
                    <div className="px-4 py-3 text-sm text-red-600">
                      Не вдалося завантажити підказки
                    </div>
                  )}

                  {!isSuggestionsLoading && !suggestionsError && suggestionItems.length > 0 && (
                    <div className="max-h-60 overflow-y-auto">
                      {suggestionItems.map((suggestion) => (
                        <button
                          key={[
                            suggestion.street,
                            suggestion.house,
                            suggestion.district,
                            suggestion.city,
                            suggestion.coordinates?.latitude,
                            suggestion.coordinates?.longitude,
                          ].join("-")}
                          type="button"
                          onMouseDown={(event) => event.preventDefault()}
                          onClick={() => handleSuggestionSelect(suggestion)}
                          className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors"
                        >
                          <div className="text-sm font-medium text-gray-900">
                            {buildSuggestionTitle(suggestion) || suggestion.label}
                          </div>
                          {buildSuggestionSubtitle(suggestion) && (
                            <div className="text-xs text-gray-500">
                              {buildSuggestionSubtitle(suggestion)}
                            </div>
                          )}
                        </button>
                      ))}
                    </div>
                  )}

                  {!isSuggestionsLoading && !suggestionsError && suggestionItems.length === 0 && (
                    <div className="px-4 py-3 text-sm text-gray-500">
                      Підказки не знайдено. Спробуйте уточнити адресу або вибрати точку на карті.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            onClick={handleSave}
            disabled={loading || isLoading}
            className="w-full px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? "Зберігаємо..." : isLoading ? "Перевіряємо адресу..." : "Зберегти адресу"}
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
          onReverseGeocode={reverseGeocode}
          defaultCenter={
            pendingCoordinates ??
            (shopAddress.coordinates
              ? { lat: shopAddress.coordinates.latitude, lng: shopAddress.coordinates.longitude }
              : undefined)
          }
        />
      )}
    </>
  );
};
