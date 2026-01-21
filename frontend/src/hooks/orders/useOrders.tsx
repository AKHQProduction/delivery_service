import { useState, useCallback } from "react";
import {
  getAllOrders,
  createOrder,
  updateOrder,
  deleteOrderById,
} from "../../services/api/ordersApi";

const PAGE_SIZE = 20;

export const useOrders = () => {
  const [orders, setOrders] = useState<any[]>();
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
    const today = new Date();
    return today.toISOString().split("T")[0];
  });

  const getOrders = async (search: string = "") => {
    setLoading(true);
    setError(null);
    setCurrentSearch(search);
    setOffset(0);
    try {
      const fetchedOrders = await getAllOrders(
        search,
        search,
        startDate,
        endDate,
        "",
        PAGE_SIZE,
        0,
      );
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
    if (loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      const fetchedOrders = await getAllOrders(
        currentSearch,
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
  }, [loadingMore, hasMore, offset, currentSearch]);

  const createNewOrder = async (orderData: any) => {
    setLoading(true);
    setError(null);
    try {
      const newOrder = await createOrder(orderData);
      // Add new order to the beginning of the list
      setOrders((prev) => [newOrder, ...(prev || [])]);
      return newOrder;
    } catch {
      setError("Не вдалося створити замовлення.");
      throw new Error("Не вдалося створити замовлення.");
    } finally {
      setLoading(false);
    }
  };

  const updateCurrentOrder = async (orderId: string, orderData: any) => {
    setLoading(true);
    setError(null);
    try {
      await updateOrder(orderId, orderData);
    } catch {
      setError("Не вдалося оновити замовлення.");
    } finally {
      setLoading(false);
    }
  };

  const deleteOrder = async (orderId: string) => {
    setLoading(true);
    setError(null);
    try {
      await deleteOrderById(orderId);
    } catch {
      setError("Не вдалося видалити замовлення.");
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
    deleteOrder,
  };
};
