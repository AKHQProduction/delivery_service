import { useCallback, useRef, useState } from "react";
import {
  forwardGeocode as forwardGeocodeApi,
  reverseGeocode as reverseGeocodeApi,
} from "../services/api/geocodingApi";

export interface MapPickerResult {
  street: string;
  house: string;
  city: string;
  district?: string;
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

  const pendingRequestsRef = useRef(0);
  const latestRequestIdRef = useRef(0);

  const beginRequest = useCallback(() => {
    const requestId = latestRequestIdRef.current + 1;
    latestRequestIdRef.current = requestId;
    pendingRequestsRef.current += 1;
    setIsLoading(true);
    setError(null);
    return requestId;
  }, []);

  const finishRequest = useCallback((requestId: number, nextError: string | null) => {
    pendingRequestsRef.current = Math.max(0, pendingRequestsRef.current - 1);
    setIsLoading(pendingRequestsRef.current > 0);

    if (requestId === latestRequestIdRef.current) {
      setError(nextError);
    }
  }, []);

  const forwardGeocode = useCallback(
    async (street: string, house?: string, city?: string): Promise<Coordinates | null> => {
      if (!street) return null;

      const requestId = beginRequest();
      let requestError: string | null = null;

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
        requestError = err instanceof Error ? err.message : "Failed to geocode address";
        console.error("Forward geocoding error:", err);
        return null;
      } finally {
        finishRequest(requestId, requestError);
      }
    },
    [beginRequest, finishRequest],
  );

  const reverseGeocode = useCallback(
    async (coordinates: Coordinates): Promise<MapPickerResult | null> => {
      const requestId = beginRequest();
      let requestError: string | null = null;

      try {
        const data = await reverseGeocodeApi(coordinates.lat, coordinates.lng);

        if (!data) {
          requestError = "Address not found";
          return null;
        }

        return {
          street: data.street || "",
          house: data.house || "",
          city: data.city || "",
          district: data.district || undefined,
          fullAddress: data.display_name || "",
        };
      } catch (err) {
        requestError = err instanceof Error ? err.message : "Failed to get address";
        console.error("Reverse geocoding error:", err);
        return null;
      } finally {
        finishRequest(requestId, requestError);
      }
    },
    [beginRequest, finishRequest],
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
