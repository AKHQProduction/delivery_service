import React, { useState, useEffect, useRef, useCallback } from "react";
import { useOrders } from "../../../hooks/orders/useOrders";
import { useClient } from "../../../hooks/clients/useClients";
import { useProducts } from "../../../hooks/products/useProducts";
import { useTimeSlotsSettings } from "../../../hooks/settings/useTimeSlotsSettings";
import { usePaymentMethodsSettings } from "../../../hooks/settings/usePaymentMethodsSettings";
import { getOrderById } from "../../../services/api/ordersApi";
import { getClientById } from "../../../services/api/clientApi";
import { type Client } from "../../../types/entities/Client";
import { type Product } from "../../../types/entities/Product";
import { SearchBar } from "../../ui/SearchBar";
import { DateInput } from "../../shared/DateInput";
import { FormSelect } from "../../shared/FormSelect";
import { convertDateToISO, formatLocalDateKey } from "../../../utils/dateUtils";
import { useError } from "../../../context/ErrorContext";
import { FormSkeleton, InlineListSkeleton } from "../../ui/Skeleton";
import { useUserShopStore } from "../../../context/useUserShopStore";

interface OrderItem {
  id?: number;
  product_id: string;
  name: string;
  price: number;
  quantity: number;
}

interface LoadedOrder {
  order_id: string;
  client_id?: string;
  phone_id?: number;
  address_id?: number;
  delivery_date?: string;
  date?: string;
  time_slot_id?: string;
  time_slot?: string;
  payment_method?: string;
  note?: string;
  comment?: string;
  items?: Array<{
    id: number;
    product_id: string;
    name?: string;
    price_per_item?: number;
    price?: number;
    quantity: number;
  }>;
}

interface EditOrderFormProps {
  order: { order_id: string };
  onClose: () => void;
  onSave?: () => void;
  onDelete?: () => void;
}

