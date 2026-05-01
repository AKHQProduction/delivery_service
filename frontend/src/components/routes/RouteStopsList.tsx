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
  onReorder: (fromIndex: number, toIndex: number) => void;
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
  onReorder,
}) => {
  return (
    <div className={`${showList ? "flex" : "hidden"} min-h-0 w-full flex-col overflow-hidden border-r border-slate-200 bg-slate-50 md:flex md:w-80 md:shrink-0 lg:w-96`}>
      <div className="border-b border-slate-200 bg-white px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Порядок зупинок</p>
        {canEdit && (
          <p className="mt-0.5 text-xs text-slate-400">Перетягніть або натисніть на номер для зміни порядку</p>
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
            onReorder={onReorder}
          />
        ))}
        {/* Drop zone for dropping after the last item */}
        {canEdit && dragIndex !== null && (
          <div
            className="min-h-16 flex-1"
            onDragOver={(e) => { e.preventDefault(); onDragOver(e, points.length); }}
            onDrop={() => onDrop(points.length)}
          >
            <div className={`mx-4 h-0.5 transition-colors ${overIndex === points.length ? "bg-blue-600" : "bg-transparent"}`} />
          </div>
        )}
      </div>
    </div>
  );
};
