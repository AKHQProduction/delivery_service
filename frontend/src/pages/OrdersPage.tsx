import { useEffect, useState } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { useOrders } from "../hooks/orders/useOrders";
import { timeMap } from "../utils/dataMap";
import { OrderDetailModal } from "../components/modals/detailsModals/OrderDetailModal";
import { RightModal } from "../components/modals/RightModal";

export const OrdersPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const { getOrders, orders, deleteOrder } = useOrders();

  useEffect(() => {
    getOrders();
  }, []);

  const ordersList = (orders ?? []).filter((order) =>
    order.client_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getOrderTotal = (order) => {
    return (order.items ?? []).reduce((sum, item) => {
      const quantity = Number(item.quantity) || 0;
      const price = Number(item.price_per_item) || 0;
      return sum + quantity * price;
    }, 0);
  };

  const handleOrderClick = (order) => {
    setSelectedOrder(order);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedOrder(null);
  };

  const handleEditClick = () => {
    // Navigate to edit page or open edit modal
    console.log("Edit order:", selectedOrder);
  };

  const handleDelete = async () => {
    if (
      selectedOrder &&
      confirm("Ви впевнені, що хочете видалити це замовлення?")
    ) {
      await deleteOrder(selectedOrder.order_id);
      handleCloseModal();
      getOrders();
    }
  };

  const handleSave = () => {
    handleCloseModal();
    getOrders();
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      <PageHeader title="Замовлення" />

      <div className="px-6 pb-4">
        <SearchBar
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          placeholder="Пошук замовлень..."
        />
      </div>

      <div className="pt-6 pb-4 w-full px-6">
        <div className="bg-linear-to-r from-yellow-50 to-amber-50 border-2 border-yellow-200 rounded-2xl p-4">
          <div className="flex items-start gap-3">
            <svg
              className="w-6 h-6 text-amber-600 shrink-0 mt-1"
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

            <div className="flex-1">
              <h3 className="font-bold text-amber-900 mb-2">
                Сформувати документ по замовленням
              </h3>

              <div className="flex items-center gap-3 flex-wrap pl-6 sm:pl-9">
                <input
                  type="date"
                  className="w-48 max-w-full px-3 py-2 border border-amber-300 rounded-lg bg-white
               focus:outline-none focus:ring-2 focus:ring-amber-400"
                />

                <button
                  className="px-4 py-2 bg-gradient-to-r from-amber-500  to-orange-500 text-white
               rounded-lg font-semibold shadow-md transition-all
               hover:from-amber-600 hover:to-orange-600
               flex items-center justify-center gap-2 whitespace-nowrap"
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
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                    />
                  </svg>
                  Завантажити
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 space-y-3">
        {ordersList.length === 0 ? (
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
            <p className="text-sm text-gray-400 mt-1">
              Спробуйте інший пошуковий запит
            </p>
          </div>
        ) : (
          ordersList.map((order) => (
            <div
              key={order.order_id}
              onClick={() => handleOrderClick(order)}
              className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md hover:-translate-y-0.5 transition-all cursor-pointer"
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
                      {order.client_name}
                    </span>
                  </div>

                  <span className="text-2xl font-bold text-indigo-600 whitespace-nowrap">
                    ₴{getOrderTotal(order)}
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
                    {order.date} - {timeMap[order.time_preference]}
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
                    {order.items.length} товари
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <RightModal isOpen={isModalOpen} onClose={handleCloseModal}>
        {selectedOrder && (
          <OrderDetailModal
            order={selectedOrder}
            onClose={handleCloseModal}
            handleEditClick={handleEditClick}
            onDelete={handleDelete}
            onSave={handleSave}
          />
        )}
      </RightModal>
    </div>
  );
};
