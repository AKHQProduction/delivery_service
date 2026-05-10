import { type ReactNode } from "react";
import { type RecurringOrder } from "../../types/entities/RecurringOrder";
import {
  formatRecurringOrderItemsCount,
  formatRecurringOrderStatusLabel,
  formatRecurringOrderTimeSlotLabel,
  formatScheduleLabel,
  formatScheduleSummaryLabel,
  getRecurringOrderStatusClassName,
} from "../../utils/recurringOrderPresentation";

interface RecurringOrderListItemProps {
  order: RecurringOrder;
  actions?: ReactNode;
  className?: string;
  showAddress?: boolean;
  showClient?: boolean;
  summaryLabel?: boolean;
}

export const RecurringOrderListItem = ({
  order,
  actions,
  className = "",
  showAddress = false,
  showClient = false,
  summaryLabel = false,
}: RecurringOrderListItemProps) => (
  <div className={`px-4 py-3 ${className}`}>
    <div className="flex items-start justify-between gap-3">
      <div className="min-w-0">
        {showClient && (
          <>
            <p className="truncate text-sm font-medium text-slate-950">{order.client_name}</p>
            <p className="mt-1 truncate text-sm text-slate-500">
              {order.phone_number || "Телефон не знайдено"}
            </p>
          </>
        )}
        <p className={`text-sm font-medium text-slate-950 ${showClient ? "mt-3" : ""}`}>
          {summaryLabel ? formatScheduleSummaryLabel(order) : formatScheduleLabel(order)}
        </p>
        <p className="mt-1 text-sm text-slate-500">
          {formatRecurringOrderTimeSlotLabel(order)} ·{" "}
          {formatRecurringOrderItemsCount(order.items_count)}
        </p>
        {showAddress && (
          <p className="mt-1 text-xs text-slate-500">
            {order.address_summary || "Адресу не знайдено"}
          </p>
        )}
      </div>
      <span
        className={`shrink-0 rounded px-2 py-1 text-xs font-medium ${getRecurringOrderStatusClassName(
          order.status,
        )}`}
      >
        {formatRecurringOrderStatusLabel(order.status)}
      </span>
    </div>
    {actions && <div className="mt-3 flex gap-2">{actions}</div>}
  </div>
);
