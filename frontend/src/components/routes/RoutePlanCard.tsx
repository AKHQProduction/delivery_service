import React from "react";
import { type RoutePlan } from "../../types/entities/Route";

interface RoutePlanCardProps {
  routePlan: RoutePlan;
  onClick: () => void;
}

export const RoutePlanCard: React.FC<RoutePlanCardProps> = ({ routePlan, onClick }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full bg-white rounded-2xl border border-gray-200 p-5 text-left hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 group"
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-gray-900 text-base group-hover:text-indigo-600 transition-colors">
            Маршрут на {routePlan.delivery_date}
          </h3>
          <p className="text-sm text-gray-500 mt-1">{routePlan.time_slot}</p>
        </div>
        <div className="shrink-0 w-9 h-9 rounded-full bg-gray-100 group-hover:bg-indigo-100 flex items-center justify-center transition-colors">
          <svg
            className="w-5 h-5 text-gray-400 group-hover:text-indigo-600 transition-colors"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>

      {/* Stats */}
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 mt-4">
        <div className="flex items-center gap-1.5 text-sm text-gray-600">
          <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span className="font-medium">{routePlan.stats.total_orders}</span>
          <span>замовлень</span>
        </div>
        <div className="flex items-center gap-1.5 text-sm text-gray-600">
          <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4" />
          </svg>
          <span className="font-medium">{routePlan.stats.unique_addresses}</span>
          <span>адрес</span>
        </div>
      </div>
    </button>
  );
};
