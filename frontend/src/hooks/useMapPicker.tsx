import { useState, useCallback } from "react";

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

/**
 * Hook for managing map picker state and reverse geocoding
 */
export const useMapPicker = () => {
  const [isMapOpen, setIsMapOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Converts address to coordinates using OpenStreetMap Nominatim API (forward geocoding)
   * @param street - Street name
   * @param house - House number (optional)
   * @param city - City name (optional, defaults to Ukraine-wide search)
   */
  const forwardGeocode = useCallback(
    async (street: string, house?: string, city?: string): Promise<Coordinates | null> => {
      if (!street) return null;

      setIsLoading(true);
      setError(null);

      try {
        const addressParts = [house, street, city, "Ukraine"].filter(Boolean);
        const query = addressParts.join(", ");
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&addressdetails=1&limit=1`,
          {
            headers: {
              "Accept-Language": "uk",
            },
          },
        );

        if (!response.ok) {
          throw new Error("Failed to geocode address");
        }

        const data = (await response.json()) as Array<{ lat: string; lon: string }>;

        if (!data || data.length === 0) {
          return null;
        }

        return {
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon),
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

  /**
   * Converts coordinates to address using OpenStreetMap Nominatim API
   */
  const reverseGeocode = useCallback(
    async (coordinates: Coordinates): Promise<MapPickerResult | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${coordinates.lat}&lon=${coordinates.lng}&addressdetails=1`,
          {
            headers: {
              "Accept-Language": "uk", // Ukrainian language for results
            },
          },
        );

        if (!response.ok) {
          throw new Error("Failed to fetch address");
        }

        const data = (await response.json()) as {
          display_name?: string;
          address?: {
            road?: string;
            street?: string;
            pedestrian?: string;
            footway?: string;
            path?: string;
            house_number?: string;
            city?: string;
            town?: string;
            village?: string;
            municipality?: string;
          };
        };

        if (!data.address) {
          throw new Error("Address not found");
        }

        // Extract street and house number from the response
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

        // Build full address for display
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
