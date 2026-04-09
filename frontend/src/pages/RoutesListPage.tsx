import { useNavigate } from "react-router-dom";
import { PageHeader } from "../components/ui/PageHeader";
import { DateInput } from "../components/shared/DateInput";
import { MapPicker } from "../components/shared/MapPicker";
import { RoutePlanCard } from "../components/routes/RoutePlanCard";
import { UnroutableOrdersList } from "../components/routes/UnroutableOrdersList";
import { Toast } from "../components/ui/Toast";
import { useRoutesList } from "../hooks/routes/useRoutesList";
import { useOrdersPdfPreview } from "../hooks/useOrdersPdfPreview";
import { useToast } from "../hooks/useToast";
import { useUserShopStore } from "../context/useUserShopStore";
import { type RoutePlan } from "../types/entities/Route";

export const RoutesListPage = () => {
  const navigate = useNavigate();
  const shop = useUserShopStore((state) => state.shop);

  const {
    deliveryDate,
    setDeliveryDate,
    routePlans,
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

  const { toast, showToast, hideToast } = useToast();
  const { previewPdf, loading: isExporting } = useOrdersPdfPreview(
    (msg) => showToast(msg, "error"),
  );

  const handleOpenRoute = (plan: RoutePlan) => {
    navigate(`/routes/${plan.route_plan_id}`, { state: { routePlan: plan, timeSlotId: plan.time_slot_id } });
  };

  return (
    <div className="min-h-screen bg-linear-to-b from-gray-50 to-gray-100 md:from-white md:to-white">
      <PageHeader title="Маршрути" />

      <div className="px-6 pb-24 pt-2 md:pb-8 md:px-8">
        {/* Filters */}
        <div className="mb-6 flex flex-col md:flex-row md:items-end gap-3">
          <div className="flex-1">
            <DateInput
              label="Дата доставки"
              value={deliveryDate}
              onChange={setDeliveryDate}
              required
            />
          </div>
          <button
            type="button"
            title="Сформувати документ зі списком замовлень"
            onClick={() => previewPdf({ deliveryDateIso: deliveryDate })}
            disabled={isExporting || routePlans.length === 0}
            className="h-[46px] px-5 bg-linear-to-r from-amber-500 to-orange-500 text-white rounded-xl font-semibold shadow-md hover:from-amber-600 hover:to-orange-600 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all w-full md:w-auto"
          >
            {isExporting ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            )}
            {isExporting ? "Формування..." : "Друк"}
          </button>
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
        {!isLoading && !error && routePlans.length === 0 && (
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
            <p className="text-sm mt-1">Оберіть іншу дату</p>
          </div>
        )}

        {/* Route plans */}
        {!isLoading && routePlans.length > 0 && (
          <div className="space-y-4">
            {routePlans.map((plan) => (
              <div key={plan.route_plan_id}>
                <RoutePlanCard routePlan={plan} onClick={() => handleOpenRoute(plan)} />
                <UnroutableOrdersList
                  orders={plan.unroutable_orders}
                  onSetAddress={handleSetAddress}
                />
              </div>
            ))}
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

      {toast.isVisible && (
        <Toast message={toast.message} type={toast.type} onClose={hideToast} />
      )}
    </div>
  );
};
