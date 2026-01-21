import { useState, useEffect, useRef, useCallback } from "react";
import { useClient } from "../clients/useClients";
import { useProducts } from "../products/useProducts";
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
  deliveryPhone: any;
  deliveryAddress: any;
  deliveryDate: string;
  deliveryTime: string;
  paymentMethod: string;
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
  const [newlyCreatedClients, setNewlyCreatedClients] = useState<Client[]>([]);

  const {
    clients: fetchedClients,
    getClients,
    loadMoreClients,
    loadingMore: clientsLoadingMore,
    hasMore: clientsHasMore,
  } = useClient();

  // Merge newly created clients (at the top) with fetched clients
  const clients = [
    ...newlyCreatedClients.filter(
      (nc) => !fetchedClients.some((fc) => fc.client_id === nc.client_id)
    ),
    ...fetchedClients,
  ];

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
    deliveryTime: "",
    paymentMethod: "",
    note: "",
  });

  // Initial load
  useEffect(() => {
    getClients();
    getProducts();
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
              itemId: item.id,
            };
          })
          .filter((p: any) => p.product) || [];

      const phone =
        client?.phones?.find((p) => p.id === initialOrder.phone_id) ||
        client?.phones?.[0];
      const address =
        client?.addresses?.find((a) => a.id === initialOrder.address_id) ||
        client?.addresses?.[0];

      setFormData({
        client: client || null,
        products: orderProducts,
        deliveryPhone: phone || null,
        deliveryAddress: address || null,
        deliveryDate: initialOrder.date || "",
        deliveryTime: initialOrder.time_preference || "",
        paymentMethod: initialOrder.payment_method || "",
        note: initialOrder.note || "",
      });
    }
  }, [initialOrder, clients, products]);

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

  const handlePhoneChange = (phone: any) => {
    if (typeof phone === "string") {
      const phoneObj = formData.client?.phones?.find((p) => p.number === phone);
      setFormData({ ...formData, deliveryPhone: phoneObj || null });
    } else {
      setFormData({ ...formData, deliveryPhone: phone });
    }
  };

  const handleAddressChange = (address: any) => {
    if (typeof address === "string" || typeof address === "number") {
      const addressId =
        typeof address === "string" ? parseInt(address, 10) : address;
      const addressObj = formData.client?.addresses?.find(
        (a) => a.id === addressId
      );
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
        return formData.deliveryDate !== "" && formData.deliveryTime !== "" && formData.paymentMethod !== "";
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

  // Select newly created client
  const selectClientById = useCallback(
    (clientId: string) => {
      const client = clients.find((c) => c.client_id === clientId);
      if (client) {
        handleClientSelect(client);
      }
    },
    [clients]
  );

  const addAndSelectNewClient = useCallback((client: Client) => {
    setNewlyCreatedClients((prev) => [
      client,
      ...prev.filter((c) => c.client_id !== client.client_id),
    ]);
    handleClientSelect(client);
  }, []);

  return {
    step,
    formData,
    searchClient,
    searchProduct,
    clients,
    products,

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
    handleTimeChange,
    handleNoteChange,
    handlePaymentMethodChange,

    handleNext,
    handleBack,
    canProceed,

    getPhoneString,
    getAddressString,
    getAddressId,

    selectClientById,
    addAndSelectNewClient,
    refreshClients: getClients,
  };
};
