import { useState, useCallback } from "react";
import { type Order } from "../../types/entities/Order";
import {
  getAllOrders,
  getOrderSummary,
  type OrderSummary,
  createOrder,
  updateOrder,
  deleteOrderById,
  payOrderFromBalance,
} from "../../services/api/ordersApi";
import { useUserShopStore } from "../../context/useUserShopStore";
import { addDaysToDateKey, formatLocalDateKey } from "../../utils/dateUtils";

const PAGE_SIZE = 20;
type OrderFilter = "all" | "today" | "tomorrow";

const getListDateRange = (
  filter: OrderFilter,
  startDate: string,
  endDate: string,
  todayKey: string,
) => {
  if (filter === "today") {
    return { startDate: todayKey, endDate: todayKey };
  }

  if (filter === "tomorrow") {
    const tomorrow = addDaysToDateKey(todayKey, 1);
    return { startDate: tomorrow, endDate: tomorrow };
  }

  return { startDate, endDate };
};

export const useOrders = () => {
  const currentDate = useUserShopStore((s) => s.currentDate);
  const todayKey = currentDate ?? formatLocalDateKey();
  const [orders, setOrders] = useState<Order[]>();
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const [currentSearch, setCurrentSearch] = useState("");
  const [currentFilter, setCurrentFilter] = useState<OrderFilter>("all");
  const [summary, setSummary] = useState<OrderSummary>({
    total_count: 0,
    today_count: 0,
    tomorrow_count: 0,
    total_amount: 0,
  });

  const [startDate, setStartDate] = useState(() => {
    return todayKey;
  });
  const [endDate, setEndDate] = useState(() => {
    return addDaysToDateKey(todayKey, 7);
  });

  const getOrders = async (search: string = "", filter: OrderFilter = "all") => {
    setLoading(true);
    setError(null);
    setCurrentSearch(search);
    setCurrentFilter(filter);
    setOffset(0);
    try {
      const listRange = getListDateRange(filter, startDate, endDate, todayKey);
      const [fetchedOrders, fetchedSummary] = await Promise.all([
        getAllOrders(search, listRange.startDate, listRange.endDate, "", PAGE_SIZE, 0),
        getOrderSummary(search, startDate, endDate, ""),
      ]);
      setOrders(fetchedOrders);
      setSummary(fetchedSummary);
      setHasMore(fetchedOrders.length >= PAGE_SIZE);
      setOffset(PAGE_SIZE);
      return fetchedOrders;
    } catch {
      setError("Не вдалося завантажити замовлення.");
      return [];
    } finally {
      setLoading(false);
    }
  };

  const loadMoreOrders = useCallback(async () => {
    if (loadingMore || loading || !hasMore) return;

    setLoadingMore(true);
    try {
      const listRange = getListDateRange(currentFilter, startDate, endDate, todayKey);
      const fetchedOrders = await getAllOrders(
        currentSearch,
        listRange.startDate,
        listRange.endDate,
        "",
        PAGE_SIZE,
        offset,
      );
      setOrders((prev) => [...(prev || []), ...fetchedOrders]);
      setHasMore(fetchedOrders.length >= PAGE_SIZE);
      setOffset((prev) => prev + PAGE_SIZE);
    } catch {
      setError("Не вдалося завантажити більше замовлень.");
    } finally {
      setLoadingMore(false);
    }
  }, [
    loadingMore,
    loading,
    hasMore,
    offset,
    currentSearch,
    currentFilter,
    startDate,
    endDate,
    todayKey,
  ]);

  const createNewOrder = async (orderData: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    try {
      const newOrder = (await createOrder(orderData)) as Order;
      setOrders((prev) => [newOrder, ...(prev || [])]);
      return newOrder;
    } catch {
      setError("Не вдалося створити замовлення.");
      throw new Error("Не вдалося створити замовлення.");
    } finally {
      setLoading(false);
    }
  };

  const updateCurrentOrder = async (orderId: string, orderData: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    try {
      await updateOrder(orderId, orderData);
    } catch (err: unknown) {
      const error = err as {
        response?: { data?: { detail?: string } };
      };
      const errorMessage = error?.response?.data?.detail || "Не вдалося оновити замовлення.";
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const payFromBalance = async (orderId: string) => {
    setLoading(true);
    setError(null);
    try {
      await payOrderFromBalance(orderId);
    } catch (err: unknown) {
      const error = err as {
        response?: { data?: { detail?: string } };
      };
      const errorMessage =
        error?.response?.data?.detail || "Не вдалося списати замовлення з балансу.";
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const deleteOrder = async (orderId: string) => {
    setLoading(true);
    setError(null);
    try {
      await deleteOrderById(orderId);
    } catch (err: unknown) {
      const error = err as {
        response?: { data?: { detail?: string } };
      };
      const errorMessage = error?.response?.data?.detail || "Не вдалося видалити замовлення.";
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    orders,
    summary,
    loading,
    loadingMore,
    error,
    hasMore,
    startDate,
    endDate,
    getOrders,
    loadMoreOrders,
    setStartDate,
    setEndDate,
    createNewOrder,
    updateCurrentOrder,
    payFromBalance,
    deleteOrder,
  };
};
