import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import { MapPicker, type MapConfirmData } from "./MapPicker";
import { MapButton } from "./MapButton";
import { Toast } from "../ui/Toast";
import { useMapPicker } from "../../hooks/useMapPicker";
import { useAddressSuggestions } from "../../hooks/useAddressSuggestions";
import { useUserShopStore } from "../../context/useUserShopStore";
import { useToast } from "../../hooks/useToast";
import { type Address, type AddressCoordinates } from "../../types/entities/Client";
import { type AddressSuggestion } from "../../services/api/geocodingApi";
import { hasDigit, hasLetter } from "../../utils/addressValidation";

type AddressValidationStatus = "found" | "not_found" | null;

interface AddressFieldError {
  street?: boolean;
  house?: boolean;
}

interface AddressRowEntry {
  fingerprint: string;
  key: string;
  persistentId?: string;
}

interface AddressRowState {
  entries: AddressRowEntry[];
  nextKey: number;
}

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

interface AddressRowProps {
  address: Address;
  index: number;
  addressCount: number;
  addressStatus: AddressValidationStatus;
  fieldError?: AddressFieldError;
  districts: District[];
  shopCity: string;
  onSetPrimary: (index: number) => void;
  onAddressFieldChange: (rowKey: string, field: keyof Address, value: string) => void;
  onAddressChange: (index: number, field: keyof Address, value: string) => void;
  onSuggestionSelect: (rowKey: string, suggestion: AddressSuggestion) => void;
  onRemove: (index: number) => void;
  onOpenMap: (rowKey: string) => void;
  rowKey: string;
}

const getInputBorderClass = (status: AddressValidationStatus) => {
  if (status === "found") return "border-green-300 bg-green-50";
  if (status === "not_found") return "border-amber-300 bg-amber-50";
  return "border-gray-300";
};

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

