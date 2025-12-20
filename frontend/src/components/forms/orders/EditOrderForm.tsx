import React from "react";
import { useOrderForm } from "../../../hooks/orders/useOrdersForm";
import { useOrders } from "../../../hooks/orders/useOrders";
import { ProgressSteps } from "../../shared/ProgressSteps";
import { ClientSelectionStep } from "./steps/ClientSelectionStep";
import { ProductSelectionStep } from "./steps/ProductSelectionStep";
import { ContactInfoStep } from "./steps/ContactInfoStep";
import { DeliveryDateStep } from "./steps/DeliveryDateStep";
import { FormNavigationButtons } from "../../shared/FormNavigationButtons";

interface EditOrderFormProps {
  order: any;
  onClose: () => void;
}

export const EditOrderForm: React.FC<EditOrderFormProps> = ({
  onClose,
  order,
}) => {
  const { updateCurrentOrder } = useOrders();

  const {
    step,
    formData,
    searchClient,
    searchProduct,
    filteredClients,
    filteredProducts,
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
  } = useOrderForm({ initialOrder: order });

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
      onClose();
    } catch (error) {
      console.error("Error updating order:", error);
      alert("Failed to update order. Please check the console for details.");
    }
  };

  return (
    <div className="flex flex-col h-full max-h-[85vh]">
      <div className="border-b border-gray-200">
        <ProgressSteps currentStep={step} totalSteps={4} />
      </div>

      <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
        {step === 1 && (
          <ClientSelectionStep
            clients={filteredClients}
            selectedClient={formData.client}
            searchValue={searchClient}
            onSearchChange={setSearchClient}
            onClientSelect={handleClientSelect}
            onAddNewClient={() => {
              /* add new client need to be added */
            }}
          />
        )}

        {step === 2 && (
          <ProductSelectionStep
            products={filteredProducts}
            selectedProducts={formData.products}
            searchValue={searchProduct}
            onSearchChange={setSearchProduct}
            onProductToggle={handleProductToggle}
            onQuantityChange={handleQuantityChange}
          />
        )}

        {step === 3 && (
          <ContactInfoStep
            client={formData.client}
            selectedPhone={getPhoneString()}
            selectedAddress={getAddressString()}
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
