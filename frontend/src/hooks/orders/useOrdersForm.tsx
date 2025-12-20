import { useState, useEffect } from "react";
import { useClient } from "../clients/useClients";
import { useProducts } from "../useProducts";
import { type Client } from "../../types/entities/Client";
import { type Product } from "../../types/entities/Product";

interface OrderFormProduct {
  product: Product;
  quantity: number;
  originalQuantity?: number;
  itemId?: number; // ID позиции для существующих items
}

interface OrderFormData {
  client: Client | null;
  products: OrderFormProduct[];
  deliveryPhone: any;
  deliveryAddress: any;
  deliveryDate: string;
  deliveryTime: string;
  note?: string;
}

interface UseOrderFormOptions {
  initialOrder?: any;
}

export const useOrderForm = (options: UseOrderFormOptions = {}) => {
  const { initialOrder } = options;
  const [step, setStep] = useState(1);
  const [searchClient, setSearchClient] = useState("");
  const [searchProduct, setSearchProduct] = useState("");

  const { clients, getClients } = useClient();
  const { products, getProducts } = useProducts();

  const [formData, setFormData] = useState<OrderFormData>({
    client: null,
    products: [],
    deliveryPhone: null,
    deliveryAddress: null,
    deliveryDate: "",
    deliveryTime: "",
    note: "",
  });

  useEffect(() => {
    getClients();
    getProducts();
  }, []);

  useEffect(() => {
    if (formData.client && !initialOrder) {
      if (formData.client.phones?.length === 1) {
        setFormData((prev) => ({
          ...prev,
          deliveryPhone: formData.client?.phones?.[0] || null,
        }));
      }
      if (formData.client.addresses?.length === 1) {
        setFormData((prev) => ({
          ...prev,
          deliveryAddress: formData.client?.addresses?.[0],
        }));
      }
    }
  }, [formData.client, initialOrder]);

  // Initialize form with existing order data (for editing)
  useEffect(() => {
    if (initialOrder && clients.length > 0 && products.length > 0) {
      const client = clients.find(
        (c) => c.client_id === initialOrder.client_id
      );

      // Map order items and preserve original quantity for edit mode
      const orderProducts =
        initialOrder.items
          ?.map((item: any) => {
            const product = products.find(
              (p) => p.product_id === item.product_id
            );
            return {
              product: product || {
                product_id: item.product_id,
                name: item.name,
                price: item.price_per_item,
              },
              quantity: item.quantity,
              originalQuantity: item.quantity,
              itemId: item.id, // Сохраняем ID позиции
            };
          })
          .filter((p: any) => p.product) || [];

      const phone =
        client?.phones?.find((p) => p.id === initialOrder.phone_id) ||
        client?.phones?.[0];
      const address =
        client?.addresses?.find((a) => a.id === initialOrder.address_id) ||
        client?.addresses?.[0];

      console.log("=== INITIALIZING EDIT ORDER ===");
      console.log("Found phone:", phone);
      console.log("Found address:", address);
        console.log("Found Products:", initialOrder)
        console.log("afasfsaf", orderProducts)
      setFormData({
        client: client || null,
        products: orderProducts,
        deliveryPhone: phone || null,
        deliveryAddress: address || null,
        deliveryDate: initialOrder.date || "",
        deliveryTime: initialOrder.time_preference || "",
        note: initialOrder.note || "",
      });
    }
  }, [initialOrder, clients, products]);

  const filteredClients = clients.filter(
    (client) =>
      client?.full_name?.toLowerCase().includes(searchClient.toLowerCase()) ||
      client?.phones?.some((num) => num.number.includes(searchClient))
  );

  const filteredProducts = products.filter((product) =>
    product.name.toLowerCase().includes(searchProduct.toLowerCase())
  );

  const handleClientSelect = (client: Client) => {
    setFormData({
      ...formData,
      client,
      deliveryPhone: client.phones?.[0] || null,
      deliveryAddress: client.addresses?.[0] || null,
    });
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
      // When adding a new product in edit mode, don't set originalQuantity
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
        p.product.product_id === productId 
          ? { ...p, quantity } // Keep originalQuantity intact
          : p
      ),
    });
  };

  const handlePhoneChange = (phone: any) => {
    console.log("handlePhoneChange called with:", phone);
    if (typeof phone === "string") {
      const phoneObj = formData.client?.phones?.find((p) => p.number === phone);
      setFormData({ ...formData, deliveryPhone: phoneObj || null });
    } else {
      setFormData({ ...formData, deliveryPhone: phone });
    }
  };

  const handleAddressChange = (address: any) => {
    console.log("handleAddressChange called with:", address);

    if (typeof address === "string") {
      const addressObj = formData.client?.addresses?.find((a) => {
        if (a.street === address) return true;

        const fullAddress = `${a.street || ""} ${a.house || ""} ${
          a.apartment || ""
        } ${a.entrance || ""} ${a.floor || ""} ${a.intercom || ""}`.trim();
        if (fullAddress === address) return true;

        return false;
      });

      setFormData({ ...formData, deliveryAddress: addressObj || null });
    } else {
      setFormData({ ...formData, deliveryAddress: address });
    }
  };

  const handleDateChange = (date: string) => {
    setFormData({ ...formData, deliveryDate: date });
  };

  const handleTimeChange = (time: string) => {
    setFormData({ ...formData, deliveryTime: time });
  };

  const handleNoteChange = (note: string) => {
    setFormData({ ...formData, note });
  };

  const handleNext = () => {
    if (step < 4) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return formData.client !== null;
      case 2:
        return formData.products.length > 0;
      case 3:
        return (
          formData.deliveryPhone !== null && formData.deliveryAddress !== null
        );
      case 4:
        return formData.deliveryDate !== "" && formData.deliveryTime !== "";
      default:
        return false;
    }
  };

  const getPhoneString = () => {
    if (typeof formData.deliveryPhone === "string") {
      return formData.deliveryPhone;
    }
    return formData.deliveryPhone?.number || "";
  };

  const getAddressString = () => {
    if (typeof formData.deliveryAddress === "string") {
      return formData.deliveryAddress;
    }
    if (!formData.deliveryAddress) return "";

    const addr = formData.deliveryAddress;
    return `${addr.street || ""} ${addr.house || ""} ${addr.apartment || ""} ${
      addr.entrance || ""
    } ${addr.floor || ""} ${addr.intercom || ""}`.trim();
  };

  return {
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
    handleNoteChange,

    handleNext,
    handleBack,
    canProceed,

    getPhoneString,
    getAddressString,
  };
};