import React, { useState } from "react";
import { EditProductForm } from "../../forms/products/EditProductForm";
import { ItemElement } from "../../ui/ItemElement";
import { ModalButtons } from "../../ui/ModalButtons";
import leftArrowIcon from "../../../assets/icons/left_arrow.svg";
import { type Product, type transformedCategories } from "../../../types/entities/Product";

interface ProductDetailModalProps {
  product: Product;
  categories: transformedCategories[];
  onClose: () => void;
  onDelete: () => void;
  onSave: (updatedProduct: Product) => Promise<void> | void;
}

export const ProductDetailModal: React.FC<ProductDetailModalProps> = ({
  product,
  onClose,
  onDelete,
  onSave,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleSaveEdit = async (updatedProduct: Product) => {
    await onSave(updatedProduct);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="h-full flex flex-col">
        <div className="bg-linear-to-br from-indigo-600 to-indigo-700 px-6 pt-12 pb-8">
          <button
            onClick={handleCancelEdit}
            type="button"
            title="cancel"
            className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center mb-6 hover:bg-white/30 transition-colors"
          >
            <img src={leftArrowIcon} alt="Back" className="w-8 h-8" />
          </button>
          <h1 className="text-3xl font-bold text-white mb-2">Редагувати товар</h1>
        </div>

        <div className="flex-1 overflow-y-auto px-6 pt-6">
          <EditProductForm product={product} onClose={handleCancelEdit} onSave={handleSaveEdit} />
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="bg-linear-to-br from-indigo-600 to-indigo-700 px-6 pt-12 pb-8">
        <button
          onClick={onClose}
          type="button"
          title="close"
          className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center mb-6 hover:bg-white/30 transition-colors"
        >
          <img src={leftArrowIcon} alt="Back" className="w-8 h-8" />
        </button>

        <h1 className="text-3xl font-bold text-white mb-2">{product.name}</h1>
        <p className="text-indigo-100">Категорія: {product.category_name || "Без категорії"}</p>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
            Основна інформація
          </h2>
          <ItemElement descriptionText={"Назва товару"} elementText={product.name} />
          <ItemElement
            descriptionText={"Категорія"}
            elementText={product.category_name || "Без категорії"}
          />
          <ItemElement descriptionText={"Ціна"} elementText={`₴${product.price}`} />
        </div>
      </div>
      <div className="px-6 py-4 border-t border-gray-200">
        <ModalButtons
          firstButtonText={"Редагувати"}
          handleEditClick={handleEditClick}
          secondButtonText="Видалити"
          onDelete={onDelete}
        />
      </div>
    </div>
  );
};
