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

export const CategoryManagementModal: React.FC<CategoryManagementModalProps> = ({
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
  const [pendingDeleteCategory, setPendingDeleteCategory] = useState<transformedCategories | null>(
    null,
  );

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

  const handleConfirmDelete = () => {
    if (!pendingDeleteCategory?.id) return;

    onDeleteCategory(pendingDeleteCategory.id);
    setPendingDeleteCategory(null);
  };

  return (
    <div className="fixed inset-0 z-9999 flex items-end justify-center bg-slate-950/45 md:items-center">
      <div className="flex max-h-[86vh] w-full flex-col rounded-t-lg bg-white shadow-xl md:mx-4 md:max-w-xl md:rounded-lg">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5">
          <h2 className="text-xl font-semibold text-slate-950">Категорії товарів</h2>
          <button
            title="Close"
            onClick={onClose}
            className="rounded-md p-2 text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-950"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-3">
            {categories.length === 0 ? (
              <div className="py-8 text-center text-slate-500">
                <p className="text-sm">Категорій ще немає</p>
                <p className="mt-1 text-xs">Додайте першу категорію, щоб почати</p>
              </div>
            ) : (
              categories.map((category, index) => (
                <div
                  key={category.id}
                  className="rounded-lg border border-slate-100 bg-slate-50 p-4"
                >
                  <div className="flex items-center gap-3">
                    <CategoryFolderIcon index={index} />

                    {editingId === category.id ? (
                      <div className="flex-1">
                        <input
                          title="Edit"
                          type="text"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          className="mb-2 w-full rounded-md border border-blue-500 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-100"
                        />
                        <div className="flex items-center gap-2">
                          <button
                            onClick={handleSaveEdit}
                            className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
                          >
                            Зберегти
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="rounded-md bg-slate-200 px-4 py-2 text-sm text-slate-700 hover:bg-slate-300"
                          >
                            Скасувати
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex-1">
                        <p className="font-medium text-slate-950">{category.name}</p>
                      </div>
                    )}

                    {editingId !== category.id && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleStartEdit(category)}
                          className="rounded-md p-2 transition-colors hover:bg-slate-200"
                          aria-label="Редагувати категорію"
                        >
                          <img src={Edit} alt="" className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => category.id && setPendingDeleteCategory(category)}
                          className="rounded-md p-2 transition-colors hover:bg-red-50"
                          aria-label="Видалити категорію"
                        >
                          <img src={Delete} alt="" className="h-5 w-5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="border-t border-slate-200 p-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={newCategoryName}
              onChange={(e) => setNewCategoryName(e.target.value)}
              placeholder="Нова категорія..."
              className="min-w-0 flex-1 rounded-md border border-slate-300 px-4 py-3 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
            <button
              onClick={handleAdd}
              disabled={!newCategoryName.trim()}
              className="rounded-md bg-blue-600 px-5 py-3 font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              Додати
            </button>
          </div>
        </div>
      </div>

      {pendingDeleteCategory && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-slate-950/45 px-4">
          <div className="w-full max-w-md rounded-lg bg-white shadow-xl">
            <div className="border-b border-slate-200 px-6 py-5">
              <h3 className="text-lg font-semibold text-slate-950">Підтвердити видалення</h3>
            </div>
            <div className="px-6 py-5">
              <p className="text-sm leading-6 text-slate-600">
                Видалити категорію "{pendingDeleteCategory.name}"?
              </p>
              <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium leading-5 text-amber-800">
                Товари з цієї категорії залишаться без категорії.
              </div>
            </div>
            <div className="flex gap-3 border-t border-slate-200 px-6 py-5">
              <button
                type="button"
                onClick={() => setPendingDeleteCategory(null)}
                className="flex-1 rounded-md bg-slate-100 px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-200"
              >
                Скасувати
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                className="flex-1 rounded-md bg-red-600 px-4 py-3 text-sm font-medium text-white hover:bg-red-700"
              >
                Видалити
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const CategoryFolderIcon = ({ index }: { index: number }) => {
  const tones = ["text-blue-600", "text-violet-600", "text-orange-600"];

  return (
    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-white">
      <svg
        className={`h-6 w-6 ${tones[index % tones.length]}`}
        fill="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path d="M3 6.75A2.75 2.75 0 0 1 5.75 4h3.879c.729 0 1.428.29 1.944.805l1.122 1.122c.234.235.552.367.884.367h4.671A2.75 2.75 0 0 1 21 9.044v8.206A2.75 2.75 0 0 1 18.25 20H5.75A2.75 2.75 0 0 1 3 17.25V6.75Z" />
      </svg>
    </div>
  );
};
