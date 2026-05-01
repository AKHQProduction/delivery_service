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
    <div className="z-10 flex shrink-0 items-center gap-3 border-b border-slate-200 bg-white px-4 py-3 md:px-6 md:py-4">
      <button
        title="Назад до списку маршрутів"
        type="button"
        onClick={onBack}
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-slate-600 transition-colors hover:bg-slate-100"
      >
        <svg
          className="h-5 w-5"
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
        className="hidden h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 sm:inline-flex"
      >
        {isExporting ? (
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-200 border-t-blue-600" />
        ) : (
          <svg
            className="h-4 w-4"
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
        <span>{isExporting ? "Формування" : "Експорт"}</span>
      </button>
      <div className="min-w-0 flex-1">
        <h1 className="truncate text-lg font-semibold text-slate-950">Маршрут</h1>
        <p className="text-xs text-slate-500">
          {routePlan.delivery_date}
          {routePlan.time_slot ? ` · ${routePlan.time_slot}` : ""} · {pointCount} зупинок
        </p>
      </div>
      {canEdit && (
        <button
          type="button"
          title="Розвернути маршрут"
          onClick={onReverseRoute}
          className="flex h-9 shrink-0 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
          </svg>
          <span className="hidden lg:inline">Перевернути</span>
        </button>
      )}
      <button
        type="button"
        onClick={onToggleList}
        aria-label={showList ? "Показати карту" : "Показати список"}
        className="flex h-9 w-9 items-center justify-center rounded-md bg-blue-50 text-blue-700 transition-colors hover:bg-blue-100 md:hidden"
      >
        {showList ? (
          <svg
            className="h-5 w-5"
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
            className="h-5 w-5"
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
