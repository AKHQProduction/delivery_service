import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getOrderStats,
  type OrderStats,
  type OrderStatsRecentOrder,
} from "../services/api/ordersApi";
import { SkeletonBlock } from "../components/ui/Skeleton";

type PeriodMode = "today" | "week" | "month" | "custom";

const formatDateKey = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const getPeriodRange = (mode: PeriodMode) => {
  const today = new Date();
  const start = new Date(today);
  const end = new Date(today);

  if (mode === "week") {
    end.setDate(today.getDate() + 6);
  }

  if (mode === "month") {
    start.setDate(1);
    end.setMonth(today.getMonth() + 1, 0);
  }

  return {
    startDate: formatDateKey(start),
    endDate: formatDateKey(end),
  };
};

const formatDate = (value: string) => {
  const [year, month, day] = value.split("-");
  return `${day}.${month}.${year}`;
};

const formatMoney = (value: number | null | undefined) =>
  `${Number(value ?? 0).toLocaleString("uk-UA")} ₴`;

const getOrderTotal = (order: OrderStatsRecentOrder) =>
  order.items.reduce((sum, item) => sum + item.quantity * item.price_per_item, 0);

const getAddressText = (order: OrderStatsRecentOrder) => {
  const address = order.delivery_address;
  if (!address) return "Адресу не вказано";
  return [address.street, address.house, address.apartment ? `кв. ${address.apartment}` : ""]
    .filter(Boolean)
    .join(", ");
};

const getInitials = (name?: string) => {
  const parts = (name || "Клієнт").trim().split(/\s+/).filter(Boolean);
  return parts
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toLocaleUpperCase("uk-UA");
};

