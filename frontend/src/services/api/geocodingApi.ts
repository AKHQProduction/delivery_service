import api from "../../config/api.config";

export interface GeocodingCoordinates {
  latitude: number;
  longitude: number;
}

export interface ReverseGeocodingResult {
  street: string;
  house: string;
  city: string;
  display_name: string;
}

export const forwardGeocode = async (street: string, house?: string, city?: string) => {
  const response = await api.get<GeocodingCoordinates>("/v1/geocoding/forward", {
    params: { street, house: house || "", city: city || "" },
  });
  return response.data;
};

export const reverseGeocode = async (lat: number, lon: number) => {
  const response = await api.get<ReverseGeocodingResult>("/v1/geocoding/reverse", {
    params: { lat, lon },
  });
  return response.data;
};
