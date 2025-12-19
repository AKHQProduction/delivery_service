import React from "react";
import { useOrderForm } from "../../../hooks/orders/useOrdersForm";
import { useOrders } from "../../../hooks/orders/useOrders";
import { ProgressSteps } from "../../shared/ProgressSteps";
import { ClientSelectionStep } from "./steps/ClientSelectionStep";
import { ProductSelectionStep } from "./steps/ProductSelectionStep";
import { ContactInfoStep } from "./steps/ContactInfoStep";
import { DeliveryDateStep } from "./steps/DeliveryDateStep";
import { FormNavigationButtons } from "../../shared/FormNavigationButtons";

interface AddOrderFormProps {
  onClose: () => void;
}

export const AddOrderForm: React.FC<AddOrderFormProps> = ({ onClose }) => {
  const { createNewOrder } = useOrders();
  
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
  } = useOrderForm();

  const handleSubmit = () => {
    console.log("Order submitted:", formData);
    console.log("deliveryPhone:", formData.deliveryPhone);
    console.log("deliveryAddress:", formData.deliveryAddress);
    console.log("phone_id:", formData.deliveryPhone?.id);
    console.log("address_id:", formData.deliveryAddress?.id);
    
    createNewOrder({
      client_id: formData.client?.client_id,
      products: formData.products.map((p) => ({
        product_id: p.product.product_id,
        quantity: p.quantity,
      })),
      phone_id: formData.deliveryPhone?.id,
      address_id: formData.deliveryAddress?.id,
      delivery_date: formData.deliveryDate,
      time_preference: formData.deliveryTime,
    });
    window.location.reload(); //TEMPORARY SOLUTION
    onClose();
  };

  return (
    <div className="flex flex-col h-full max-h-[85vh]">
      <ProgressSteps currentStep={step} totalSteps={4} />

      <div className="flex-1 overflow-y-auto px-6 pb-4">
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