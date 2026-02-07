import React, { useRef, useEffect, useCallback } from "react";
import { type Product } from "../../../../types/entities/Product";
import { SearchBar } from "../../../ui/SearchBar";

interface SelectedProduct {
  product: Product;
  quantity: number;
}

interface ProductSelectionStepProps {
  products: Product[];
  selectedProducts: SelectedProduct[];
  searchValue: string;
  onSearchChange: (value: string) => void;
  onProductToggle: (product: Product) => void;
  onQuantityChange: (productId: string, quantity: number) => void;
  loadMore?: () => void;
  loadingMore?: boolean;
  hasMore?: boolean;
}

export const ProductSelectionStep: React.FC<ProductSelectionStepProps> = ({
  products,
  selectedProducts,
  searchValue,
  onSearchChange,
  onProductToggle,
  onQuantityChange,
  loadMore,
  loadingMore,
  hasMore,
}) => {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      if (entry.isIntersecting && hasMore && !loadingMore && loadMore) {
        loadMore();
      }
    },
    [hasMore, loadingMore, loadMore],
  );

  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(handleObserver, {
      root: scrollContainerRef.current,
      rootMargin: "100px",
      threshold: 0,
    });

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [handleObserver]);

  const totalSelectedItems = selectedProducts.reduce((sum, p) => sum + p.quantity, 0);

  const totalAmount = selectedProducts.reduce((sum, p) => sum + p.product.price * p.quantity, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-gray-900">Вибір товарів</h3>
        {selectedProducts.length > 0 && (
          <div className="text-sm">
            <span className="font-semibold text-indigo-600">{selectedProducts.length}</span>
            <span className="text-gray-600"> товарів</span>
            <span className="mx-1 text-gray-400">•</span>
            <span className="font-semibold text-indigo-600">{totalSelectedItems}</span>
            <span className="text-gray-600"> шт.</span>
          </div>
        )}
      </div>

      <SearchBar
        searchTerm={searchValue}
        setSearchTerm={onSearchChange}
        placeholder="Пошук товару..."
      />

      <div ref={scrollContainerRef} className="space-y-2 max-h-96 overflow-y-auto">
        {products.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <svg
              className="w-12 h-12 mx-auto mb-3 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
            <p className="font-medium">Товарів не знайдено</p>
            <p className="text-sm">Спробуйте інший пошуковий запит</p>
          </div>
        ) : (
          <>
            {products.map((product) => {
              const selected = selectedProducts.find(
                (p) => p.product.product_id === product.product_id,
              );
              return (
                <div
                  key={product.product_id}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selected
                      ? "border-indigo-600 bg-indigo-50"
                      : "border-gray-200 hover:border-indigo-300 bg-white"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-gray-900 truncate">{product.name}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-base font-bold text-indigo-600">
                          {product.price} ₴
                        </span>
                      </div>
                    </div>

                    {selected ? (
                      <div className="flex items-center  shrink-0">
                        <button
                          onClick={() => {
                            if (selected.quantity <= 1) {
                              onProductToggle(product);
                            } else {
                              onQuantityChange(product.product_id, selected.quantity - 1);
                            }
                          }}
                          type="button"
                          className="w-9 h-9 rounded-lg bg-gray-200 hover:bg-gray-300 flex items-center justify-center transition-colors font-bold text-lg"
                        >
                          −
                        </button>
                        <div className="w-14 text-center">
                          <span className="text-lg font-bold text-gray-900">
                            {selected.quantity}
                          </span>
                        </div>
                        <button
                          onClick={() =>
                            onQuantityChange(product.product_id, selected.quantity + 1)
                          }
                          type="button"
                          className="w-9 h-9 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center transition-colors font-bold text-lg"
                        >
                          +
                        </button>
                        <button
                          title="remove"
                          onClick={() => onProductToggle(product)}
                          type="button"
                          className="ml-2 w-9 h-9 rounded-lg bg-red-100 hover:bg-red-200 text-red-600 flex items-center justify-center transition-colors"
                        >
                          <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                            />
                          </svg>
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => onProductToggle(product)}
                        type="button"
                        className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                      >
                        <svg
                          className="w-5 h-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 4v16m8-8H4"
                          />
                        </svg>
                        Додати
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
            <div ref={loadMoreRef} className="py-2 flex justify-center">
              {loadingMore && (
                <div className="flex items-center gap-2 text-gray-500">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  <span className="text-sm">Завантаження...</span>
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {selectedProducts.length > 0 && (
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between p-4 bg-indigo-50 rounded-xl">
            <div>
              <div className="text-sm text-gray-600">Всього до сплати</div>
              <div className="text-2xl font-bold text-indigo-600">{totalAmount} ₴</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600">Обрано товарів</div>
              <div className="text-xl font-bold text-gray-900">{totalSelectedItems} шт.</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
