import { useEffect, useMemo, useState } from "react";
import { Modal } from "../modals/Modal";
import { AddOrderForm } from "../forms/orders/AddOrderForm";
import { getRecentOrdersByClient } from "../../services/api/ordersApi";
import { type Client } from "../../types/entities/Client";
import { type Order } from "../../types/entities/Order";
import { addDaysToDateKey, formatLocalDateKey } from "../../utils/dateUtils";
import { useUserShopStore } from "../../context/useUserShopStore";

interface ClientRecentOrdersSectionProps {
  client: Client;
  limit: number;
  onCreateRegular?: (order: Order) => void;
}

const getItemsSummary = (order: Order) => {
  const quantity = order.items?.reduce((sum, item) => sum + item.quantity, 0);
  return `${quantity || 0} товарів`;
};

export const ClientRecentOrdersSection = ({
  client,
  limit,
  onCreateRegular,
}: ClientRecentOrdersSectionProps) => {
  const currentDate = useUserShopStore((state) => state.currentDate);
  const tomorrow = addDaysToDateKey(currentDate ?? formatLocalDateKey(), 1);
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [repeatOrder, setRepeatOrder] = useState<Order | null>(null);

  useEffect(() => {
    const loadOrders = async () => {
      if (!client.full_name) return;

      setIsLoading(true);
      try {
        const data = (await getRecentOrdersByClient(
          client.full_name,
          limit,
        )) as Order[];
        setOrders(data.filter((order) => order.client_id === client.client_id));
      } finally {
        setIsLoading(false);
      }
    };
    loadOrders();
  }, [client.client_id, client.full_name, limit]);

  const initialRepeatOrder = useMemo(() => {
    if (!repeatOrder) return undefined;

    return {
      client_id: repeatOrder.client_id,
      delivery_date: tomorrow,
      payment_method: repeatOrder.payment_method,
      comment: repeatOrder.comment || repeatOrder.note || "",
      items: repeatOrder.items
        .filter((item) => item.product_id)
        .map((item) => ({
          id: item.id,
          product_id: item.product_id as string,
          name: item.name,
          price_per_item: item.price_per_item,
          quantity: item.quantity,
        })),
    };
  }, [repeatOrder, tomorrow]);

  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-950">
            Останні замовлення
          </h2>
          <p className="text-xs text-slate-500">{orders.length} у списку</p>
        </div>
      </div>

      <div className="divide-y divide-slate-200">
        {isLoading ? (
          <p className="px-4 py-3 text-sm text-slate-500">Завантаження...</p>
        ) : orders.length ? (
          orders.map((order) => (
            <div key={order.order_id} className="px-4 py-3">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-950">
                    {order.date} · {order.time_slot || order.time_preference}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {getItemsSummary(order)}
                  </p>
                </div>
                <span
                  className={`shrink-0 rounded px-2 py-1 text-xs font-medium ${
                    order.is_paid
                      ? "bg-emerald-50 text-emerald-700"
                      : "bg-slate-100 text-slate-600"
                  }`}
                >
                  {order.is_paid ? "Оплачено" : "Не оплачено"}
                </span>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => setRepeatOrder(order)}
                  className="h-8 rounded-md border border-slate-300 px-3 text-xs font-medium text-slate-700 hover:bg-slate-100"
                >
                  Повторити
                </button>
                {onCreateRegular && (
                  <button
                    type="button"
                    onClick={() => onCreateRegular(order)}
                    className="h-8 rounded-md border border-blue-300 px-3 text-xs font-medium text-blue-700 hover:bg-blue-50"
                  >
                    Створити регулярне
                  </button>
                )}
              </div>
            </div>
          ))
        ) : (
          <p className="px-4 py-3 text-sm text-slate-500">
            Замовлень поки немає.
          </p>
        )}
      </div>

      <Modal
        isOpen={!!repeatOrder}
        onClose={() => setRepeatOrder(null)}
        title="Повторити замовлення"
        size="5xl"
      >
        {repeatOrder && (
          <AddOrderForm
            initialOrder={initialRepeatOrder}
            onClose={() => setRepeatOrder(null)}
            onSave={() => setRepeatOrder(null)}
          />
        )}
      </Modal>
    </section>
  );
};
