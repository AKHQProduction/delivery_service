import React, { useState, useEffect } from "react";
import { useClient } from "../../../hooks/clients/useClients";
import { useProducts } from "../../../hooks/useProducts";
import { type Client } from "../../../types/entities/Client";
import { type Product } from "../../../types/entities/Product";

import { ProgressSteps } from "../../shared/ProgressSteps";
import { ClientSelectionStep } from "./steps/ClientSelectionStep";
import { ProductSelectionStep } from "./steps/ProductSelectionStep";
import { ContactInfoStep } from "./steps/ContactInfoStep";
import { DeliveryDateStep } from "./steps/DeliveryDateStep";
import { FormNavigationButtons } from "../../shared/FormNavigationButtons";
import { useOrders } from "../../../hooks/orders/useOrders";

interface AddOrderFormProps {
  onClose: () => void;
}

export const AddOrderForm: React.FC<AddOrderFormProps> = ({ onClose }) => {
  const [step, setStep] = useState(1);
  const [searchClient, setSearchClient] = useState("");
  const [searchProduct, setSearchProduct] = useState("");
  const { clients, getClients } = useClient();
  const { products, getProducts } = useProducts();
  const { createNewOrder } = useOrders();
  const [formData, setFormData] = useState({
    client: null as Client | null,
    products: [] as { product: Product; quantity: number }[],
    deliveryPhone: "",
    deliveryAddress: "",
    deliveryDate: "",
    deliveryTime: "",
  });

  useEffect(() => {
    getProducts();
    getClients();
    console.log("Selected client changed:", formData);
    console.log("Selected client:", clients);
    console.log("Selected client details:", products);
  }, []);

  useEffect(() => {
    if (formData.client) {
      if (formData.client.phones?.length === 1) {
        setFormData((prev) => ({
          ...prev,
          deliveryPhone: formData.client?.phones?.[0]?.number || "",
        }));
      }
      if (formData.client.addresses?.length === 1) {
        const addr = formData.client.addresses[0];
        const fullAddress = `${addr.street || ""} ${addr.house || ""} ${
          addr.apartment || ""
        } ${addr.entrance || ""} ${addr.floor || ""} ${
          addr.intercom || ""
        }`.trim();

        setFormData((prev) => ({
          ...prev,
          deliveryAddress: fullAddress,
        }));
      }
    }
    console.log("Selected client changed:", formData);
    console.log("Selected client:", clients);
    console.log("Selected client details:", products);
  }, [formData.client]);

  const filteredClients = clients.filter(
    (client) =>
      client?.full_name.toLowerCase().includes(searchClient.toLowerCase()) ||
      client?.phones?.some((num) => num.number.includes(searchClient))
  );

  const filteredProducts = products.filter((product) =>
    product.name.toLowerCase().includes(searchProduct.toLowerCase())
  );

  const handleClientSelect = (client: Client) => {
    setFormData({ ...formData, client });
  };

  const handleProductToggle = (product: Product) => {
    const exists = formData.products.find(
      (p) => p.product.product_id === product.product_id
    );
    if (exists) {
      setFormData({
        ...formData,
        products: formData.products.filter(
          (p) => p.product.product_id !== product.product_id
        ),
      });
    } else {
      setFormData({
        ...formData,
        products: [...formData.products, { product, quantity: 1 }],
      });
    }
  };

  const handleQuantityChange = (productId: string, quantity: number) => {
    setFormData({
      ...formData,
      products: formData.products.map((p) =>
        p.product.product_id === productId ? { ...p, quantity } : p
      ),
    });
  };

  const handleNext = () => {
    if (step < 4) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = () => {
    console.log("Order submitted:", formData);
    createNewOrder({
      client_id: formData.client?.client_id,
      products: formData.products.map((p) => ({
        product_id: p.product.product_id,
        quantity: p.quantity,
      })),
      phone_id: formData.client.phones[0]?.id,
      address_id: formData.client.addresses[0]?.id,
      delivery_date: formData.deliveryDate,
      time_preference: formData.deliveryTime,
    });

    onClose();
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return formData.client !== null;
      case 2:
        return formData.products.length > 0;
      case 3:
        return (
          formData.deliveryPhone.trim() !== "" &&
          formData.deliveryAddress.trim() !== ""
        );
      case 4:
        return (
          formData.deliveryDate.trim() !== "" &&
          formData.deliveryTime.trim() !== ""
        );
      default:
        return false;
    }
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
            selectedPhone={formData.deliveryPhone}
            selectedAddress={formData.deliveryAddress}
            onPhoneChange={(phone) =>
              setFormData({ ...formData, deliveryPhone: phone })
            }
            onAddressChange={(address) =>
              setFormData({ ...formData, deliveryAddress: address })
            }
          />
        )}

        {step === 4 && (
          <DeliveryDateStep
            client={formData.client}
            selectedPhone={formData.deliveryPhone}
            selectedAddress={formData.deliveryAddress}
            selectedProducts={formData.products}
            deliveryDate={formData.deliveryDate}
            deliveryTime={formData.deliveryTime}
            onDateChange={(date) =>
              setFormData({ ...formData, deliveryDate: date })
            }
            onTimeChange={(time) =>
              setFormData({ ...formData, deliveryTime: time })
            }
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
