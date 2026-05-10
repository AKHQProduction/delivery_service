import { type ReactNode, useEffect, useState } from "react";
import { useRecurringOrderPlanning } from "../../hooks/recurringOrders/useRecurringOrderPlanning";
import {
  getRecurringOrderById,
  type RecurringOrderFilters,
} from "../../services/api/recurringOrderApi";
import { fetchRecentOrdersForClient } from "../../services/clientPlanningData";
import { type Client } from "../../types/entities/Client";
import { type Order } from "../../types/entities/Order";
import { type RecurringOrder } from "../../types/entities/RecurringOrder";
import {
  buildRecurringTemplateSeed,
  type RecurringTemplateSeed,
} from "../../utils/recurringOrderFormModel";
import { getOrderItemsSummary } from "../../utils/orderDraft";
import {
  formatRecurringOrderTimeSlotLabel,
  formatRunSummaryLines,
  formatScheduleLabel,
  WEEKDAYS,
} from "../../utils/recurringOrderPresentation";
import { Modal } from "../modals/Modal";
import { RecurringOrderListItem } from "./RecurringOrderListItem";

interface RecurringOrderPlanningSectionProps {
  client: Client;
  seed?: RecurringTemplateSeed | null;
  onSeedConsumed?: () => void;
  filters?: Omit<RecurringOrderFilters, "client_id" | "client_name">;
}

const selectClassName =
  "h-10 w-full appearance-none rounded-md border border-slate-300 bg-white px-3 pr-10 text-sm text-slate-950";

