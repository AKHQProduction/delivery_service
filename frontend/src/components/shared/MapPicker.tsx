import React, { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import type { LatLng } from "leaflet";
import "leaflet/dist/leaflet.css";
import { type Coordinates, type MapPickerResult } from "../../hooks/useMapPicker";
import { hasLetter, hasDigit } from "../../utils/addressValidation";

//default marker icons in React-Leaflet
import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

export interface MapConfirmData {
  lat: number;
  lng: number;
  street: string;
  house: string;
  city: string;
}

interface MapPickerProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (data: MapConfirmData) => void;
  isLoading?: boolean;
  defaultCenter?: Coordinates;
  initialStreet?: string;
  initialHouse?: string;
  city?: string;
  onGeocode?: (street: string, house?: string, city?: string) => Promise<Coordinates | null>;
  onReverseGeocode?: (coordinates: Coordinates) => Promise<MapPickerResult | null>;
}

/**
 * Component that handles map click events and marker placement
 */
const MapClickHandler: React.FC<{
  onPositionChange: (position: LatLng) => void;
}> = ({ onPositionChange }) => {
  useMapEvents({
    click: (e) => {
      onPositionChange(e.latlng);
    },
  });
  return null;
};

/**
 * Component that updates map center when coordinates change
 */
const MapCenterController: React.FC<{ center: Coordinates }> = ({ center }) => {
  const map = useMapEvents({});

  useEffect(() => {
    if (!isValidCoordinates(center)) return;
    map.setView([center.lat, center.lng], 17.5);
  }, [center, map]);

  return null;
};

/**
 * Map picker component with marker placement
 */
const DEFAULT_CENTER: Coordinates = { lat: 50.4501, lng: 30.5234 }; // Kyiv, Ukraine
const MAP_TILE_URL =
  import.meta.env.VITE_MAP_TILE_URL || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const MAP_TILE_SUBDOMAINS = import.meta.env.VITE_MAP_TILE_URL
  ? ["mt0", "mt1", "mt2", "mt3"]
  : ["a", "b", "c"];
const isValidCoordinates = (coordinates: Coordinates | null | undefined): coordinates is Coordinates =>
  Number.isFinite(coordinates?.lat) && Number.isFinite(coordinates?.lng);