export const MainPage = () => {
  const navigate = useNavigate();
  const [{ startDate, endDate }, setRange] = useState(() => getPeriodRange("today"));
  const [periodMode, setPeriodMode] = useState<PeriodMode>("today");
  const [stats, setStats] = useState<OrderStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadStats = async () => {
      setLoading(true);
      try {
        const data = await getOrderStats(startDate, endDate);
        if (!cancelled) {
          setStats(data);
        }
      } catch (error) {
        console.error("Failed to fetch dashboard stats:", error);
        if (!cancelled) {
          setStats(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadStats();

    return () => {
      cancelled = true;
    };
  }, [startDate, endDate]);

  const periodLabel = useMemo(() => {
    if (startDate === endDate) return formatDate(startDate);
    return `${formatDate(startDate)} - ${formatDate(endDate)}`;
  }, [startDate, endDate]);

  const handlePeriodChange = (mode: PeriodMode) => {
    setPeriodMode(mode);
    if (mode !== "custom") {
      setRange(getPeriodRange(mode));
    }
  };

  const handleCustomDateChange = (field: "startDate" | "endDate", value: string) => {
    setPeriodMode("custom");
    setRange((current) => ({ ...current, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 pb-28 pt-6 sm:px-6 md:px-8 md:pb-10">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <h1 className="text-2xl font-semibold leading-8 text-slate-950">Головна</h1>
          <p className="mt-1 text-sm text-slate-500">Огляд замовлень і статистика</p>
        </div>

        <div className="grid gap-2 sm:grid-cols-[auto_auto]">
          <div className="grid grid-cols-4 rounded-md border border-slate-200 bg-white p-1">
            {[
              ["today", "Сьогодні"],
              ["week", "Тиждень"],
              ["month", "Місяць"],
              ["custom", "Період"],
            ].map(([mode, label]) => (
              <button
                key={mode}
                type="button"
                onClick={() => handlePeriodChange(mode as PeriodMode)}
                className={`h-9 rounded px-3 text-sm font-medium transition-colors ${
                  periodMode === mode
                    ? "bg-blue-50 text-blue-700"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="inline-flex h-11 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700">
            <CalendarIcon className="h-4 w-4 text-slate-500" />
            <span>{periodLabel}</span>
          </div>
        </div>
      </div>

      {periodMode === "custom" && (
        <div className="mt-4 grid gap-2 sm:grid-cols-2 md:max-w-lg">
          <DateField
            label="Від"
            value={startDate}
            onChange={(value) => handleCustomDateChange("startDate", value)}
          />
          <DateField
            label="До"
            value={endDate}
            onChange={(value) => handleCustomDateChange("endDate", value)}
          />
        </div>
      )}

      {loading ? (
        <HomeSkeleton />
      ) : (
        <DashboardContent stats={stats} onOpenOrders={() => navigate("/orders")} />
      )}
    </div>
  );
};

const DashboardContent = ({
  stats,
  onOpenOrders,
}: {
  stats: OrderStats | null;
  onOpenOrders: () => void;
}) => {
  if (!stats) {
    return (
      <div className="mt-4 rounded-lg border border-slate-200 bg-white p-8 text-center">
        <p className="text-sm font-medium text-slate-950">Не вдалося завантажити статистику.</p>
        <p className="mt-1 text-sm text-slate-500">Спробуйте оновити сторінку.</p>
      </div>
    );
  }

  return (
    <>
      <div className="mt-4 grid grid-cols-2 gap-2 lg:grid-cols-4">
        <MetricCard label="Замовлень" value={String(stats.total_orders)} helper="за період" />
        <MetricCard
          label="Сума замовлень"
          value={formatMoney(stats.total_orders_sum)}
          helper="за період"
        />
        <MetricCard
          label="Товарів у замовленнях"
          value={String(stats.total_products_quantity)}
          helper="позицій"
        />
        <MetricCard
          label="Середній чек"
          value={formatMoney(stats.average_order_value)}
          helper="на замовлення"
        />
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)]">
        <BreakdownCard
          title="Способи оплати"
          rows={stats.payment_method_stats.map((item) => ({
            label: item.method || "Не вказано",
            value: item.orders_sum,
            suffix: formatMoney(item.orders_sum),
          }))}
          total={stats.total_orders_sum}
        />
        <BreakdownCard
          title="Категорії товарів"
          rows={stats.category_stats.map((item) => ({
            label: item.name,
            value: item.orders_sum,
            suffix: `${item.quantity} поз. / ${formatMoney(item.orders_sum)}`,
          }))}
          total={stats.total_orders_sum}
        />
        <BreakdownCard
          title="Часові слоти"
          rows={stats.time_slot_stats.map((item) => ({
            label: item.time_slot,
            value: item.orders_sum,
            suffix: `${item.total} зам. / ${formatMoney(item.orders_sum)}`,
          }))}
          total={stats.total_orders_sum}
        />
      </div>

      <RecentOrdersTable
        orders={stats.recent_orders}
        total={stats.total_orders}
        onOpenOrders={onOpenOrders}
      />
    </>
  );
};

const MetricCard = ({ label, value, helper }: { label: string; value: string; helper: string }) => (
  <div className="rounded-lg border border-slate-200 bg-white p-4">
    <p className="text-sm font-medium text-slate-500">{label}</p>
    <p className="mt-3 text-3xl font-semibold leading-9 text-slate-950">{value}</p>
    <p className="mt-1 text-sm text-slate-500">{helper}</p>
  </div>
);

const BreakdownCard = ({
  title,
  rows,
  total,
}: {
  title: string;
  rows: Array<{ label: string; value: number; suffix: string }>;
  total: number;
}) => (
  <section className="overflow-hidden rounded-lg border border-slate-200 bg-white">
    <div className="border-b border-slate-200 px-4 py-3">
      <h2 className="text-base font-semibold text-slate-950">{title}</h2>
    </div>
    {rows.length > 0 ? (
      <div className="divide-y divide-slate-200">
        {rows.map((row, index) => {
          const percent = total > 0 ? Math.round((row.value / total) * 100) : 0;
          return (
            <div key={`${row.label}-${index}`} className="px-4 py-3">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-slate-700">{row.label}</span>
                <span className="shrink-0 text-slate-600">{row.suffix}</span>
              </div>
              <div className="mt-2 flex items-center gap-3">
                <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className={`h-full rounded-full ${index % 3 === 1 ? "bg-cyan-500" : index % 3 === 2 ? "bg-indigo-500" : "bg-blue-600"}`}
                    style={{ width: `${percent}%` }}
                  />
                </div>
                <span className="w-10 text-right text-xs font-medium text-slate-500">
                  {percent}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    ) : (
      <p className="px-4 py-8 text-sm text-slate-500">Даних за період немає.</p>
    )}
  </section>
);

const RecentOrdersTable = ({
  orders,
  total,
  onOpenOrders,
}: {
  orders: OrderStatsRecentOrder[];
  total: number;
  onOpenOrders: () => void;
}) => (
  <section className="mt-4 overflow-hidden rounded-lg border border-slate-200 bg-white">
    <div className="flex items-center justify-between gap-4 border-b border-slate-200 px-4 py-3">
      <h2 className="text-base font-semibold text-slate-950">Останні замовлення</h2>
      <button
        type="button"
        onClick={onOpenOrders}
        className="text-sm font-medium text-blue-600 hover:text-blue-700"
      >
        Перейти до замовлень
      </button>
    </div>

    {orders.length > 0 ? (
      <>
        <div className="hidden overflow-x-auto lg:block">
          <table className="min-w-full table-fixed divide-y divide-slate-200 text-sm">
            <thead className="bg-white text-left text-xs font-medium text-slate-500">
              <tr>
                <th className="w-[22%] px-4 py-3">Клієнт</th>
                <th className="w-[12%] px-4 py-3">Час</th>
                <th className="w-[28%] px-4 py-3">Адреса</th>
                <th className="w-[20%] px-4 py-3">Товари</th>
                <th className="w-[10%] px-4 py-3 text-right">Сума</th>
                <th className="w-[12%] px-4 py-3">Оплата</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {orders.map((order) => (
                <tr key={order.order_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700">
                        {getInitials(order.client_name)}
                      </span>
                      <span className="truncate font-medium text-slate-950">
                        {order.client_name}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{order.time_slot}</td>
                  <td className="px-4 py-3 text-slate-600">
                    <span className="line-clamp-2">{getAddressText(order)}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    <span className="line-clamp-2">
                      {order.items.map((item) => `${item.name} x ${item.quantity}`).join(", ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-slate-950">
                    {formatMoney(getOrderTotal(order))}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {order.payment_method || "Не вказано"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="grid gap-3 p-3 lg:hidden">
          {orders.map((order) => (
            <div key={order.order_id} className="rounded-lg border border-slate-200 p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-slate-950">
                    {order.client_name}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">{order.time_slot}</p>
                </div>
                <p className="shrink-0 text-sm font-semibold text-slate-950">
                  {formatMoney(getOrderTotal(order))}
                </p>
              </div>
              <p className="mt-3 truncate text-sm text-slate-600">{getAddressText(order)}</p>
              <p className="mt-2 truncate text-sm text-slate-500">
                {order.items.map((item) => `${item.name} x ${item.quantity}`).join(", ")}
              </p>
            </div>
          ))}
        </div>

        <div className="border-t border-slate-200 px-4 py-3 text-sm text-slate-500">
          Всього замовлень: {total}
        </div>
      </>
    ) : (
      <p className="px-4 py-8 text-sm text-slate-500">Замовлень за період немає.</p>
    )}
  </section>
);

const HomeSkeleton = () => (
  <>
    <div className="mt-4 grid grid-cols-2 gap-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="rounded-lg border border-slate-200 bg-white p-4">
          <SkeletonBlock className="h-4 w-28" />
          <SkeletonBlock className="mt-4 h-9 w-24" />
          <SkeletonBlock className="mt-2 h-4 w-20" />
        </div>
      ))}
    </div>
    <div className="mt-4 grid gap-4 xl:grid-cols-3">
      {Array.from({ length: 3 }).map((_, cardIndex) => (
        <section key={cardIndex} className="rounded-lg border border-slate-200 bg-white">
          <div className="border-b border-slate-200 px-4 py-3">
            <SkeletonBlock className="h-5 w-32" />
          </div>
          <div className="space-y-5 p-4">
            {Array.from({ length: 3 }).map((_, rowIndex) => (
              <div key={rowIndex}>
                <div className="flex justify-between gap-3">
                  <SkeletonBlock className="h-4 w-24" />
                  <SkeletonBlock className="h-4 w-20" />
                </div>
                <SkeletonBlock className="mt-2 h-2 w-full rounded-full" />
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
    <section className="mt-4 rounded-lg border border-slate-200 bg-white p-4">
      <SkeletonBlock className="h-5 w-40" />
      <div className="mt-4 space-y-4">
        {Array.from({ length: 5 }).map((_, index) => (
          <SkeletonBlock key={index} className="h-10 w-full" />
        ))}
      </div>
    </section>
  </>
);

const DateField = ({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) => (
  <label className="grid gap-1 text-xs font-medium text-slate-600">
    {label}
    <input
      type="date"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm font-medium text-slate-950 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
    />
  </label>
);

const CalendarIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M8 7V3m8 4V3M5 11h14M5 7h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z"
    />
  </svg>
);
