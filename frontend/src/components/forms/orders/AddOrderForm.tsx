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
import { usePlatform } from "../../../platforms/usePlatform";
import { AddOrderFormWeb } from "./AddOrderFormWeb";
import { FormSkeleton } from "../../ui/Skeleton";

interface AddOrderFormProps {
  onClose: () => void;
  onSave?: (order?: unknown) => void;
}

export const AddOrderForm: React.FC<AddOrderFormProps> = ({ onClose, onSave }) => {
  const { type } = usePlatform();

  if (type === "web") {
    return <AddOrderFormWeb onClose={onClose} onSave={onSave} />;
  }

  return <AddOrderFormNative onClose={onClose} onSave={onSave} />;
};

const AddOrderFormNative: React.FC<AddOrderFormProps> = ({ onClose, onSave }) => {
  const { createNewOrder } = useOrders();
  const [showAddClient, setShowAddClient] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    step,
    formData,
    searchClient,
    searchProduct,
    clients,
    timeSlots,
    paymentMethods,
    products,
    referencesReady,
    clientsLoading,
    productsLoading,
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
    handleTimeSlotChange,
    handlePaymentMethodChange,
    handleNoteChange,
    handleNext,
    handleBack,
    canProceed,
    getPhoneString,
    getAddressString,
    getAddressId,
    addAndSelectNewClient,
  } = useOrderForm();

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
    if (isSubmitting) return;

    setIsSubmitting(true);
    try {
      const newOrder = await createNewOrder({
        client_id: formData.client?.client_id,
        products: formData.products.map((p) => ({
          product_id: p.product.product_id,
          quantity: p.quantity,
        })),
        phone_id: formData.deliveryPhone?.id,
        address_id: formData.deliveryAddress?.id,
        delivery_date: formData.deliveryDate,
        time_slot_id: formData.timeSlotId,
        payment_method: formData.paymentMethod,
        comment: formData.note,
      });
      if (onSave) {
        onSave(newOrder);
      } else {
        onClose();
      }
    } catch (error) {
      console.error("Error creating order:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (showAddClient) {
    return (
      <AddClientForm onClose={() => setShowAddClient(false)} onSuccess={handleClientCreated} />
    );
  }

  if (!referencesReady) {
    return <FormSkeleton fields={6} />;
  }

  return (
    <div className="flex flex-col h-full max-h-[85vh]">
      <ProgressSteps currentStep={step} totalSteps={4} />

      <div className="flex-1 overflow-y-auto px-6 pb-4">
        {step === 1 && (
          <ClientSelectionStep
            clients={clients}
            selectedClient={formData.client}
            searchValue={searchClient}
            onSearchChange={setSearchClient}
            onClientSelect={handleClientSelect}
            onAddNewClient={handleAddNewClient}
            loadMore={loadMoreClients}
            loading={clientsLoading}
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
            loading={productsLoading}
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
            timeSlotId={formData.timeSlotId}
            timeSlots={timeSlots}
            paymentMethod={formData.paymentMethod}
            paymentMethods={paymentMethods}
            note={formData.note || ""}
            onDateChange={handleDateChange}
            onTimeChange={handleTimeSlotChange}
            onPaymentMethodChange={handlePaymentMethodChange}
            onNoteChange={handleNoteChange}
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
