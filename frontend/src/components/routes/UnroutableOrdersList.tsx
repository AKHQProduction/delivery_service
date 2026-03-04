import React from "react";
import { type RoutePoint } from "../../types/entities/Route";
import { paymentMap } from "../../utils/dataMap";

interface UnroutableOrdersListProps {
  orders: RoutePoint[];
  onSetAddress: (order: RoutePoint) => void;
}

export const UnroutableOrdersList: React.FC<UnroutableOrdersListProps> = ({ orders, onSetAddress }) => {
  if (orders.length === 0) return null;

  return (
    <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
      <div className="px-5 py-4 bg-amber-50 border-b border-amber-100 flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-amber-100 flex items-center justify-center shrink-0">
          <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h4 className="font-semibold text-gray-900 text-sm">
            Без координат ({orders.length})
          </h4>
          <p className="text-xs text-gray-500 mt-0.5">Вкажіть адресу на карті для додавання в маршрут</p>
        </div>
      </div>
      <div className="divide-y divide-gray-100">
        {orders.map((order) => (
          <div key={order.order_id} className="px-5 py-3 flex items-center gap-3">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{order.client_name}</p>
              <p className="text-xs text-gray-500 mt-0.5 truncate">{order.address || "Адреса не вказана"}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-gray-400">{order.items_summary}</span>
                <span className="text-xs text-gray-300">·</span>
                <span className="text-xs text-gray-400">{order.total_price} ₴</span>
                <span className="text-xs text-gray-300">·</span>
                <span className="text-xs text-gray-400">{paymentMap[order.payment_method] ?? order.payment_method}</span>
              </div>
            </div>
            <button
              type="button"
              onClick={() => onSetAddress(order)}
              className="shrink-0 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
