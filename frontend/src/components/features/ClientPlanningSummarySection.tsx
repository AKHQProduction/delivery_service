import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getRecurringOrders } from "../../services/api/recurringOrderApi";
import { type Client } from "../../types/entities/Client";
import { type RecurringOrder } from "../../types/entities/RecurringOrder";

interface ClientPlanningSummarySectionProps {
  client: Client;
  onNavigate?: () => void;
}

export const ClientPlanningSummarySection = ({
  client,
  onNavigate,
}: ClientPlanningSummarySectionProps) => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState<RecurringOrder[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadOrders = async () => {
      setIsLoading(true);
      try {
        const data = await getRecurringOrders({
          client_name: client.full_name || "",
        });
        setOrders(
          data.filter((order) => order.client_id === client.client_id),
        );
      } finally {
        setIsLoading(false);
      }
    };
    loadOrders();
  }, [client.client_id, client.full_name]);

  const activeCount = orders.filter((order) => order.status === "ACTIVE").length;
  const pausedCount = orders.filter((order) => order.status === "PAUSED").length;

  const handleManage = () => {
    onNavigate?.();
    navigate(`/planning?client_id=${client.client_id}`);
  };

  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="flex items-center justify-between gap-3 px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-950">Планування</h2>
          <p className="mt-1 text-xs text-slate-500">
            {isLoading
              ? "Завантаження..."
              : `${activeCount} активних · ${pausedCount} на паузі`}
          </p>
        </div>
        <button
          type="button"
          onClick={handleManage}
          className="inline-flex h-9 items-center justify-center rounded-md border border-blue-300 px-3 text-sm font-medium text-blue-700 hover:bg-blue-50"
        >
          Керувати
        </button>
      </div>
      {orders[0] && (
        <div className="border-t border-slate-200 px-4 py-3">
          <p className="text-sm font-medium text-slate-950">
            {orders[0].schedule_type === "WEEKLY"
              ? "Щотижневе замовлення"
              : "Щомісячне замовлення"}
          </p>
          <p className="mt-1 text-sm text-slate-500">
            {orders[0].time_slot_label ||
              `${orders[0].delivery_start_time}-${orders[0].delivery_end_time}`}{" "}
            · {orders[0].items_count} товарів
          </p>
        </div>
      )}
    </section>
  );
};
