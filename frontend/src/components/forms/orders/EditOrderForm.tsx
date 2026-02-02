import React, { useState, useEffect, useRef, useCallback } from "react";
import { useOrders } from "../../../hooks/orders/useOrders";
import { useClient } from "../../../hooks/clients/useClients";
import { useProducts } from "../../../hooks/products/useProducts";
import { useTimeSlotsSettings } from "../../../hooks/settings/useTimeSlotsSettings";
import { getOrderById } from "../../../services/api/ordersApi";
import { getClientById } from "../../../services/api/clientApi";
import { type Client } from "../../../types/entities/Client";
import { type Product } from "../../../types/entities/Product";
import { SearchBar } from "../../ui/searchBar";
import { DateSelectInput } from "../../shared/DateSelectInput";
import { FormSelect } from "../../shared/FormSelect";

interface OrderItem {
  id?: number;
  product_id: string;
  name: string;
  price: number;
  quantity: number;
}

interface EditOrderFormProps {
  order: any;
  onClose: () => void;
  onSave?: () => void;
  onDelete?: () => void;
}

export const EditOrderForm: React.FC<EditOrderFormProps> = ({
  onClose,
  onSave,
  order,
}) => {
  const { updateCurrentOrder } = useOrders();
  const {
    clients,
    getClients,
    loadMoreClients,
    loadingMore: clientsLoadingMore,
    hasMore: clientsHasMore,
  } = useClient();
  const {
    products,
    getProducts,
    loadMoreProducts,
    loadingMore: productsLoadingMore,
    hasMore: productsHasMore,
  } = useProducts();
  const { timeSlots } = useTimeSlotsSettings();

  // Form state
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [selectedPhoneId, setSelectedPhoneId] = useState<number | null>(null);
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(
    null,
  );
  const [orderItems, setOrderItems] = useState<OrderItem[]>([]);
  const [deliveryDate, setDeliveryDate] = useState("");
  const [timeSlot, setTimeSlot] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("");
  const [note, setNote] = useState("");

  // UI state
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [showClientSearch, setShowClientSearch] = useState(false);
  const [productSearch, setProductSearch] = useState("");
  const [clientSearch, setClientSearch] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadedOrder, setLoadedOrder] = useState<any>(null);

  // Refs for infinite scroll
  const productListRef = useRef<HTMLDivElement>(null);
  const clientListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [orderData, , fetchedProducts] = await Promise.all([
          getOrderById(order.order_id),
          getClients(),
          getProducts(),
        ]);
        setLoadedOrder(orderData);

        if (orderData.client_id) {
          const orderClient = await getClientById(orderData.client_id);
          setSelectedClient(orderClient);

          const matchedPhone = orderClient?.phones?.find(
            (p: any) => p.id === orderData.phone_id,
          );
          const primaryPhone = orderClient?.phones?.find(
            (p: any) => p.is_primary,
          );
          setSelectedPhoneId(
            matchedPhone?.id ||
              primaryPhone?.id ||
              orderClient?.phones?.[0]?.id ||
              null,
          );

          const matchedAddress = orderClient?.addresses?.find(
            (a: any) => a.id === orderData.address_id,
          );
          const primaryAddress = orderClient?.addresses?.find(
            (a: any) => a.is_primary,
          );
          setSelectedAddressId(
            matchedAddress?.id ||
              primaryAddress?.id ||
              orderClient?.addresses?.[0]?.id ||
              null,
          );
        }

        const items: OrderItem[] =
          orderData.items?.map((item: any) => ({
            id: item.id,
            product_id: item.product_id,
            name:
              item.name ||
              fetchedProducts?.find(
                (p: any) => p.product_id === item.product_id,
              )?.name ||
              "",
            price:
              item.price_per_item ||
              item.price ||
              fetchedProducts?.find(
                (p: any) => p.product_id === item.product_id,
              )?.price ||
              0,
            quantity: item.quantity,
          })) || [];

        setOrderItems(items);
        setDeliveryDate(orderData.delivery_date || orderData.date || "");
        
        // Find matching time slot ID from the formatted time_slot string
        if (orderData.time_slot_id) {
          setTimeSlot(orderData.time_slot_id);
        } else if (orderData.time_slot) {
          // Match the formatted string like "13:33-23:12" with timeSlots
          const matchingSlot = timeSlots.find(slot => {
            const formatTime = (timeStr: string) => timeStr ? timeStr.slice(0, 5) : "";
            const slotFormatted = `${formatTime(slot.start_time)}-${formatTime(slot.end_time)}`;
            return slotFormatted === orderData.time_slot;
          });
          setTimeSlot(matchingSlot?.time_slot_id || "");
        }
        
        setPaymentMethod(orderData.payment_method || "");
        setNote(orderData.note || orderData.comment || "");
        console.log("Loaded order data:", orderData);
      } catch (error) {
        console.error("Error loading order:", error);
      }
    };
    loadData();
  }, [order.order_id, timeSlots]);

  const productDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    if (productDebounceRef.current) clearTimeout(productDebounceRef.current);
    productDebounceRef.current = setTimeout(() => {
      getProducts(productSearch);
    }, 300);
    return () => {
      if (productDebounceRef.current) clearTimeout(productDebounceRef.current);
    };
  }, [productSearch]);

  const clientDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    if (clientDebounceRef.current) clearTimeout(clientDebounceRef.current);
    clientDebounceRef.current = setTimeout(() => {
      getClients(clientSearch);
    }, 300);
    return () => {
      if (clientDebounceRef.current) clearTimeout(clientDebounceRef.current);
    };
  }, [clientSearch]);

  // Infinite scroll for products
  const handleProductScroll = useCallback(() => {
    if (!productListRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = productListRef.current;
    if (
      scrollHeight - scrollTop - clientHeight < 100 &&
      productsHasMore &&
      !productsLoadingMore
    ) {
      loadMoreProducts();
    }
  }, [productsHasMore, productsLoadingMore, loadMoreProducts]);

  // Infinite scroll for clients
  const handleClientScroll = useCallback(() => {
    if (!clientListRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = clientListRef.current;
    if (
      scrollHeight - scrollTop - clientHeight < 100 &&
      clientsHasMore &&
      !clientsLoadingMore
    ) {
      loadMoreClients();
    }
  }, [clientsHasMore, clientsLoadingMore, loadMoreClients]);

  // Handle client selection
  const handleClientSelect = (client: Client) => {
    setSelectedClient(client);
    setSelectedPhoneId(client.phones?.[0]?.id || null);
    setSelectedAddressId(client.addresses?.[0]?.id || null);
    setShowClientSearch(false);
    setClientSearch("");
  };

  // Order items management
  const handleQuantityChange = (index: number, delta: number) => {
    setOrderItems((prev) =>
      prev.map((item, i) =>
        i === index
          ? { ...item, quantity: Math.max(1, item.quantity + delta) }
          : item,
      ),
    );
  };

  const handleRemoveItem = (index: number) => {
    setOrderItems((prev) => prev.filter((_, i) => i !== index));
  };

  const handleAddProduct = (product: Product) => {
    const existingIndex = orderItems.findIndex(
      (item) => item.product_id === product.product_id,
    );
    if (existingIndex >= 0) {
      handleQuantityChange(existingIndex, 1);
    } else {
      setOrderItems((prev) => [
        ...prev,
        {
          product_id: product.product_id,
          name: product.name,
          price: product.price,
          quantity: 1,
        },
      ]);
    }
    setShowAddProduct(false);
    setProductSearch("");
  };

  // Calculate totals
  const totalItems = orderItems.reduce((sum, item) => sum + item.quantity, 0);
  const totalAmount = orderItems.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0,
  );

  // Filter products for search (exclude already added)
  const availableProducts = products.filter(
    (p) => !orderItems.some((item) => item.product_id === p.product_id),
  );

  const formatTimeSlotLabel = (slot: any) => {
    const formatTime = (timeStr: string) => {
      if (!timeStr) return "";
      // Handle both HH:MM:SS and HH:MM formats
      return timeStr.slice(0, 5);
    };

    const start = formatTime(slot.start_time);
    const end = formatTime(slot.end_time);
    
    if (slot.label) {
      return `${slot.label} (${start} - ${end})`;
    }
    return `${start} - ${end}`;
  };

  const handleSubmit = async () => {
    if (
      !selectedClient ||
      !selectedPhoneId ||
      !selectedAddressId ||
      orderItems.length === 0 ||
      !loadedOrder
    ) {
      alert("Будь ласка, заповніть всі обов'язкові поля");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload: Record<string, any> = {};

      if (selectedClient.client_id !== loadedOrder.client_id) {
        payload.client_id = selectedClient.client_id;
      }

      // Always send phone_id and address_id
      payload.phone_id = selectedPhoneId;
      payload.address_id = selectedAddressId;

      if (deliveryDate !== loadedOrder.delivery_date && deliveryDate !== loadedOrder.date) {
        payload.delivery_date = deliveryDate;
      }
      if (timeSlot !== loadedOrder.time_slot_id) {
        payload.time_slot_id = timeSlot;
      }
      if (paymentMethod !== loadedOrder.payment_method) {
        payload.payment_method = paymentMethod;
      }
      if (note !== (loadedOrder.note || loadedOrder.comment || "")) {
        payload.comment = note;
      }

      payload.items = orderItems.map((item) => {
        if (item.id) {
          return { id: item.id, quantity: item.quantity };
        } else {
          return { product_id: item.product_id, quantity: item.quantity };
        }
      });

      console.log("Submitting payload:", payload);
      await updateCurrentOrder(order.order_id, payload);
      onSave ? onSave() : onClose();
    } catch (error) {
      console.error("Error updating order:", error);
      alert("Помилка при оновленні замовлення");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col h-full ">
      {/* Content */}
      <div className="flex-1 overflow-y-auto space-y-6">
        {/* Order Items Section */}
        <div className="space-y-3">
          {orderItems.length === 0 ? (
            <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-xl">
              <svg
                className="w-12 h-12 mx-auto mb-3 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
              </svg>
              <p className="font-medium">Немає товарів</p>
              <p className="text-sm">Додайте товари до замовлення</p>
            </div>
          ) : (
            orderItems.map((item, index) => (
              <div
                key={`${item.product_id}-${index}`}
                className="p-4 rounded-xl border-2 border-indigo-600 bg-indigo-50"
              >
                <div className="flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-gray-900 truncate">
                      {item.name}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-base font-bold text-indigo-600">
                        {item.price} ₴
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center shrink-0">
                    <button
                      onClick={() => handleQuantityChange(index, -1)}
                      disabled={item.quantity <= 1}
                      type="button"
                      className="w-9 h-9 rounded-lg bg-gray-200 hover:bg-gray-300 disabled:opacity-50 flex items-center justify-center transition-colors font-bold text-lg"
                    >
                      −
                    </button>
                    <div className="w-14 text-center">
                      <span className="text-lg font-bold text-gray-900">
                        {item.quantity}
                      </span>
                    </div>
                    <button
                      onClick={() => handleQuantityChange(index, 1)}
                      type="button"
                      className="w-9 h-9 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center transition-colors font-bold text-lg"
                    >
                      +
                    </button>
                    <button
                      title="remove"
                      onClick={() => handleRemoveItem(index)}
                      type="button"
                      className="ml-2 w-9 h-9 rounded-lg bg-red-100 hover:bg-red-200 text-red-600 flex items-center justify-center transition-colors"
                    >
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}

          {/* Add Product Button */}
          {!showAddProduct ? (
            <button
              onClick={() => setShowAddProduct(true)}
              className="w-full py-3 border-2 border-dashed border-gray-300 rounded-xl text-gray-500 hover:border-indigo-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors flex items-center justify-center gap-2 font-medium"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Додати товар
            </button>
          ) : (
            <div className="bg-white rounded-xl border-2 border-indigo-200 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-900">Вибрати товар</span>
                <button
                  title="Product select"
                  type="button"
                  onClick={() => {
                    setShowAddProduct(false);
                    setProductSearch("");
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              <SearchBar
                searchTerm={productSearch}
                setSearchTerm={setProductSearch}
                placeholder="Пошук товару..."
              />

              <div
                ref={productListRef}
                onScroll={handleProductScroll}
                className="max-h-48 overflow-y-auto space-y-2"
              >
                {availableProducts.length === 0 ? (
                  <p className="text-center text-gray-500 py-4 text-sm">
                    Товарів не знайдено
                  </p>
                ) : (
                  availableProducts.map((product) => (
                    <div
                      key={product.product_id}
                      onClick={() => handleAddProduct(product)}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-indigo-50 cursor-pointer transition-colors"
                    >
                      <div>
                        <div className="font-medium text-gray-900">
                          {product.name}
                        </div>
                        <div className="text-sm text-indigo-600 font-semibold">
                          {product.price} ₴
                        </div>
                      </div>
                      <svg
                        className="w-5 h-5 text-indigo-600"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 4v16m8-8H4"
                        />
                      </svg>
                    </div>
                  ))
                )}
                {productsLoadingMore && (
                  <div className="flex justify-center py-2">
                    <svg
                      className="animate-spin h-5 w-5 text-indigo-600"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Order Total */}
          {orderItems.length > 0 && (
            <div className="p-4 bg-linear-to-r from-indigo-600 to-purple-600 rounded-xl text-white">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm opacity-90">Всього</div>
                  <div className="text-xl font-bold">{totalItems} шт.</div>
                </div>
                <div className="text-right">
                  <div className="text-sm opacity-90">До сплати</div>
                  <div className="text-2xl font-bold">{totalAmount} ₴</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Client Section */}
        <div className="space-y-3">
          <label className="text-sm font-medium text-gray-700">
            Клієнт <span className="text-red-500">*</span>
          </label>

          {!showClientSearch ? (
            <div
              onClick={() => setShowClientSearch(true)}
              className="p-4 bg-white rounded-xl border-2 border-gray-200 cursor-pointer hover:border-indigo-300 transition-colors"
            >
              {selectedClient ? (
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold shrink-0">
                    {(selectedClient.full_name || "")
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .toUpperCase()
                      .slice(0, 2)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-gray-900">
                      {selectedClient.full_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {selectedClient.phones?.[0]?.number || "—"}
                    </div>
                  </div>
                  <svg
                    className="w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              ) : (
                <div className="flex items-center justify-between text-gray-500">
                  <span>Оберіть клієнта...</span>
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-xl border-2 border-indigo-200 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-900">
                  Вибрати клієнта
                </span>
                <button
                  title="Client choose"
                  type="button"
                  onClick={() => {
                    setShowClientSearch(false);
                    setClientSearch("");
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              <SearchBar
                searchTerm={clientSearch}
                setSearchTerm={setClientSearch}
                placeholder="Пошук за ім'ям або телефоном..."
              />

              <div
                ref={clientListRef}
                onScroll={handleClientScroll}
                className="max-h-48 overflow-y-auto space-y-2"
              >
                {clients.length === 0 ? (
                  <p className="text-center text-gray-500 py-4 text-sm">
                    Клієнтів не знайдено
                  </p>
                ) : (
                  clients.map((client) => (
                    <div
                      key={client.client_id}
                      onClick={() => handleClientSelect(client)}
                      className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedClient?.client_id === client.client_id
                          ? "bg-indigo-50 border-2 border-indigo-300"
                          : "bg-gray-50 hover:bg-gray-100"
                      }`}
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                          selectedClient?.client_id === client.client_id
                            ? "bg-indigo-600 text-white"
                            : "bg-gray-300 text-gray-600"
                        }`}
                      >
                        {(client.full_name || "")
                          .split(" ")
                          .map((n) => n[0])
                          .join("")
                          .toUpperCase()
                          .slice(0, 2)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 truncate">
                          {client.full_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {client.phones?.[0]?.number || "—"}
                        </div>
                      </div>
                      {selectedClient?.client_id === client.client_id && (
                        <svg
                          className="w-5 h-5 text-indigo-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </div>
                  ))
                )}
                {clientsLoadingMore && (
                  <div className="flex justify-center py-2">
                    <svg
                      className="animate-spin h-5 w-5 text-indigo-600"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Phone & Address */}
          {selectedClient && (
            <div className="space-y-3">
              {/* Phone */}
              {selectedClient.phones && selectedClient.phones.length > 1 ? (
                <div className="relative">
                  <select
                    title="Select phone"
                    value={selectedPhoneId || ""}
                    onChange={(e) => setSelectedPhoneId(Number(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 appearance-none bg-white pr-10 font-medium"
                  >
                    <option value="">Оберіть телефон...</option>
                    {selectedClient.phones.map((phone) => (
                      <option key={phone.id} value={phone.id}>
                        {phone.number} {phone.is_primary ? "(основний)" : ""}
                      </option>
                    ))}
                  </select>
                  <svg
                    className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              ) : (
                <div className="px-4 py-3 bg-indigo-50 border-2 border-indigo-200 rounded-xl font-medium text-gray-900 flex items-center gap-2">
                  <svg
                    className="w-5 h-5 text-indigo-600"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  {selectedClient.phones?.[0]?.number || "Немає телефону"}
                </div>
              )}

              {/* Address */}
              {selectedClient.addresses &&
              selectedClient.addresses.length > 1 ? (
                <div className="relative">
                  <select
                    title="Address select"
                    value={selectedAddressId || ""}
                    onChange={(e) =>
                      setSelectedAddressId(Number(e.target.value))
                    }
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 appearance-none bg-white pr-10 font-medium"
                  >
                    <option value="">Оберіть адресу...</option>
                    {selectedClient.addresses.map((addr) => (
                      <option key={addr.id} value={addr.id}>
                        {addr.street} {addr.house}{" "}
                        {addr.is_primary ? "(основна)" : ""}
                      </option>
                    ))}
                  </select>
                  <svg
                    className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              ) : (
                <div className="px-4 py-3 bg-indigo-50 border-2 border-indigo-200 rounded-xl font-medium text-gray-900 flex items-center gap-2">
                  <svg
                    className="w-5 h-5 text-indigo-600"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  {selectedClient.addresses?.[0]
                    ? `${selectedClient.addresses[0].street} ${selectedClient.addresses[0].house}`
                    : "Немає адреси"}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Delivery Date Section */}
        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pb-3">
            
            <DateSelectInput
              value={deliveryDate}
              onChange={setDeliveryDate}
              required
              minDate={new Date().toISOString().split("T")[0]}
              icon={
                <svg
                  className="w-5 h-5 text-indigo-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              }
            />

            <FormSelect
              label="Час"
              name="timeSlot"
              value={timeSlot}
              required={true}
              onChange={setTimeSlot}
              options={[
                ...timeSlots.map((slot) => ({
                  value: slot.time_slot_id,
                  label: formatTimeSlotLabel(slot),
                })),
              ]}
            />

            <FormSelect
              label="Спосіб оплати"
              name="paymentMethod"
              value={paymentMethod}
              required={true}
              onChange={setPaymentMethod}
              options={[
                { value: "CASH", label: "Готівка" },
                { value: "BANK_TRANSFER", label: "На рахунок" },
                { value: "OTHER", label: "Інше" },
              ]}
            />
          </div>

          {/* Note */}
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Примітка для кур'єра..."
            rows={2}
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none text-sm"
          />
        </div>
      </div>

      {/* Footer Actions */}
      <div className="pt-4 border-t border-gray-200 mt-4">
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-colors"
          >
            Скасувати
          </button>

          <button
            onClick={handleSubmit}
            disabled={
              isSubmitting || !selectedClient || orderItems.length === 0
            }
            className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            ) : null}
            Зберегти
          </button>
        </div>
      </div>
    </div>
  );
};