import React, { useState } from "react";
import { type RoutePoint } from "../../types/entities/Route";

interface RouteStopItemProps {
  point: RoutePoint;
  index: number;
  totalCount: number;
  canEdit: boolean;
  isDragging: boolean;
  isOver: boolean;
  isEditingMarker: boolean;
  onDragStart: (index: number) => void;
  onDragOver: (e: React.DragEvent, index: number) => void;
  onDrop: (index: number) => void;
  onDragEnd: () => void;
  onMoveUp: (index: number) => void;
  onMoveDown: (index: number) => void;
  onToggleEditMarker: (orderId: string) => void;
  onReorder: (fromIndex: number, toIndex: number) => void;
}

export const RouteStopItem: React.FC<RouteStopItemProps> = ({
  point,
  index,
  totalCount,
  canEdit,
  isDragging,
  isOver,
  isEditingMarker,
  onDragStart,
  onDragOver,
  onDrop,
  onDragEnd,
  onMoveUp,
  onMoveDown,
  onToggleEditMarker,
  onReorder,
}) => {
  const [editingNumber, setEditingNumber] = useState(false);
  const [inputValue, setInputValue] = useState("");

  const handleNumberSubmit = () => {
    const newPos = parseInt(inputValue, 10) - 1;
    setEditingNumber(false);
    if (isNaN(newPos) || newPos < 0 || newPos >= totalCount || newPos === index) return;
    onReorder(index, newPos);
  };
  return (
    <div
      draggable={canEdit}
      onDragStart={canEdit ? () => onDragStart(index) : undefined}
      onDragOver={canEdit ? (e) => onDragOver(e, index) : undefined}
      onDrop={canEdit ? () => onDrop(index) : undefined}
      onDragEnd={canEdit ? onDragEnd : undefined}
      className={`rounded-lg border bg-white transition-all ${
        isDragging ? "opacity-40" : ""
      } ${isOver ? "border-blue-400 ring-2 ring-blue-100" : "border-slate-200"}`}
    >
      <div className="flex items-start gap-3 p-3">
        <div className="flex shrink-0 flex-col items-center gap-1 pt-0.5">
          {canEdit && editingNumber ? (
            <input
              type="number"
              min={1}
              max={totalCount}
              title="Позиція в маршруті"
              autoFocus
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleNumberSubmit();
                if (e.key === "Escape") setEditingNumber(false);
              }}
              onBlur={handleNumberSubmit}
              className="h-8 w-8 rounded-full bg-blue-600 text-center text-sm font-bold text-white outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
            />
          ) : (
            <button
              type="button"
              onClick={
                canEdit
                  ? () => {
                      setInputValue(String(index + 1));
                      setEditingNumber(true);
                    }
                  : undefined
              }
              className={`flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white ${canEdit ? "hover:bg-blue-700" : "cursor-default"}`}
              title={canEdit ? "Змінити позицію" : undefined}
              aria-label={`Зупинка ${index + 1}`}
            >
              {index + 1}
            </button>
          )}
          {canEdit && (
            <svg
              className="h-4 w-4 cursor-grab text-slate-300 active:cursor-grabbing"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M8 6h2v2H8V6zm6 0h2v2h-2V6zM8 11h2v2H8v-2zm6 0h2v2h-2v-2zm-6 5h2v2H8v-2zm6 0h2v2h-2v-2z" />
            </svg>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-slate-950">{point.client_name}</p>
              <p className="mt-0.5 truncate text-sm text-slate-500">{point.address}</p>
            </div>
            <span className="shrink-0 text-sm font-semibold text-slate-950">
              {point.total_price} ₴
            </span>
          </div>
          {point.delivery_phone && (
            <p className="mt-1 truncate text-xs text-slate-500">{point.delivery_phone}</p>
          )}
          {point.comment && (
            <p className="mt-2 rounded-md bg-amber-50 px-2 py-1 text-xs text-amber-700">
              {point.comment}
            </p>
          )}
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
              {point.items_summary}
            </span>
            <span className="rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
              {point.payment_method}
            </span>
          </div>
        </div>

        {canEdit && (
          <div className="flex shrink-0 flex-col gap-1">
            {index > 0 && (
              <button
                type="button"
                title="Вгору"
                onClick={() => onMoveUp(index)}
                className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-100 transition-colors hover:bg-slate-200 md:hidden"
                aria-label="Перемістити вище"
              >
                <svg
                  className="h-4 w-4 text-slate-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 15l7-7 7 7"
                  />
                </svg>
              </button>
            )}
            {index < totalCount - 1 && (
              <button
                type="button"
                title="Вниз"
                onClick={() => onMoveDown(index)}
                className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-100 transition-colors hover:bg-slate-200 md:hidden"
                aria-label="Перемістити нижче"
              >
                <svg
                  className="h-4 w-4 text-slate-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
            )}
            <button
              type="button"
              onClick={() => onToggleEditMarker(point.order_id)}
              title="Редагувати маркер"
              className={`flex h-8 w-8 items-center justify-center rounded-md transition-colors ${
                isEditingMarker
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
              aria-label="Редагувати маркер"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
