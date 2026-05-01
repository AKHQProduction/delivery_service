import React from "react";
import { type Product } from "../../types/entities/Product";

interface ProductCardProps {
  product: Product;
  onClick: (product: Product) => void;
  onEdit?: (product: Product) => void;
  onDelete?: (product: Product) => void;
}

const getCategoryTone = (categoryName?: string) => {
  const normalized = categoryName?.toLowerCase() ?? "";

  if (normalized.includes("облад")) {
    return "bg-orange-50 text-orange-700";
  }

  if (normalized.includes("супут")) {
    return "bg-violet-50 text-violet-700";
  }

  return "bg-blue-50 text-blue-700";
};

const formatPrice = (price: Product["price"] | null | undefined) => {
  const numericPrice = Number(price);
  return Number.isFinite(numericPrice) ? `${numericPrice.toLocaleString("uk-UA")} ₴` : "—";
};

export const ProductCard: React.FC<ProductCardProps> = ({ product, onClick, onEdit, onDelete }) => {
  const categoryName = product.category_name || "Без категорії";

  return (
    <div
      onClick={() => onClick(product)}
      className="cursor-pointer rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-colors hover:border-blue-200 hover:bg-blue-50/30"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="text-base font-semibold leading-6 text-slate-950">{product.name}</h3>
          <span
            className={`mt-2 inline-flex rounded px-2 py-1 text-xs font-medium leading-4 ${getCategoryTone(
              categoryName,
            )}`}
          >
            {categoryName}
          </span>
          <p className="mt-3 text-lg font-semibold leading-7 text-slate-950">
            {formatPrice(product.price)}
          </p>
        </div>

        {(onEdit || onDelete) && (
          <div className="flex shrink-0 items-center gap-2 pt-8">
            {onEdit && (
              <button
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  onEdit(product);
                }}
                className="rounded-md p-2 text-slate-700 hover:bg-slate-100"
                aria-label="Редагувати товар"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125"
                  />
                </svg>
              </button>
            )}
            {onDelete && (
              <button
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  onDelete(product);
                }}
                className="rounded-md p-2 text-red-600 hover:bg-red-50"
                aria-label="Видалити товар"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.68.107 1.022.166m-1.022-.165L18.16 19.673A2.25 2.25 0 0 1 15.916 21H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
                  />
                </svg>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
