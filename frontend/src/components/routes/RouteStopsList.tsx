import React from "react";
import { type RoutePoint } from "../../types/entities/Route";
import { RouteStopItem } from "./RouteStopItem";

interface RouteStopsListProps {
  points: RoutePoint[];
  canEdit: boolean;
  dragIndex: number | null;
  overIndex: number | null;
  editingOrderId: string | null;
  showList: boolean;
  onDragStart: (index: number) => void;
  onDragOver: (e: React.DragEvent, index: number) => void;
  onDrop: (index: number) => void;
  onDragEnd: () => void;
  onMovePoint: (from: number, direction: "up" | "down") => void;
  onToggleEditMarker: (orderId: string) => void;
}

export const RouteStopsList: React.FC<RouteStopsListProps> = ({
  points,
  canEdit,
  dragIndex,
  overIndex,
  editingOrderId,
  showList,
  onDragStart,
  onDragOver,
  onDrop,
  onDragEnd,
  onMovePoint,
  onToggleEditMarker,
}) => {
  return (
    <div className={`${showList ? "flex" : "hidden"} md:flex flex-col w-full md:w-80 lg:w-96 border-r border-gray-200 bg-gray-50 min-h-0 md:shrink-0 overflow-hidden`}>
      <div className="px-4 py-3 border-b border-gray-200 bg-white">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Порядок зупинок</p>
        {canEdit && (
          <p className="text-xs text-gray-400 mt-0.5">Перетягніть для зміни порядку</p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {points.map((point, index) => (
          <RouteStopItem
            key={point.order_id}
            point={point}
            index={index}
            totalCount={points.length}
            canEdit={canEdit}
            isDragging={dragIndex === index}
            isOver={overIndex === index && dragIndex !== index}
            isEditingMarker={editingOrderId === point.order_id}
            onDragStart={onDragStart}
            onDragOver={onDragOver}
            onDrop={onDrop}
            onDragEnd={onDragEnd}
            onMoveUp={(i) => onMovePoint(i, "up")}
            onMoveDown={(i) => onMovePoint(i, "down")}
            onToggleEditMarker={onToggleEditMarker}
          />
        ))}
        {/* Drop zone for dropping after the last item */}
        {canEdit && dragIndex !== null && (
          <div
            className="min-h-16 flex-1"
            onDragOver={(e) => { e.preventDefault(); onDragOver(e, points.length); }}
            onDrop={() => onDrop(points.length)}
          >
            <div className={`h-0.5 mx-4 transition-colors ${overIndex === points.length ? "bg-indigo-500" : "bg-transparent"}`} />
          </div>
        )}
      </div>
    </div>
  );
};
