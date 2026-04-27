import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useClient } from "../clients/useClients";
import { useProducts } from "../products/useProducts";
import { useTimeSlotsSettings } from "../settings/useTimeSlotsSettings";
import { usePaymentMethodsSettings } from "../settings/usePaymentMethodsSettings";
import { type Client } from "../../types/entities/Client";
import { type Product } from "../../types/entities/Product";

interface OrderFormProduct {
  product: Product;
  quantity: number;
  originalQuantity?: number;
  itemId?: number;
}

interface OrderFormData {
  client: Client | null;
  products: OrderFormProduct[];
  deliveryPhone: { id?: number; number: string; is_primary: boolean } | null;
  deliveryAddress: {
    id?: number;
    street: string;
    house: string;
    apartment?: string;
    entrance?: string;
    floor?: string;
    intercom?: string;
    is_primary: boolean;
    comment?: string;
    coordinates?: { latitude: number; longitude: number } | null;
    district_id?: string | null;
  } | null;
  deliveryDate: string;
  timeSlotId: string;
  paymentMethod: string;
  note?: string;
}

interface UseOrderFormOptions {
  initialOrder?: {
    client_id?: string;
    phone_id?: number;
    address_id?: number;
    delivery_date?: string;
    date?: string;
    time_slot_id?: string;
    payment_method?: string;
    comment?: string;
    note?: string;
    items?: Array<{
      id: number;
      product_id: string;
      name?: string;
      price_per_item?: number;
      quantity: number;
    }>;
  };
}

