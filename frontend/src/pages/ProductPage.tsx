import { useEffect, useMemo, useRef, useState } from "react";
import { ProductCard } from "../components/ui/ProductCard";
import { ProductDetailModal } from "../components/modals/detailsModals/ProductDetailModal";
import { DetailModal } from "../components/modals/DetailModal";
import { Modal } from "../components/modals/Modal";
import { CategoryManagementModal } from "../components/features/AddCategoryComponent";
import { AddProductForm } from "../components/forms/products/AddProductForm";
import { EditProductForm } from "../components/forms/products/EditProductForm";
import { useProducts } from "../hooks/products/useProducts";
import { useCategories } from "../hooks/products/useCategories";
import { getProductById } from "../services/api/productApi";
import { type Product } from "../types/entities/Product";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";
import {
  ProductCardSkeleton,
  SidePanelSkeleton,
  SkeletonBlock,
  TableSkeleton,
} from "../components/ui/Skeleton";

const getCategoryName = (product: Product) => product.category_name || "Без категорії";

const getCategoryTone = (categoryName: string) => {
  const normalized = categoryName.toLowerCase();

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

export const ProductPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [productPendingDelete, setProductPendingDelete] = useState<Product | null>(null);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>("all");

  const {
    getProducts,
    deleteProduct,
    updateProduct,
    products,
    loadMoreProducts,
    loading,
    loadingMore,
    hasMore,
  } = useProducts();
  const {
    categories,
    isLoaded: categoriesLoaded,
    fetchCategories,
    addCategory,
    updateCategory,
    deleteCategory,
  } = useCategories();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const initialLoadRef = useRef(false);

  const { sentinelRef } = useInfiniteScroll({
    onLoadMore: loadMoreProducts,
    hasMore,
    isLoading: loadingMore,
  });

  useEffect(() => {
    if (initialLoadRef.current) return;
    initialLoadRef.current = true;

    const initProducts = async () => {
      await getProducts();
      await fetchCategories();

      const openProductId = sessionStorage.getItem("openProductId");
      if (openProductId) {
        try {
          const product = (await getProductById(openProductId)) as Product;
          setSelectedProduct(product);
          setIsProductModalOpen(true);
        } catch {
          console.error("Failed to fetch product by ID");
        }
        sessionStorage.removeItem("openProductId");
      }
    };
    initProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
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
  }, [searchTerm]);

  const categoryChips = useMemo(() => {
    const counts = products.reduce<Record<string, number>>((acc, product) => {
      if (product.category_id) {
        acc[product.category_id] = (acc[product.category_id] ?? 0) + 1;
      }
      return acc;
    }, {});

    return [
      { key: "all", id: "all", name: "Усі", count: products.length },
      ...categories.map((category, index) => ({
        key: category.category_id || `${category.name}-${index}`,
        id: category.category_id || `${category.name}-${index}`,
        name: category.name,
        count: counts[category.category_id] ?? 0,
      })),
    ];
  }, [categories, products]);

  const visibleProducts = useMemo(() => {
    if (selectedCategoryId === "all") {
      return products;
    }

    return products.filter((product) => product.category_id === selectedCategoryId);
  }, [products, selectedCategoryId]);

  useEffect(() => {
    if (selectedProduct) {
      const updatedSelection = products.find(
        (product) => product.product_id === selectedProduct.product_id,
      );

      if (updatedSelection) {
        setSelectedProduct(updatedSelection);
      }
    } else if (visibleProducts.length > 0) {
      setSelectedProduct(visibleProducts[0]);
    }
  }, [products, selectedProduct, visibleProducts]);

  const transformedCategories = [
    {
      id: null,
      name: "Без категорії",
    },
    ...categories.map((cat) => ({
      id: cat.category_id,
      name: cat.name,
    })),
  ];

  const openProductDetail = (product: Product) => {
    setSelectedProduct(product);
    setIsProductModalOpen(true);
  };

  const openProductEditor = (product: Product) => {
    setSelectedProduct(product);
    setIsProductModalOpen(false);
    setIsEditModalOpen(true);
  };

  const handleCloseProductModal = () => {
    setIsProductModalOpen(false);
  };

  const handleSave = async (updatedProduct: Product) => {
    const updateData: {
      name: string;
      price: number;
      category_id?: string;
    } = {
      name: updatedProduct.name,
      price: updatedProduct.price,
    };

    if (updatedProduct.category_id) {
      updateData.category_id = updatedProduct.category_id;
    }

    await updateProduct(
      updatedProduct.product_id,
      updateData.name,
      updateData.price,
      updateData.category_id ?? "",
    );
    await getProducts(searchTerm);
    await fetchCategories();

    const categoryName = updatedProduct.category_id
      ? categories.find((cat) => cat.category_id === updatedProduct.category_id)?.name ||
        "Без категорії"
      : "Без категорії";

    setSelectedProduct({
      ...updatedProduct,
      category_name: categoryName,
    });
  };

  const requestDeleteProduct = (product: Product) => {
    setProductPendingDelete(product);
  };

  const confirmDeleteProduct = async () => {
    if (!productPendingDelete) return;

    const product = productPendingDelete;
    await deleteProduct(product.product_id);
    if (selectedProduct?.product_id === product.product_id) {
      setSelectedProduct(null);
      setIsProductModalOpen(false);
      setIsEditModalOpen(false);
    }
    setProductPendingDelete(null);
    await getProducts(searchTerm);
  };

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
      if (selectedCategoryId === id) {
        setSelectedCategoryId("all");
      }
    } catch (error) {
      console.error("Failed to delete category:", error);
    }
  };

  const handleProductCreated = async (productId?: string) => {
    setIsAddModalOpen(false);
    const refreshedProducts = await getProducts(searchTerm);
    await fetchCategories();

    if (productId) {
      const createdProduct = refreshedProducts.find((product) => product.product_id === productId);
      setSelectedProduct(createdProduct ?? null);
    }
  };

  const handleProductEdited = async (updatedProduct: Product) => {
    await handleSave(updatedProduct);
    setIsEditModalOpen(false);
  };

  const emptyTitle = searchTerm ? "Товари не знайдено" : "Товарів поки немає";
  const emptyDescription = searchTerm
    ? "Спробуйте інший пошуковий запит або змініть категорію."
    : "Додайте перший товар, щоб почати роботу.";
  const isInitialLoading = (loading && products.length === 0) || !categoriesLoaded;

  return (
    <div className="min-h-screen bg-slate-50 px-4 pb-28 pt-6 sm:px-6 md:px-8 md:pb-10">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-semibold leading-8 text-slate-950">Товари</h1>
          <span className="rounded bg-slate-100 px-2 py-1 text-sm font-medium leading-5 text-slate-500">
            {products.length}
          </span>
        </div>

        <div className="grid grid-cols-[1fr_auto_auto] gap-2 md:flex md:min-w-[680px] md:justify-end">
          <div className="hidden md:block md:w-80 lg:w-[420px]">
            <ProductSearchInput searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
          </div>
          <button
            type="button"
            onClick={() => setIsCategoryModalOpen(true)}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 text-sm font-medium text-slate-950 hover:bg-slate-100 md:px-4"
          >
            <FolderIcon className="h-5 w-5 text-slate-700" />
            <span>Категорії</span>
          </button>
          <button
            type="button"
            onClick={() => setIsAddModalOpen(true)}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-blue-600 px-3 text-sm font-medium text-white hover:bg-blue-700 md:px-4"
          >
            <PlusIcon className="h-5 w-5" />
            <span className="hidden sm:inline">Додати товар</span>
            <span className="sm:hidden">Додати</span>
          </button>
        </div>
      </div>

      <div className="mt-4 md:hidden">
        <ProductSearchInput searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
      </div>

      {isInitialLoading ? (
        <ProductChipSkeleton />
      ) : (
        <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
          {categoryChips.map((category) => {
            const isActive = selectedCategoryId === category.id;
            return (
              <button
                key={category.key}
                type="button"
                onClick={() => setSelectedCategoryId(category.id)}
                className={`inline-flex shrink-0 items-center gap-2 rounded-full border px-3 py-2 text-sm leading-5 transition-colors ${
                  isActive
                    ? "border-blue-300 bg-blue-50 text-blue-700"
                    : "border-slate-200 bg-white text-slate-700 hover:bg-slate-100"
                }`}
              >
                <span className="font-medium">{category.name}</span>
                <span className={isActive ? "text-blue-600" : "text-slate-500"}>
                  {category.count}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {isInitialLoading ? (
        <ProductLoadingState />
      ) : visibleProducts.length === 0 ? (
        <ProductEmptyState
          title={emptyTitle}
          description={emptyDescription}
          onAdd={() => setIsAddModalOpen(true)}
        />
      ) : (
        <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_25rem]">
          <section className="hidden overflow-hidden rounded-lg border border-slate-200 bg-white lg:block">
            <ProductTable
              products={visibleProducts}
              selectedProduct={selectedProduct}
              onSelect={setSelectedProduct}
              onEdit={openProductEditor}
              onDelete={requestDeleteProduct}
            />
            <ProductTableFooter shown={visibleProducts.length} total={products.length} />
          </section>

          <section className="grid grid-cols-1 gap-3 lg:hidden">
            {visibleProducts.map((product) => (
              <ProductCard
                key={product.product_id}
                product={product}
                onClick={openProductDetail}
                onEdit={openProductEditor}
                onDelete={requestDeleteProduct}
              />
            ))}
          </section>

          <aside className="hidden rounded-lg border border-slate-200 bg-white p-6 xl:block">
            {selectedProduct ? (
              <ProductSidePanel
                product={selectedProduct}
                onClose={() => setSelectedProduct(null)}
                onEdit={() => openProductEditor(selectedProduct)}
                onDelete={() => requestDeleteProduct(selectedProduct)}
              />
            ) : (
              <div className="flex h-full min-h-64 items-center justify-center text-center text-sm text-slate-500">
                Оберіть товар у таблиці, щоб переглянути деталі.
              </div>
            )}
          </aside>

          <div ref={sentinelRef} className="py-4 xl:col-span-2">
            {loadingMore && <ProductLoadingMoreState />}
          </div>
        </div>
      )}

      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Додати товар"
        size="lg"
      >
        <AddProductForm onClose={() => setIsAddModalOpen(false)} onSuccess={handleProductCreated} />
      </Modal>

      <DetailModal isOpen={isProductModalOpen} onClose={handleCloseProductModal}>
        {selectedProduct && (
          <ProductDetailModal
            key={selectedProduct.product_id}
            product={selectedProduct}
            onClose={handleCloseProductModal}
            onDelete={() => requestDeleteProduct(selectedProduct)}
            onEdit={() => openProductEditor(selectedProduct)}
            categories={transformedCategories}
          />
        )}
      </DetailModal>

      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Редагувати товар"
        size="lg"
      >
        {selectedProduct && (
          <EditProductForm
            product={selectedProduct}
            onClose={() => setIsEditModalOpen(false)}
            onSave={handleProductEdited}
          />
        )}
      </Modal>

      <CategoryManagementModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        categories={transformedCategories.filter((cat) => cat.id !== null)}
        onAddCategory={handleAddCategory}
        onUpdateCategory={handleUpdateCategory}
        onDeleteCategory={handleDeleteCategory}
      />

      <ConfirmDeleteModal
        isOpen={!!productPendingDelete}
        title="Підтвердити видалення"
        message={productPendingDelete ? `Видалити товар "${productPendingDelete.name}"?` : ""}
        warning="Цю дію не можна скасувати."
        confirmLabel="Видалити товар"
        onCancel={() => setProductPendingDelete(null)}
        onConfirm={confirmDeleteProduct}
      />
    </div>
  );
};

const ProductSearchInput = ({
  searchTerm,
  setSearchTerm,
}: {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
}) => (
  <div className="relative">
    <SearchIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
    <input
      type="text"
      placeholder="Пошук товарів..."
      value={searchTerm}
      onChange={(event) => setSearchTerm(event.target.value)}
      className="h-10 w-full rounded-md border border-slate-300 bg-white pl-10 pr-3 text-sm leading-5 text-slate-950 placeholder:text-slate-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
    />
  </div>
);

const ProductTable = ({
  products,
  selectedProduct,
  onSelect,
  onEdit,
  onDelete,
}: {
  products: Product[];
  selectedProduct: Product | null;
  onSelect: (product: Product) => void;
  onEdit: (product: Product) => void;
  onDelete: (product: Product) => void;
}) => (
  <div className="overflow-x-auto">
    <table className="min-w-full table-fixed divide-y divide-slate-200 text-sm">
      <colgroup>
        <col className="w-12" />
        <col className="w-[38%]" />
        <col className="w-[24%]" />
        <col className="w-[18%]" />
        <col className="w-28" />
      </colgroup>
      <thead className="bg-white text-left text-xs font-medium uppercase tracking-normal text-slate-500">
        <tr>
          <th className="px-5 py-4">
            <span className="block h-4 w-4 rounded border border-slate-300 bg-white" />
          </th>
          <th className="px-4 py-4 font-medium normal-case">Назва</th>
          <th className="px-4 py-4 font-medium normal-case">Категорія</th>
          <th className="px-4 py-4 font-medium normal-case">Ціна</th>
          <th className="px-4 py-4 text-center font-medium normal-case">Дії</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-200">
        {products.map((product) => {
          const isSelected = selectedProduct?.product_id === product.product_id;
          const categoryName = getCategoryName(product);

          return (
            <tr
              key={product.product_id}
              onClick={() => onSelect(product)}
              className={`cursor-pointer transition-colors ${
                isSelected ? "bg-blue-50/70" : "bg-white hover:bg-slate-50"
              }`}
            >
              <td className="px-5 py-4">
                <span
                  className={`flex h-4 w-4 items-center justify-center rounded border ${
                    isSelected ? "border-blue-600 bg-blue-600" : "border-slate-300 bg-white"
                  }`}
                >
                  {isSelected && (
                    <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 16 16">
                      <path
                        d="m3.5 8 3 3 6-6"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                      />
                    </svg>
                  )}
                </span>
              </td>
              <td className="px-4 py-4 font-medium text-slate-950">{product.name}</td>
              <td className="px-4 py-4">
                <span
                  className={`inline-flex rounded px-2 py-1 text-xs font-medium leading-4 ${getCategoryTone(
                    categoryName,
                  )}`}
                >
                  {categoryName}
                </span>
              </td>
              <td className="px-4 py-4 text-slate-900">{formatPrice(product.price)}</td>
              <td className="px-4 py-4">
                <div className="flex justify-center gap-2">
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      onEdit(product);
                    }}
                    className="rounded-md p-2 text-slate-700 hover:bg-slate-100"
                    aria-label="Редагувати товар"
                  >
                    <EditIcon className="h-5 w-5" />
                  </button>
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      onDelete(product);
                    }}
                    className="rounded-md p-2 text-red-600 hover:bg-red-50"
                    aria-label="Видалити товар"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

const ProductTableFooter = ({ shown, total }: { shown: number; total: number }) => (
  <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3 text-sm text-slate-500">
    <span>
      Показано 1-{shown} з {total}
    </span>
    <span className="rounded-md border border-slate-200 bg-white px-3 py-2 text-slate-700">
      20 / сторінка
    </span>
  </div>
);

const ProductSidePanel = ({
  product,
  onClose,
  onEdit,
  onDelete,
}: {
  product: Product;
  onClose: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) => (
  <div className="flex h-full flex-col">
    <div className="flex items-start justify-between gap-4">
      <h2 className="text-xl font-semibold leading-7 text-slate-950">{product.name}</h2>
      <button
        type="button"
        onClick={onClose}
        className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-950"
        aria-label="Закрити деталі товару"
      >
        <CloseIcon className="h-5 w-5" />
      </button>
    </div>

    <dl className="mt-7 divide-y divide-slate-200 text-sm">
      <div className="flex items-center justify-between gap-4 py-4">
        <dt className="text-slate-500">Категорія</dt>
        <dd className="font-medium text-slate-950">{getCategoryName(product)}</dd>
      </div>
      <div className="flex items-center justify-between gap-4 py-4">
        <dt className="text-slate-500">Ціна</dt>
        <dd className="font-medium text-slate-950">{formatPrice(product.price)}</dd>
      </div>
    </dl>

    <div className="mt-7 space-y-3">
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

const ProductLoadingState = () => (
  <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_25rem]">
    <TableSkeleton columns={5} rows={6} />
    <section className="grid grid-cols-1 gap-3 lg:hidden">
      {Array.from({ length: 5 }).map((_, index) => (
        <ProductCardSkeleton key={index} />
      ))}
    </section>
    <SidePanelSkeleton />
  </div>
);

const ProductChipSkeleton = () => (
  <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
    {Array.from({ length: 4 }).map((_, index) => (
      <SkeletonBlock key={index} className="h-10 w-24 shrink-0 rounded-full" />
    ))}
  </div>
);

const ProductLoadingMoreState = () => (
  <>
    <div className="hidden lg:block">
      <TableSkeleton columns={5} rows={2} />
    </div>
    <div className="grid grid-cols-1 gap-3 lg:hidden">
      {Array.from({ length: 2 }).map((_, index) => (
        <ProductCardSkeleton key={index} />
      ))}
    </div>
  </>
);

const ProductEmptyState = ({
  title,
  description,
  onAdd,
}: {
  title: string;
  description: string;
  onAdd: () => void;
}) => (
  <div className="mt-4 flex min-h-80 flex-col items-center justify-center rounded-lg border border-slate-200 bg-white px-6 text-center">
    <CubeIcon className="h-14 w-14 text-slate-400" />
    <h2 className="mt-5 text-lg font-semibold text-slate-950">{title}</h2>
    <p className="mt-2 max-w-sm text-sm leading-5 text-slate-500">{description}</p>
    <button
      type="button"
      onClick={onAdd}
      className="mt-6 inline-flex h-10 items-center justify-center rounded-md bg-blue-600 px-5 text-sm font-medium text-white hover:bg-blue-700"
    >
      Додати товар
    </button>
  </div>
);

const ConfirmDeleteModal = ({
  isOpen,
  title,
  message,
  warning,
  confirmLabel,
  onCancel,
  onConfirm,
}: {
  isOpen: boolean;
  title: string;
  message: string;
  warning?: string;
  confirmLabel: string;
  onCancel: () => void;
  onConfirm: () => void;
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-9999 flex items-center justify-center bg-slate-950/45 px-4">
      <div className="w-full max-w-md rounded-lg bg-white shadow-xl">
        <div className="border-b border-slate-200 px-6 py-5">
          <h2 className="text-xl font-semibold text-slate-950">{title}</h2>
        </div>
        <div className="px-6 py-5">
          <p className="text-sm leading-6 text-slate-600">{message}</p>
          {warning && (
            <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium leading-5 text-amber-800">
              {warning}
            </div>
          )}
        </div>
        <div className="flex gap-3 border-t border-slate-200 px-6 py-5">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 rounded-md bg-slate-100 px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-200"
          >
            Скасувати
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="flex-1 rounded-md bg-red-600 px-4 py-3 text-sm font-medium text-white hover:bg-red-700"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

const SearchIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.197 5.197a7.5 7.5 0 0 0 10.606 10.606Z"
    />
  </svg>
);

const FolderIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M2.25 12.75V6.75A2.25 2.25 0 0 1 4.5 4.5h4.318c.597 0 1.17.237 1.591.659l1.432 1.432c.422.422.995.659 1.591.659H19.5a2.25 2.25 0 0 1 2.25 2.25v3.25m-19.5 0v4.5A2.25 2.25 0 0 0 4.5 19.5h15a2.25 2.25 0 0 0 2.25-2.25v-4.5m-19.5 0h19.5"
    />
  </svg>
);

const PlusIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.5v15m7.5-7.5h-15" />
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

const CloseIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18 18 6M6 6l12 12" />
  </svg>
);

const CubeIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={1.8}
      d="m21 7.5-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25m0-9L3 7.5m9 5.25v9M3 7.5v9l9 5.25"
    />
  </svg>
);
