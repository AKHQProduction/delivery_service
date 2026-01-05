import { useEffect, useState, useRef, useCallback } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { ProductCard } from "../components/ui/productCard";
import { ProductDetailModal } from "../components/modals/detailsModals/ProductDetailModal";
import { RightModal } from "../components/modals/RightModal";
import { CategoryManagementModal } from "../components/features/addCategoryComponent";
import { useProducts } from "../hooks/products/useProducts";
import { useCategories } from "../hooks/products/useCategories";
import { getProductById } from "../services/api/productApi";
import { type Product } from "../types/entities/Product";

export const ProductPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);

  const {
    getProducts,
    deleteProduct,
    updateProduct,
    products,
    loadMoreProducts,
    loadingMore,
    hasMore,
  } = useProducts();
  const {
    categories,
    fetchCategories,
    addCategory,
    updateCategory,
    deleteCategory,
  } = useCategories();
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const initialLoadRef = useRef(false);

  // Initial load - runs only once
  useEffect(() => {
    if (initialLoadRef.current) return;
    initialLoadRef.current = true;

    const initProducts = async () => {
      await getProducts();
      await fetchCategories();

      const openProductId = sessionStorage.getItem("openProductId");
      if (openProductId) {
        try {
          const product = await getProductById(openProductId);
          console.log("Fetched product for modal:", product);
          setSelectedProduct(product);
          setIsModalOpen(true);
        } catch (e) {
          console.error("Failed to fetch product by ID");
        }
        sessionStorage.removeItem("openProductId");
      }
    };
    initProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  // Search effect - only runs when searchTerm changes
  useEffect(() => {
    // Skip initial mount when searchTerm is empty

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      getProducts(searchTerm);
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm]); // Only depend on searchTerm

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      if (entry.isIntersecting && hasMore && !loadingMore) {
        loadMoreProducts();
      }
    },
    [hasMore, loadingMore, loadMoreProducts]
  );

  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(handleObserver, {
      root: null,
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

  const handleProductClick = (product: Product) => {
    setSelectedProduct(product);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedProduct(null), 300);
  };

  const handleSave = async (updatedProduct: Product) => {
    await updateProduct(
      updatedProduct.product_id,
      updatedProduct.name,
      updatedProduct.price,
      updatedProduct.category_id
    );
    await getProducts();

    const categoryName = categories.find(
      (cat) => cat.category_id === updatedProduct.category_id
    )?.name;

    setSelectedProduct({
      category_name: categoryName || "Без категорії",
      ...updatedProduct,
    });
  };

  const handleDelete = async () => {
    if (selectedProduct) {
      await deleteProduct(selectedProduct.product_id);
      handleCloseModal();
      getProducts(searchTerm);
    }
  };

  // Transform categories for modal
  const transformedCategories = categories.map((cat) => ({
    id: cat.category_id,
    name: cat.name,
    emoji: "📁",
  }));

  const handleAddCategory = async (name: string) => {
    try {
      await addCategory(name);
      await fetchCategories();
    } catch (error) {
      console.error("Failed to add category:", error);
    }
  };

  const handleUpdateCategory = async (id: string, name: string) => {
    try {
      await updateCategory(id, name);
      await fetchCategories();
      await getProducts(searchTerm);
    } catch (error) {
      console.error("Failed to update category:", error);
    }
  };

  const handleDeleteCategory = async (id: string) => {
    try {
      await deleteCategory(id);
      await fetchCategories();
      await getProducts(searchTerm);
    } catch (error) {
      console.error("Failed to delete category:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <PageHeader title="Товари" />

      <div className="px-6 pb-4">
        <SearchBar
          placeholder="Пошук товарів"
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
        />
      </div>

      {products.length === 0 ? (
        <div className="flex flex-col items-center justify-center mt-20">
          <svg
            className="w-16 h-16 mx-auto mb-4 text-gray-300"
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
          <p className="text-gray-500 text-lg font-medium">
            {searchTerm ? "Товари не знайдено" : "Товари відсутні"}
          </p>
          {searchTerm && (
            <p className="text-gray-400 text-sm mt-2">
              Спробуйте інший пошуковий запит
            </p>
          )}
        </div>
      ) : (
        <div className="px-6 pb-24">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onClick={() => handleProductClick(product)}
              />
            ))}
          </div>

          <div ref={loadMoreRef} className="py-4 flex justify-center">
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
                <span>Завантаження...</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Floating Action Buttons */}
      <div className="fixed bottom-27 right-6 flex flex-col gap-3">
        {/* Category Management Button */}
        <button
          onClick={() => setIsCategoryModalOpen(true)}
          className="relative w-14 h-14 bg-gray-700 hover:bg-gray-800 active:bg-gray-900 rounded-full flex items-center justify-center shadow-lg transition-all duration-200 hover:shadow-xl transform hover:scale-105 active:scale-95"
          aria-label="Manage Categories"
        >
          <svg
            className="w-6 h-6 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
            />
          </svg>
        </button>

        <div className="relative">
          <div className="absolute inset-0 bg-indigo-600 rounded-full animate-ping-slow opacity-75"></div>
          <button
            onClick={() => {
              /* your add handler */
            }}
            className="relative w-14 h-14 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 rounded-full flex items-center justify-center shadow-lg transition-all duration-200 hover:shadow-xl transform hover:scale-105 active:scale-95"
            aria-label="Add"
          >
            <svg
              className="w-7 h-7 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              strokeWidth={2.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 4v16m8-8H4"
              />
            </svg>
          </button>
        </div>
      </div>

      <RightModal isOpen={isModalOpen} onClose={handleCloseModal}>
        {selectedProduct && (
          <ProductDetailModal
            product={selectedProduct}
            onClose={handleCloseModal}
            onDelete={handleDelete}
            onSave={handleSave}
          />
        )}
      </RightModal>

      <CategoryManagementModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        categories={transformedCategories}
        onAddCategory={handleAddCategory}
        onUpdateCategory={handleUpdateCategory}
        onDeleteCategory={handleDeleteCategory}
      />
    </div>
  );
};
