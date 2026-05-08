import { type ReactNode, useEffect, useMemo, useState } from "react";
import { usePaymentMethodsSettings } from "../../hooks/settings/usePaymentMethodsSettings";
import { useTimeSlotsSettings } from "../../hooks/settings/useTimeSlotsSettings";
import { useProducts } from "../../hooks/products/useProducts";
import {
  createRecurringOrder,
  deleteRecurringOrder,
  getRecurringOrders,
  pauseRecurringOrder,
  resumeRecurringOrder,
  runRecurringOrder,
} from "../../services/api/recurringOrderApi";
import { type Client } from "../../types/entities/Client";
import { type Order } from "../../types/entities/Order";
import {
  type RecurringOrder,
  type RunRecurringOrderResult,
  type ScheduleType,
} from "../../types/entities/RecurringOrder";
import { Modal } from "../modals/Modal";

interface RecurringOrderPlanningSectionProps {
  client: Client;
  compact?: boolean;
  seedOrder?: Order | null;
  onSeedConsumed?: () => void;
}

type RunDialogState =
  | { step: "activate"; order: RecurringOrder }
  | { step: "today"; order: RecurringOrder; activate: boolean }
  | {
      step: "summary";
      order: RecurringOrder;
      result: RunRecurringOrderResult;
    };

const WEEKDAYS = [
  { value: 1, label: "Пн" },
  { value: 2, label: "Вт" },
  { value: 3, label: "Ср" },
  { value: 4, label: "Чт" },
  { value: 5, label: "Пт" },
  { value: 6, label: "Сб" },
  { value: 7, label: "Нд" },
];

const scheduleLabel = (order: RecurringOrder) => {
  if (order.schedule_type === "WEEKLY") {
    const days = order.weekdays
      ?.map((day) => WEEKDAYS.find((item) => item.value === day)?.label)
      .filter(Boolean)
      .join(", ");
    return days ? `Щотижня: ${days}` : "Щотижня";
  }

  return order.month_days?.length
    ? `Щомісяця: ${order.month_days.join(", ")}`
    : "Щомісяця";
};

const timeSlotLabel = (order: RecurringOrder) =>
  order.time_slot_label
    ? `${order.time_slot_label} (${order.delivery_start_time}-${order.delivery_end_time})`
    : `${order.delivery_start_time}-${order.delivery_end_time}`;

const selectClassName =
  "h-10 w-full appearance-none rounded-md border border-slate-300 bg-white px-3 pr-10 text-sm text-slate-950";

const getPrimaryPhone = (client: Client) =>
  client.phones?.find((phone) => phone.is_primary) ?? client.phones?.[0];

const getPrimaryAddress = (client: Client) =>
  client.addresses?.find((address) => address.is_primary) ??
  client.addresses?.[0];

const formatRunSummary = (result: RunRecurringOrderResult) => {
  if (result.paused) {
    return "Шаблон поставлено на паузу. Перевірте адресу, телефон, слот або товари.";
  }

  const parts = [
    result.created_dates.length
      ? `Створено: ${result.created_dates.length}`
      : null,
    result.already_scheduled_dates.length
      ? `Вже заплановано: ${result.already_scheduled_dates.length}`
      : null,
    result.cancelled_dates.length
      ? `Скасовано раніше: ${result.cancelled_dates.length}`
      : null,
  ].filter(Boolean);

  return parts.length ? parts.join("\n") : "Нових дат для планування немає.";
};

