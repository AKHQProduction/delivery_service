import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "../components/ui/PageHeader";
import { DateInput } from "../components/shared/DateInput";
import { FormSelect } from "../components/shared/FormSelect";
import { useTimeSlotsSettings } from "../hooks/settings/useTimeSlotsSettings";
import { getRoutes } from "../services/api/routesApi";
import { type RoutePlan } from "../types/entities/Route";
import { paymentMap } from "../utils/dataMap";

export const RoutesListPage = () => {
  const navigate = useNavigate();
  const { timeSlots } = useTimeSlotsSettings();

  const today = new Date().toISOString().split("T")[0];
  const [deliveryDate, setDeliveryDate] = useState(today);
  const [timeSlotId, setTimeSlotId] = useState<string>("");

  const [routePlan, setRoutePlan] = useState<RoutePlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRoute = useCallback(async () => {
    if (!deliveryDate) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = (await getRoutes(deliveryDate, timeSlotId || null)) as RoutePlan;
      setRoutePlan(data);
    } catch (err) {
      console.error("Error fetching routes:", err);
      setError("Не вдалося завантажити маршрут");
      setRoutePlan(null);
    } finally {
      setIsLoading(false);
    }
  }, [deliveryDate, timeSlotId]);

  useEffect(() => {
    fetchRoute();
  }, [fetchRoute]);

  const handleOpenRoute = () => {
    if (!routePlan) return;
    navigate(`/routes/${routePlan.route_plan_id}`, { state: { routePlan } });
  };

  const formatTimeSlotLabel = (slot: { start_time: string; end_time: string; label?: string }) => {
    const start = slot.start_time.slice(0, 5);
    const end = slot.end_time.slice(0, 5);
    return slot.label ? `${slot.label} (${start} - ${end})` : `${start} - ${end}`;
  };

  return (
    <div className="min-h-screen bg-linear-to-b from-gray-50 to-gray-100 md:from-white md:to-white">
      <PageHeader title="Маршрути" />

      <div className="px-6 pb-24 pt-2 md:pb-8 md:px-8">
        {/* Filters */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
          <DateInput
            label="Дата доставки"
            value={deliveryDate}
            onChange={setDeliveryDate}
            required
          />
          <FormSelect
            label="Часовий слот"
            name="timeSlot"
            value={timeSlotId}
            onChange={(e) => setTimeSlotId(e.target.value)}
            options={timeSlots.map((slot) => ({
              value: slot.time_slot_id,
              label: formatTimeSlotLabel(slot),
            }))}
            required={false}
          />
        </div>

        {/* Loading */}
        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
          </div>
        )}

        {/* Error */}
        {error && !isLoading && (
          <div className="text-center py-16">
            <p className="text-red-500 font-medium">{error}</p>
            <button
              type="button"
              onClick={fetchRoute}
              className="mt-4 px-5 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              Спробувати знову
            </button>
          </div>
        )}

        {/* Empty */}
        {!isLoading && !error && !routePlan && (
          <div className="text-center py-16 text-gray-400">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
            <p className="font-medium text-lg">Маршрутів не знайдено</p>
            <p className="text-sm mt-1">Оберіть іншу дату або часовий слот</p>
          </div>
        )}

        {/* Route plan card */}
        {!isLoading && routePlan && (
          <div className="space-y-4">
            <button
              type="button"
              onClick={handleOpenRoute}
              className="w-full bg-white rounded-2xl border border-gray-200 p-5 text-left hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-gray-900 text-base group-hover:text-indigo-600 transition-colors">
                    Маршрут на {routePlan.delivery_date}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">{routePlan.time_slot}</p>
                </div>
                <div className="shrink-0 w-9 h-9 rounded-full bg-gray-100 group-hover:bg-indigo-100 flex items-center justify-center transition-colors">
                  <svg
                    className="w-5 h-5 text-gray-400 group-hover:text-indigo-600 transition-colors"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2.5}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>

              {/* Stats */}
              <div className="flex flex-wrap items-center gap-x-5 gap-y-2 mt-4">
                <div className="flex items-center gap-1.5 text-sm text-gray-600">
                  <svg
                    className="w-4 h-4 text-indigo-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                  <span className="font-medium">{routePlan.stats.total_orders}</span>
                  <span>замовлень</span>
                </div>
                <div className="flex items-center gap-1.5 text-sm text-gray-600">
                  <svg
                    className="w-4 h-4 text-indigo-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4"
                    />
                  </svg>
                  <span className="font-medium">{routePlan.stats.unique_addresses}</span>
                  <span>адрес</span>
                </div>
              </div>

              {/* Mini stop list */}
              <div className="mt-3 flex items-center gap-1 overflow-hidden">
                {routePlan.points.slice(0, 3).map((point, i) => (
                  <span key={point.order_id} className="text-xs text-gray-400 truncate">
                    {i > 0 && <span className="mx-1">→</span>}
                    {point.client_name}
                  </span>
                ))}
                {routePlan.points.length > 3 && (
                  <span className="text-xs text-gray-400 shrink-0">
                    +{routePlan.points.length - 3}
                  </span>
                )}
              </div>
            </button>

            {/* Unroutable orders */}
            {routePlan.unroutable_orders.length > 0 && (
              <div className="bg-amber-50 rounded-2xl border border-amber-200 p-4">
                <div className="flex items-center gap-2 mb-3">
                  <svg
                    className="w-5 h-5 text-amber-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                    />
                  </svg>
                  <h4 className="font-semibold text-amber-800 text-sm">
                    Не вдалося побудувати маршрут ({routePlan.unroutable_orders.length})
                  </h4>
                </div>
                <div className="space-y-2">
                  {routePlan.unroutable_orders.map((order) => (
                    <div
                      key={order.order_id}
                      className="flex items-center justify-between bg-white rounded-xl px-3 py-2 border border-amber-100"
                    >
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {order.client_name}
                        </p>
                        <p className="text-xs text-gray-500 truncate">{order.address}</p>
                      </div>
                      <span className="text-xs text-amber-600 font-medium shrink-0 ml-2">
                        {paymentMap[order.payment_method] ?? order.payment_method} ·{" "}
                        {order.total_price} ₴
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