export const useOrderForm = (options: UseOrderFormOptions = {}) => {
  const { initialOrder } = options;
  const [step, setStep] = useState(1);
  const [searchClient, setSearchClient] = useState("");
  const [searchProduct, setSearchProduct] = useState("");
  const [newlyCreatedClients, setNewlyCreatedClients] = useState<Client[]>([]);

  const {
    clients: fetchedClients,
    getClients,
    loadMoreClients,
    loadingMore: clientsLoadingMore,
    hasMore: clientsHasMore,
  } = useClient();

  // Get time slots and payment methods
  const { timeSlots } = useTimeSlotsSettings();
  const { paymentMethods } = usePaymentMethodsSettings();

  // Merge newly created clients (at the top) with fetched clients
  const clients = useMemo(
    () => [
      ...newlyCreatedClients.filter(
        (nc) => !fetchedClients.some((fc) => fc.client_id === nc.client_id),
      ),
      ...fetchedClients,
    ],
    [newlyCreatedClients, fetchedClients],
  );

  const {
    products,
    getProducts,
    loadMoreProducts,
    loadingMore: productsLoadingMore,
    hasMore: productsHasMore,
  } = useProducts();

  const clientDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const productDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [formData, setFormData] = useState<OrderFormData>({
    client: null,
    products: [],
    deliveryPhone: null,
    deliveryAddress: null,
    deliveryDate: new Date().toISOString().split("T")[0],
    timeSlotId: "",
    paymentMethod: "",
    note: "",
  });

  // Initial load
  useEffect(() => {
    getClients();
    getProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Debounced client search
  useEffect(() => {
    if (clientDebounceRef.current) {
      clearTimeout(clientDebounceRef.current);
    }

    clientDebounceRef.current = setTimeout(() => {
      getClients(searchClient);
    }, 300);

    return () => {
      if (clientDebounceRef.current) {
        clearTimeout(clientDebounceRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchClient]);

  // Debounced product search
  useEffect(() => {
    if (productDebounceRef.current) {
      clearTimeout(productDebounceRef.current);
    }

    productDebounceRef.current = setTimeout(() => {
      getProducts(searchProduct);
    }, 300);

    return () => {
      if (productDebounceRef.current) {
        clearTimeout(productDebounceRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchProduct]);

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
          deliveryAddress: formData.client?.addresses?.[0] || null,
        }));
      }
    }
  }, [formData.client, initialOrder]);

  // Initialize form with existing order data (for editing)
  useEffect(() => {
    if (initialOrder && clients.length > 0 && products.length > 0) {
      const client = clients.find((c) => c.client_id === initialOrder.client_id);

      const orderProducts =
        initialOrder.items
          ?.map((item) => {
            const product = products.find((p) => p.product_id === item.product_id);
            return {
              product: product || {
                product_id: item.product_id,
                name: item.name || "",
                price: item.price_per_item || 0,
                category_id: "",
              },
              quantity: item.quantity,
              originalQuantity: item.quantity,
              itemId: item.id,
            };
          })
          .filter((p) => p.product) || [];

      const phone =
        client?.phones?.find((p) => p.id === initialOrder.phone_id) || client?.phones?.[0];
      const address =
        client?.addresses?.find((a) => a.id === initialOrder.address_id) || client?.addresses?.[0];

      setFormData({
        client: client || null,
        products: orderProducts,
        deliveryPhone: phone || null,
        deliveryAddress: address || null,
        deliveryDate: initialOrder.delivery_date || initialOrder.date || "",
        timeSlotId: initialOrder.time_slot_id || "",
        paymentMethod: initialOrder.payment_method || "",
        note: initialOrder.comment || initialOrder.note || "",
      });
    }
  }, [initialOrder, clients, products]);

  const handleClientSelect = useCallback((client: Client) => {
    setFormData((prev) => ({
      ...prev,
      client,
      deliveryPhone: client.phones?.[0] || null,
      deliveryAddress: client.addresses?.[0] || null,
      timeSlotId: initialOrder ? prev.timeSlotId : client.preferred_time_slot_id || "",
    }));
  }, [initialOrder]);

  const handleProductToggle = (product: Product) => {
    const exists = formData.products.find((p) => p.product.product_id === product.product_id);
    if (exists) {
      setFormData({
        ...formData,
        products: formData.products.filter((p) => p.product.product_id !== product.product_id),
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
        p.product.product_id === productId ? { ...p, quantity } : p,
      ),
    });
  };

  const handlePhoneChange = (
    phone: string | { id?: number; number: string; is_primary: boolean },
  ) => {
    if (typeof phone === "string") {
      const phoneObj = formData.client?.phones?.find((p) => p.number === phone);
      setFormData({ ...formData, deliveryPhone: phoneObj || null });
    } else {
      setFormData({ ...formData, deliveryPhone: phone });
    }
  };

  const handleAddressChange = (
    address:
      | string
      | number
      | {
          id?: number;
          street: string;
          house: string;
          apartment?: string;
          entrance?: string;
          floor?: string;
          intercom?: string;
          is_primary: boolean;
          comment?: string;
          coordinates?: { latitude: number; longitude: number } | null;
          district_id?: string | null;
        },
  ) => {
    if (typeof address === "string" || typeof address === "number") {
      const addressId = typeof address === "string" ? parseInt(address, 10) : address;
      const addressObj = formData.client?.addresses?.find((a) => a.id === addressId);
      setFormData({ ...formData, deliveryAddress: addressObj || null });
    } else {
      setFormData({ ...formData, deliveryAddress: address });
    }
  };

  const handleDateChange = (date: string) => {
    setFormData({ ...formData, deliveryDate: date });
  };

  const handlePaymentMethodChange = (paymentMethod: string) => {
    setFormData({ ...formData, paymentMethod });
  };

  const handleTimeSlotChange = (timeSlotId: string) => {
    setFormData({ ...formData, timeSlotId });
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
        return formData.deliveryPhone !== null && formData.deliveryAddress !== null;
      case 4:
        return (
          formData.deliveryDate !== "" &&
          formData.timeSlotId !== "" &&
          formData.paymentMethod !== ""
        );
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
    return `${addr.street || ""} ${addr.house || ""}`.trim();
  };

  const getAddressId = () => {
    return formData.deliveryAddress?.id?.toString() || "";
  };

  const getSelectedTimeSlot = () => {
    return timeSlots.find((slot) => slot.time_slot_id === formData.timeSlotId);
  };

  // Select newly created client
  const selectClientById = useCallback(
    (clientId: string) => {
      const client = clients.find((c) => c.client_id === clientId);
      if (client) {
        handleClientSelect(client);
      }
    },
    [clients, handleClientSelect],
  );

  const addAndSelectNewClient = useCallback(
    (client: Client) => {
      setNewlyCreatedClients((prev) => [
        client,
        ...prev.filter((c) => c.client_id !== client.client_id),
      ]);
      handleClientSelect(client);
    },
    [handleClientSelect],
  );

  // Format order data for API submission
  const getOrderPayload = () => {
    return {
      client_id: formData.client?.client_id || "",
      delivery_date: formData.deliveryDate,
      time_slot_id: formData.timeSlotId,
      address_id: formData.deliveryAddress?.id || 0,
      phone_id: formData.deliveryPhone?.id || 0,
      products: formData.products.map((p) => ({
        product_id: p.product.product_id,
        quantity: p.quantity,
      })),
      payment_method: formData.paymentMethod,
      comment: formData.note || "",
    };
  };

  return {
    step,
    formData,
    searchClient,
    searchProduct,
    clients,
    products,
    timeSlots,
    paymentMethods,

    // Infinite scroll for clients
    loadMoreClients,
    clientsLoadingMore,
    clientsHasMore,

    // Infinite scroll for products
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
    handleNoteChange,
    handlePaymentMethodChange,

    handleNext,
    handleBack,
    canProceed,

    getPhoneString,
    getAddressString,
    getAddressId,
    getSelectedTimeSlot,
    getOrderPayload,

    selectClientById,
    addAndSelectNewClient,
    refreshClients: getClients,
  };
};
