import { useState, useEffect, useCallback } from "react";
import { getAllRoutes, updateOrderCoordinates } from "../../services/api/routesApi";
import { type RoutePlan, type RoutePoint } from "../../types/entities/Route";
import { useMapPicker } from "../useMapPicker";
import { type MapConfirmData } from "../../components/shared/MapPicker";
import { formatLocalDateKey } from "../../utils/dateUtils";
import { useUserShopStore } from "../../context/useUserShopStore";

let savedDeliveryDate: string | null = null;

export const useRoutesList = () => {
  const currentDate = useUserShopStore((s) => s.currentDate);
  const today = currentDate ?? formatLocalDateKey();
  const [deliveryDate, setDeliveryDate] = useState(savedDeliveryDate || today);

  useEffect(() => { savedDeliveryDate = deliveryDate; }, [deliveryDate]);

  const [routePlans, setRoutePlans] = useState<RoutePlan[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRoute = useCallback(async () => {
    if (!deliveryDate) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = (await getAllRoutes(deliveryDate)) as RoutePlan[];
      setRoutePlans(data);
    } catch {
      setError("Не вдалося завантажити маршрути");
      setRoutePlans([]);
    } finally {
      setIsLoading(false);
    }
  }, [deliveryDate]);

  useEffect(() => {
    fetchRoute();
  }, [fetchRoute]);

  const { isMapOpen, isLoading: mapLoading, openMap, closeMap, reverseGeocode, forwardGeocode } = useMapPicker();
  const [editingOrder, setEditingOrder] = useState<RoutePoint | null>(null);

  const handleSetAddress = (order: RoutePoint) => {
    setEditingOrder(order);
    openMap();
  };

  const handleMapConfirm = async (data: MapConfirmData) => {
    if (!editingOrder) return;
    closeMap();
    try {
      await updateOrderCoordinates(editingOrder.order_id, data.lat, data.lng);
      await fetchRoute();
    } catch (err) {
      console.error("Failed to update coordinates:", err);
    }
    setEditingOrder(null);
  };

  const handleMapClose = () => {
    closeMap();
    setEditingOrder(null);
  };

  return {
    deliveryDate,
    setDeliveryDate,
    routePlans,
    isLoading,
    error,
    fetchRoute,
    editingOrder,
    isMapOpen,
    mapLoading,
    reverseGeocode,
    forwardGeocode,
    handleSetAddress,
    handleMapConfirm,
    handleMapClose,
  };
};