const normalizeDistrictName = (value: string) =>
  value
    .toLocaleLowerCase("uk-UA")
    .replace(/[’'`]/g, "")
    .replace(
      /(^|\s)(район|району|районі|р-н|мікрорайон|мікрорайону|мікрорайоні|микрорайон|микрорайону|микрорайоні|мкр|м-н)(?=\s|$)/giu,
      " ",
    )
    .replace(/[^0-9a-zа-яіїєґ]+/giu, " ")
    .replace(/\s+/g, " ")
    .trim();

const findMatchingDistrictId = (districtName: string | undefined, districts: District[]) => {
  const normalizedDistrictName = normalizeDistrictName(districtName || "");

  if (!normalizedDistrictName) {
    return "";
  }

  const match = districts.find(
    (district) => normalizeDistrictName(district.name) === normalizedDistrictName,
  );

  return match?.district_id ?? "";
};

const getAddressFingerprint = (address: Address) =>
  JSON.stringify({
    apartment: address.apartment || "",
    comment: address.comment || "",
    coordinates: address.coordinates
      ? {
          latitude: address.coordinates.latitude,
          longitude: address.coordinates.longitude,
        }
      : null,
    district_id: address.district_id || "",
    entrance: address.entrance || "",
    floor: address.floor || "",
    house: address.house || "",
    id: address.id ?? null,
    intercom: address.intercom || "",
    is_primary: address.is_primary,
    street: address.street || "",
  });

const syncAddressRowEntries = (
  addresses: Address[],
  previousState: AddressRowState,
): AddressRowState => {
  const previousEntries = previousState.entries;
  const nextEntries = new Array<AddressRowEntry>(addresses.length);
  const usedPreviousEntries = new Array(previousEntries.length).fill(false);
  let nextKey = previousState.nextKey;
  const fingerprints = addresses.map(getAddressFingerprint);
  const persistentIds = addresses.map((address) =>
    address.id !== undefined && address.id !== null ? `address:${address.id}` : undefined,
  );

  const assignFromPrevious = (nextIndex: number, previousIndex: number) => {
    const previousEntry = previousEntries[previousIndex];

    nextEntries[nextIndex] = {
      key: previousEntry.key,
      persistentId: persistentIds[nextIndex],
      fingerprint: fingerprints[nextIndex],
    };
    usedPreviousEntries[previousIndex] = true;
  };

  addresses.forEach((_, index) => {
    const persistentId = persistentIds[index];

    if (!persistentId) {
      return;
    }

    const previousIndex = previousEntries.findIndex(
      (entry, entryIndex) =>
        !usedPreviousEntries[entryIndex] && entry.persistentId === persistentId,
    );

    if (previousIndex !== -1) {
      assignFromPrevious(index, previousIndex);
    }
  });

  addresses.forEach((_, index) => {
    if (nextEntries[index]) {
      return;
    }

    const previousEntry = previousEntries[index];

    if (!previousEntry || usedPreviousEntries[index]) {
      return;
    }

    if (previousEntry.fingerprint === fingerprints[index]) {
      assignFromPrevious(index, index);
    }
  });

  addresses.forEach((_, index) => {
    if (nextEntries[index]) {
      return;
    }

    const previousIndex = previousEntries.findIndex(
      (entry, entryIndex) =>
        !usedPreviousEntries[entryIndex] && entry.fingerprint === fingerprints[index],
    );

    if (previousIndex !== -1) {
      assignFromPrevious(index, previousIndex);
    }
  });

  if (previousEntries.length === addresses.length) {
    addresses.forEach((_, index) => {
      if (nextEntries[index]) {
        return;
      }

      const previousEntry = previousEntries[index];

      if (!previousEntry || usedPreviousEntries[index]) {
        return;
      }

      assignFromPrevious(index, index);
    });
  }

  addresses.forEach((_, index) => {
    if (!nextEntries[index]) {
      nextEntries[index] = {
        key: `address-row-${nextKey}`,
        persistentId: persistentIds[index],
        fingerprint: fingerprints[index],
      };
      nextKey += 1;
    }
  });

  return {
    entries: nextEntries,
    nextKey,
  };
};

const createInitialAddressRowState = (addresses: Address[]): AddressRowState =>
  syncAddressRowEntries(addresses, { entries: [], nextKey: 0 });

const pruneRecord = <T,>(record: Record<string, T>, activeRowKeys: Set<string>) => {
  let changed = false;
  const nextRecord: Record<string, T> = {};

  Object.entries(record).forEach(([key, value]) => {
    if (activeRowKeys.has(key)) {
      nextRecord[key] = value;
      return;
    }

    changed = true;
  });

  return changed ? nextRecord : record;
};

const AddressRow: React.FC<AddressRowProps> = ({
  address,
  index,
  addressCount,
  addressStatus,
  fieldError,
  districts,
  shopCity,
  onSetPrimary,
  onAddressFieldChange,
  onAddressChange,
  onSuggestionSelect,
  onRemove,
  onOpenMap,
  rowKey,
}) => {
  const dropdownRef = useRef<HTMLDivElement>(null);
  const suggestionQuery = buildSuggestionQuery(address.street, address.house);
  const { items, isLoading, isOpen, error, open, close, clear } = useAddressSuggestions(
    suggestionQuery,
    {
      city: shopCity,
      enabled: shopCity.trim().length > 0,
      limit: 5,
      debounceMs: 300,
    },
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        close();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [close]);

  useEffect(() => {
    if (!suggestionQuery || !shopCity.trim()) {
      clear();
    }
  }, [clear, shopCity, suggestionQuery]);

  const handleStreetHouseChange = (field: "street" | "house", value: string) => {
    onAddressFieldChange(rowKey, field, value);

    if (shopCity.trim()) {
      open();
    } else {
      close();
    }
  };

  const handleSuggestionClick = (suggestion: AddressSuggestion) => {
    close();
    onSuggestionSelect(rowKey, suggestion);
  };

  const showSuggestions = isOpen && suggestionQuery.length > 0;

  return (
    <div className="p-4 border-2 border-gray-200 rounded-xl space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-medium text-gray-600">Адреса #{index + 1}</label>
        <div className="flex items-center gap-2">
          {!address.is_primary && addressCount > 1 && (
            <button
              type="button"
              onClick={() => onSetPrimary(index)}
              className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
            >
              Зробити основною
            </button>
          )}
          <MapButton onClick={() => onOpenMap(rowKey)} />
          {address.is_primary && (
            <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full font-medium">
              Основна
            </span>
          )}
          {addressCount > 1 && (
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
        <div className="relative" ref={dropdownRef}>
          <div className="flex items-start gap-2">
            <div className="grid grid-cols-2 gap-2 flex-1">
              <div className="relative">
                <input
                  type="text"
                  value={address.street}
                  onChange={(e) => handleStreetHouseChange("street", e.target.value)}
                  onFocus={open}
                  placeholder="Вулиця *"
                  required
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${fieldError?.street ? "border-red-400 bg-red-50" : getInputBorderClass(addressStatus)}`}
                />
              </div>

              <input
                type="text"
                value={address.house}
                onChange={(e) => handleStreetHouseChange("house", e.target.value)}
                onFocus={open}
                placeholder="Будинок *"
                required
                className={`px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${fieldError?.house ? "border-red-400 bg-red-50" : getInputBorderClass(addressStatus)}`}
              />
            </div>
          </div>

          {showSuggestions && (
            <div className="absolute z-50 mt-2 w-full rounded-xl border border-gray-200 bg-white shadow-lg overflow-hidden">
              {isLoading && <div className="px-4 py-3 text-sm text-gray-500">Пошук адрес...</div>}

              {!isLoading && error && (
                <div className="px-4 py-3 text-sm text-red-600">
                  Не вдалося завантажити підказки
                </div>
              )}

              {!isLoading && !error && items.length > 0 && (
                <div className="max-h-60 overflow-y-auto">
                  {items.map((suggestion) => (
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
                      onClick={() => handleSuggestionClick(suggestion)}
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

              {!isLoading && !error && items.length === 0 && (
                <div className="px-4 py-3 text-sm text-gray-500">
                  Підказки не знайдено. Спробуйте уточнити адресу або вибрати точку на карті.
                </div>
              )}
            </div>
          )}
        </div>

        {addressStatus === "not_found" && (
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
  );
};

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
  const { forwardGeocode: backgroundForwardGeocode } = useMapPicker();
  const {
    isMapOpen,
    isLoading: isMapLoading,
    openMap,
    closeMap,
    reverseGeocode,
    forwardGeocode: mapForwardGeocode,
  } = useMapPicker();

  const [currentEditingRowKey, setCurrentEditingRowKey] = useState<string | null>(null);
  const [addressStatus, setAddressStatus] = useState<Record<string, AddressValidationStatus>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, AddressFieldError>>({});
  const [pendingSuggestionDistrictIds, setPendingSuggestionDistrictIds] = useState<
    Record<string, string>
  >({});

  const debounceTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const validationTokens = useRef<Record<string, number>>({});
  const [addressRowState, setAddressRowState] = useState<AddressRowState>(() =>
    createInitialAddressRowState(addresses),
  );

  useLayoutEffect(() => {
    queueMicrotask(() => {
      setAddressRowState((previousState) => syncAddressRowEntries(addresses, previousState));
    });
  }, [addresses]);

  const addressRowEntries = addressRowState.entries;
  const addressRowKeys = React.useMemo(
    () => addressRowEntries.map((entry) => entry.key),
    [addressRowEntries],
  );
  const addressIndexByRowKey = React.useMemo(
    () => Object.fromEntries(addressRowEntries.map((entry, index) => [entry.key, index])),
    [addressRowEntries],
  );

  useEffect(() => {
    const timers = debounceTimers.current;
    return () => {
      Object.values(timers).forEach(clearTimeout);
    };
  }, []);

  useEffect(() => {
    const activeRowKeys = new Set(addressRowKeys);
    queueMicrotask(() => {
      setAddressStatus((prev) => pruneRecord(prev, activeRowKeys));
      setFieldErrors((prev) => pruneRecord(prev, activeRowKeys));
      setPendingSuggestionDistrictIds((prev) => pruneRecord(prev, activeRowKeys));

      Object.keys(debounceTimers.current).forEach((rowKey) => {
        if (!activeRowKeys.has(rowKey)) {
          clearTimeout(debounceTimers.current[rowKey]);
          delete debounceTimers.current[rowKey];
        }
      });

      Object.keys(validationTokens.current).forEach((rowKey) => {
        if (!activeRowKeys.has(rowKey)) {
          delete validationTokens.current[rowKey];
        }
      });

      if (currentEditingRowKey && !activeRowKeys.has(currentEditingRowKey)) {
        setCurrentEditingRowKey(null);
      }
    });
  }, [addressRowKeys, currentEditingRowKey]);

  const getAddressIndex = (rowKey: string) => {
    const index = addressIndexByRowKey[rowKey];
    return typeof index === "number" ? index : null;
  };

  const clearDebounceTimer = (rowKey: string) => {
    if (debounceTimers.current[rowKey]) {
      clearTimeout(debounceTimers.current[rowKey]);
      delete debounceTimers.current[rowKey];
    }
  };

  const bumpValidationToken = (rowKey: string) => {
    const nextToken = (validationTokens.current[rowKey] ?? 0) + 1;
    validationTokens.current[rowKey] = nextToken;
    return nextToken;
  };

  const isValidationTokenCurrent = (rowKey: string, token: number) =>
    validationTokens.current[rowKey] === token;

  const invalidateValidation = (rowKey: string) => {
    bumpValidationToken(rowKey);
    clearDebounceTimer(rowKey);
  };

  const checkAddress = async (
    rowKey: string,
    street: string,
    house: string,
    validationToken: number,
  ) => {
    if (!street.trim() || !house.trim() || !hasLetter(street) || !hasDigit(house)) {
      if (isValidationTokenCurrent(rowKey, validationToken)) {
        setAddressStatus((prev) => ({ ...prev, [rowKey]: null }));
      }
      return;
    }

    const city = shop?.city ?? undefined;
    const coords = await backgroundForwardGeocode(street, house, city);

    if (!isValidationTokenCurrent(rowKey, validationToken)) {
      return;
    }

    const index = getAddressIndex(rowKey);

    if (index === null) {
      return;
    }

    if (coords) {
      setAddressStatus((prev) => ({ ...prev, [rowKey]: "found" }));
      onCoordinatesChange(index, {
        latitude: coords.lat,
        longitude: coords.lng,
      });

      showToast(`Адресу "${street}, ${house}" знайдено${city ? ` в м. ${city}` : ""}`, "success");
    } else {
      setAddressStatus((prev) => ({ ...prev, [rowKey]: "not_found" }));
      showToast(`Адресу "${street}, ${house}" не знайдено. Спробуйте вибрати на карті`, "warning");
    }
  };

  const handleAddressFieldChange = (rowKey: string, field: keyof Address, value: string) => {
    const index = getAddressIndex(rowKey);

    if (index === null) {
      return;
    }

    const currentAddress = addresses[index];
    const validationToken = bumpValidationToken(rowKey);

    onAddressChange(index, field, value);

    if (field === "street" || field === "house") {
      onCoordinatesChange(index, null);
      setAddressStatus((prev) => ({ ...prev, [rowKey]: null }));
      setFieldErrors((prev) => ({ ...prev, [rowKey]: {} }));
      setPendingSuggestionDistrictIds((prev) => {
        if (!(rowKey in prev)) {
          return prev;
        }

        const next = { ...prev };
        delete next[rowKey];
        return next;
      });
      clearDebounceTimer(rowKey);

      const street = field === "street" ? value : currentAddress.street;
      const house = field === "house" ? value : currentAddress.house;

      if (street.trim() && house.trim()) {
        debounceTimers.current[rowKey] = setTimeout(() => {
          if (!isValidationTokenCurrent(rowKey, validationToken)) {
            return;
          }

          const streetValid = hasLetter(street);
          const houseValid = hasDigit(house);

          if (streetValid && houseValid) {
            checkAddress(rowKey, street, house, validationToken);
            return;
          }

          if (
            !isValidationTokenCurrent(rowKey, validationToken) ||
            getAddressIndex(rowKey) === null
          ) {
            return;
          }

          setFieldErrors((prev) => ({
            ...prev,
            [rowKey]: { street: !streetValid, house: !houseValid },
          }));
        }, 2000);
      }
    }
  };

  const handleSuggestionSelect = (rowKey: string, suggestion: AddressSuggestion) => {
    const index = getAddressIndex(rowKey);

    if (index === null) {
      return;
    }

    invalidateValidation(rowKey);
    setFieldErrors((prev) => ({ ...prev, [rowKey]: {} }));
    setAddressStatus((prev) => ({ ...prev, [rowKey]: suggestion.coordinates ? "found" : null }));

    onAddressChange(index, "street", suggestion.street);
    onAddressChange(index, "house", suggestion.house);
    onCoordinatesChange(
      index,
      suggestion.coordinates
        ? {
            latitude: suggestion.coordinates.latitude,
            longitude: suggestion.coordinates.longitude,
          }
        : null,
    );

    const matchedSuggestionDistrictId = findMatchingDistrictId(
      suggestion.district || undefined,
      districts,
    );
    if (matchedSuggestionDistrictId) {
      onAddressChange(index, "district_id", matchedSuggestionDistrictId);
    }

    setPendingSuggestionDistrictIds((prev) => {
      if (!matchedSuggestionDistrictId) {
        if (!(rowKey in prev)) {
          return prev;
        }

        const next = { ...prev };
        delete next[rowKey];
        return next;
      }

      return {
        ...prev,
        [rowKey]: matchedSuggestionDistrictId,
      };
    });

    setCurrentEditingRowKey(rowKey);
    openMap();
  };

  const handleOpenMap = (rowKey: string) => {
    invalidateValidation(rowKey);
    setCurrentEditingRowKey(rowKey);
    openMap();
  };

  const handleMapConfirm = async (data: MapConfirmData) => {
    if (!currentEditingRowKey) {
      return;
    }

    const index = getAddressIndex(currentEditingRowKey);

    if (index === null) {
      return;
    }

    invalidateValidation(currentEditingRowKey);
    const reverseGeocodeResult = await reverseGeocode({ lat: data.lat, lng: data.lng });
    let street = data.street;
    let house = data.house;

    if (!street && reverseGeocodeResult) {
      street = reverseGeocodeResult.street || reverseGeocodeResult.fullAddress;
      house = reverseGeocodeResult.house || "-";
    }

    if (street) {
      onAddressChange(index, "street", street);
      onAddressChange(index, "house", house);
    }

    const matchedDistrictId =
      findMatchingDistrictId(reverseGeocodeResult?.district, districts) ||
      pendingSuggestionDistrictIds[currentEditingRowKey] ||
      "";

    if (matchedDistrictId) {
      onAddressChange(index, "district_id", matchedDistrictId);
    }

    onCoordinatesChange(index, {
      latitude: data.lat,
      longitude: data.lng,
    });
    setAddressStatus((prev) => ({ ...prev, [currentEditingRowKey]: "found" }));
    setFieldErrors((prev) => ({ ...prev, [currentEditingRowKey]: {} }));
    setPendingSuggestionDistrictIds((prev) => {
      if (!(currentEditingRowKey in prev)) {
        return prev;
      }

      const next = { ...prev };
      delete next[currentEditingRowKey];
      return next;
    });
    showToast("Адресу вибрано з карти", "success");
    closeMap();
    setCurrentEditingRowKey(null);
  };

  const currentEditingIndex = currentEditingRowKey ? addressIndexByRowKey[currentEditingRowKey] ?? null : null;

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">Адреси</label>
      {addresses.map((address, index) => {
        const rowKey = addressRowEntries[index].key;

        return (
          <AddressRow
            key={rowKey}
            rowKey={rowKey}
            address={address}
            index={index}
            addressCount={addresses.length}
            addressStatus={addressStatus[rowKey] ?? null}
            fieldError={fieldErrors[rowKey]}
            districts={districts}
            shopCity={shop?.city ?? ""}
            onSetPrimary={onSetPrimary}
            onAddressFieldChange={handleAddressFieldChange}
            onAddressChange={onAddressChange}
            onSuggestionSelect={handleSuggestionSelect}
            onRemove={onRemove}
            onOpenMap={handleOpenMap}
          />
        );
      })}
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
        isLoading={isMapLoading}
        initialStreet={currentEditingIndex !== null ? addresses[currentEditingIndex]?.street : ""}
        initialHouse={currentEditingIndex !== null ? addresses[currentEditingIndex]?.house : ""}
        city={shop?.city ?? undefined}
        onGeocode={mapForwardGeocode}
        onReverseGeocode={reverseGeocode}
        defaultCenter={
          currentEditingIndex !== null && addresses[currentEditingIndex]?.coordinates
            ? {
                lat: addresses[currentEditingIndex].coordinates!.latitude,
                lng: addresses[currentEditingIndex].coordinates!.longitude,
              }
            : undefined
        }
      />

      {toast.isVisible && <Toast message={toast.message} type={toast.type} onClose={hideToast} />}
    </div>
  );
};
