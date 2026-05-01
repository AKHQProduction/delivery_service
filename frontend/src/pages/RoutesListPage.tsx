import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { DateInput } from "../components/shared/DateInput";
import { MapPicker } from "../components/shared/MapPicker";
import { RoutePlanCard } from "../components/routes/RoutePlanCard";
import { UnroutableOrdersList } from "../components/routes/UnroutableOrdersList";
import { Toast } from "../components/ui/Toast";
import { SkeletonBlock } from "../components/ui/Skeleton";
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
  const { previewPdf, loading: isExporting } = useOrdersPdfPreview((msg) => showToast(msg, "error"));
  const [selectedRoutePlanId, setSelectedRoutePlanId] = useState<string | null>(null);

  const totalOrders = routePlans.reduce((sum, plan) => sum + plan.stats.total_orders, 0);
  const totalAddresses = routePlans.reduce((sum, plan) => sum + plan.stats.unique_addresses, 0);
  const totalUnroutable = routePlans.reduce((sum, plan) => sum + plan.unroutable_orders.length, 0);
  const selectedRoutePlan = useMemo(
    () => routePlans.find((plan) => plan.route_plan_id === selectedRoutePlanId) ?? routePlans[0] ?? null,
    [routePlans, selectedRoutePlanId],
  );

  const handleOpenRoute = (plan: RoutePlan) => {
    navigate(`/routes/${plan.route_plan_id}`, {
      state: { routePlan: plan, timeSlotId: plan.time_slot_id },
    });
  };

  const formatDateKey = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const shiftDate = (days: number) => {
    const nextDate = new Date(`${deliveryDate}T00:00:00`);
    nextDate.setDate(nextDate.getDate() + days);
    setDeliveryDate(formatDateKey(nextDate));
  };

  const [initialStreet = "", initialHouse = ""] = editingOrder?.address
    ?.split(",")
    .map((part) => part.trim()) ?? [];

  return (
    <div className="min-h-screen bg-slate-50 px-4 pb-28 pt-6 sm:px-6 md:px-8 md:pb-10">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <h1 className="text-2xl font-semibold leading-8 text-slate-950">Маршрути</h1>
          <p className="mt-1 text-sm text-slate-500">План доставки та замовлення без координат</p>
        </div>

        <div className="grid gap-2 sm:grid-cols-[minmax(13rem,16rem)_auto_auto]">
          <DateInput value={deliveryDate} onChange={setDeliveryDate} required className="w-full" />
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => shiftDate(-1)}
              className="inline-flex h-12 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-slate-700 transition-colors hover:bg-slate-100"
              aria-label="Попередній день"
            >
              <ChevronLeftIcon className="h-5 w-5" />
            </button>
            <button
              type="button"
              onClick={() => shiftDate(1)}
              className="inline-flex h-12 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-slate-700 transition-colors hover:bg-slate-100"
              aria-label="Наступний день"
            >
              <ChevronRightIcon className="h-5 w-5" />
            </button>
          </div>
          <button
            type="button"
            title="Сформувати документ зі списком замовлень"
            onClick={() => previewPdf({ deliveryDateIso: deliveryDate })}
            disabled={isExporting || routePlans.length === 0}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-blue-600 px-4 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isExporting ? (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            ) : (
              <DownloadIcon className="h-4 w-4" />
            )}
            <span>{isExporting ? "Формування" : "Експорт"}</span>
          </button>
        </div>
      </div>

      {routePlans.length > 0 && (
        <div className="mt-4 grid grid-cols-3 gap-2">
          <SummaryCard label="Маршрутів" value={routePlans.length} />
          <SummaryCard label="Замовлень" value={totalOrders} />
          <SummaryCard label="Адрес" value={totalAddresses} />
        </div>
      )}

      {totalUnroutable > 0 && !isLoading && (
        <section className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-100 text-amber-700">
                <AlertIcon className="h-5 w-5" />
              </span>
              <div>
                <p className="text-sm font-semibold text-slate-950">
                  {totalUnroutable} замовлень без координат
                </p>
                <p className="mt-1 text-sm text-slate-600">Ці замовлення не додані до маршрутів</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => document.getElementById("unroutable-orders")?.scrollIntoView({ behavior: "smooth" })}
              className="inline-flex h-10 items-center justify-center rounded-md border border-amber-200 bg-white px-4 text-sm font-medium text-slate-700 hover:bg-amber-100"
            >
              Вказати координати
            </button>
          </div>
        </section>
      )}

      {isLoading && <RoutesSkeleton />}

      {error && !isLoading && (
        <div className="mt-4 rounded-lg border border-red-200 bg-white p-8 text-center">
          <p className="font-medium text-red-600">{error}</p>
          <button
            type="button"
            onClick={fetchRoute}
            className="mt-4 rounded-md bg-blue-600 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            Спробувати знову
          </button>
        </div>
      )}

      {!isLoading && !error && routePlans.length === 0 && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-white p-10 text-center">
          <svg className="mx-auto mb-4 h-14 w-14 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="m9 20-5.45-2.72A1 1 0 0 1 3 16.38V5.62a1 1 0 0 1 1.45-.9L9 7m0 13 6-3m-6 3V7m6 10 4.55 2.28A1 1 0 0 0 21 18.38V7.62a1 1 0 0 0-.55-.9L15 4m0 13V4m0 0L9 7"
            />
          </svg>
          <p className="text-lg font-semibold text-slate-950">Маршрутів не знайдено</p>
          <p className="mt-1 text-sm text-slate-500">Оберіть іншу дату</p>
        </div>
      )}

      {!isLoading && routePlans.length > 0 && (
        <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(18rem,22rem)_minmax(0,1fr)]">
          <section className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-950">Маршрути на дату</h2>
              <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
                {routePlans.length}
              </span>
            </div>
            <div className="space-y-3">
              {routePlans.map((plan, index) => (
                <RoutePlanCard
                  key={plan.route_plan_id}
                  routePlan={plan}
                  index={index}
                  isSelected={selectedRoutePlan?.route_plan_id === plan.route_plan_id}
                  onClick={() => handleOpenRoute(plan)}
                  onSelect={() => setSelectedRoutePlanId(plan.route_plan_id)}
                />
              ))}
            </div>
          </section>

          <section className="space-y-4">
            {selectedRoutePlan && (
              <RoutePreview routePlan={selectedRoutePlan} onOpen={() => handleOpenRoute(selectedRoutePlan)} />
            )}
            {routePlans.map((plan) => (
              <div key={plan.route_plan_id} id={plan.unroutable_orders.length > 0 ? "unroutable-orders" : undefined}>
                <UnroutableOrdersList orders={plan.unroutable_orders} onSetAddress={handleSetAddress} />
              </div>
            ))}
          </section>
        </div>
      )}

      <MapPicker
        isOpen={isMapOpen}
        onClose={handleMapClose}
        onConfirm={handleMapConfirm}
        isLoading={mapLoading}
        initialStreet={initialStreet}
        initialHouse={initialHouse}
        city={shop?.city ?? undefined}
        onGeocode={forwardGeocode}
        onReverseGeocode={reverseGeocode}
      />

      {toast.isVisible && <Toast message={toast.message} type={toast.type} onClose={hideToast} />}
    </div>
  );
};

