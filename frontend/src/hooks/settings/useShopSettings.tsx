import { useState, useCallback } from "react";
import {
  updateShopAddress,
  updateShopRepeatOrderMode,
  type ShopAddressPayload,
} from "../../services/api/settingsApi";
import { useUserShopStore } from "../../context/useUserShopStore";
import type { RepeatOrderMode, Shop } from "../../types/entities/user";

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

  const patchShopInStore = useCallback((patch: Partial<Shop>) => {
    const currentShop = useUserShopStore.getState().shop;
    useUserShopStore.getState().setShop({
      shop_id: currentShop?.shop_id ?? "",
      city: currentShop?.city ?? null,
      street: currentShop?.street ?? null,
      house: currentShop?.house ?? null,
      ...(currentShop ?? {}),
      ...patch,
    });
  }, []);

  const saveShopAddress = useCallback(async (address: ShopAddress): Promise<boolean> => {
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

      patchShopInStore({
        city: address.city,
        street: address.street,
        house: address.house,
      });

      return true;
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to save shop address";
      setError(errorMessage);
      console.error("Error saving shop address:", err);
      return false;
    } finally {
      setLoading(false);
    }
  }, [patchShopInStore]);

  const saveRepeatOrderMode = useCallback(
    async (repeatOrderMode: RepeatOrderMode): Promise<boolean> => {
      setLoading(true);
      setError(null);

      try {
        await updateShopRepeatOrderMode({ repeat_order_mode: repeatOrderMode });
        patchShopInStore({ repeat_order_mode: repeatOrderMode });

        return true;
      } catch (err: unknown) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to save repeat order mode";
        setError(errorMessage);
        console.error("Error saving repeat order mode:", err);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [patchShopInStore],
  );

  return {
    loading,
    error,
    saveShopAddress,
    saveRepeatOrderMode,
  };
};
