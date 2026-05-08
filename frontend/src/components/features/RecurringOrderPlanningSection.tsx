import { type ReactNode } from "react";
import { useRecurringOrderPlanning } from "../../hooks/recurringOrders/useRecurringOrderPlanning";
import { type Client } from "../../types/entities/Client";
import { type RecurringTemplateSeed } from "../../utils/recurringOrderFormModel";
import {
  formatRecurringOrderItemsCount,
  formatRecurringOrderStatusLabel,
  formatRecurringOrderTimeSlotLabel,
  formatRunSummaryLines,
  formatScheduleLabel,
  getRecurringOrderStatusClassName,
  WEEKDAYS,
} from "../../utils/recurringOrderPresentation";
import { Modal } from "../modals/Modal";

interface RecurringOrderPlanningSectionProps {
  client: Client;
  compact?: boolean;
  seed?: RecurringTemplateSeed | null;
  onSeedConsumed?: () => void;
}

const selectClassName =
  "h-10 w-full appearance-none rounded-md border border-slate-300 bg-white px-3 pr-10 text-sm text-slate-950";

export const RecurringOrderPlanningSection = ({
  client,
  compact = false,
  seed = null,
  onSeedConsumed,
}: RecurringOrderPlanningSectionProps) => {
  const planning = useRecurringOrderPlanning(client, seed, onSeedConsumed);
  const {
    addressId,
    clientOrders,
    closeRunDialog,
    comment,
    continueAfterActivation,
    deleteOrder,
    executeRun,
    handleCreate,
    handleRunClick,
    isFormOpen,
    isLoading,
    isRunning,
    monthDays,
    paymentMethod,
    paymentMethods,
    phoneId,
    productId,
    products,
    quantity,
    runDialog,
    scheduleType,
    setAddressId,
    setComment,
    setIsFormOpen,
    setMonthDays,
    setPaymentMethod,
    setPhoneId,
    setProductId,
    setQuantity,
    setScheduleType,
    setTimeSlotId,
    timeSlotId,
    timeSlots,
    toggleStatus,
    toggleWeekday,
    weekdays,
  } = planning;

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
                    {formatScheduleLabel(order)}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {formatRecurringOrderTimeSlotLabel(order)} ·{" "}
                    {formatRecurringOrderItemsCount(order.items_count)}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {order.address_summary || "Адресу не знайдено"}
                  </p>
                </div>
                <span
                  className={`shrink-0 rounded px-2 py-1 text-xs font-medium ${
                    getRecurringOrderStatusClassName(order.status)
                  }`}
                >
                  {formatRecurringOrderStatusLabel(order.status)}
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
                  onClick={() => toggleStatus(order)}
                  className="h-8 rounded-md border border-slate-300 px-3 text-xs font-medium text-slate-700 hover:bg-slate-100"
                >
                  {order.status === "ACTIVE" ? "Пауза" : "Активувати"}
                </button>
                <button
                  type="button"
                  onClick={() => deleteOrder(order)}
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
                {formatScheduleLabel(runDialog.order)}
              </p>
              <p className="mt-1 text-sm text-slate-500">
                {formatRecurringOrderTimeSlotLabel(runDialog.order)}
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
                onClick={continueAfterActivation}
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
                {formatScheduleLabel(runDialog.order)}
              </p>
              <p className="mt-1 text-sm text-slate-500">
                {formatRecurringOrderTimeSlotLabel(runDialog.order)}
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
              {formatRunSummaryLines(runDialog.result).map((line) => (
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
