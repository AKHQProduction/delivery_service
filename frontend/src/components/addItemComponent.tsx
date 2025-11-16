import { useState } from "react";
import { BottomModal } from "./ui/modals/bottomModal";
import { MODAL_CONFIG } from "../config/modalContent";
import { AddProductForm } from "./ui/forms/addProductForm";
import { AddClientForm } from "./ui/forms/addClientForm";
import { AddOrderForm } from "./ui/forms/addOrderForm";
import { AddStaffForm } from "./ui/forms/addStaffForm";

export const AddItemComponent = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAddClick = () => {
    setIsModalOpen(true);
  };

  const currentConfig =
    MODAL_CONFIG[location.pathname as keyof typeof MODAL_CONFIG] || MODAL_CONFIG["/products"];

  const renderModalContent = () => {
    switch (currentConfig.component) {
      case "AddProductForm":
        return <AddProductForm onClose={() => setIsModalOpen(false)} />;
      case "AddClientForm":
        return <AddClientForm onClose={() => setIsModalOpen(false)} />;
      case "AddOrderForm":
        return <AddOrderForm onClose={() => setIsModalOpen(false)} />;
      case "AddStaffForm":
        return <AddStaffForm onClose={() => setIsModalOpen(false)} />;
      default:
        return <div>Виберіть дію</div>;
    }
  };

  return (
    <div className="fixed bottom-27 right-6">
      <div className="absolute inset-0 bg-indigo-600 rounded-full animate-ping-slow opacity-75"></div>
      <button
        onClick={handleAddClick}
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

      <BottomModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={currentConfig.title}
        height={currentConfig.height}
      >
        {renderModalContent()}
      </BottomModal>
    </div>
  );
};
