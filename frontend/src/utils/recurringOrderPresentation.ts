import {
  type RecurringOrder,
  type RecurringOrderStatus,
  type RunRecurringOrderResult,
  type ScheduleType,
} from "../types/entities/RecurringOrder";

export const WEEKDAYS = [
  { value: 1, label: "Пн" },
  { value: 2, label: "Вт" },
  { value: 3, label: "Ср" },
  { value: 4, label: "Чт" },
  { value: 5, label: "Пт" },
  { value: 6, label: "Сб" },
  { value: 7, label: "Нд" },
];

export const formatScheduleTypeLabel = (scheduleType: ScheduleType) =>
  scheduleType === "WEEKLY" ? "Тиждень" : "Місяць";

export const formatRecurringOrderStatusLabel = (
  status: RecurringOrderStatus,
) => (status === "ACTIVE" ? "Активний" : "Пауза");

export const getRecurringOrderStatusClassName = (
  status: RecurringOrderStatus,
) =>
  status === "ACTIVE"
    ? "bg-emerald-50 text-emerald-700"
    : "bg-slate-100 text-slate-600";

export const formatScheduleLabel = (order: RecurringOrder) => {
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

export const formatScheduleSummaryLabel = (order: RecurringOrder) =>
  order.schedule_type === "WEEKLY"
    ? "Щотижневе замовлення"
    : "Щомісячне замовлення";

export const formatRecurringOrderTimeSlotLabel = (order: RecurringOrder) =>
  !order.delivery_start_time || !order.delivery_end_time
    ? "Слот видалено"
    : order.time_slot_label
      ? `${order.time_slot_label} (${order.delivery_start_time}-${order.delivery_end_time})`
      : `${order.delivery_start_time}-${order.delivery_end_time}`;

export const formatRecurringOrderItemsCount = (itemsCount: number) =>
  `${itemsCount} товарів`;

export const formatRunSummaryLines = (result: RunRecurringOrderResult) => {
  if (result.paused) {
    return [
      "Шаблон поставлено на паузу. Перевірте адресу, телефон, слот або товари.",
    ];
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
  ].filter((part): part is string => Boolean(part));

  return parts.length ? parts : ["Нових дат для планування немає."];
};