export const MapPicker: React.FC<MapPickerProps> = ({
  isOpen,
  onClose,
  onConfirm,
  isLoading = false,
  defaultCenter,
  initialStreet = "",
  initialHouse = "",
  city,
  onGeocode,
  onReverseGeocode,
}) => {
  const center = defaultCenter ?? DEFAULT_CENTER;
  const [markerPosition, setMarkerPosition] = useState<LatLng | null>(null);
  const [mapCenter, setMapCenter] = useState<Coordinates>(center);
  const hasGeocodedRef = useRef(false);
  const prevIsOpenRef = useRef(isOpen);

  const [addressCity, setAddressCity] = useState(city ?? "");
  const [addressStreet, setAddressStreet] = useState(initialStreet);
  const [addressHouse, setAddressHouse] = useState(initialHouse);
  const [searchError, setSearchError] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [showValidation, setShowValidation] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    setAddressCity(city ?? "");
    setAddressStreet(initialStreet);
    setAddressHouse(initialHouse);
  }, [isOpen, city, initialStreet, initialHouse]);

  // Update map center when defaultCenter changes and map opens
  useEffect(() => {
    if (isOpen && isValidCoordinates(defaultCenter)) {
      setMapCenter(defaultCenter);
      const latLng = L.latLng(defaultCenter.lat, defaultCenter.lng);
      setMarkerPosition(latLng);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, defaultCenter?.lat, defaultCenter?.lng]);

  // Geocode initial address or city when map opens (only once)
  useEffect(() => {
    if (isOpen && !hasGeocodedRef.current && onGeocode && !defaultCenter) {
      hasGeocodedRef.current = true;

      if (initialStreet) {
        // Geocode the full address with city
        onGeocode(initialStreet, initialHouse, city).then((coords) => {
          if (isValidCoordinates(coords)) {
            const latLng = L.latLng(coords.lat, coords.lng);
            setMarkerPosition(latLng);
            setMapCenter(coords);
          } else if (city) {
            // If address not found, at least center on the city
            onGeocode(city).then((cityCoords) => {
              if (isValidCoordinates(cityCoords)) {
                setMapCenter(cityCoords);
              }
            });
          }
        });
      } else if (city) {
        // No address, just center on the city
        onGeocode(city).then((coords) => {
          if (isValidCoordinates(coords)) {
            setMapCenter(coords);
          }
        });
      }
    }
  }, [isOpen, initialStreet, initialHouse, city, onGeocode, defaultCenter]);

  // Reset when map closes
  useEffect(() => {
    if (prevIsOpenRef.current && !isOpen) {
      hasGeocodedRef.current = false;
      setMarkerPosition(null);
      setMapCenter(DEFAULT_CENTER);
      setSearchError(false);
      setShowValidation(false);
    }
    prevIsOpenRef.current = isOpen;
  }, [isOpen]);

  const handleAddressSearch = async () => {
    setShowValidation(true);
    if (!onGeocode || !addressStreet.trim() || !addressCity.trim()) return;
    if (!hasLetter(addressStreet)) return;
    setIsSearching(true);
    setSearchError(false);
    const house = hasDigit(addressHouse) ? addressHouse : undefined;
    const coords = await onGeocode(addressStreet, house, addressCity);
    if (isValidCoordinates(coords)) {
      setMarkerPosition(L.latLng(coords.lat, coords.lng));
      setMapCenter(coords);
    } else {
      setSearchError(true);
    }
    setIsSearching(false);
  };

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (markerPosition) {
      onConfirm({
        lat: markerPosition.lat,
        lng: markerPosition.lng,
        street: addressStreet,
        house: addressHouse || "-",
        city: addressCity,
      });
    }
  };

  return createPortal(
    <div className="fixed inset-0 z-[9999] flex items-end justify-center bg-slate-950/45 p-0 sm:items-center sm:p-4">
      <div className="flex max-h-[94vh] w-full max-w-4xl flex-col overflow-hidden rounded-t-2xl bg-white shadow-xl sm:rounded-lg">
        <div className="flex items-start justify-between border-b border-slate-200 px-5 py-4 sm:px-6">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">Встановлення координат</h2>
            <p className="mt-1 text-sm text-slate-500">Знайдіть адресу або натисніть на карту</p>
          </div>
          <button
            type="button"
            aria-label="Закрити карту"
            onClick={onClose}
            className="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-950"
            disabled={isLoading}
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Address search */}
        {onGeocode && (
          <div className="border-b border-slate-200 bg-slate-50 px-5 py-4 sm:px-6">
            <div className="grid gap-2 sm:grid-cols-[9rem_minmax(0,1fr)_7rem_auto]">
              <input
                type="text"
                value={addressCity}
                onChange={(e) => { setAddressCity(e.target.value); setSearchError(false); setShowValidation(false); }}
                placeholder="Місто"
                className="h-11 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-950 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
              <input
                type="text"
                value={addressStreet}
                onChange={(e) => { setAddressStreet(e.target.value); setSearchError(false); setShowValidation(false); }}
                placeholder="Вулиця"
                className={`h-11 rounded-md border bg-white px-3 text-sm text-slate-950 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100 ${showValidation && addressStreet.trim() && !hasLetter(addressStreet) ? "border-red-400 bg-red-50" : "border-slate-300"}`}
              />
              <input
                type="text"
                value={addressHouse}
                onChange={(e) => { setAddressHouse(e.target.value); setSearchError(false); setShowValidation(false); }}
                placeholder="Будинок"
                className={`h-11 rounded-md border bg-white px-3 text-sm text-slate-950 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100 ${showValidation && addressHouse.trim() && !hasDigit(addressHouse) ? "border-red-400 bg-red-50" : "border-slate-300"}`}
              />
              <button
                type="button"
                onClick={handleAddressSearch}
                disabled={isSearching || !addressStreet.trim() || !addressCity.trim() || !hasLetter(addressStreet)}
                className="inline-flex h-11 items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {isSearching ? "Пошук..." : "Знайти"}
              </button>
            </div>
            {searchError && (
              <p className="mt-2 text-xs text-red-600">Адресу не знайдено. Спробуйте інший запит або виберіть точку на карті.</p>
            )}
          </div>
        )}

        <div className="relative h-[24rem] min-h-0 w-full sm:h-[32rem]">
          <MapContainer
            center={[mapCenter.lat, mapCenter.lng]}
            zoom={17.5}
            style={{ height: "100%", width: "100%" }}
            scrollWheelZoom={true}
          >
            <TileLayer
              url={MAP_TILE_URL}
              subdomains={MAP_TILE_SUBDOMAINS}
              maxZoom={21}
            />
            <MapCenterController center={mapCenter} />
            <MapClickHandler onPositionChange={(pos) => {
              setMarkerPosition(pos);
              if (onReverseGeocode) {
                onReverseGeocode({ lat: pos.lat, lng: pos.lng }).then((result) => {
                  if (result) {
                    setAddressCity(result.city);
                    setAddressStreet(result.street || result.fullAddress);
                    setAddressHouse(result.house || "-");
                  }
                });
              }
            }} />
            {markerPosition && <Marker position={markerPosition} />}
          </MapContainer>

          {/* Loading overlay */}
          {isLoading && (
            <div className="absolute inset-0 z-[1000] flex items-center justify-center bg-white/80">
              <div className="text-center">
                <div className="mx-auto mb-3 h-10 w-10 animate-spin rounded-full border-2 border-blue-100 border-t-blue-600" />
                <p className="font-medium text-slate-700">Визначення адреси...</p>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3 border-t border-slate-200 bg-white px-5 py-4 sm:px-6">
          <button
            type="button"
            onClick={onClose}
            className="h-12 rounded-md bg-slate-100 px-5 font-medium text-slate-700 transition-colors hover:bg-slate-200"
            disabled={isLoading}
          >
            Скасувати
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={!markerPosition || isLoading}
            className="h-12 rounded-md bg-blue-600 px-5 font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Зберегти координати
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
};
