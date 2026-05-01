import { useNavigate, useLocation } from "react-router-dom";
import { type RoutePlan } from "../types/entities/Route";
import { useRouteDetail } from "../hooks/routes/useRouteDetail";
import { useOrdersPdfPreview } from "../hooks/useOrdersPdfPreview";
import { useToast } from "../hooks/useToast";
import { convertDateToISO } from "../utils/dateUtils";
import { RouteDetailHeader } from "../components/routes/RouteDetailHeader";
import { RouteStopsList } from "../components/routes/RouteStopsList";
import { RouteMap } from "../components/routes/RouteMap";
import { Toast } from "../components/ui/Toast";

export const RouteDetailPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as { routePlan?: RoutePlan; timeSlotId?: string | null } | null;
  const routePlan = state?.routePlan ?? null;
  const timeSlotId = state?.timeSlotId ?? null;

  const {
    points,
    showList,
    dragIndex,
    overIndex,
    editingOrderId,
    canEdit,
    pointsWithCoords,
    handleDragStart,
    handleDragOver,
    handleDrop,
    handleDragEnd,
    movePoint,
    handleMarkerMove,
    toggleEditMarker,
    cancelEditMarker,
    toggleList,
    handleReverseRoute,
    reorderByIndex,
  } = useRouteDetail(routePlan, timeSlotId);

  const { toast, showToast, hideToast } = useToast();
  const { previewPdf, loading: isExporting } = useOrdersPdfPreview(
    (msg) => showToast(msg, "error"),
  );

  const handleExportDocument = () => {
    if (!routePlan) return;
    previewPdf({
      deliveryDateIso: convertDateToISO(routePlan.delivery_date),
      timeSlotId: routePlan.time_slot_id,
    });
  };

  if (!routePlan || points.length === 0) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 px-6">
        <svg className="h-16 w-16 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        <p className="text-lg font-medium text-slate-500">{routePlan ? "Маршрут порожній" : "Маршрут не знайдено"}</p>
        <button
          type="button"
          onClick={() => navigate("/routes")}
          className="rounded-md bg-blue-600 px-5 py-2.5 font-medium text-white transition-colors hover:bg-blue-700"
        >
          До списку маршрутів
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-dvh flex-col bg-white md:h-screen">
      <RouteDetailHeader
        routePlan={routePlan}
        pointCount={points.length}
        showList={showList}
        canEdit={canEdit}
        isExporting={isExporting}
        onToggleList={toggleList}
        onBack={() => navigate("/routes")}
        onReverseRoute={handleReverseRoute}
        onExportDocument={handleExportDocument}
      />

      <div className="flex min-h-0 flex-1 flex-col md:flex-row">
        <RouteStopsList
          points={points}
          canEdit={canEdit}
          dragIndex={dragIndex}
          overIndex={overIndex}
          editingOrderId={editingOrderId}
          showList={showList}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onDragEnd={handleDragEnd}
          onMovePoint={movePoint}
          onToggleEditMarker={toggleEditMarker}
          onReorder={reorderByIndex}
        />

        {/* Map */}
        <div className={`${!showList ? "flex" : "hidden"} relative min-h-0 flex-1 md:flex`}>
          {editingOrderId && (
            <div className="absolute left-1/2 top-3 z-[1000] flex -translate-x-1/2 items-center gap-2 rounded-full bg-amber-500 px-4 py-2 text-sm font-medium text-white shadow-lg">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Натисніть на карту для нової позиції
              <button
                title="cancelButton"
                type="button"
                onClick={cancelEditMarker}
                className="ml-1 flex h-5 w-5 items-center justify-center rounded-full bg-white/20 hover:bg-white/30"
              >
                <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          )}
          <RouteMap
            points={pointsWithCoords}
            editingOrderId={editingOrderId}
            onMarkerMove={handleMarkerMove}
          />
        </div>
      </div>
      {/* Spacer for bottom nav on mobile */}
      <div className="h-20 shrink-0 md:hidden" />

      {toast.isVisible && (
        <Toast message={toast.message} type={toast.type} onClose={hideToast} />
      )}
    </div>
  );
};
