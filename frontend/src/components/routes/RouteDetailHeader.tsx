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
    <div className="z-10 shrink-0 border-b border-slate-200 bg-white px-4 py-3 md:px-6">
      <div className="flex items-center gap-3">
        <button
          title="Назад до маршрутів"
          type="button"
          onClick={onBack}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-slate-600 transition-colors hover:bg-slate-100"
          aria-label="Назад до маршрутів"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="truncate text-lg font-semibold text-slate-950">Маршрут</h1>
            <span className="rounded bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
              {pointCount} зупинок
            </span>
          </div>
          <p className="mt-0.5 truncate text-xs text-slate-500">
            {routePlan.delivery_date}
            {routePlan.time_slot ? ` · ${routePlan.time_slot}` : " · Всі проміжки"}
          </p>
        </div>
        <button
          title="Сформувати документ"
          type="button"
          onClick={onExportDocument}
          disabled={isExporting}
          className="flex h-9 shrink-0 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Експорт маршруту"
        >
          {isExporting ? (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-200 border-t-blue-600" />
          ) : (
            <DownloadIcon className="h-4 w-4" />
          )}
          <span className="hidden sm:inline">{isExporting ? "Формування" : "Експорт"}</span>
        </button>
        {canEdit && (
          <button
            type="button"
            title="Розвернути маршрут"
            onClick={onReverseRoute}
            className="flex h-9 shrink-0 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
              />
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
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
          ) : (
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    </div>
  );
};

const DownloadIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 3v12m0 0 4-4m-4 4-4-4M5 21h14"
    />
  </svg>
);
