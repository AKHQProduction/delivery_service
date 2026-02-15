import { useEffect, useState, useRef } from "react";
import { PageHeader } from "../components/ui/PageHeader";
import { SearchBar } from "../components/ui/SearchBar";
import { useOrders } from "../hooks/orders/useOrders";
import { paymentMap } from "../utils/dataMap";
import { OrderDetailModal } from "../components/modals/detailsModals/OrderDetailModal";
import { RightModal } from "../components/modals/RightModal";
import { getOrderById } from "../services/api/ordersApi";
import { SearchFiltersPopup } from "../components/shared/SearchFiltersPopup";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";
import { DateInput } from "../components/shared/DateInput";
import { OrderCardSkeleton } from "../components/ui/Skeleton";
import { ExportPdfModal } from "../components/features/ExportPdfModal";

export interface OrderItem {
  name: string;
  quantity?: number | string;
  price_per_item?: number | string;
}

export interface DeliveryAddress {
  street?: string;
  house?: string;
}

export interface Order {
  order_id: string;

  client_name: string;
  items?: OrderItem[];

  delivery_phone?: string;
  delivery_address?: DeliveryAddress;

  date: string;
  time_slot: string;
  payment_method: keyof typeof paymentMap;

  note?: string;
  comment?: string;
}

export const OrdersPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const {
    getOrders,
    orders,
    deleteOrder,
    loadMoreOrders,
    setStartDate,
    setEndDate,
    startDate,
    endDate,
    loading,
    loadingMore,
    hasMore,
  } = useOrders();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { sentinelRef } = useInfiniteScroll({
    onLoadMore: loadMoreOrders,
    hasMore,
    isLoading: loadingMore,
  });

  useEffect(() => {
    const initOrders = async () => {
      await getOrders();

      const openOrderId = sessionStorage.getItem("openOrderId");
      if (openOrderId) {
        try {
          const order = (await getOrderById(openOrderId)) as Order;
          setSelectedOrder(order);
          setIsModalOpen(true);
        } catch {
          console.error("Failed to fetch order by ID");
        }
        sessionStorage.removeItem("openOrderId");
      }
    };
    initOrders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      getOrders(searchTerm);
    }, 100);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm]);

  const getOrderTotal = (order: Order) => {
    return (order.items ?? []).reduce((sum, item) => {
      const quantity = Number(item.quantity) || 0;
      const price = Number(item.price_per_item) || 0;
      return sum + quantity * price;
    }, 0);
  };

  const handleOrderClick = (order: Order) => {
    setSelectedOrder(order);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedOrder(null);
  };

  const handleDelete = async () => {
    if (!selectedOrder) return;

    await deleteOrder(selectedOrder.order_id);
    handleCloseModal();
    getOrders(searchTerm);
  };

  const handleSave = async () => {
    const orderId = selectedOrder?.order_id;
    const freshOrders = await getOrders(searchTerm);
    if (orderId && freshOrders) {
      const updatedOrder = freshOrders.find((o: { order_id: string }) => o.order_id === orderId);
      if (updatedOrder) {
        setSelectedOrder(updatedOrder as Order);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24 lg:bg-white lg:pb-8">
      <PageHeader title="Замовлення" />

      <div className="px-6 pb-4 flex items-center gap-3 relative lg:px-8">
        <div className="flex-1">
          <SearchBar
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            placeholder="Пошук замовлень..."
          />
        </div>

        <SearchFiltersPopup
          title="Фільтри замовлень"
          buttonTitle="Фільтри замовлень"
          onApply={() => getOrders(searchTerm)}
        >
          <DateInput label="Від" value={startDate} onChange={setStartDate} title="start date" />
          <DateInput label="До" value={endDate} onChange={setEndDate} title="end date" />
        </SearchFiltersPopup>
      </div>

      <div className="px-6 pb-4 lg:px-8">
        <button
          type="button"
          onClick={() => setIsExportModalOpen(true)}
          className="w-full px-4 py-3 bg-linear-to-r from-amber-500 to-orange-500 text-white rounded-2xl font-semibold shadow-md transition-all hover:from-amber-600 hover:to-orange-600 flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Сформувати документ
        </button>
      </div>

      <div className="px-6 pb-24 lg:pb-8 lg:px-8">
        {loading && (orders ?? []).length === 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <OrderCardSkeleton key={i} />
            ))}
          </div>
        ) : (orders ?? []).length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-gray-500 font-medium">Замовлень не знайдено</p>
            <p className="text-sm text-gray-400 mt-1">Спробуйте інший пошуковий запит</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {(orders ?? []).map((order) => {
              const typedOrder = order as unknown as Order;
              return (
                <div
                  key={order.order_id}
                  onClick={() => handleOrderClick(typedOrder)}
                  className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 cursor-pointer"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between w-full gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-9 h-9 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
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
                              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                            />
                          </svg>
                        </div>

                        <span className="text-gray-700 font-medium truncate">
                          {String(typedOrder.client_name)}
                        </span>
                      </div>

                      <span className="text-2xl font-bold text-indigo-600 whitespace-nowrap">
                        ₴{getOrderTotal(typedOrder)}
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-purple-100 flex items-center justify-center shrink-0">
                        <svg
                          className="w-5 h-5 text-purple-600"
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
                      </div>
                      <span className="text-gray-700">
                        {String(typedOrder.date)} | {String(typedOrder.time_slot)}
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-orange-100 flex items-center justify-center shrink-0">
                        <svg
                          className="w-5 h-5 text-orange-600"
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
                      </div>
                      <span className="text-gray-700">
                        {(typedOrder.items ?? []).reduce(
                          (sum: number, item: OrderItem) => sum + (Number(item.quantity) || 0),
                          0,
                        )}{" "}
                        товарів
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
            </div>

            <div ref={sentinelRef} className="py-4 flex justify-center">
              {loadingMore && (
                <div className="flex items-center gap-2 text-gray-500">
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
                  <span>Завантаження...</span>
                </div>
              )}
            </div>
          </>
        )}
      </div>

      <RightModal isOpen={isModalOpen} onClose={handleCloseModal}>
        {selectedOrder && (
          <OrderDetailModal
            order={selectedOrder}
            onClose={handleCloseModal}
            onDelete={handleDelete}
            onSave={handleSave}
          />
        )}
      </RightModal>

      <ExportPdfModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
      />
    </div>
  );
};