const SummaryCard = ({ label, value }: { label: string; value: number }) => (
  <div className="rounded-lg border border-slate-200 bg-white p-4">
    <p className="text-sm font-medium text-slate-500">{label}</p>
    <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
  </div>
);

const RoutePreview = ({ routePlan, onOpen }: { routePlan: RoutePlan; onOpen: () => void }) => (
  <section className="overflow-hidden rounded-lg border border-slate-200 bg-white">
    <div className="flex flex-col gap-3 border-b border-slate-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-2">
          <h2 className="text-base font-semibold text-slate-950">Маршрут</h2>
          <span className="rounded bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">
            {routePlan.unroutable_orders.length > 0 ? "Потребує адрес" : "Готовий"}
          </span>
        </div>
        <p className="mt-1 text-sm text-slate-500">{routePlan.time_slot || "Всі проміжки"}</p>
      </div>
      <button
        type="button"
        onClick={onOpen}
        className="inline-flex h-10 items-center justify-center rounded-md border border-blue-200 bg-blue-50 px-4 text-sm font-medium text-blue-700 hover:bg-blue-100"
      >
        Відкрити маршрут
      </button>
    </div>
    {routePlan.points.length > 0 ? (
      <div className="divide-y divide-slate-200">
        {routePlan.points.slice(0, 5).map((point) => (
          <div key={point.order_id} className="flex items-center gap-3 px-4 py-3">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
              {point.sequence}
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-slate-950">{point.client_name}</p>
              <p className="mt-0.5 truncate text-xs text-slate-500">{point.address}</p>
            </div>
            <span className="shrink-0 text-sm font-semibold text-slate-950">{point.total_price} ₴</span>
          </div>
        ))}
      </div>
    ) : (
      <p className="px-4 py-8 text-sm text-slate-500">У маршруті ще немає точок для перегляду.</p>
    )}
    <div className="grid grid-cols-2 border-t border-slate-200">
      <div className="px-4 py-3">
        <p className="text-xs text-slate-500">Замовлень</p>
        <p className="mt-1 text-lg font-semibold text-slate-950">{routePlan.stats.total_orders}</p>
      </div>
      <div className="border-l border-slate-200 px-4 py-3">
        <p className="text-xs text-slate-500">Адрес</p>
        <p className="mt-1 text-lg font-semibold text-slate-950">{routePlan.stats.unique_addresses}</p>
      </div>
    </div>
  </section>
);

const RoutesSkeleton = () => (
  <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(18rem,22rem)_minmax(0,1fr)]">
    <section className="rounded-lg border border-slate-200 bg-white p-4">
      <SkeletonBlock className="h-5 w-36" />
      <div className="mt-4 space-y-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="rounded-lg border border-slate-200 p-4">
            <SkeletonBlock className="h-5 w-32" />
            <SkeletonBlock className="mt-3 h-4 w-24" />
            <SkeletonBlock className="mt-4 h-4 w-40" />
          </div>
        ))}
      </div>
    </section>
    <section className="rounded-lg border border-slate-200 bg-white p-5">
      <SkeletonBlock className="h-5 w-48" />
      <div className="mt-5 space-y-4">
        {Array.from({ length: 5 }).map((_, index) => (
          <SkeletonBlock key={index} className="h-12 w-full" />
        ))}
      </div>
    </section>
  </div>
);

const ChevronLeftIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m15 18-6-6 6-6" />
  </svg>
);

const ChevronRightIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m9 18 6-6-6-6" />
  </svg>
);

const DownloadIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v12m0 0 4-4m-4 4-4-4M5 21h14" />
  </svg>
);

const AlertIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v4m0 4h.01M10.29 3.86 2.82 17a2 2 0 0 0 1.71 3h14.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
  </svg>
);
