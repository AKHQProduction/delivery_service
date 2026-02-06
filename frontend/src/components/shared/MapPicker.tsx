import React, { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import type { LatLng } from "leaflet";
import "leaflet/dist/leaflet.css";
import { type Coordinates } from "../../hooks/useMapPicker";

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

interface MapPickerProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (coordinates: Coordinates) => void;
  isLoading?: boolean;
  defaultCenter?: Coordinates;
  initialStreet?: string;
  initialHouse?: string;
  city?: string;
  onGeocode?: (
    street: string,
    house?: string,
    city?: string
  ) => Promise<Coordinates | null>;
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
    map.setView([center.lat, center.lng], 13);
  }, [center, map]);

  return null;
};

/**
 * Map picker component with marker placement
 */
const DEFAULT_CENTER: Coordinates = { lat: 50.4501, lng: 30.5234 }; // Kyiv, Ukraine

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
}) => {
  const center = defaultCenter ?? DEFAULT_CENTER;
  const [markerPosition, setMarkerPosition] = useState<LatLng | null>(null);
  const [mapCenter, setMapCenter] = useState<Coordinates>(center);
  const hasGeocodedRef = useRef(false);
  const prevIsOpenRef = useRef(isOpen);

  // Update map center when defaultCenter changes and map opens
  useEffect(() => {
    if (isOpen && defaultCenter) {
      setMapCenter(defaultCenter);
      const latLng = L.latLng(defaultCenter.lat, defaultCenter.lng);
      setMarkerPosition(latLng);
    }
  }, [isOpen, defaultCenter?.lat, defaultCenter?.lng]);

  // Geocode initial address or city when map opens (only once)
  useEffect(() => {
    if (isOpen && !hasGeocodedRef.current && onGeocode && !defaultCenter) {
      hasGeocodedRef.current = true;

      if (initialStreet) {
        // Geocode the full address with city
        onGeocode(initialStreet, initialHouse, city).then((coords) => {
          if (coords) {
            const latLng = L.latLng(coords.lat, coords.lng);
            setMarkerPosition(latLng);
            setMapCenter(coords);
          } else if (city) {
            // If address not found, at least center on the city
            onGeocode(city).then((cityCoords) => {
              if (cityCoords) {
                setMapCenter(cityCoords);
              }
            });
          }
        });
      } else if (city) {
        // No address, just center on the city
        onGeocode(city).then((coords) => {
          if (coords) {
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
    }
    prevIsOpenRef.current = isOpen;
  }, [isOpen]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (markerPosition) {
      onConfirm({
        lat: markerPosition.lat,
        lng: markerPosition.lng,
      });
    }
  };

  return createPortal(
    <div className="fixed inset-0 z-9999 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-full overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Виберіть адресу на карті
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Натисніть на карту, щоб розмістити маркер
            </p>
          </div>
          <button
            type="button"
            title="mapPicker"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={isLoading}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Map */}
        <div className="relative h-[60vh] sm:h-[500px] shrink w-full">
          <MapContainer
            center={[mapCenter.lat, mapCenter.lng]}
            zoom={13}
            style={{ height: "100%", width: "100%" }}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapCenterController center={mapCenter} />
            <MapClickHandler onPositionChange={setMarkerPosition} />
            {markerPosition && <Marker position={markerPosition} />}
          </MapContainer>

          {/* Loading overlay */}
          {isLoading && (
            <div className="absolute inset-0 bg-white bg-opacity-80 flex items-center justify-center z-[1000]">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-3"></div>
                <p className="text-gray-700 font-medium">
                  Визначення адреси...
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-center bg-gray-50">
          <div className="flex items-center gap-4">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
              disabled={isLoading}
            >
              Скасувати
            </button>
            <button
              onClick={handleConfirm}
              disabled={!markerPosition || isLoading}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Підтвердити
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
};
