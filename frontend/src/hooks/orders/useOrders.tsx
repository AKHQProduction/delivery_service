import { useState } from "react";
import {
  getAllOrders,
  createOrder,
  updateOrder,
} from "../../services/api/ordersApi";

export const useOrders = () => {
  const [orders, setOrders] = useState();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getOrders = async (search: string = "") => {
    setLoading(true);
    setError(null);
    try {
      const fetchedOrders = await getAllOrders(search, search, "", "", 100, 0);
      setOrders(fetchedOrders);
      return fetchedOrders;
    } catch {
      setError("Не вдалося завантажити замовлення.");
      return [];
    } finally {
      setLoading(false);
    }
  };

  const createNewOrder = async (orderData: any) => {
    setLoading(true);
    setError(null);
    try {
      await createOrder(orderData);
    } catch {
      setError("Не вдалося створити замовлення.");
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

  return {
    orders,
    loading,
    error,
    getOrders,
    createNewOrder,
    updateCurrentOrder,
  };
};
