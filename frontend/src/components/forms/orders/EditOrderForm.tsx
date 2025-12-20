import React, { useState } from "react";
import { useOrderForm } from "../../../hooks/orders/useOrdersForm";
import { useOrders } from "../../../hooks/orders/useOrders";
import { ProgressSteps } from "../../shared/ProgressSteps";
import { ClientSelectionStep } from "./steps/ClientSelectionStep";
import { ProductSelectionStep } from "./steps/ProductSelectionStep";
import { ContactInfoStep } from "./steps/ContactInfoStep";
import { DeliveryDateStep } from "./steps/DeliveryDateStep";
import { FormNavigationButtons } from "../../shared/FormNavigationButtons";
import { AddClientForm } from "../client/AddClientForm";
import { type Client } from "../../../types/entities/Client";

interface EditOrderFormProps {
  order: any;
  onClose: () => void;
  onSave?: () => void;
}

export const EditOrderForm: React.FC<EditOrderFormProps> = ({
  onClose,
  onSave,
  order,
}) => {
  const { updateCurrentOrder } = useOrders();
  const [showAddClient, setShowAddClient] = useState(false);

  const {
    step,
    formData,
    searchClient,
    searchProduct,
    clients,
    products,
    loadMoreClients,
    clientsLoadingMore,
    clientsHasMore,
    loadMoreProducts,
    productsLoadingMore,
    productsHasMore,
    setSearchClient,
    setSearchProduct,
    handleClientSelect,
    handleProductToggle,
    handleQuantityChange,
    handlePhoneChange,
    handleAddressChange,
    handleDateChange,
    handleTimeChange,
    handleNext,
    handleBack,
    canProceed,
    getPhoneString,
    getAddressString,
    getAddressId,
    addAndSelectNewClient,
  } = useOrderForm({ initialOrder: order });

  const handleAddNewClient = () => {
    setShowAddClient(true);
  };

  const handleClientCreated = (newClient?: Client) => {
    setShowAddClient(false);
    if (newClient) {
      addAndSelectNewClient(newClient);
    }
  };

  const handleSubmit = async () => {
    console.log("=== EDIT ORDER SUBMIT ===");
    console.log("Full formData:", formData);
    console.log("deliveryPhone:", formData.deliveryPhone);
    console.log("deliveryPhone type:", typeof formData.deliveryPhone);
    console.log("deliveryAddress:", formData.deliveryAddress);
    console.log("deliveryAddress type:", typeof formData.deliveryAddress);
    console.log("phone_id:", formData.deliveryPhone?.id);
    console.log("address_id:", formData.deliveryAddress?.id);

    // Ensure we have valid IDs before submitting
    if (!formData.deliveryPhone?.id || !formData.deliveryAddress?.id) {
      console.error("Missing phone_id or address_id!");
      console.error("Phone object:", formData.deliveryPhone);
      console.error("Address object:", formData.deliveryAddress);

      // Show error to user
      alert("Please select valid phone and address");
      return;
    }

    try {
      await updateCurrentOrder(order.order_id, {
        client_id: formData.client?.client_id,
        items: formData.products.map((p) => {
          if (p.itemId) {
            // Existing item - send id + quantity
            return { id: p.itemId, quantity: p.quantity };
          } else {
            // New item - send product_id + quantity
            return { product_id: p.product.product_id, quantity: p.quantity };
          }
        }),
        phone_id: formData.deliveryPhone.id,
        address_id: formData.deliveryAddress.id,
        delivery_date: formData.deliveryDate,
        time_preference: formData.deliveryTime,
        comment: formData.note,
      });
      onSave ? onSave() : onClose();
    } catch (error) {
      console.error("Error updating order:", error);
      alert("Failed to update order. Please check the console for details.");
    }
  };

  if (showAddClient) {
    return (
      <AddClientForm
        onClose={() => setShowAddClient(false)}
        onSuccess={handleClientCreated}
      />
    );
  }

  return (
    <div className="flex flex-col h-full max-h-[85vh]">
      <div className="border-b border-gray-200">
        <ProgressSteps currentStep={step} totalSteps={4} />
      </div>

      <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
        {step === 1 && (
          <ClientSelectionStep
            clients={clients}
            selectedClient={formData.client}
            searchValue={searchClient}
            onSearchChange={setSearchClient}
            onClientSelect={handleClientSelect}
            onAddNewClient={handleAddNewClient}
            loadMore={loadMoreClients}
            loadingMore={clientsLoadingMore}
            hasMore={clientsHasMore}
          />
        )}

        {step === 2 && (
          <ProductSelectionStep
            products={products}
            selectedProducts={formData.products}
            searchValue={searchProduct}
            onSearchChange={setSearchProduct}
            onProductToggle={handleProductToggle}
            onQuantityChange={handleQuantityChange}
            loadMore={loadMoreProducts}
            loadingMore={productsLoadingMore}
            hasMore={productsHasMore}
          />
        )}

        {step === 3 && (
          <ContactInfoStep
            client={formData.client}
            selectedPhone={getPhoneString()}
            selectedAddress={getAddressId()}
            onPhoneChange={handlePhoneChange}
            onAddressChange={handleAddressChange}
          />
        )}

        {step === 4 && (
          <DeliveryDateStep
            client={formData.client}
            selectedPhone={getPhoneString()}
            selectedAddress={getAddressString()}
            selectedProducts={formData.products}
            deliveryDate={formData.deliveryDate}
            deliveryTime={formData.deliveryTime}
            onDateChange={handleDateChange}
            onTimeChange={handleTimeChange}
          />
        )}
      </div>

      <FormNavigationButtons
        currentStep={step}
        totalSteps={4}
        canProceed={canProceed()}
        onBack={handleBack}
        onNext={handleNext}
        onSubmit={handleSubmit}
      />
    </div>
  );
};
