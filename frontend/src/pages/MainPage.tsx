import { useEffect, useState } from "react";
import {
  getOrderStats,
  type OrderStats,
} from "../services/api/ordersApi";
import { DateRangePicker } from "../components/ui/DateRangePicker";
import { SkeletonBlock } from "../components/ui/Skeleton";
import { useUserShopStore } from "../context/useUserShopStore";
import { formatLocalDateKey } from "../utils/dateUtils";

type PeriodMode = "today" | "week" | "month" | "custom";

const getPeriodRange = (mode: PeriodMode, todayKey: string) => {
  const start = new Date(`${todayKey}T00:00:00`);
  const end = new Date(start);

  if (mode === "week") {
    const daysFromMonday = (start.getDay() + 6) % 7;
    start.setDate(start.getDate() - daysFromMonday);
    end.setTime(start.getTime());
    end.setDate(start.getDate() + 6);
  }

  if (mode === "month") {
    start.setDate(1);
    end.setMonth(start.getMonth() + 1, 0);
  }

  return {
    startDate: formatLocalDateKey(start),
    endDate: formatLocalDateKey(end),
  };
};

const formatMoney = (value: number | null | undefined) =>
  `${Number(value ?? 0).toLocaleString("uk-UA")} ₴`;

export const MainPage = () => {
  const currentDate = useUserShopStore((s) => s.currentDate);
  const todayKey = currentDate ?? formatLocalDateKey();
  const [{ startDate, endDate }, setRange] = useState(() => getPeriodRange("today", todayKey));
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

  const handlePeriodChange = (mode: PeriodMode) => {
    setPeriodMode(mode);
    if (mode !== "custom") {
      setRange(getPeriodRange(mode, todayKey));
    }
  };

  const handleCustomDateChange = (range: { startDate: string; endDate: string }) => {
    setPeriodMode("custom");
    setRange(range);
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
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onChange={handleCustomDateChange}
            className="w-full sm:w-64"
          />
        </div>
      </div>

      {loading ? (
        <HomeSkeleton />
      ) : (
        <DashboardContent stats={stats} />
      )}
    </div>
  );
};

const DashboardContent = ({
  stats,
}: {
  stats: OrderStats | null;
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

      <div className="mt-4 grid gap-4 xl:grid-cols-3">
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

      <ProductStatsTable products={stats.product_stats} total={stats.total_orders_sum} />
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

const ProductStatsTable = ({
  products,
  total,
}: {
  products: OrderStats["product_stats"];
  total: number;
}) => (
  <section className="mt-4 overflow-hidden rounded-lg border border-slate-200 bg-white">
    <div className="border-b border-slate-200 px-4 py-3">
      <h2 className="text-base font-semibold text-slate-950">Товари</h2>
    </div>

    {products.length > 0 ? (
      <div className="max-h-80 overflow-auto">
        <table className="min-w-full table-fixed divide-y divide-slate-200 text-sm">
          <thead className="sticky top-0 z-10 bg-white text-left text-xs font-medium text-slate-500 shadow-[0_1px_0_0_#e2e8f0]">
            <tr>
              <th className="w-[46%] px-4 py-3">Товар</th>
              <th className="w-[18%] px-4 py-3 text-right">Кількість</th>
              <th className="w-[18%] px-4 py-3 text-right">Сума</th>
              <th className="w-[18%] px-4 py-3 text-right">Частка</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {products.map((product) => {
              const percent = total > 0 ? Math.round((product.orders_sum / total) * 100) : 0;
              return (
                <tr key={product.name} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-950">
                    <span className="line-clamp-2">{product.name}</span>
                  </td>
                  <td className="px-4 py-3 text-right text-slate-600">{product.quantity} поз.</td>
                  <td className="px-4 py-3 text-right font-semibold text-slate-950">
                    {formatMoney(product.orders_sum)}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-600">{percent}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    ) : (
      <p className="px-4 py-8 text-sm text-slate-500">Даних за період немає.</p>
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
    <section className="mt-4 overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-4 py-3">
        <SkeletonBlock className="h-5 w-24" />
      </div>
      <div className="max-h-80 space-y-0 overflow-hidden">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="border-b border-slate-200 px-4 py-3">
            <SkeletonBlock className="h-5 w-full" />
          </div>
        ))}
      </div>
    </section>
  </>
);
