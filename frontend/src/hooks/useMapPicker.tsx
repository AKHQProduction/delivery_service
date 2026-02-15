import { useState, useCallback } from "react";
import api from "../config/api.config";

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
        const response = await api.get("/v1/geocoding/forward", {
          params: { street, house: house || "", city: city || "" },
        });

        if (!response.data) {
          return null;
        }

        return {
          lat: response.data.latitude,
          lng: response.data.longitude,
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
        const response = await api.get("/v1/geocoding/reverse", {
          params: { lat: coordinates.lat, lon: coordinates.lng },
        });

        const data = response.data;

        if (!data.address) {
          throw new Error("Address not found");
        }

        const address = data.address;
        const street =
          address.road ||
          address.street ||
          address.pedestrian ||
          address.footway ||
          address.path ||
          "";
        const house = address.house_number || "";
        const city = address.city || address.town || address.village || address.municipality || "";
        const fullAddress = data.display_name || "";

        return {
          street,
          house,
          city,
          fullAddress,
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