import { useState, useCallback } from "react";
import {
  updateShopAddress,
  type ShopAddressPayload,
} from "../../services/api/settingsApi";
import { useUserShopStore } from "../../context/useUserShopStore";

export interface ShopAddress {
  city: string;
  street: string;
  house: string;
  coordinates: {
    latitude: number;
    longitude: number;
  } | null;
}

export const useShopSettings = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveShopAddress = useCallback(
    async (address: ShopAddress): Promise<boolean> => {
      setLoading(true);
      setError(null);

      try {
        const payload: ShopAddressPayload = {
          address: {
            city: address.city,
            street: address.street,
            house: address.house,
            ...(address.coordinates && {
              coordinates: {
                latitude: address.coordinates.latitude,
                longitude: address.coordinates.longitude,
              },
            }),
          },
        };

        await updateShopAddress(payload);

        // Update shop city in the store
        const currentShop = useUserShopStore.getState().shop;
        useUserShopStore.getState().setShop({
          shop_id: currentShop?.shop_id ?? "",
          city: address.city,
          street: address.street,
          house: address.house,
        });

        return true;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to save shop address";
        setError(errorMessage);
        console.error("Error saving shop address:", err);
        return false;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    loading,
    error,
    saveShopAddress,
  };
};
