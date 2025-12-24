import { useEffect, useState } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { getOrderStats } from "../services/api/ordersApi";

interface OrderStats {
  total_orders: number;
  total_orders_in_first_half: number;
  total_orders_in_second_half: number;
  total_orders_sum: number;
  total_water: number;
  total_other: number;
}

export const OrdersStatsPage = () => {
  const [selectedDate, setSelectedDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split("T")[0];
  });
  const [stats, setStats] = useState<OrderStats | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStats = async (date: string) => {
    setLoading(true);
    try {
      const data = await getOrderStats(date);
      setStats(data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedDate) {
      fetchStats(selectedDate);
    }
  }, [selectedDate]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("uk-UA", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      <PageHeader title="Статистика" />

      <div className="px-6 pt-6 pb-4">
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-200">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Оберіть дату
          </label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full px-4 py-3 border-2 border-indigo-200 rounded-xl bg-white
                     focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                     text-gray-900 font-medium"
          />
          <p className="text-xs text-gray-500 mt-2">
            за {formatDate(selectedDate)}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : stats ? (
        <div className="px-6 space-y-4">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0">
                <svg
                  className="w-7 h-7 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                  Всього замовлень
                </p>
                <p className="text-4xl font-bold text-gray-900 mt-1">
                  {stats.total_orders}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  за {formatDate(selectedDate)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shrink-0">
                <svg
                  className="w-7 h-7 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                  Загальна сума
                </p>
                <p className="text-4xl font-bold text-emerald-600 mt-1">
                  ₴{stats.total_orders_sum}
                </p>
                <p className="text-xs text-gray-400 mt-1">всіх замовлень</p>
              </div>
            </div>
          </div>

          {/* Time Distribution */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-200">
            <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Розподіл по часу
            </h3>

            <div className="space-y-3">
              {/* До обіду */}
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl border border-yellow-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-yellow-400 flex items-center justify-center">
                    <span className="text-xl">☀️</span>
                  </div>
                  <span className="font-semibold text-gray-900">До обіду</span>
                </div>
                <span className="text-2xl font-bold text-gray-900">
                  {stats.total_orders_in_first_half}
                </span>
              </div>

              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-xl border border-orange-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-orange-400 flex items-center justify-center">
                    <span className="text-xl">🏙️</span>
                  </div>
                  <span className="font-semibold text-gray-900">
                    Після обіду
                  </span>
                </div>
                <span className="text-2xl font-bold text-gray-900">
                  {stats.total_orders_in_second_half}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-200">
            <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              Товари
            </h3>

            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl border border-blue-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-400 flex items-center justify-center">
                    <span className="text-xl">💧</span>
                  </div>
                  <span className="font-semibold text-gray-900">Вода</span>
                </div>
                <span className="text-2xl font-bold text-gray-900">
                  {stats.total_water}
                </span>
              </div>

              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-purple-400 flex items-center justify-center">
                    <span className="text-xl">📦</span>
                  </div>
                  <span className="font-semibold text-gray-900">Інше</span>
                </div>
                <span className="text-2xl font-bold text-gray-900">
                  {stats.total_other}
                </span>
              </div>
            </div>
          </div>

          {stats.total_orders === 0 && (
            <div className="bg-white rounded-2xl p-8 text-center shadow-sm border border-gray-200 mt-6">
              <svg
                className="w-16 h-16 mx-auto mb-4 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <p className="text-gray-500 font-medium">
                Немає замовлень на цю дату
              </p>
              <p className="text-sm text-gray-400 mt-1">
                Оберіть іншу дату для перегляду статистики
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <p>Оберіть дату для перегляду статистики</p>
        </div>
      )}
    </div>
  );
};
