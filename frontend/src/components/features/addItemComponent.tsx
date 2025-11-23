import { useState } from "react";
import { useLocation } from "react-router-dom";
import { BottomModal } from "../ui/bottomModal";
import { MODAL_CONFIG } from "../../constants/modalContent";
import { AddProductForm } from "../forms/addProductForm";
import { AddClientForm } from "../forms/addClientForm";
import { AddOrderForm } from "../forms/addOrderForm";
import { AddStaffForm } from "../forms/addStaffForm";
import { useUserStore } from "../../context/useUserStore";

export const AddItemComponent = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const location = useLocation()
  const user = useUserStore((s) => s.user);
  
  const handleAddClick = () => {
    setIsModalOpen(true);
  };

  const currentConfig =
    MODAL_CONFIG[location.pathname as keyof typeof MODAL_CONFIG];

  const hasAccess = currentConfig && user 
    ? currentConfig.allowedRoles.includes(user.role)
    : false;

  if (!hasAccess || !currentConfig) {
    return null;
  }

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
      >
        {renderModalContent()}
      </BottomModal>
    </div>
  );
};
