import { useState, useCallback } from "react";
import { forwardGeocode as forwardGeocodeApi, reverseGeocode as reverseGeocodeApi } from "../services/api/geocodingApi";

export interface MapPickerResult {
  street: string;
  house: string;
  city: string;
  fullAddress: string;
}

export interface Coordinates {
  lat: number;
  lng: number;
}

export const useMapPicker = () => {
  const [isMapOpen, setIsMapOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const forwardGeocode = useCallback(
    async (street: string, house?: string, city?: string): Promise<Coordinates | null> => {
      if (!street) return null;

      setIsLoading(true);
      setError(null);

      try {
        const data = await forwardGeocodeApi(street, house, city);

        if (!data) {
          return null;
        }

        return {
          lat: data.latitude,
          lng: data.longitude,
        };
      } catch (err) {
        console.error("Forward geocoding error:", err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const reverseGeocode = useCallback(
    async (coordinates: Coordinates): Promise<MapPickerResult | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await reverseGeocodeApi(coordinates.lat, coordinates.lng);

        if (!data) {
          throw new Error("Address not found");
        }

        return {
          street: data.street || "",
          house: data.house || "",
          city: data.city || "",
          fullAddress: data.display_name || "",
        };
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to get address";
        setError(errorMessage);
        console.error("Reverse geocoding error:", err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const openMap = () => {
    setIsMapOpen(true);
    setError(null);
  };

  const closeMap = () => {
    setIsMapOpen(false);
    setError(null);
  };

  return {
    isMapOpen,
    isLoading,
    error,
    openMap,
    closeMap,
    reverseGeocode,
    forwardGeocode,
  };
};