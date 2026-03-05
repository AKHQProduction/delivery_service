import { useState, useEffect, useCallback } from "react";
import { getRoutes, updateOrderCoordinates } from "../../services/api/routesApi";
import { type RoutePlan, type RoutePoint } from "../../types/entities/Route";
import { useMapPicker } from "../useMapPicker";
import { type MapConfirmData } from "../../components/shared/MapPicker";

let savedDeliveryDate: string | null = null;
let savedTimeSlotId: string | null = null;

export const useRoutesList = () => {
  const today = new Date().toISOString().split("T")[0];
  const [deliveryDate, setDeliveryDate] = useState(savedDeliveryDate || today);
  const [timeSlotId, setTimeSlotId] = useState(savedTimeSlotId || "");

  useEffect(() => { savedDeliveryDate = deliveryDate; }, [deliveryDate]);
  useEffect(() => { savedTimeSlotId = timeSlotId; }, [timeSlotId]);

  const [routePlan, setRoutePlan] = useState<RoutePlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRoute = useCallback(async () => {
    if (!deliveryDate) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = (await getRoutes(deliveryDate, timeSlotId || null)) as RoutePlan;
      setRoutePlan(data);
    } catch {
      setError("Не вдалося завантажити маршрут");
      setRoutePlan(null);
    } finally {
      setIsLoading(false);
    }
  }, [deliveryDate, timeSlotId]);

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
    timeSlotId,
    setTimeSlotId,
    routePlan,
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
