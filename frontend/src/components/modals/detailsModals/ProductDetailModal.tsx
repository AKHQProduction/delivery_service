import React from "react";
import { type Product, type transformedCategories } from "../../../types/entities/Product";

interface ProductDetailModalProps {
  product: Product;
  categories: transformedCategories[];
  onClose: () => void;
  onDelete: () => void;
  onEdit: () => void;
}

const formatPrice = (price: number) => `${price.toLocaleString("uk-UA")} ₴`;

export const ProductDetailModal: React.FC<ProductDetailModalProps> = ({
  product,
  onClose,
  onDelete,
  onEdit,
}) => {
  return (
    <div className="flex h-full flex-col bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5">
        <h1 className="text-xl font-semibold text-slate-950">{product.name}</h1>
        <button
          onClick={onClose}
          type="button"
          className="rounded-md p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-950"
          aria-label="Закрити"
        >
          <CloseIcon className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <dl className="divide-y divide-slate-200 rounded-lg border border-slate-200 text-sm">
          <div className="flex items-center justify-between gap-4 px-4 py-4">
            <dt className="text-slate-500">Категорія</dt>
            <dd className="font-medium text-slate-950">
              {product.category_name || "Без категорії"}
            </dd>
          </div>
          <div className="flex items-center justify-between gap-4 px-4 py-4">
            <dt className="text-slate-500">Ціна</dt>
            <dd className="font-medium text-slate-950">{formatPrice(product.price)}</dd>
          </div>
        </dl>
      </div>

      <div className="space-y-3 border-t border-slate-200 px-6 py-5">
        <button
          type="button"
          onClick={onEdit}
          className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-md border border-slate-300 bg-white text-sm font-medium text-slate-950 hover:bg-slate-100"
        >
          <EditIcon className="h-5 w-5" />
          Редагувати
        </button>
        <button
          type="button"
          onClick={onDelete}
          className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-md border border-red-300 bg-white text-sm font-medium text-red-600 hover:bg-red-50"
        >
          <TrashIcon className="h-5 w-5" />
          Видалити
        </button>
      </div>
    </div>
  );
};

const CloseIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18 18 6M6 6l12 12" />
  </svg>
);

const EditIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125"
    />
  </svg>
);

const TrashIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.68.107 1.022.166m-1.022-.165L18.16 19.673A2.25 2.25 0 0 1 15.916 21H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
    />
  </svg>
);
