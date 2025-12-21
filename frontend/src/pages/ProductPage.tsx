import { useEffect, useState, useRef, useCallback } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { ProductCard } from "../components/ui/productCard";
import { ProductDetailModal } from "../components/modals/detailsModals/ProductDetailModal";
import { RightModal } from "../components/modals/RightModal";
import { useProducts } from "../hooks/useProducts";
import { getProductById } from "../services/api/productApi";
import { reverseCategoryMap } from "../utils/dataMap";
import { type Product } from "../types/entities/Product";

export const ProductPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { getProducts, deleteProduct, updateProduct, products, loadMoreProducts, loadingMore, hasMore } = useProducts();
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const initProducts = async () => {
      await getProducts();

      const openProductId = sessionStorage.getItem("openProductId");
      if (openProductId) {
        try {
          const product = await getProductById(openProductId);
          setSelectedProduct(product);
          setIsModalOpen(true);
        } catch (e) {
          console.error("Failed to fetch product by ID");
        }
        sessionStorage.removeItem("openProductId");
      }
    };
    initProducts();
  }, []);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      getProducts(searchTerm);
    }, 100);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [searchTerm]);

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
    const reverseCategory = reverseCategoryMap[updatedProduct.category];
    await updateProduct(
      updatedProduct.product_id,
      updatedProduct.name,
      updatedProduct.price,
      reverseCategory
    );
    await getProducts();
    setSelectedProduct({
      ...updatedProduct,
      category: reverseCategory,
    });
  };

  const handleDelete = async () => {
    if (selectedProduct) {
      await deleteProduct(selectedProduct.product_id);
      handleCloseModal();
      getProducts();
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
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Завантаження...</span>
              </div>
            )}
          </div>
        </div>
      )}
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
    </div>
  );
};