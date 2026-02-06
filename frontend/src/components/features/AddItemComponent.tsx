import { useState } from "react";
import { useLocation } from "react-router-dom";
import { BottomModal } from "../modals/BottomModal";
import { MODAL_CONFIG } from "../../constants/modalContent";
import { AddProductForm } from "../forms/products/AddProductForm";
import { AddClientForm } from "../forms/client/AddClientForm";
import { AddOrderForm } from "../forms/orders/AddOrderForm";
import { InviteUserForm } from "../forms/employees/InviteUserForm";
import { useUserShopStore } from "../../context/useUserShopStore";
import { InviteLinkModal } from "../modals/InviteLinkModal";

export const AddItemComponent = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [inviteLink, setInviteLink] = useState<string | null>(null);

  const location = useLocation();
  const user = useUserShopStore((s) => s.user);

  const handleAddClick = () => setIsModalOpen(true);

  const currentConfig =
    MODAL_CONFIG[location.pathname as keyof typeof MODAL_CONFIG];

  const hasAccess =
    currentConfig && user
      ? currentConfig.allowedRoles.includes(user.role)
      : false;

  if (!hasAccess || !currentConfig) {
    return null;
  }

  const renderModalContent = () => {
    switch (currentConfig.component) {
      case "AddProductForm":
        return (
          <AddProductForm
            onClose={() => setIsModalOpen(false)}
            onSuccess={(productId: any) => {
              const id =
                typeof productId === "string"
                  ? productId
                  : (productId?.product_id ?? productId?.id);
              sessionStorage.setItem("openProductId", id);
              window.location.reload();
            }}
          />
        );
      case "AddClientForm":
        return (
          <AddClientForm
            onClose={() => setIsModalOpen(false)}
            onSuccess={(clientData: any) => {
              const id =
                typeof clientData === "string"
                  ? clientData
                  : (clientData?.client_id ?? clientData?.id);
              sessionStorage.setItem("openClientId", id);
              window.location.reload();
            }}
          />
        );
      case "AddOrderForm":
        return (
          <AddOrderForm
            onClose={() => setIsModalOpen(false)}
            onSave={(orderData: any) => {
              const id =
                typeof orderData === "string"
                  ? orderData
                  : (orderData?.order_id ?? orderData?.id);
              if (id) {
                sessionStorage.setItem("openOrderId", id);
              }
              setIsModalOpen(false);
              window.location.reload();
            }}
          />
        );
      case "InviteUserForm":
        return (
          <InviteUserForm
            onClose={() => setIsModalOpen(false)}
            onInviteCreated={(link) => setInviteLink(link)}
          />
        );
    }
  };

  return (
    <>
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

      {inviteLink && (
        <InviteLinkModal
          link={inviteLink}
          onClose={() => setInviteLink(null)}
        />
      )}
    </>
  );
};
