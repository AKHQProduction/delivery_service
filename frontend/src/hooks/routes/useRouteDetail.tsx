import { useState, useCallback, useMemo } from "react";
import { type RoutePlan, type RoutePoint } from "../../types/entities/Route";
import { useUserShopStore } from "../../context/useUserShopStore";
import { UserRole } from "../../constants/roles";
import { reorderRoute, updateOrderCoordinates } from "../../services/api/routesApi";

export const useRouteDetail = (routePlan: RoutePlan | null) => {
  const user = useUserShopStore((s) => s.user);
  const canEdit = user?.role === UserRole.OWNER;

  const [points, setPoints] = useState<RoutePoint[]>(routePlan?.points ?? []);
  const [showList, setShowList] = useState(true);

  // Drag state
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [overIndex, setOverIndex] = useState<number | null>(null);

  // Marker edit mode
  const [editingOrderId, setEditingOrderId] = useState<string | null>(null);

  const handleDragStart = useCallback((index: number) => {
    setDragIndex(index);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent, index: number) => {
    e.preventDefault();
    setOverIndex(index);
  }, []);

  const applyReorder = useCallback(async (orderId: string, newPosition: number) => {
    if (!routePlan) return;
    setPoints((prev) => {
      const oldIndex = prev.findIndex((p) => p.order_id === orderId);
      if (oldIndex === -1 || oldIndex === newPosition) return prev;
      const next = [...prev];
      const [moved] = next.splice(oldIndex, 1);
      next.splice(newPosition, 0, moved);
      return next.map((p, i) => ({ ...p, sequence: i }));
    });
    try {
      const updated = await reorderRoute(
        routePlan.delivery_date,
        orderId,
        newPosition,
        routePlan.time_slot || null,
      ) as RoutePlan;
      if (updated?.points) {
        setPoints(updated.points);
      }
    } catch (err) {
      console.error("Failed to reorder route:", err);
    }
  }, [routePlan]);

  const handleDrop = useCallback((index: number) => {
    if (dragIndex === null || dragIndex === index) {
      setDragIndex(null);
      setOverIndex(null);
      return;
    }
    const orderId = points[dragIndex].order_id;
    setDragIndex(null);
    setOverIndex(null);
    applyReorder(orderId, index);
  }, [dragIndex, points, applyReorder]);

  const handleDragEnd = useCallback(() => {
    setDragIndex(null);
    setOverIndex(null);
  }, []);

  const movePoint = useCallback((from: number, direction: "up" | "down") => {
    const to = direction === "up" ? from - 1 : from + 1;
    if (to < 0 || to >= points.length) return;
    applyReorder(points[from].order_id, to);
  }, [points, applyReorder]);

  const handleMarkerMove = useCallback(async (orderId: string, lat: number, lng: number) => {
    setPoints((prev) =>
      prev.map((p) =>
        p.order_id === orderId
          ? { ...p, coordinates: { latitude: lat, longitude: lng } }
          : p,
      ),
    );
    setEditingOrderId(null);
    try {
      await updateOrderCoordinates(orderId, lat, lng);
    } catch (err) {
      console.error("Failed to update coordinates:", err);
    }
  }, []);

  const toggleEditMarker = useCallback((orderId: string) => {
    setEditingOrderId((prev) => (prev === orderId ? null : orderId));
    setShowList(false);
  }, []);

  const cancelEditMarker = useCallback(() => {
    setEditingOrderId(null);
  }, []);

  const toggleList = useCallback(() => {
    setShowList((v) => !v);
  }, []);

  const pointsWithCoords = useMemo(
    () => points.filter((p) => p.coordinates),
    [points],
  );

  return {
    points,
    showList,
    dragIndex,
    overIndex,
    editingOrderId,
    canEdit,
    pointsWithCoords,
    handleDragStart,
    handleDragOver,
    handleDrop,
    handleDragEnd,
    movePoint,
    handleMarkerMove,
    toggleEditMarker,
    cancelEditMarker,
    toggleList,
  };
};
