import { useNavigate, useLocation } from "react-router-dom";
import { type RoutePlan } from "../types/entities/Route";
import { useRouteDetail } from "../hooks/routes/useRouteDetail";
import { RouteDetailHeader } from "../components/routes/RouteDetailHeader";
import { RouteStopsList } from "../components/routes/RouteStopsList";
import { RouteMap } from "../components/routes/RouteMap";

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
  } = useRouteDetail(routePlan, timeSlotId);

  if (!routePlan || points.length === 0) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 px-6">
        <svg className="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        <p className="text-gray-500 text-lg">{routePlan ? "Маршрут порожній" : "Маршрут не знайдено"}</p>
        <button
          type="button"
          onClick={() => navigate("/routes")}
          className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors"
        >
          До списку маршрутів
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-dvh md:h-screen bg-white">
      <RouteDetailHeader
        routePlan={routePlan}
        pointCount={points.length}
        showList={showList}
        onToggleList={toggleList}
        onBack={() => navigate("/routes")}
      />

      <div className="flex-1 min-h-0 flex flex-col md:flex-row">
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
        />

        {/* Map */}
        <div className={`${!showList ? "flex" : "hidden"} md:flex flex-1 min-h-0 relative`}>
          {editingOrderId && (
            <div className="absolute top-3 left-1/2 -translate-x-1/2 z-[1000] bg-amber-500 text-white text-sm font-medium px-4 py-2 rounded-full shadow-lg flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                className="ml-1 w-5 h-5 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    </div>
  );
};