export const RecurringOrderPlanningSection = ({
  client,
  seed = null,
  onSeedConsumed,
  filters = {},
}: RecurringOrderPlanningSectionProps) => {
  const planning = useRecurringOrderPlanning(client, seed, onSeedConsumed, filters);
  const [settingsOrder, setSettingsOrder] = useState<RecurringOrder | null>(null);
  const [recentOrders, setRecentOrders] = useState<Order[]>([]);
  const [selectedRecentOrderId, setSelectedRecentOrderId] = useState<string | null>(null);
  const [isRecentOrdersLoading, setIsRecentOrdersLoading] = useState(false);
  const [rebuildFutureOrders, setRebuildFutureOrders] = useState(false);
  const { clientOrders, form, formActions, isLoading, options, workflow } = planning;
  const {
    addressId,
    comment,
    monthDays,
    paymentMethod,
    phoneId,
    items,
    scheduleType,
    timeSlotId,
    weekdays,
  } = form.draft;
  const { paymentMethods, products, timeSlots } = options;
  const {
    closeRunDialog,
    confirmDelete,
    confirmPause,
    continueRunAfterActivation,
    deleteDialogOrder,
    executeRun,
    isRunning,
    pauseDialogOrder,
    requestDelete,
    runDialog,
    setDeleteDialogOrder,
    setPauseDialogOrder,
    toggleStatus,
  } = workflow;

  const handleToggleSettingsOrder = async () => {
    if (!settingsOrder) return;

    const order = settingsOrder;
    setSettingsOrder(null);
    formActions.close();
    await toggleStatus(order);
  };

  const handleDeleteSettingsOrder = () => {
    if (!settingsOrder) return;

    const order = settingsOrder;
    setSettingsOrder(null);
    formActions.close();
    requestDelete(order);
  };

  const handleOpenCreate = () => {
    setSettingsOrder(null);
    setSelectedRecentOrderId(null);
    setRebuildFutureOrders(false);
    formActions.open();
  };

  const handleCloseForm = () => {
    setSettingsOrder(null);
    setRebuildFutureOrders(false);
    formActions.close();
  };

  const handleOpenSettings = async (order: RecurringOrder) => {
    const detail = await getRecurringOrderById(order.recurring_order_id);
    setSettingsOrder(detail);
    setSelectedRecentOrderId(null);
    setRebuildFutureOrders(false);
    formActions.startEdit(detail);
  };

  useEffect(() => {
    if (!form.isOpen) return;

    const loadRecentOrders = async () => {
      setIsRecentOrdersLoading(true);
      try {
        const orders = await fetchRecentOrdersForClient(client, 5);
        setRecentOrders(orders);
      } finally {
        setIsRecentOrdersLoading(false);
      }
    };

    loadRecentOrders();
  }, [client, form.isOpen]);

  const applyRecentOrderSeed = (order: Order) => {
    setSelectedRecentOrderId(order.order_id);
    formActions.applySeed(buildRecurringTemplateSeed(order));
  };

  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="flex flex-col gap-4 border-b border-slate-200 px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">
            {client.full_name || "Без імені"}
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            {client.phones?.[0]?.number || "Телефон не вказано"}
            {typeof client.balance === "number" ? ` · Баланс: ${client.balance} ₴` : ""}
          </p>
        </div>
        <button
          type="button"
          onClick={handleOpenCreate}
          className="inline-flex h-10 items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700"
        >
          Створити регулярне
        </button>
      </div>

      <Modal
        isOpen={form.isOpen}
        onClose={handleCloseForm}
        title={form.mode === "edit" ? "Налаштування планування" : "Створити регулярне"}
        size="2xl"
      >
        <div className="grid gap-5">
          {form.mode === "create" && (
            <div className="rounded-md border border-slate-200 bg-slate-50">
              <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
                <div>
                  <p className="text-sm font-semibold text-slate-950">
                    Створити з останнього замовлення
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    Оберіть замовлення, щоб підтягнути товари, оплату і коментар.
                  </p>
                </div>
              </div>
              <div className="divide-y divide-slate-200">
                {isRecentOrdersLoading ? (
                  <p className="px-4 py-3 text-sm text-slate-500">Завантаження...</p>
                ) : recentOrders.length ? (
                  recentOrders.map((order) => (
                    <button
                      key={order.order_id}
                      type="button"
                      onClick={() => applyRecentOrderSeed(order)}
                      className={`grid w-full gap-3 px-4 py-3 text-left hover:bg-white sm:grid-cols-[minmax(0,1fr)_auto] ${
                        selectedRecentOrderId === order.order_id ? "bg-blue-50" : ""
                      }`}
                    >
                      <span className="min-w-0">
                        <span className="block truncate text-sm font-medium text-slate-950">
                          {order.date} · {order.time_slot || order.time_preference}
                        </span>
                        <span className="mt-1 block text-sm text-slate-500">
                          {getOrderItemsSummary(order)}
                        </span>
                      </span>
                      <span className="flex items-center gap-2">
                        <span
                          className={`rounded px-2 py-1 text-xs font-medium ${
                            order.is_paid
                              ? "bg-emerald-50 text-emerald-700"
                              : "bg-slate-100 text-slate-600"
                          }`}
                        >
                          {order.is_paid ? "Оплачено" : "Не оплачено"}
                        </span>
                        <span className="rounded-md border border-blue-300 px-3 py-1.5 text-xs font-medium text-blue-700">
                          Використати
                        </span>
                      </span>
                    </button>
                  ))
                ) : (
                  <p className="px-4 py-3 text-sm text-slate-500">Останніх замовлень немає.</p>
                )}
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => formActions.setScheduleType("WEEKLY")}
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
              onClick={() => formActions.setScheduleType("MONTHLY_BY_DAY")}
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
                  onClick={() => formActions.toggleWeekday(day.value)}
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
              onChange={(event) => formActions.setMonthDays(event.target.value)}
              placeholder="Дні місяця, наприклад 1, 13"
              className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-950"
            />
          )}

          <div className="grid gap-3 sm:grid-cols-2">
            <SelectShell>
              <select
                value={phoneId}
                onChange={(event) => formActions.selectPhone(Number(event.target.value))}
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
                onChange={(event) => formActions.selectAddress(Number(event.target.value))}
                className={selectClassName}
              >
                {client.addresses?.map((address) => (
                  <option key={address.id} value={address.id}>
                    {[address.street, address.house, address.apartment].filter(Boolean).join(", ")}
                  </option>
                ))}
              </select>
            </SelectShell>
            <SelectShell>
              <select
                value={timeSlotId}
                onChange={(event) => formActions.selectTimeSlot(event.target.value)}
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
                onChange={(event) => formActions.selectPaymentMethod(event.target.value)}
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

          <div className="grid gap-3 rounded-md border border-slate-200 bg-slate-50 p-3">
            {items.map((item) => (
              <div key={item.id} className="grid grid-cols-[minmax(0,1fr)_5.5rem_2.5rem] gap-2">
                <SelectShell>
                  <select
                    value={item.productId}
                    onChange={(event) => formActions.selectItemProduct(item.id, event.target.value)}
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
                  value={item.quantity}
                  onChange={(event) =>
                    formActions.setItemQuantity(item.id, Number(event.target.value))
                  }
                  className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                />
                <button
                  type="button"
                  disabled={items.length <= 1}
                  onClick={() => formActions.removeItem(item.id)}
                  aria-label="Видалити товар"
                  className="h-10 rounded-md border border-slate-300 bg-white text-lg leading-none text-slate-500 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  -
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={formActions.addItem}
              className="h-9 rounded-md border border-dashed border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 hover:bg-slate-100"
            >
              Додати товар
            </button>
          </div>

          <input
            value={comment}
            onChange={(event) => formActions.setComment(event.target.value)}
            placeholder="Коментар"
            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
          />
          {form.mode === "edit" && settingsOrder && (
            <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-950">Майбутні замовлення</p>
              {settingsOrder.status === "PAUSED" ? (
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Шаблон на паузі. Зміни збережуться тільки в шаблоні; щоб застосувати їх до
                  майбутніх замовлень, спочатку активуйте планування.
                </p>
              ) : (
                <div className="mt-3 grid gap-3">
                  <label className="flex items-start gap-3 text-sm text-slate-700">
                    <input
                      type="checkbox"
                      checked={rebuildFutureOrders}
                      onChange={(event) => setRebuildFutureOrders(event.target.checked)}
                      className="mt-1 h-4 w-4 rounded border-slate-300"
                    />
                    <span>
                      Перебудувати майбутні замовлення з завтра
                    </span>
                  </label>
                  <p className="pl-7 text-xs leading-5 text-slate-500">
                    Майбутні замовлення, створені цим плануванням, будуть видалені і створені
                    заново за новими налаштуваннями.
                  </p>
                </div>
              )}
            </div>
          )}
          <button
            type="button"
            disabled={!form.canSubmit}
            onClick={() =>
              formActions.create({
                rebuild_future_orders: rebuildFutureOrders,
              })
            }
            className="h-11 rounded-md bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {form.mode === "edit" ? "Зберегти" : "Створити регулярне"}
          </button>
          {form.mode === "edit" && settingsOrder && (
            <div className="grid gap-2 border-t border-slate-200 pt-4 sm:grid-cols-[1fr_1fr]">
              <button
                type="button"
                onClick={handleToggleSettingsOrder}
                className="min-h-11 rounded-md border border-slate-300 px-4 py-2 text-sm font-medium leading-5 text-slate-700 hover:bg-slate-100"
              >
                {settingsOrder.status === "ACTIVE" ? "Поставити на паузу" : "Активувати"}
              </button>
              <button
                type="button"
                onClick={handleDeleteSettingsOrder}
                className="min-h-11 rounded-md border border-red-300 px-4 py-2 text-sm font-medium leading-5 text-red-600 hover:bg-red-50"
              >
                Видалити планування
              </button>
            </div>
          )}
        </div>
      </Modal>

      <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-950">Шаблони планування</h3>
          <p className="mt-1 text-xs text-slate-500">
            {clientOrders.length} активних або призупинених шаблонів
          </p>
        </div>
      </div>

      <div className="grid gap-3 p-4 lg:grid-cols-2">
        {isLoading ? (
          <p className="px-4 py-3 text-sm text-slate-500">Завантаження...</p>
        ) : clientOrders.length ? (
          clientOrders.map((order) => (
            <RecurringOrderListItem
              key={order.recurring_order_id}
              order={order}
              showAddress
              className="rounded-lg border border-slate-200"
              actions={
                <button
                  type="button"
                  onClick={() => handleOpenSettings(order)}
                  title="Налаштування"
                  aria-label="Налаштування планування"
                  className="ml-auto inline-flex h-8 items-center gap-2 rounded-md border border-slate-300 px-2.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
                >
                  <GearIcon className="h-4 w-4" />
                  <span>Налаштування</span>
                </button>
              }
            />
          ))
        ) : (
          <p className="rounded-lg border border-dashed border-slate-300 px-4 py-8 text-center text-sm text-slate-500 lg:col-span-2">
            Планувань поки немає.
          </p>
        )}
      </div>

      <Modal
        isOpen={pauseDialogOrder !== null}
        onClose={() => setPauseDialogOrder(null)}
        title="Поставити на паузу"
      >
        {pauseDialogOrder && (
          <div className="space-y-5">
            <div>
              <p className="text-sm leading-6 text-slate-700">
                Шаблон перестане створювати нові замовлення. Уже створені майбутні замовлення можна
                залишити або видалити починаючи з завтра.
              </p>
              <p className="mt-3 text-sm font-medium text-slate-950">
                {formatScheduleLabel(pauseDialogOrder)}
              </p>
              <p className="mt-1 text-sm text-slate-500">
                {formatRecurringOrderTimeSlotLabel(pauseDialogOrder)}
              </p>
            </div>
            <div className="grid gap-2">
              <button
                type="button"
                onClick={() => confirmPause(false)}
                className="min-h-11 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium leading-5 text-white hover:bg-slate-700"
              >
                Лише пауза
              </button>
              <button
                type="button"
                onClick={() => confirmPause(true)}
                className="min-h-11 rounded-md border border-red-300 px-4 py-2 text-sm font-medium leading-5 text-red-600 hover:bg-red-50"
              >
                Пауза і видалити майбутні
              </button>
            </div>
          </div>
        )}
      </Modal>

      <Modal
        isOpen={deleteDialogOrder !== null}
        onClose={() => setDeleteDialogOrder(null)}
        title="Видалити планування"
      >
        {deleteDialogOrder && (
          <div className="space-y-5">
            <div>
              <p className="text-sm leading-6 text-slate-700">
                За замовчуванням буде видалено тільки шаблон. Уже створені замовлення залишаться як
                звичайні.
              </p>
              <p className="mt-3 text-sm font-medium text-slate-950">
                {formatScheduleLabel(deleteDialogOrder)}
              </p>
            </div>
            <div className="grid gap-2">
              <button
                type="button"
                onClick={() => confirmDelete(false)}
                className="min-h-11 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium leading-5 text-white hover:bg-slate-700"
              >
                Видалити тільки шаблон
              </button>
              <button
                type="button"
                onClick={() => confirmDelete(true)}
                className="min-h-11 rounded-md border border-red-300 px-4 py-2 text-sm font-medium leading-5 text-red-600 hover:bg-red-50"
              >
                Також видалити майбутні
              </button>
            </div>
          </div>
        )}
      </Modal>

      <Modal
        isOpen={runDialog !== null}
        onClose={closeRunDialog}
        title={runDialog?.step === "summary" ? "Планування виконано" : "Запустити планування"}
      >
        {runDialog?.step === "activate" && (
          <div className="space-y-5">
            <div>
              <p className="text-sm leading-6 text-slate-700">
                Шаблон зараз на паузі. Щоб створити замовлення, спочатку активуйте його.
              </p>
              <p className="mt-3 text-sm font-medium text-slate-950">
                {formatScheduleLabel(runDialog.order)}
              </p>
              <p className="mt-1 text-sm text-slate-500">
                {formatRecurringOrderTimeSlotLabel(runDialog.order)}
              </p>
            </div>
            <div className="grid gap-2">
              <button
                type="button"
                onClick={closeRunDialog}
                className="min-h-11 rounded-md bg-slate-100 px-4 py-2 text-sm font-medium leading-5 text-slate-700 hover:bg-slate-200"
              >
                Скасувати
              </button>
              <button
                type="button"
                onClick={continueRunAfterActivation}
                className="min-h-11 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium leading-5 text-white hover:bg-slate-700"
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
                Створити замовлення на сьогодні, якщо сьогоднішній день входить у розклад? Без цього
                будуть заплановані дати з завтра до наступних 14 днів.
              </p>
              <p className="mt-3 text-sm font-medium text-slate-950">
                {formatScheduleLabel(runDialog.order)}
              </p>
              <p className="mt-1 text-sm text-slate-500">
                {formatRecurringOrderTimeSlotLabel(runDialog.order)}
              </p>
            </div>
            <div className="grid gap-2">
              <button
                type="button"
                disabled={isRunning}
                onClick={() =>
                  executeRun(runDialog.order, {
                    includeToday: false,
                    activate: runDialog.activate,
                  })
                }
                className="min-h-11 rounded-md bg-slate-100 px-4 py-2 text-sm font-medium leading-5 text-slate-700 hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
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
                className="min-h-11 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium leading-5 text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
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
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path d="m6 9 6 6 6-6" strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} />
  </svg>
);

const GearIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      d="M12 15.5A3.5 3.5 0 1 0 12 8a3.5 3.5 0 0 0 0 7.5Z"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
    />
    <path
      d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.38a1.7 1.7 0 0 0-1 .55V20a2 2 0 1 1-4 0v-.08a1.7 1.7 0 0 0-1-.55 1.7 1.7 0 0 0-1.88.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.62 15a1.7 1.7 0 0 0-.55-1H4a2 2 0 1 1 0-4h.08a1.7 1.7 0 0 0 .55-1 1.7 1.7 0 0 0-.34-1.88l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.62a1.7 1.7 0 0 0 1-.55V4a2 2 0 1 1 4 0v.08a1.7 1.7 0 0 0 1 .55 1.7 1.7 0 0 0 1.88-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.38 9c.21.34.4.69.55 1H20a2 2 0 1 1 0 4h-.08a1.7 1.7 0 0 0-.52 1Z"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
    />
  </svg>
);
