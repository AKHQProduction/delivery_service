import React, { useState, useEffect } from "react";
import Edit from "../../assets/icons/edit.svg";
import Delete from "../../assets/icons/delete.svg";
import { type transformedCategories } from "../../types/entities/Product";


interface CategoryManagementModalProps {
  isOpen: boolean;
  onClose: () => void;
  categories: transformedCategories[];
  onAddCategory: (name: string) => void;
  onUpdateCategory: (id: string, name: string) => void;
  onDeleteCategory: (id: string) => void;
}

export const CategoryManagementModal: React.FC<
  CategoryManagementModalProps
> = ({
  isOpen,
  onClose,
  categories,
  onAddCategory,
  onUpdateCategory,
  onDeleteCategory,
}) => {
  const [newCategoryName, setNewCategoryName] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleAdd = () => {
    if (newCategoryName.trim()) {
      onAddCategory(newCategoryName.trim());
      setNewCategoryName("");
    }
  };

  const handleStartEdit = (category: transformedCategories) => {
    console.log("Editing category:", category);
    setEditingId(category.id);
    setEditingName(category.name);
  };

  const handleSaveEdit = () => {
    if (editingId && editingName.trim()) {
      onUpdateCategory(editingId, editingName.trim());
      setEditingId(null);
      setEditingName("");
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingName("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-2xl w-full max-w-md mx-4 max-h-[80vh] flex flex-col shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold">Управління категоріями</h2>
          <button
            title="Close"
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Category List */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-3">
            {categories.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <p className="text-sm">Категорій ще немає</p>
                <p className="text-xs mt-1">
                  Додайте першу категорію, щоб почати
                </p>
              </div>
            ) : (
              categories.map((category) => (
                <div
                  key={category.id}
                  className="p-4 bg-gray-50 rounded-xl"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center text-2xl">
                      {category.emoji}
                    </div>

                    {editingId === category.id ? (
                      <div className="flex-1">
                        <input
                          title="Edit"
                          type="text"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          className="w-full px-3 py-2 border border-blue-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                        />
                        <div className="flex items-center gap-2">
                          <button
                            onClick={handleSaveEdit}
                            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                          >
                            Зберегти
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                          >
                            Скасувати
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex-1">
                        <p className="font-medium">{category.name}</p>
                      </div>
                    )}

                    {editingId !== category.id && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleStartEdit(category)}
                          className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                        >
                          <img src={Edit} alt="Edit" className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => onDeleteCategory(category.id)}
                          className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <img src={Delete} alt="Delete" className="w-5 h-5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Add New Category */}
        <div className="p-6 border-t">
          <div className="flex gap-3">
            <input
              type="text"
              value={newCategoryName}
              onChange={(e) => setNewCategoryName(e.target.value)}
              placeholder="Нова категорія..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleAdd}
              disabled={!newCategoryName.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Додати
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
