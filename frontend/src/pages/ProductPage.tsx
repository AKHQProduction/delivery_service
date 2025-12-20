import { useEffect, useState, useRef } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { ProductCard } from "../components/ui/productCard";
import { ProductDetailModal } from "../components/modals/detailsModals/ProductDetailModal";
import { RightModal } from "../components/modals/RightModal";
import { useProducts } from "../hooks/useProducts";
import { reverseCategoryMap } from "../utils/dataMap";
import { type Product } from "../types/entities/Product";

export const ProductPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { getProducts, deleteProduct, updateProduct, products } = useProducts();
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    getProducts();
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
    // Update selectedProduct with the new data (use backend category format)
    setSelectedProduct({
      ...updatedProduct,
      category: reverseCategory,
    });
  };

  const handleDelete = () => {
    console.log("Delete product:", selectedProduct);
    deleteProduct(selectedProduct!.product_id);
    window.location.reload(); //TEMPORARY SOLUTION
    handleCloseModal();
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
