import React from "react";
import { type RoutePoint } from "../../types/entities/Route";


interface UnroutableOrdersListProps {
  orders: RoutePoint[];
  onSetAddress: (order: RoutePoint) => void;
}

export const UnroutableOrdersList: React.FC<UnroutableOrdersListProps> = ({ orders, onSetAddress }) => {
  if (orders.length === 0) return null;

  return (
    <div className="mt-3 overflow-hidden rounded-lg border border-amber-200 bg-white">
      <div className="flex items-center gap-3 border-b border-amber-100 bg-amber-50 px-4 py-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-100">
          <svg className="h-5 w-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-slate-950">
            Без координат ({orders.length})
          </h4>
          <p className="mt-0.5 text-xs text-slate-500">Вкажіть адресу на карті для додавання в маршрут</p>
        </div>
      </div>
      <div className="divide-y divide-slate-200">
        {orders.map((order) => (
          <div key={order.order_id} className="flex flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center">
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-slate-950">{order.client_name}</p>
              <p className="mt-0.5 truncate text-xs text-slate-500">{order.address || "Адреса не вказана"}</p>
              <div className="mt-1 flex flex-wrap items-center gap-2">
                <span className="text-xs text-slate-500">{order.items_summary}</span>
                <span className="text-xs text-slate-300">·</span>
                <span className="text-xs text-slate-500">{order.total_price} ₴</span>
                <span className="text-xs text-slate-300">·</span>
                <span className="text-xs text-slate-500">{order.payment_method}</span>
              </div>
            </div>
            <button
              type="button"
              onClick={() => onSetAddress(order)}
              className="inline-flex h-9 shrink-0 items-center justify-center gap-1.5 rounded-md border border-blue-200 bg-blue-50 px-3 text-xs font-medium text-blue-700 transition-colors hover:bg-blue-100 sm:w-auto"
            >
              <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              На карті
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
