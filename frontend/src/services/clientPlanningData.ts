import { listRecurringOrders } from "./api/recurringOrderApi";
import { getRecentOrdersByClient } from "./api/ordersApi";
import { type Client } from "../types/entities/Client";
import { type Order } from "../types/entities/Order";
import { type RecurringOrder } from "../types/entities/RecurringOrder";

export const fetchRecurringOrdersForClient = async (
  client: Client,
): Promise<RecurringOrder[]> => {
  const data = await listRecurringOrders({
    client_name: client.full_name || "",
  });
  return data.filter((order) => order.client_id === client.client_id);
};

export const fetchRecentOrdersForClient = async (
  client: Client,
  limit: number,
): Promise<Order[]> => {
  if (!client.full_name) {
    return [];
  }

  const data = (await getRecentOrdersByClient(client.full_name, limit)) as Order[];
  return data.filter((order) => order.client_id === client.client_id);
};
