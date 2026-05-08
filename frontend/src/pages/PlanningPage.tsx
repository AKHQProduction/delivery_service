import { type ReactNode, useEffect, useRef, useState } from "react";
import { useLocation, useSearchParams } from "react-router-dom";
import { ClientRecentOrdersSection } from "../components/features/ClientRecentOrdersSection";
import { RecurringOrderPlanningSection } from "../components/features/RecurringOrderPlanningSection";
import { useClient } from "../hooks/clients/useClients";
import { listRecurringOrders } from "../services/api/recurringOrderApi";
import { type Client } from "../types/entities/Client";
import {
  type RecurringOrder,
  type RecurringOrderStatus,
  type ScheduleType,
} from "../types/entities/RecurringOrder";
import {
  formatRecurringOrderItemsCount,
  formatRecurringOrderStatusLabel,
  formatRecurringOrderTimeSlotLabel,
  formatScheduleLabel,
  getRecurringOrderStatusClassName,
  WEEKDAYS,
} from "../utils/recurringOrderPresentation";
import { type RecurringTemplateSeed } from "../utils/recurringOrderFormModel";

const selectClassName =
  "h-10 w-full appearance-none rounded-md border border-slate-300 bg-white px-3 pr-10 text-sm text-slate-950";

export const PlanningPage = () => {
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const routeSeedConsumedRef = useRef(false);
  const targetClientId = searchParams.get("client_id");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [orders, setOrders] = useState<RecurringOrder[]>([]);
  const [statusFilter, setStatusFilter] = useState<RecurringOrderStatus | "">(
    "",
  );
  const [scheduleType, setScheduleType] = useState<ScheduleType | "">("");
  const [weekday, setWeekday] = useState<number | "">("");
  const [monthDay, setMonthDay] = useState("");
  const [recurringSeed, setRecurringSeed] =
    useState<RecurringTemplateSeed | null>(null);

  const { clients, getClients, loading } = useClient();

  const refreshOrders = async () => {
    const parsedMonthDay = Number(monthDay);
    const data = await listRecurringOrders({
      client_name: searchTerm || undefined,
      status: statusFilter || undefined,
      schedule_type: scheduleType || undefined,
      weekday: weekday || undefined,
      month_day: Number.isInteger(parsedMonthDay) ? parsedMonthDay : undefined,
    });
    setOrders(data);
  };

  useEffect(() => {
    getClients(searchTerm);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm]);

  useEffect(() => {
    refreshOrders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, statusFilter, scheduleType, weekday, monthDay]);

  useEffect(() => {
    if (targetClientId) {
      const targetClient = clients.find(
        (client) => client.client_id === targetClientId,
      );
      if (targetClient && selectedClient?.client_id !== targetClientId) {
        setSelectedClient(targetClient);
      }
      return;
    }

    if (!selectedClient && clients[0]) {
      setSelectedClient(clients[0]);
    }
  }, [clients, selectedClient, targetClientId]);

  useEffect(() => {
    if (routeSeedConsumedRef.current) return;
    const state = location.state as { recurringSeed?: RecurringTemplateSeed } | null;
    if (state?.recurringSeed) {
      setRecurringSeed(state.recurringSeed);
      routeSeedConsumedRef.current = true;
    }
  }, [location.state]);

  return (
    <div className="min-h-screen bg-slate-50 px-4 pb-28 pt-6 sm:px-6 md:px-8 md:pb-10">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold leading-8 text-slate-950">
            Планування
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Регулярні замовлення, клієнти та історія повторень
          </p>
        </div>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          <SelectShell>
            <select
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(
                  event.target.value as RecurringOrderStatus | "",
                )
              }
              className={selectClassName}
            >
              <option value="">Усі статуси</option>
              <option value="ACTIVE">Активні</option>
              <option value="PAUSED">Пауза</option>
            </select>
          </SelectShell>
          <SelectShell>
            <select
              value={scheduleType}
              onChange={(event) =>
                setScheduleType(event.target.value as ScheduleType | "")
              }
              className={selectClassName}
            >
              <option value="">Усі типи</option>
              <option value="WEEKLY">Тиждень</option>
              <option value="MONTHLY_BY_DAY">Місяць</option>
            </select>
          </SelectShell>
          <SelectShell>
            <select
              value={weekday}
              onChange={(event) =>
                setWeekday(event.target.value ? Number(event.target.value) : "")
              }
              className={selectClassName}
            >
              <option value="">День тижня</option>
              {WEEKDAYS.map((day) => (
                <option key={day.value} value={day.value}>
                  {day.label}
                </option>
              ))}
            </select>
          </SelectShell>
          <input
            value={monthDay}
            onChange={(event) => setMonthDay(event.target.value)}
            placeholder="День місяця"
            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
          />
        </div>
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-[20rem_minmax(0,1fr)_22rem]">
        <aside className="rounded-lg border border-slate-200 bg-white">
          <div className="border-b border-slate-200 p-4">
            <input
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Пошук клієнта"
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm"
            />
          </div>
          <div className="max-h-[calc(100vh-14rem)] overflow-y-auto">
            {loading && clients.length === 0 ? (
              <p className="p-4 text-sm text-slate-500">Завантаження...</p>
            ) : clients.length ? (
              clients.map((client) => {
                const clientOrdersCount = orders.filter(
                  (order) => order.client_id === client.client_id,
                ).length;
                const isSelected =
                  selectedClient?.client_id === client.client_id;
                return (
                  <button
                    key={client.client_id}
                    type="button"
                    onClick={() => setSelectedClient(client)}
                    className={`flex w-full items-center justify-between gap-3 border-b border-slate-100 px-4 py-3 text-left ${
                      isSelected ? "bg-blue-50" : "hover:bg-slate-50"
                    }`}
                  >
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-medium text-slate-950">
                        {client.full_name || "Без імені"}
                      </span>
                      <span className="mt-1 block text-xs text-slate-500">
                        {client.phones?.[0]?.number || "Телефон не вказано"}
                      </span>
                    </span>
                    <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">
                      {clientOrdersCount}
                    </span>
                  </button>
                );
              })
            ) : (
              <p className="p-4 text-sm text-slate-500">Клієнтів не знайдено.</p>
            )}
          </div>
        </aside>

        <section className="rounded-lg border border-slate-200 bg-white">
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
            <h2 className="text-sm font-semibold text-slate-950">
              Регулярні замовлення
            </h2>
            <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-500">
              {orders.length}
            </span>
          </div>
          <div className="divide-y divide-slate-200">
            {orders.length ? (
              orders.map((order) => (
                <div key={order.recurring_order_id} className="px-4 py-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-950">
                        {order.client_name}
                      </p>
                      <p className="mt-1 truncate text-sm text-slate-500">
                        {order.phone_number || "Телефон не знайдено"}
                      </p>
                    </div>
                    <span
                      className={`h-7 justify-self-start whitespace-nowrap rounded px-2 py-1 text-xs font-medium ${getRecurringOrderStatusClassName(
                        order.status,
                      )}`}
                    >
                      {formatRecurringOrderStatusLabel(order.status)}
                    </span>
                  </div>
                  <p className="mt-3 text-sm text-slate-950">
                    {formatScheduleLabel(order)}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {formatRecurringOrderTimeSlotLabel(order)} ·{" "}
                    {formatRecurringOrderItemsCount(order.items_count)}
                  </p>
                </div>
              ))
            ) : (
              <p className="px-4 py-8 text-center text-sm text-slate-500">
                Планувань не знайдено.
              </p>
            )}
          </div>
        </section>

        <aside className="space-y-4">
          {selectedClient ? (
            <>
              <RecurringOrderPlanningSection
                client={selectedClient}
                compact
                seed={recurringSeed}
                onSeedConsumed={() => setRecurringSeed(null)}
              />
              <ClientRecentOrdersSection
                client={selectedClient}
                limit={10}
                onCreateRegular={setRecurringSeed}
              />
            </>
          ) : (
            <div className="rounded-lg border border-slate-200 bg-white p-6 text-center text-sm text-slate-500">
              Оберіть клієнта для перегляду деталей.
            </div>
          )}
        </aside>
      </div>
    </div>
  );
};

const SelectShell = ({ children }: { children: ReactNode }) => (
  <div className="relative">
    {children}
    <ChevronDownIcon className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
  </div>
);

const ChevronDownIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      d="m6 9 6 6 6-6"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
    />
  </svg>
);
