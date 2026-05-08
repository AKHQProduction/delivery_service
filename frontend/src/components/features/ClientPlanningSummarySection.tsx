import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchRecurringOrdersForClient } from "../../services/clientPlanningData";
import { type Client } from "../../types/entities/Client";
import { type RecurringOrder } from "../../types/entities/RecurringOrder";
import {
  formatRecurringOrderItemsCount,
  formatRecurringOrderTimeSlotLabel,
  formatScheduleSummaryLabel,
} from "../../utils/recurringOrderPresentation";

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
        setOrders(await fetchRecurringOrdersForClient(client));
      } finally {
        setIsLoading(false);
      }
    };
    loadOrders();
  }, [client]);

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
            {formatScheduleSummaryLabel(orders[0])}
          </p>
          <p className="mt-1 text-sm text-slate-500">
            {formatRecurringOrderTimeSlotLabel(orders[0])} ·{" "}
            {formatRecurringOrderItemsCount(orders[0].items_count)}
          </p>
        </div>
      )}
    </section>
  );
};
