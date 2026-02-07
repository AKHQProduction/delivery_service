import { useEffect, useState } from "react";
import { PageHeader } from "../components/ui/PageHeader";
import { getOrderStats } from "../services/api/ordersApi";
import { paymentMap } from "../utils/dataMap";
import { DateInput } from "../components/shared/DateInput";

interface OrderStats {
  total_orders: number;
  payment_method_stats: {
    method: string;
    orders_sum: number;
  }[];
  time_slot_stats: {
    time_slot: string;
    total: number;
  }[];
  total_orders_sum: number;
  category_stats: {
    name: string;
    quantity: number;
  }[];
}

export const OrdersStatsPage = () => {
  const [startDate, setStartDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split("T")[0];
  });
  const [endDate, setEndDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split("T")[0];
  });
  const [stats, setStats] = useState<OrderStats | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStats = async (start_date: string, end_date: string) => {
    setLoading(true);
    try {
      const data = await getOrderStats(start_date, end_date);
      setStats(data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (startDate && endDate) {
      fetchStats(startDate, endDate);
    }
  }, [startDate, endDate]);

  return (
    <div className="min-h-screen bg-gray-50 pb-24 lg:bg-white lg:pb-8">
      <PageHeader title="Статистика" />

      <div className="px-4 sm:px-6 pt-6 pb-4 lg:px-8">
        <div className="bg-white rounded-2xl p-3 sm:p-4 shadow-sm border border-gray-200 overflow-hidden">
          <label className="block text-sm font-semibold text-gray-700 mb-2">Оберіть період</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <DateInput
              label="Від"
              value={startDate}
              onChange={setStartDate}
              title="start date selector"
              className="min-w-0 w-full"
            />
            <DateInput
              label="До"
              value={endDate}
              onChange={setEndDate}
              title="end date selector"
              className="min-w-0 w-full"
            />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : stats ? (
        <div className="px-6 space-y-4 pb-6 lg:px-8">
          {/* Summary Block - Combined */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
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
                  d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              Загальна статистика
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {/* Total Orders */}
              <div className="flex flex-col items-center text-center p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mb-3">
                  <svg
                    className="w-6 h-6 text-white"
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
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                  Замовлень
                </p>
                <p className="text-3xl font-bold text-gray-900">{stats.total_orders}</p>
              </div>

              {/* Total Sum */}
              <div className="flex flex-col items-center text-center p-4 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl border border-emerald-100">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center mb-3">
                  <svg
                    className="w-6 h-6 text-white"
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
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                  Сума
                </p>
                <p className="text-3xl font-bold text-emerald-600">{stats.total_orders_sum}₴</p>
              </div>
            </div>

            {/* Payment Methods */}
            {stats.payment_method_stats && stats.payment_method_stats.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-3">
                  Методи оплати
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {stats.payment_method_stats.map((payment, index) => {
                    return (
                      <div
                        key={`${payment.method}-${index}`}
                        className="flex flex-col items-center p-3 bg-gray-50 rounded-lg border border-gray-100"
                      >
                        <p className="text-xs text-gray-600 mb-1">{paymentMap[payment.method]}</p>
                        <p className="text-lg font-bold text-gray-900">{payment.orders_sum}₴</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
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
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Розподіл по часу
            </h3>

            <div className="space-y-3">
              {stats.time_slot_stats?.map((slot: { time_slot: string; total: number }) => {
                // Extract start time from time_slot (e.g., "09:00" from "09:00-14:00")
                const startTime = slot.time_slot.split("-")[0];
                const [hours] = startTime.split(":").map(Number);

                // Determine if it's before or after 18:00
                const isBeforeEvening = hours < 18;

                return (
                  <div
                    key={slot.time_slot}
                    className={`flex items-center justify-between p-4 rounded-xl border ${
                      isBeforeEvening
                        ? "bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200"
                        : "bg-gradient-to-r from-orange-50 to-red-50 border-orange-200"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          isBeforeEvening ? "bg-yellow-400" : "bg-orange-400"
                        }`}
                      >
                        <span className="text-xl">{isBeforeEvening ? "☀️" : "🏙️"}</span>
                      </div>
                      <span className="font-semibold text-gray-900">{slot.time_slot}</span>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">{slot.total}</span>
                  </div>
                );
              })}
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
              Розподіл по категоріям
            </h3>

            {stats.category_stats.length > 0 ? (
              stats.category_stats.map((category) => (
                <div
                  key={category.name}
                  className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200 mb-3"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-purple-400 flex items-center justify-center">
                      <span className="text-xl">📦</span>
                    </div>
                    <span className="font-semibold text-gray-900">{category.name}</span>
                  </div>
                  <span className="text-2xl font-bold text-gray-900">{category.quantity}</span>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center py-6">
                <p className="text-gray-500 text-center">Немає даних по категоріям.</p>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};
