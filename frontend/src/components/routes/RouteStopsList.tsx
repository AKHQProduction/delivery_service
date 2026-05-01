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
  const totalAmount = points.reduce((sum, point) => sum + point.total_price, 0);

  return (
    <div
      className={`${showList ? "flex" : "hidden"} min-h-0 w-full flex-col overflow-hidden border-r border-slate-200 bg-slate-50 md:flex md:w-[23rem] md:shrink-0 lg:w-[26rem]`}
    >
      <div className="border-b border-slate-200 bg-white px-4 py-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-base font-semibold text-slate-950">Порядок зупинок</p>
            <p className="mt-1 text-sm text-slate-500">
              {points.length} адрес · {totalAmount} ₴
            </p>
          </div>
          <span className="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
            {canEdit ? "Редагування" : "Перегляд"}
          </span>
        </div>
        {canEdit && (
          <p className="mt-3 rounded-md bg-blue-50 px-3 py-2 text-xs text-blue-700">
            Перетягніть зупинку або натисніть на номер, щоб змінити порядок.
          </p>
        )}
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto p-3">
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
            className="min-h-12 flex-1"
            onDragOver={(e) => {
              e.preventDefault();
              onDragOver(e, points.length);
            }}
            onDrop={() => onDrop(points.length)}
          >
            <div
              className={`h-0.5 transition-colors ${overIndex === points.length ? "bg-blue-600" : "bg-transparent"}`}
            />
          </div>
        )}
      </div>
    </div>
  );
};
