import React from "react";
import { type RoutePlan } from "../../types/entities/Route";

interface RouteDetailHeaderProps {
  routePlan: RoutePlan;
  pointCount: number;
  showList: boolean;
  canEdit: boolean;
  isExporting: boolean;
  onToggleList: () => void;
  onBack: () => void;
  onReverseRoute: () => void;
  onExportDocument: () => void;
}

export const RouteDetailHeader: React.FC<RouteDetailHeaderProps> = ({
  routePlan,
  pointCount,
  showList,
  canEdit,
  isExporting,
  onToggleList,
  onBack,
  onReverseRoute,
  onExportDocument,
}) => {
  return (
    <div className="shrink-0 bg-white border-b border-gray-200 px-4 py-3 md:px-6 md:py-4 flex items-center gap-3 z-10">
      <button
        title="Назад до списку маршрутів"
        type="button"
        onClick={onBack}
        className="w-9 h-9 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors shrink-0"
      >
        <svg
          className="w-5 h-5 text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <button
        title="Сформувати документ"
        type="button"
        onClick={onExportDocument}
        disabled={isExporting}
        className="w-9 h-9 rounded-full bg-amber-100 hover:bg-amber-200 flex items-center justify-center transition-colors shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isExporting ? (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-amber-600" />
        ) : (
          <svg
            className="w-5 h-5 text-amber-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        )}
      </button>
      <div className="flex-1 min-w-0">
        <h1 className="font-bold text-gray-900 text-lg truncate">
          {routePlan.delivery_date}
          {routePlan.time_slot ? ` · ${routePlan.time_slot}` : ""}
        </h1>
        <p className="text-xs text-gray-500">{pointCount} зупинок</p>
      </div>
      {/* Reverse route */}
      {canEdit && (
        <button
          type="button"
          title="Розвернути маршрут"
          onClick={onReverseRoute}
          className="w-9 h-9 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors shrink-0"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
          </svg>
        </button>
      )}
      {/* Toggle list/map on mobile */}
      <button
        type="button"
        onClick={onToggleList}
        className="md:hidden w-9 h-9 rounded-full bg-indigo-100 hover:bg-indigo-200 flex items-center justify-center transition-colors"
      >
        {showList ? (
          <svg
            className="w-5 h-5 text-indigo-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
            />
          </svg>
        ) : (
          <svg
            className="w-5 h-5 text-indigo-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        )}
      </button>
    </div>
  );
};
