import { useState } from "react";
import { getAllOrders, createOrder } from "../../services/api/ordersApi";

export const useOrders = () => {
  const [orders, setOrders] = useState();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedOrders = await getAllOrders("", "", 100, 0);
      setOrders(fetchedOrders);
    } catch {
      setError("Не вдалося завантажити замовлення.");
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

  return { orders, loading, error, getOrders, createNewOrder };
};
