import { useEffect, useState } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { useOrders } from "../hooks/orders/useOrders";

export const OrdersPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const { getOrders, orders } = useOrders();

  useEffect(() => {
    getOrders();
  }, []);

  const ordersList = (orders ?? []).filter((order) =>
    order.client_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <PageHeader title="Замовлення" />

      <div className="px-6 pb-4">
        <SearchBar
          placeholder="Пошук замовлень"
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
        />
      </div>
      {ordersList.length === 0 ? (
        <div className="flex flex-col items-center justify-center mt-20">
          <p className="text-gray-500 text-lg font-medium">
            {searchTerm ? "Замовлення не знайдено" : "Замовлення відсутні"}
          </p>
          {searchTerm && (
            <p className="text-gray-400 text-sm mt-2">
              Спробуйте інший пошуковий запит
            </p>
          )}
        </div>
      ) : (
        <div className="px-6 pb-24">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {ordersList.map((order) => (
              <div key={order.order_id}>{order.client_name}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
