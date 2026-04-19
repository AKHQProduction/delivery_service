import { useState, useCallback } from "react";
import { type Order } from "../../types/entities/Order";
import {
  getAllOrders,
  createOrder,
  updateOrder,
  deleteOrderById,
  payOrderFromBalance,
} from "../../services/api/ordersApi";

const PAGE_SIZE = 20;

export const useOrders = () => {
  const [orders, setOrders] = useState<Order[]>();
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const [currentSearch, setCurrentSearch] = useState("");

  const [startDate, setStartDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split("T")[0];
  });
  const [endDate, setEndDate] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() + 7);
    return date.toISOString().split("T")[0];
  });

  const getOrders = async (search: string = "") => {
    setLoading(true);
    setError(null);
    setCurrentSearch(search);
    setOffset(0);
    try {
      const fetchedOrders = await getAllOrders(search, startDate, endDate, "", PAGE_SIZE, 0);
      setOrders(fetchedOrders);
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
      const fetchedOrders = await getAllOrders(
        currentSearch,
        startDate,
        endDate,
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
  }, [loadingMore, loading, hasMore, offset, currentSearch, startDate, endDate]);

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
