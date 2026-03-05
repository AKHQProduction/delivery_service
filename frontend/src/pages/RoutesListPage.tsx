import { useNavigate } from "react-router-dom";
import { PageHeader } from "../components/ui/PageHeader";
import { DateInput } from "../components/shared/DateInput";
import { FormSelect } from "../components/shared/FormSelect";
import { useTimeSlotsSettings } from "../hooks/settings/useTimeSlotsSettings";
import { MapPicker } from "../components/shared/MapPicker";
import { RoutePlanCard } from "../components/routes/RoutePlanCard";
import { UnroutableOrdersList } from "../components/routes/UnroutableOrdersList";
import { useRoutesList } from "../hooks/routes/useRoutesList";
import { useUserShopStore } from "../context/useUserShopStore";

const formatTimeSlotLabel = (slot: { start_time: string; end_time: string; label?: string }) => {
  const start = slot.start_time.slice(0, 5);
  const end = slot.end_time.slice(0, 5);
  return slot.label ? `${slot.label} (${start} - ${end})` : `${start} - ${end}`;
};

export const RoutesListPage = () => {
  const navigate = useNavigate();
  const shop = useUserShopStore((state) => state.shop);
  const { timeSlots } = useTimeSlotsSettings();

  const {
    deliveryDate,
    setDeliveryDate,
    timeSlotId,
    setTimeSlotId,
    routePlan,
    isLoading,
    error,
    fetchRoute,
    editingOrder,
    isMapOpen,
    mapLoading,
    reverseGeocode,
    forwardGeocode,
    handleSetAddress,
    handleMapConfirm,
    handleMapClose,
  } = useRoutesList();

  const handleOpenRoute = () => {
    if (!routePlan) return;
    navigate(`/routes/${routePlan.route_plan_id}`, { state: { routePlan, timeSlotId: timeSlotId || null } });
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

        {/* Route plan */}
        {!isLoading && routePlan && (
          <div className="space-y-4">
            <RoutePlanCard routePlan={routePlan} onClick={handleOpenRoute} />
            <UnroutableOrdersList
              orders={routePlan.unroutable_orders}
              onSetAddress={handleSetAddress}
            />
          </div>
        )}
      </div>

      <MapPicker
        isOpen={isMapOpen}
        onClose={handleMapClose}
        onConfirm={handleMapConfirm}
        isLoading={mapLoading}
        initialStreet={editingOrder?.address?.split(",")[0]?.trim()}
        city={shop?.city ?? undefined}
        onGeocode={forwardGeocode}
        onReverseGeocode={reverseGeocode}
      />
    </div>
  );
};