export const EditOrderForm: React.FC<EditOrderFormProps> = ({ onClose, onSave, order }) => {
  const { updateCurrentOrder } = useOrders();
  const { showWarning } = useError();
  const currentDate = useUserShopStore((s) => s.currentDate);
  const {
    clients,
    getClients,
    loadMoreClients,
    loading: clientsLoading,
    loadingMore: clientsLoadingMore,
    hasMore: clientsHasMore,
  } = useClient();
  const {
    products,
    getProducts,
    loadMoreProducts,
    loading: productsLoading,
    loadingMore: productsLoadingMore,
    hasMore: productsHasMore,
  } = useProducts();
  const { timeSlots, isLoaded: timeSlotsLoaded } = useTimeSlotsSettings();
  const { paymentMethods, isLoaded: paymentMethodsLoaded } = usePaymentMethodsSettings();

  // Form state
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [selectedPhoneId, setSelectedPhoneId] = useState<number | null>(null);
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null);
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
  const [loadedOrder, setLoadedOrder] = useState<LoadedOrder | null>(null);

  // Refs for infinite scroll
  const productListRef = useRef<HTMLDivElement>(null);
  const clientListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [orderData, , fetchedProducts] = await Promise.all([
          getOrderById(order.order_id) as Promise<LoadedOrder>,
          getClients(),
          getProducts(),
        ]);
        setLoadedOrder(orderData);

        if (orderData.client_id) {
          const orderClient = (await getClientById(orderData.client_id)) as Client;
          setSelectedClient(orderClient);

          const matchedPhone = orderClient?.phones?.find((p) => p.id === orderData.phone_id);
          const primaryPhone = orderClient?.phones?.find((p) => p.is_primary);
          setSelectedPhoneId(
            matchedPhone?.id || primaryPhone?.id || orderClient?.phones?.[0]?.id || null,
          );

          const matchedAddress = orderClient?.addresses?.find((a) => a.id === orderData.address_id);
          const primaryAddress = orderClient?.addresses?.find((a) => a.is_primary);
          setSelectedAddressId(
            matchedAddress?.id || primaryAddress?.id || orderClient?.addresses?.[0]?.id || null,
          );
        }

        const items: OrderItem[] =
          orderData.items?.map((item) => ({
            id: item.id,
            product_id: item.product_id,
            name:
              item.name ||
              fetchedProducts?.find((p) => p.product_id === item.product_id)?.name ||
              "",
            price:
              item.price_per_item ||
              item.price ||
              fetchedProducts?.find((p) => p.product_id === item.product_id)?.price ||
              0,
            quantity: item.quantity,
          })) || [];

        setOrderItems(items);
        const dateValue = orderData.delivery_date || orderData.date || "";
        const isoDate = convertDateToISO(dateValue);
        setDeliveryDate(isoDate);

        // Find matching time slot ID from the formatted time_slot string
        if (orderData.time_slot_id) {
          setTimeSlot(orderData.time_slot_id);
        } else if (orderData.time_slot) {
          // Match the formatted string like "13:33-23:12" with timeSlots
          const matchingSlot = timeSlots.find((slot) => {
            const formatTime = (timeStr: string) => (timeStr ? timeStr.slice(0, 5) : "");
            const slotFormatted = `${formatTime(slot.start_time)}-${formatTime(slot.end_time)}`;
            return slotFormatted === orderData.time_slot;
          });
          setTimeSlot(matchingSlot?.time_slot_id || "");
        }

        setPaymentMethod(orderData.payment_method || "");

        setNote(orderData.note || orderData.comment || "");
      } catch (error) {
        console.error("Error loading order:", error);
      }
    };
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clientSearch]);

  // Infinite scroll for products
  const handleProductScroll = useCallback(() => {
    if (!productListRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = productListRef.current;
    if (scrollHeight - scrollTop - clientHeight < 100 && productsHasMore && !productsLoadingMore) {
      loadMoreProducts();
    }
  }, [productsHasMore, productsLoadingMore, loadMoreProducts]);

  // Infinite scroll for clients
  const handleClientScroll = useCallback(() => {
    if (!clientListRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = clientListRef.current;
    if (scrollHeight - scrollTop - clientHeight < 100 && clientsHasMore && !clientsLoadingMore) {
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
        i === index ? { ...item, quantity: Math.max(1, item.quantity + delta) } : item,
      ),
    );
  };

  const handleRemoveItem = (index: number) => {
    setOrderItems((prev) => prev.filter((_, i) => i !== index));
  };

  const handleAddProduct = (product: Product) => {
    const existingIndex = orderItems.findIndex((item) => item.product_id === product.product_id);
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
  const totalAmount = orderItems.reduce((sum, item) => sum + item.price * item.quantity, 0);

  // Filter products for search (exclude already added)
  const availableProducts = products.filter(
    (p) => !orderItems.some((item) => item.product_id === p.product_id),
  );

  const formatTimeSlotLabel = (slot: {
    time_slot_id: string;
    start_time: string;
    end_time: string;
    label?: string;
  }) => {
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
      !loadedOrder ||
      !timeSlot
    ) {
      showWarning("Будь ласка, заповніть всі обов'язкові поля");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload: Record<string, unknown> = {};

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
      if (onSave) {
        onSave();
      } else {
        onClose();
      }
    } catch (error) {
      console.error("Error updating order:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!loadedOrder || !timeSlotsLoaded || !paymentMethodsLoaded) {
    return <FormSkeleton fields={6} />;
  }

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="space-y-5">
          <section className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2.5 mb-3">
              <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold shrink-0">
                1
              </span>
              <h3 className="text-sm font-bold text-gray-900">Клієнт</h3>
              {selectedClient && !showClientSearch && (
                <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              )}
            </div>

            {selectedClient && !showClientSearch ? (
              <div className="p-3 rounded-md border border-blue-600 bg-white flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                    {(selectedClient.full_name || "")
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .toUpperCase()
                      .slice(0, 2)}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 text-sm">
                      {selectedClient.full_name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {selectedClient.phones?.[0]?.number || ""}
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setShowClientSearch(true)}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  Змінити
                </button>
              </div>
            ) : (
              <>
                <SearchBar
                  searchTerm={clientSearch}
                  setSearchTerm={setClientSearch}
                  placeholder="Пошук за ім'ям або телефоном..."
                />
                <div
                  ref={clientListRef}
                  onScroll={handleClientScroll}
                  className="mt-2 space-y-1.5 max-h-48 overflow-y-auto"
                >
                  {clientsLoading && clients.length === 0 ? (
                    <InlineListSkeleton rows={3} variant="client" />
                  ) : clients.length === 0 ? (
                    <p className="text-sm text-gray-400 text-center py-4">Клієнтів не знайдено</p>
                  ) : (
                    clients.map((client) => (
                      <div
                        key={client.client_id}
                        onClick={() => handleClientSelect(client)}
                        className="p-3 rounded-md border border-gray-200 hover:border-blue-300 bg-white cursor-pointer transition-colors flex items-center gap-3"
                      >
                        <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-xs">
                          {(client.full_name || "")
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .toUpperCase()
                            .slice(0, 2)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900 text-sm truncate">
                            {client.full_name || "Unknown"}
                          </div>
                          <div className="text-xs text-gray-500">
                            {client.phones?.[0]?.number || "—"}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  {clientsLoadingMore && <InlineListSkeleton rows={2} variant="client" />}
                </div>
              </>
            )}
          </section>

          {selectedClient && (
            <section className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="flex items-center gap-2.5 mb-3">
                <h3 className="text-sm font-bold text-gray-900">Контактна інформація</h3>
                {selectedPhoneId && selectedAddressId && (
                  <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                )}
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Телефон <span className="text-red-500">*</span>
                  </label>
                  {selectedClient.phones && selectedClient.phones.length > 1 ? (
                    <select
                      title="Select phone"
                      value={selectedPhoneId || ""}
                      onChange={(e) => setSelectedPhoneId(Number(e.target.value))}
                      className="w-full px-3 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm bg-white"
                    >
                      <option value="">Оберіть телефон...</option>
                      {selectedClient.phones.map((phone) => (
                        <option key={phone.id} value={phone.id}>
                          {phone.number} {phone.is_primary ? "(основний)" : ""}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="px-3 py-2.5 bg-white border border-gray-200 rounded-md text-sm text-gray-900 font-medium">
                      {selectedClient.phones?.[0]?.number || "—"}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Адреса доставки <span className="text-red-500">*</span>
                  </label>
                  {selectedClient.addresses && selectedClient.addresses.length > 1 ? (
                    <select
                      title="Address select"
                      value={selectedAddressId || ""}
                      onChange={(e) => setSelectedAddressId(Number(e.target.value))}
                      className="w-full px-3 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm bg-white"
                    >
                      <option value="">Оберіть адресу...</option>
                      {selectedClient.addresses.map((addr) => (
                        <option key={addr.id} value={addr.id}>
                          {addr.street} {addr.house} {addr.is_primary ? "(основна)" : ""}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="px-3 py-2.5 bg-white border border-gray-200 rounded-md text-sm text-gray-900 font-medium">
                      {selectedClient.addresses?.[0]?.street} {selectedClient.addresses?.[0]?.house}
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}
        </div>

        <section className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2.5 mb-3">
            <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold shrink-0">
              2
            </span>
            <h3 className="text-sm font-bold text-gray-900">Товари</h3>
            {orderItems.length > 0 && (
              <>
                <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-xs text-gray-500 font-medium">
                  {orderItems.length} / {totalItems} шт.
                </span>
              </>
            )}
          </div>

          <div className="space-y-1.5">
            {orderItems.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">Немає товарів</p>
            ) : (
              orderItems.map((item, index) => (
                <div
                  key={`${item.product_id}-${index}`}
                  className="p-3 rounded-md border border-blue-600 bg-white"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 text-sm truncate">{item.name}</div>
                      <div className="text-xs font-semibold text-blue-600">{item.price} ₴</div>
                    </div>

                    <div className="flex items-center shrink-0">
                      <button
                        onClick={() => handleQuantityChange(index, -1)}
                        disabled={item.quantity <= 1}
                        type="button"
                        className="w-7 h-7 rounded-lg bg-gray-200 hover:bg-gray-300 disabled:opacity-50 flex items-center justify-center transition-colors font-bold text-sm"
                      >
                        −
                      </button>
                      <span className="w-10 text-center text-sm font-bold text-gray-900">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => handleQuantityChange(index, 1)}
                        type="button"
                        className="w-7 h-7 rounded-lg bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center transition-colors font-bold text-sm"
                      >
                        +
                      </button>
                      <button
                        title="remove"
                        onClick={() => handleRemoveItem(index)}
                        type="button"
                        className="ml-1.5 w-7 h-7 rounded-lg bg-red-100 hover:bg-red-200 text-red-600 flex items-center justify-center transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {!showAddProduct ? (
            <button
              type="button"
              onClick={() => setShowAddProduct(true)}
              className="mt-2 w-full py-2.5 border border-dashed border-gray-300 rounded-md text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-all font-medium text-sm flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Додати товар
            </button>
          ) : (
            <div className="mt-2 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-900 text-sm">Вибрати товар</span>
                <button
                  title="Product select"
                  type="button"
                  onClick={() => {
                    setShowAddProduct(false);
                    setProductSearch("");
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
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
                className="max-h-48 overflow-y-auto space-y-1.5"
              >
                {productsLoading && availableProducts.length === 0 ? (
                  <InlineListSkeleton rows={3} />
                ) : availableProducts.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-4">Товарів не знайдено</p>
                ) : (
                  availableProducts.map((product) => (
                    <div
                      key={product.product_id}
                      onClick={() => handleAddProduct(product)}
                      className="p-3 rounded-md border border-gray-200 hover:border-blue-300 bg-white cursor-pointer transition-colors flex items-center gap-3"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 text-sm truncate">{product.name}</div>
                        <div className="text-xs font-semibold text-blue-600">{product.price} ₴</div>
                      </div>
                      <button
                        type="button"
                        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-xs"
                      >
                        Додати
                      </button>
                    </div>
                  ))
                )}
                {productsLoadingMore && <InlineListSkeleton rows={2} />}
              </div>
            </div>
          )}

          {orderItems.length > 0 && (
            <div className="mt-3 p-3 bg-blue-100 rounded-md flex items-center justify-between">
              <div>
                <div className="text-xs text-gray-600">Всього до сплати</div>
                <div className="text-lg font-bold text-blue-600">{totalAmount} ₴</div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-600">Кількість</div>
                <div className="text-base font-bold text-gray-900">{totalItems} шт.</div>
              </div>
            </div>
          )}
        </section>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <section className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2.5 mb-3">
            <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold shrink-0">
              3
            </span>
            <h3 className="text-sm font-bold text-gray-900">Дата доставки</h3>
            {deliveryDate && timeSlot && (
              <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
          </div>

          <div className="space-y-3">
            <DateInput
              label="Дата доставки"
              value={deliveryDate}
              onChange={setDeliveryDate}
              required
              minDate={currentDate ?? formatLocalDateKey()}
            />

            <FormSelect
              label="Час доставки"
              name="timeSlot"
              value={timeSlot}
              required={true}
              onChange={(e) => setTimeSlot(e.target.value)}
              options={timeSlots.map((slot) => ({
                value: slot.time_slot_id,
                label: formatTimeSlotLabel(slot),
              }))}
            />
          </div>
        </section>

        <section className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2.5 mb-3">
            <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold shrink-0">
              4
            </span>
            <h3 className="text-sm font-bold text-gray-900">Оплата</h3>
            {paymentMethod && (
              <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
          </div>

          <div className="space-y-3">
            <FormSelect
              label="Спосіб оплати"
              name="paymentMethod"
              value={paymentMethod}
              required={true}
              onChange={(e) => setPaymentMethod(e.target.value)}
              options={paymentMethods.map((m) => ({
                value: m.name,
                label: m.name,
              }))}
            />

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Примітка</label>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Примітка до замовлення..."
                rows={2}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-sm bg-white"
              />
            </div>
          </div>
        </section>
      </div>

      <div className="sticky bottom-0 bg-white pt-4 pb-4">
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-3.5 rounded-md font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
          >
            Скасувати
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isSubmitting || !selectedClient || orderItems.length === 0}
            className={`flex-1 py-3.5 rounded-md font-semibold text-white transition-colors flex items-center justify-center gap-2 ${
              !isSubmitting && selectedClient && orderItems.length > 0
                ? "bg-blue-600 hover:bg-blue-700"
                : "bg-gray-300 cursor-not-allowed"
            }`}
          >
            {isSubmitting ? "Зберігаємо..." : "Зберегти"}
          </button>
        </div>
      </div>
    </div>
  );
};
