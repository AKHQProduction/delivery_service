import { listRecurringOrders, type RecurringOrderFilters } from "./api/recurringOrderApi";
import { getRecentOrdersByClient } from "./api/ordersApi";
import { type Client } from "../types/entities/Client";
import { type Order } from "../types/entities/Order";
import { type RecurringOrder } from "../types/entities/RecurringOrder";

export const fetchRecurringOrdersForClient = async (
  client: Client,
  filters: Omit<RecurringOrderFilters, "client_id" | "client_name"> = {},
): Promise<RecurringOrder[]> => {
  return await listRecurringOrders({
    client_id: client.client_id,
    ...filters,
  });
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
