import React from "react";
import { type RoutePlan } from "../../types/entities/Route";

interface RoutePlanCardProps {
  routePlan: RoutePlan;
  onClick: () => void;
  onSelect?: () => void;
  index?: number;
  isSelected?: boolean;
}

const routeColors = ["bg-blue-600", "bg-orange-500", "bg-slate-400", "bg-cyan-500"];

export const RoutePlanCard: React.FC<RoutePlanCardProps> = ({
  routePlan,
  onClick,
  onSelect,
  index = 0,
  isSelected = false,
}) => {
  const hasUnroutable = routePlan.unroutable_orders.length > 0;
  const statusLabel = hasUnroutable ? "Потребує адрес" : "Готовий";
  const statusClass = hasUnroutable
    ? "bg-amber-50 text-amber-700"
    : "bg-emerald-50 text-emerald-700";
  const colorClass = routeColors[index % routeColors.length];

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onSelect?.();
        }
      }}
      className={`group w-full rounded-lg border bg-white p-4 text-left transition-colors hover:border-blue-300 hover:bg-blue-50/30 ${
        isSelected ? "border-blue-300 bg-blue-50/30" : "border-slate-200"
      }`}
      title="Вибрати маршрут"
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex min-w-0 flex-1 items-start gap-3">
          <span className={`mt-1 h-3 w-3 shrink-0 rounded-full ${colorClass}`} />
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="truncate text-base font-semibold text-slate-950">
                Маршрут {index + 1}
              </h3>
              <span className={`rounded px-2 py-1 text-xs font-medium ${statusClass}`}>
                {statusLabel}
              </span>
            </div>
            <p className="mt-1 text-sm text-slate-500">{routePlan.time_slot || "Всі проміжки"}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            onClick();
          }}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600"
          aria-label={`Відкрити маршрут ${index + 1}`}
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 pl-6">
        <div className="flex items-center gap-1.5 text-sm text-slate-600">
          <svg className="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span className="font-semibold text-slate-950">{routePlan.stats.total_orders}</span>
          <span>замовлень</span>
        </div>
        <div className="flex items-center gap-1.5 text-sm text-slate-600">
          <svg className="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4" />
          </svg>
          <span className="font-semibold text-slate-950">{routePlan.stats.unique_addresses}</span>
          <span>адрес</span>
        </div>
      </div>
    </div>
  );
};
