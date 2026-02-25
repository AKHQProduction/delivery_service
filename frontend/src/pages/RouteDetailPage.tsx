import { useNavigate, useLocation } from "react-router-dom";
import { type RoutePlan } from "../types/entities/Route";
import { useRouteDetail } from "../hooks/routes/useRouteDetail";
import { RouteDetailHeader } from "../components/routes/RouteDetailHeader";
import { RouteStopsList } from "../components/routes/RouteStopsList";
import { RouteMap } from "../components/routes/RouteMap";

export const RouteDetailPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const routePlan = (location.state as { routePlan?: RoutePlan })?.routePlan ?? null;

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
  } = useRouteDetail(routePlan);

  if (!routePlan) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 px-6">
        <p className="text-gray-500 text-lg">Маршрут не знайдено</p>
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
    <div className="flex flex-col h-[100dvh] md:h-screen bg-white">
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
            encodedPolyline={routePlan.geometry?.encoded_polyline}
            editingOrderId={editingOrderId}
            onMarkerMove={handleMarkerMove}
          />
        </div>
      </div>
    </div>
  );
};