export const RecurringOrderPlanningSection = ({
  client,
  compact = false,
  seedOrder = null,
  onSeedConsumed,
}: RecurringOrderPlanningSectionProps) => {
  const [orders, setOrders] = useState<RecurringOrder[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [scheduleType, setScheduleType] = useState<ScheduleType>("WEEKLY");
  const [weekdays, setWeekdays] = useState<number[]>([1]);
  const [monthDays, setMonthDays] = useState("1");
  const [phoneId, setPhoneId] = useState<number | "">("");
  const [addressId, setAddressId] = useState<number | "">("");
  const [timeSlotId, setTimeSlotId] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("");
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [comment, setComment] = useState("");
  const [runDialog, setRunDialog] = useState<RunDialogState | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const { timeSlots } = useTimeSlotsSettings();
  const { paymentMethods } = usePaymentMethodsSettings();
  const { products, getProducts } = useProducts();

  const clientOrders = useMemo(
    () => orders.filter((order) => order.client_id === client.client_id),
    [client.client_id, orders],
  );

  const refresh = async () => {
    setIsLoading(true);
    try {
      const data = await getRecurringOrders({
        client_name: client.full_name || "",
      });
      setOrders(data);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunClick = (order: RecurringOrder) => {
    if (order.status === "PAUSED") {
      setRunDialog({ step: "activate", order });
      return;
    }

    setRunDialog({ step: "today", order, activate: false });
  };

  const executeRun = async (
    order: RecurringOrder,
    options: { includeToday: boolean; activate: boolean },
  ) => {
    setIsRunning(true);
    const result = await runRecurringOrder(order.recurring_order_id, {
      include_today: options.includeToday,
      activate: options.activate,
    });
    await refresh();
    setRunDialog({ step: "summary", order, result });
    setIsRunning(false);
  };

  const closeRunDialog = () => {
    if (isRunning) {
      return;
    }
    setRunDialog(null);
  };

  useEffect(() => {
    refresh();
    getProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [client.client_id]);

  useEffect(() => {
    setPhoneId(getPrimaryPhone(client)?.id ?? "");
    setAddressId(getPrimaryAddress(client)?.id ?? "");
  }, [client]);

  useEffect(() => {
    if (!timeSlotId && timeSlots[0]) {
      setTimeSlotId(timeSlots[0].time_slot_id);
    }
  }, [timeSlotId, timeSlots]);

  useEffect(() => {
    if (!paymentMethod && paymentMethods[0]) {
      setPaymentMethod(paymentMethods[0].name);
    }
  }, [paymentMethod, paymentMethods]);

  useEffect(() => {
    if (!productId && products[0]) {
      setProductId(products[0].product_id);
    }
  }, [productId, products]);

  useEffect(() => {
    if (!seedOrder) return;

    const seedItem = seedOrder.items.find((item) => item.product_id);
    if (seedItem?.product_id) {
      setProductId(seedItem.product_id);
      setQuantity(seedItem.quantity);
    }
    if (seedOrder.payment_method) {
      setPaymentMethod(seedOrder.payment_method);
    }
    setComment(seedOrder.comment || seedOrder.note || "");
    setScheduleType("WEEKLY");
    setWeekdays([1]);
    setIsFormOpen(true);
    onSeedConsumed?.();
  }, [onSeedConsumed, seedOrder]);

  const toggleWeekday = (day: number) => {
    setWeekdays((current) =>
      current.includes(day)
        ? current.filter((value) => value !== day)
        : [...current, day].sort((a, b) => a - b),
    );
  };

  const handleCreate = async () => {
    if (!phoneId || !addressId || !timeSlotId || !paymentMethod || !productId) {
      return;
    }

    const parsedMonthDays = monthDays
      .split(",")
      .map((value) => Number(value.trim()))
      .filter((value) => Number.isInteger(value));

    await createRecurringOrder({
      client_id: client.client_id,
      address_id: addressId,
      phone_id: phoneId,
      time_slot_id: timeSlotId,
      items: [{ product_id: productId, quantity }],
      payment_method: paymentMethod,
      comment: comment.trim() || null,
      schedule_type: scheduleType,
      weekdays: scheduleType === "WEEKLY" ? weekdays : null,
      month_days: scheduleType === "MONTHLY_BY_DAY" ? parsedMonthDays : null,
    });

    setIsFormOpen(false);
    await refresh();
  };

  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-950">Планування</h2>
          <p className="text-xs text-slate-500">
            {clientOrders.length} активних або призупинених шаблонів
          </p>
        </div>
        <button
          type="button"
          onClick={() => setIsFormOpen((value) => !value)}
          className="inline-flex h-9 items-center justify-center rounded-md bg-blue-600 px-3 text-sm font-medium text-white hover:bg-blue-700"
        >
          {isFormOpen ? "Закрити" : "Додати"}
        </button>
      </div>

      {isFormOpen && (
        <div className="grid gap-3 border-b border-slate-200 bg-slate-50 px-4 py-4">
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setScheduleType("WEEKLY")}
              className={`h-10 rounded-md border text-sm font-medium ${
                scheduleType === "WEEKLY"
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-slate-300 bg-white text-slate-700"
              }`}
            >
              Тиждень
            </button>
            <button
              type="button"
              onClick={() => setScheduleType("MONTHLY_BY_DAY")}
              className={`h-10 rounded-md border text-sm font-medium ${
                scheduleType === "MONTHLY_BY_DAY"
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-slate-300 bg-white text-slate-700"
              }`}
            >
              Місяць
            </button>
          </div>

          {scheduleType === "WEEKLY" ? (
            <div className="grid grid-cols-7 gap-1">
              {WEEKDAYS.map((day) => (
                <button
                  key={day.value}
                  type="button"
                  onClick={() => toggleWeekday(day.value)}
                  className={`h-9 rounded-md border text-xs font-medium ${
                    weekdays.includes(day.value)
                      ? "border-blue-600 bg-blue-50 text-blue-700"
                      : "border-slate-300 bg-white text-slate-700"
                  }`}
                >
                  {day.label}
                </button>
              ))}
            </div>
          ) : (
            <input
              value={monthDays}
              onChange={(event) => setMonthDays(event.target.value)}
              placeholder="Дні місяця, наприклад 1, 13"
              className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-950"
            />
          )}

          <div className={`grid gap-2 ${compact ? "" : "sm:grid-cols-2"}`}>
            <SelectShell>
              <select
                value={phoneId}
                onChange={(event) => setPhoneId(Number(event.target.value))}
                className={selectClassName}
              >
                {client.phones?.map((phone) => (
                  <option key={phone.id} value={phone.id}>
                    {phone.number}
                  </option>
                ))}
              </select>
            </SelectShell>
            <SelectShell>
              <select
                value={addressId}
                onChange={(event) => setAddressId(Number(event.target.value))}
                className={selectClassName}
              >
                {client.addresses?.map((address) => (
                  <option key={address.id} value={address.id}>
                    {[address.street, address.house, address.apartment]
                      .filter(Boolean)
                      .join(", ")}
                  </option>
                ))}
              </select>
            </SelectShell>
            <SelectShell>
              <select
                value={timeSlotId}
                onChange={(event) => setTimeSlotId(event.target.value)}
                className={selectClassName}
              >
                {timeSlots.map((slot) => (
                  <option key={slot.time_slot_id} value={slot.time_slot_id}>
                    {slot.label
                      ? `${slot.label} (${slot.start_time}-${slot.end_time})`
                      : `${slot.start_time}-${slot.end_time}`}
                  </option>
                ))}
              </select>
            </SelectShell>
            <SelectShell>
              <select
                value={paymentMethod}
                onChange={(event) => setPaymentMethod(event.target.value)}
                className={selectClassName}
              >
                {paymentMethods.map((method) => (
                  <option key={method.payment_method_id} value={method.name}>
                    {method.name}
                  </option>
                ))}
              </select>
            </SelectShell>
          </div>

          <div className={`grid gap-2 ${compact ? "" : "sm:grid-cols-[1fr_7rem]"}`}>
            <SelectShell>
              <select
                value={productId}
                onChange={(event) => setProductId(event.target.value)}
                className={selectClassName}
              >
                {products.map((product) => (
                  <option key={product.product_id} value={product.product_id}>
                    {product.name}
                  </option>
                ))}
              </select>
            </SelectShell>
            <input
              type="number"
              min={1}
              value={quantity}
              onChange={(event) => setQuantity(Number(event.target.value))}
              className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
            />
          </div>

          <input
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            placeholder="Коментар"
            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
          />
          <button
            type="button"
            disabled={weekdays.length === 0 || quantity < 1}
            onClick={handleCreate}
            className="h-10 rounded-md bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Зберегти шаблон
          </button>
        </div>
      )}

      <div className="divide-y divide-slate-200">
        {isLoading ? (
          <p className="px-4 py-3 text-sm text-slate-500">Завантаження...</p>
        ) : clientOrders.length ? (
          clientOrders.map((order) => (
            <div key={order.recurring_order_id} className="px-4 py-3">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-950">
                    {scheduleLabel(order)}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {timeSlotLabel(order)} · {order.items_count} товарів
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {order.address_summary || "Адресу не знайдено"}
                  </p>
                </div>
                <span
                  className={`shrink-0 rounded px-2 py-1 text-xs font-medium ${
                    order.status === "ACTIVE"
                      ? "bg-emerald-50 text-emerald-700"
                      : "bg-slate-100 text-slate-600"
                  }`}
                >
                  {order.status === "ACTIVE" ? "Активний" : "Пауза"}
                </span>
              </div>
              <div className="mt-3 flex gap-2">
                <button
                  type="button"
                  onClick={() => handleRunClick(order)}
                  className="h-8 rounded-md bg-slate-900 px-3 text-xs font-medium text-white hover:bg-slate-700"
                >
                  Запустити
                </button>
                <button
                  type="button"
                  onClick={async () => {
                    if (order.status === "ACTIVE") {
                      await pauseRecurringOrder(order.recurring_order_id);
                    } else {
                      await resumeRecurringOrder(order.recurring_order_id);
                    }
                    await refresh();
                  }}
                  className="h-8 rounded-md border border-slate-300 px-3 text-xs font-medium text-slate-700 hover:bg-slate-100"
                >
                  {order.status === "ACTIVE" ? "Пауза" : "Активувати"}
                </button>
                <button
                  type="button"
                  onClick={async () => {
                    await deleteRecurringOrder(order.recurring_order_id);
                    await refresh();
                  }}
                  className="h-8 rounded-md border border-red-300 px-3 text-xs font-medium text-red-600 hover:bg-red-50"
                >
                  Видалити
                </button>
              </div>
            </div>
          ))
        ) : (
          <p className="px-4 py-3 text-sm text-slate-500">
            Планувань поки немає.
          </p>
        )}
      </div>

      <Modal
        isOpen={runDialog !== null}
        onClose={closeRunDialog}
        title={
          runDialog?.step === "summary"
            ? "Планування виконано"
            : "Запустити планування"
        }
      >
        {runDialog?.step === "activate" && (
          <div className="space-y-5">
            <div>
              <p className="text-sm leading-6 text-slate-700">
                Шаблон зараз на паузі. Щоб створити замовлення, спочатку
                активуйте його.
              </p>
              <p className="mt-3 text-sm font-medium text-slate-950">
                {scheduleLabel(runDialog.order)}
              </p>
              <p className="mt-1 text-sm text-slate-500">
                {timeSlotLabel(runDialog.order)}
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={closeRunDialog}
                className="h-11 rounded-md bg-slate-100 px-4 text-sm font-medium text-slate-700 hover:bg-slate-200"
              >
                Скасувати
              </button>
              <button
                type="button"
                onClick={() =>
                  setRunDialog({
                    step: "today",
                    order: runDialog.order,
                    activate: true,
                  })
                }
                className="h-11 rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-700"
              >
                Активувати
              </button>
            </div>
          </div>
        )}

        {runDialog?.step === "today" && (
          <div className="space-y-5">
            <div>
              <p className="text-sm leading-6 text-slate-700">
                Створити замовлення на сьогодні, якщо сьогоднішній день
                входить у розклад? Без цього будуть заплановані дати з завтра
                до наступних 14 днів.
              </p>
              <p className="mt-3 text-sm font-medium text-slate-950">
                {scheduleLabel(runDialog.order)}
              </p>
              <p className="mt-1 text-sm text-slate-500">
                {timeSlotLabel(runDialog.order)}
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                disabled={isRunning}
                onClick={() =>
                  executeRun(runDialog.order, {
                    includeToday: false,
                    activate: runDialog.activate,
                  })
                }
                className="h-11 rounded-md bg-slate-100 px-4 text-sm font-medium text-slate-700 hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                З завтра
              </button>
              <button
                type="button"
                disabled={isRunning}
                onClick={() =>
                  executeRun(runDialog.order, {
                    includeToday: true,
                    activate: runDialog.activate,
                  })
                }
                className="h-11 rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Включити сьогодні
              </button>
            </div>
          </div>
        )}

        {runDialog?.step === "summary" && (
          <div className="space-y-5">
            <div className="rounded-md border border-slate-200 bg-slate-50 px-4 py-3">
              {formatRunSummary(runDialog.result)
                .split("\n")
                .map((line) => (
                  <p key={line} className="text-sm leading-6 text-slate-700">
                    {line}
                  </p>
                ))}
            </div>
            <button
              type="button"
              onClick={closeRunDialog}
              className="h-11 w-full rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-700"
            >
              Готово
            </button>
          </div>
        )}
      </Modal>
    </section>
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
