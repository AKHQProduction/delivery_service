import { useEffect, useMemo, useRef, useState } from "react";
import { AddOrderForm } from "../components/forms/orders/AddOrderForm";
import { ExportPdfModal } from "../components/features/ExportPdfModal";
import { DetailModal } from "../components/modals/DetailModal";
import { Modal } from "../components/modals/Modal";
import { OrderDetailModal } from "../components/modals/detailsModals/OrderDetailModal";
import {
  OrderCardSkeleton,
  SidePanelSkeleton,
  SummaryCardsSkeleton,
  TableSkeleton,
} from "../components/ui/Skeleton";
import { ConfirmDeleteModal } from "../components/ui/ConfirmDeleteModal";
import { DateRangePicker } from "../components/ui/DateRangePicker";
import { FloatingAddButton } from "../components/ui/FloatingAddButton";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";
import { useOrders } from "../hooks/orders/useOrders";
import { getOrderById } from "../services/api/ordersApi";
import { type Order } from "../types/entities/Order";

type OrderFilter = "all" | "today" | "tomorrow";

const formatMoney = (value: number) => `${value.toLocaleString("uk-UA")} ₴`;

const formatDate = (value?: string) => {
  if (!value) return "Дата не вказана";
  if (/^\d{2}\.\d{2}\.\d{4}$/.test(value)) return value;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("uk-UA", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};

const getOrderTotal = (order: Order) =>
  (order.items ?? []).reduce((sum, item) => {
    const quantity = Number(item.quantity) || 0;
    const price = Number(item.price_per_item) || 0;
    return sum + quantity * price;
  }, 0);

const getAddressText = (order: Order) => {
  const address = order.delivery_address;
  if (!address) return "Адресу не вказано";
  return [address.street, address.house, address.apartment ? `кв. ${address.apartment}` : ""]
    .filter(Boolean)
    .join(", ");
};

const getInitials = (name?: string) => {
  const parts = (name || "Клієнт").trim().split(/\s+/).filter(Boolean);
  return parts
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toLocaleUpperCase("uk-UA");
};

export const OrdersPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isDetailEditing, setIsDetailEditing] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [orderPendingDelete, setOrderPendingDelete] = useState<Order | null>(null);
  const [pausePlanningAfterDelete, setPausePlanningAfterDelete] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<OrderFilter>("all");
  const [paymentError, setPaymentError] = useState("");
  const {
    getOrders,
    orders,
    summary,
    deleteOrder,
    payFromBalance,
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
  const hasInitializedSearchRef = useRef(false);

  const orderList = useMemo(() => orders ?? [], [orders]);

  const { sentinelRef } = useInfiniteScroll({
    onLoadMore: loadMoreOrders,
    hasMore,
    isLoading: loadingMore,
  });

  useEffect(() => {
    const initOrders = async () => {
      const initialOrders = await getOrders();
      setSelectedOrder((initialOrders[0] as Order | undefined) ?? null);

      const openOrderId = sessionStorage.getItem("openOrderId");
      if (openOrderId) {
        try {
          const order = (await getOrderById(openOrderId)) as Order;
          setSelectedOrder(order);
          setIsDetailModalOpen(true);
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
    if (!hasInitializedSearchRef.current) {
      hasInitializedSearchRef.current = true;
      return;
    }

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      getOrders(searchTerm, selectedFilter);
    }, 200);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, selectedFilter]);

  useEffect(() => {
    if (!hasInitializedSearchRef.current) return;
    getOrders(searchTerm, selectedFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startDate, endDate]);

  const filterChips = useMemo(() => {
    return [
      { id: "all" as const, label: "Усі", count: summary.total_count },
      { id: "today" as const, label: "Сьогодні", count: summary.today_count },
      { id: "tomorrow" as const, label: "Завтра", count: summary.tomorrow_count },
    ];
  }, [summary]);

  const selectedOrderTotal =
    selectedFilter === "today"
      ? summary.today_count
      : selectedFilter === "tomorrow"
        ? summary.tomorrow_count
        : summary.total_count;

  useEffect(() => {
    if (selectedOrder) {
      const updatedSelection = orderList.find((order) => order.order_id === selectedOrder.order_id);
      if (updatedSelection) {
        setSelectedOrder(updatedSelection);
      }
    } else if (orderList.length > 0) {
      setSelectedOrder(orderList[0]);
    }
  }, [orderList, selectedOrder]);

  const refreshOrders = async () => {
    const refreshedOrders = await getOrders(searchTerm, selectedFilter);
    return refreshedOrders as Order[];
  };

  const handleOpenOrder = (order: Order, edit = false) => {
    setSelectedOrder(order);
    setIsDetailEditing(edit);
    setPaymentError("");
    setIsDetailModalOpen(true);
  };

  const handleCloseDetail = () => {
    setIsDetailModalOpen(false);
    setIsDetailEditing(false);
    setPaymentError("");
  };

  const handleDelete = async () => {
    if (!orderPendingDelete) return;

    const order = orderPendingDelete;
    await deleteOrder(order.order_id, {
      pause_recurring_order:
        pausePlanningAfterDelete && Boolean(order.recurring_order_id),
    });
    if (selectedOrder?.order_id === order.order_id) {
      setSelectedOrder(null);
      setIsDetailModalOpen(false);
    }
    setOrderPendingDelete(null);
    setPausePlanningAfterDelete(false);
    await refreshOrders();
  };

  const handleSave = async () => {
    const orderId = selectedOrder?.order_id;
    const refreshedOrders = await refreshOrders();
    if (orderId) {
      const updatedOrder = refreshedOrders.find((order) => order.order_id === orderId);
      if (updatedOrder) {
        setSelectedOrder(updatedOrder);
      }
    }
  };

  const handleOrderCreated = async () => {
    setIsAddModalOpen(false);
    const refreshedOrders = await refreshOrders();
    setSelectedOrder(refreshedOrders[0] ?? null);
  };

  const handlePayFromBalance = async (orderId: string) => {
    setPaymentError("");
    try {
      await payFromBalance(orderId);
      const refreshedOrder = (await getOrderById(orderId)) as Order;
      setSelectedOrder(refreshedOrder);
      await refreshOrders();
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Не вдалося списати кошти з балансу.";
      setPaymentError(message);
    }
  };

  const emptyTitle = searchTerm ? "Замовлень не знайдено" : "Замовлень поки немає";
  const emptyDescription = searchTerm
    ? "Спробуйте інший пошуковий запит або змініть діапазон дат."
    : "Створіть перше замовлення для клієнта.";
  const isInitialLoading = loading && orderList.length === 0;

  const handleDateRangeChange = (range: { startDate: string; endDate: string }) => {
    setSelectedFilter("all");
    setStartDate(range.startDate);
    setEndDate(range.endDate);
  };

  const handleFilterChange = (filter: OrderFilter) => {
    setSelectedFilter(filter);
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 pb-28 pt-6 sm:px-6 md:px-8 md:pb-10">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-semibold leading-8 text-slate-950">Замовлення</h1>
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onChange={handleDateRangeChange}
            className="w-64"
          />
        </div>

        <div className="grid grid-cols-2 gap-2 sm:grid-cols-[minmax(0,1fr)_auto_auto] xl:min-w-[760px]">
          <div className="col-span-2 sm:col-span-1">
            <OrderSearchInput searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
          </div>
          <button
            type="button"
            onClick={() => setIsExportModalOpen(true)}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 text-sm font-medium text-slate-950 hover:bg-slate-100 md:px-4"
          >
            <DocumentIcon className="h-5 w-5 text-slate-700" />
            <span>Експорт PDF</span>
          </button>
          <button
            type="button"
            onClick={() => setIsAddModalOpen(true)}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-blue-600 px-3 text-sm font-medium text-white hover:bg-blue-700 md:px-4"
          >
            <PlusIcon className="h-5 w-5" />
            <span className="hidden sm:inline">Нове замовлення</span>
            <span className="sm:hidden">Нове</span>
          </button>
        </div>
      </div>

      {isInitialLoading ? (
        <SummaryCardsSkeleton />
      ) : (
        <div className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-[repeat(4,minmax(0,1fr))]">
          <SummaryCard label="Замовлень" value={summary.total_count.toString()} />
          <SummaryCard label="Сьогодні" value={summary.today_count.toString()} tone="success" />
          <SummaryCard label="Завтра" value={summary.tomorrow_count.toString()} />
          <SummaryCard label="Сума" value={formatMoney(summary.total_amount)} />
        </div>
      )}

      <div className="mt-4">
        <div className="flex gap-2 overflow-x-auto pb-1">
          {filterChips.map((filter) => {
            const isActive = selectedFilter === filter.id;
            return (
              <button
                key={filter.id}
                type="button"
                onClick={() => handleFilterChange(filter.id)}
                className={`inline-flex shrink-0 items-center gap-2 rounded-md border px-3 py-2 text-sm leading-5 transition-colors ${
                  isActive
                    ? "border-blue-300 bg-blue-50 text-blue-700"
                    : "border-slate-200 bg-white text-slate-700 hover:bg-slate-100"
                }`}
              >
                <span className="font-medium">{filter.label}</span>
                <span className={isActive ? "text-blue-600" : "text-slate-500"}>
                  {filter.count}
                </span>
              </button>
            );
          })}
        </div>

      </div>

      {isInitialLoading ? (
        <OrderLoadingState />
      ) : orderList.length === 0 ? (
        <OrderEmptyState
          title={emptyTitle}
          description={emptyDescription}
          onAdd={() => setIsAddModalOpen(true)}
        />
      ) : (
        <div className="mt-4 grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_25rem]">
          <section className="hidden overflow-hidden rounded-lg border border-slate-200 bg-white lg:block">
            <OrdersTable
              orders={orderList}
              selectedOrder={selectedOrder}
              onSelect={setSelectedOrder}
              onOpen={handleOpenOrder}
            />
            <OrdersTableFooter shown={orderList.length} total={selectedOrderTotal} />
          </section>

          <section className="grid grid-cols-1 gap-3 lg:hidden">
            {orderList.map((order) => (
              <OrderCard
                key={order.order_id}
                order={order}
                onClick={() => handleOpenOrder(order)}
              />
            ))}
          </section>

          <aside className="hidden max-h-[calc(100vh-3rem)] overflow-y-auto rounded-lg border border-slate-200 bg-white p-6 xl:sticky xl:top-6 xl:block xl:self-start">
            {selectedOrder ? (
              <OrderSidePanel
                order={selectedOrder}
                onOpen={() => handleOpenOrder(selectedOrder)}
                onEdit={() => handleOpenOrder(selectedOrder, true)}
                onDelete={() => setOrderPendingDelete(selectedOrder)}
              />
            ) : (
              <div className="flex h-full min-h-64 items-center justify-center text-center text-sm text-slate-500">
                Оберіть замовлення у таблиці, щоб переглянути деталі.
              </div>
            )}
          </aside>

          <div ref={sentinelRef} className="py-4 xl:col-span-2">
            {loadingMore && <OrderLoadingMoreState />}
          </div>
        </div>
      )}

      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Нове замовлення"
        size="5xl"
      >
        <AddOrderForm onClose={() => setIsAddModalOpen(false)} onSave={handleOrderCreated} />
      </Modal>

      <FloatingAddButton label="Нове замовлення" onClick={() => setIsAddModalOpen(true)} />

      <DetailModal isOpen={isDetailModalOpen} onClose={handleCloseDetail} size="5xl">
        {selectedOrder && (
          <OrderDetailModal
            key={`${selectedOrder.order_id}-${isDetailEditing ? "edit" : "view"}`}
            order={selectedOrder}
            onClose={handleCloseDetail}
            onDelete={() => setOrderPendingDelete(selectedOrder)}
            onSave={handleSave}
            onPayFromBalance={handlePayFromBalance}
            paymentError={paymentError}
            initialEditing={isDetailEditing}
            initialEditReturnTarget={isDetailEditing ? "close" : "view"}
          />
        )}
      </DetailModal>

      <ExportPdfModal isOpen={isExportModalOpen} onClose={() => setIsExportModalOpen(false)} />

      {orderPendingDelete?.recurring_order_id ? (
        <Modal
          isOpen
          onClose={() => {
            setOrderPendingDelete(null);
            setPausePlanningAfterDelete(false);
          }}
          title="Видалити заплановане замовлення"
        >
          <div className="space-y-5">
            <div>
              <p className="text-sm leading-6 text-slate-700">
                Видалити замовлення для "{orderPendingDelete.client_name}"?
                Повторне створення цієї дати буде скасовано.
              </p>
              <label className="mt-4 flex items-start gap-3 rounded-md border border-slate-200 p-3 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={pausePlanningAfterDelete}
                  onChange={(event) =>
                    setPausePlanningAfterDelete(event.target.checked)
                  }
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600"
                />
                <span>Також поставити планування на паузу</span>
              </label>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={() => {
                  setOrderPendingDelete(null);
                  setPausePlanningAfterDelete(false);
                }}
                className="min-h-11 rounded-md bg-slate-100 px-4 py-2.5 text-sm font-medium leading-5 text-slate-700 hover:bg-slate-200"
              >
                Скасувати
              </button>
              <button
                type="button"
                onClick={handleDelete}
                className="min-h-11 rounded-md bg-red-600 px-4 py-2.5 text-sm font-medium leading-5 text-white hover:bg-red-700"
              >
                Видалити замовлення
              </button>
            </div>
          </div>
        </Modal>
      ) : (
        <ConfirmDeleteModal
          isOpen={!!orderPendingDelete}
          title="Підтвердити видалення"
          message={orderPendingDelete ? `Видалити замовлення для "${orderPendingDelete.client_name}"?` : ""}
          warning="Цю дію не можна скасувати."
          confirmLabel="Видалити замовлення"
          onCancel={() => {
            setOrderPendingDelete(null);
            setPausePlanningAfterDelete(false);
          }}
          onConfirm={handleDelete}
        />
      )}
    </div>
  );
};

const OrderSearchInput = ({
  searchTerm,
  setSearchTerm,
}: {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
}) => (
  <div className="relative">
    <SearchIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
    <input
      type="text"
      placeholder="Пошук замовлень, клієнта, адреси..."
      value={searchTerm}
      onChange={(event) => setSearchTerm(event.target.value)}
      className="h-10 w-full rounded-md border border-slate-300 bg-white pl-10 pr-3 text-sm leading-5 text-slate-950 placeholder:text-slate-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
    />
  </div>
);

const SummaryCard = ({
  label,
  value,
  helper,
  tone = "default",
}: {
  label: string;
  value: string;
  helper?: string;
  tone?: "default" | "success" | "danger";
}) => {
  const toneClass = {
    default: "text-slate-950",
    success: "text-emerald-700",
    danger: "text-red-700",
  }[tone];

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <div className="mt-2 flex items-end justify-between gap-3">
        <p className={`text-2xl font-semibold leading-8 ${toneClass}`}>{value}</p>
        {helper && <p className="pb-1 text-xs font-medium text-slate-500">{helper}</p>}
      </div>
    </div>
  );
};

const OrdersTable = ({
  orders,
  selectedOrder,
  onSelect,
  onOpen,
}: {
  orders: Order[];
  selectedOrder: Order | null;
  onSelect: (order: Order) => void;
  onOpen: (order: Order) => void;
}) => (
  <div className="overflow-x-auto">
    <table className="w-full min-w-[880px] text-left text-sm">
      <thead className="border-b border-slate-200 bg-white text-xs font-medium text-slate-500">
        <tr>
          <th className="w-10 px-4 py-3">
            <span className="block h-4 w-4 rounded border border-slate-300" />
          </th>
          <th className="px-4 py-3">Клієнт</th>
          <th className="px-4 py-3">Адреса</th>
          <th className="px-4 py-3">Час</th>
          <th className="px-4 py-3">Товарів</th>
          <th className="px-4 py-3">Спосіб оплати</th>
          <th className="px-4 py-3 text-right">Сума</th>
          <th className="w-16 px-4 py-3 text-right">Дії</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-200">
        {orders.map((order) => {
          const isSelected = selectedOrder?.order_id === order.order_id;
          return (
            <tr
              key={order.order_id}
              onClick={() => onSelect(order)}
              onDoubleClick={() => onOpen(order)}
              className={`cursor-pointer transition-colors ${
                isSelected ? "bg-blue-50" : "bg-white hover:bg-slate-50"
              }`}
            >
              <td className="px-4 py-3">
                <span
                  className={`flex h-4 w-4 items-center justify-center rounded border ${
                    isSelected ? "border-blue-600 bg-blue-600" : "border-slate-300 bg-white"
                  }`}
                >
                  {isSelected && <CheckIcon className="h-3 w-3 text-white" />}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="font-medium text-slate-950">{order.client_name}</div>
                <div className="text-xs text-slate-500">{order.delivery_phone || "Телефон не вказано"}</div>
              </td>
              <td className="max-w-[220px] truncate px-4 py-3 text-slate-600">{getAddressText(order)}</td>
              <td className="px-4 py-3 text-slate-600">
                <div>{formatDate(order.date)}</div>
                <div className="text-xs text-slate-500">{order.time_slot || order.time_preference || "Час не вказано"}</div>
              </td>
              <td className="px-4 py-3 text-slate-600">{order.items?.length ?? 0}</td>
              <td className="px-4 py-3 text-slate-600">{order.payment_method || "Не вказано"}</td>
              <td className="px-4 py-3 text-right font-semibold text-slate-950">{formatMoney(getOrderTotal(order))}</td>
              <td className="px-4 py-3 text-right">
                <button
                  type="button"
                  aria-label="Відкрити замовлення"
                  onClick={(event) => {
                    event.stopPropagation();
                    onOpen(order);
                  }}
                  className="inline-flex h-8 w-8 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-950"
                >
                  <MoreIcon className="h-5 w-5" />
                </button>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

const OrderCard = ({ order, onClick }: { order: Order; onClick: () => void }) => (
  <button
    type="button"
    onClick={onClick}
    className="rounded-lg border border-slate-200 bg-white p-4 text-left shadow-sm transition-colors hover:border-blue-300"
  >
    <div className="flex items-start justify-between gap-3">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700">
          {getInitials(order.client_name)}
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-slate-950">{order.client_name}</p>
          <p className="mt-1 text-xs text-slate-500">{formatDate(order.date)}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-sm font-semibold text-slate-950">{formatMoney(getOrderTotal(order))}</p>
        <p className="mt-1 text-xs text-slate-500">{order.payment_method || "Оплату не вказано"}</p>
      </div>
    </div>
    <div className="mt-4 grid gap-2 text-sm text-slate-600">
      <div className="flex items-center gap-2">
        <MapPinIcon className="h-4 w-4 text-slate-400" />
        <span className="truncate">{getAddressText(order)}</span>
      </div>
      <div className="flex items-center justify-between gap-3">
        <span className="inline-flex items-center gap-2">
          <ClockIcon className="h-4 w-4 text-slate-400" />
          {order.time_slot || order.time_preference || "Час не вказано"}
        </span>
        <span>{order.items?.length ?? 0} товарів</span>
      </div>
    </div>
  </button>
);

const OrderSidePanel = ({
  order,
  onOpen,
  onEdit,
  onDelete,
}: {
  order: Order;
  onOpen: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) => (
  <div className="flex min-h-[28rem] flex-col">
    <div className="flex items-start justify-between gap-3 border-b border-slate-200 pb-4">
      <div>
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-slate-950">Замовлення</h2>
        </div>
        <p className="mt-1 text-sm text-slate-500">{order.client_name}</p>
      </div>
      <button
        type="button"
        onClick={onOpen}
        className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
      >
        Відкрити
      </button>
    </div>

    <div className="grid gap-4 py-4 text-sm">
      <InfoRow label="Телефон" value={order.delivery_phone || "Не вказано"} />
      <InfoRow label="Адреса" value={getAddressText(order)} />
      <InfoRow label="Дата" value={formatDate(order.date)} />
      <InfoRow label="Час" value={order.time_slot || order.time_preference || "Не вказано"} />
      <InfoRow label="Спосіб оплати" value={order.payment_method || "Не вказано"} />
    </div>

    <div className="border-t border-slate-200 pt-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-950">Товари</h3>
        <span className="text-sm font-medium text-slate-500">{order.items?.length ?? 0} товарів</span>
      </div>
      <div className="space-y-2">
        {(order.items ?? []).slice(0, 4).map((item) => (
          <div key={`${item.product_id ?? item.name}-${item.id}`} className="flex justify-between gap-3 text-sm">
            <span className="truncate text-slate-600">{item.name}</span>
            <span className="shrink-0 font-medium text-slate-950">{item.quantity} шт.</span>
          </div>
        ))}
      </div>
      <div className="mt-4 flex items-center justify-between border-t border-slate-200 pt-3">
        <span className="text-sm font-semibold text-slate-950">Разом</span>
        <span className="text-lg font-semibold text-slate-950">{formatMoney(getOrderTotal(order))}</span>
      </div>
    </div>

    <div className="mt-auto grid grid-cols-2 gap-3 pt-6">
      <button
        type="button"
        onClick={onEdit}
        className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
      >
        Редагувати
      </button>
      <button
        type="button"
        onClick={onDelete}
        className="rounded-md border border-red-200 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
      >
        Видалити
      </button>
    </div>
  </div>
);

const InfoRow = ({ label, value }: { label: string; value: string }) => (
  <div>
    <p className="text-xs font-medium text-slate-500">{label}</p>
    <p className="mt-1 font-medium text-slate-950">{value}</p>
  </div>
);

const OrdersTableFooter = ({ shown, total }: { shown: number; total: number }) => (
  <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3 text-sm text-slate-500">
    <span>
      Показано 1-{shown} з {total}
    </span>
    <span className="rounded-md border border-slate-200 bg-white px-3 py-2 font-medium text-slate-700">
      20 / сторінка
    </span>
  </div>
);

const OrderLoadingState = () => (
  <div className="mt-4 grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_25rem]">
    <TableSkeleton columns={8} rows={6} />
    <section className="grid grid-cols-1 gap-3 lg:hidden">
      {Array.from({ length: 6 }).map((_, index) => (
        <OrderCardSkeleton key={index} />
      ))}
    </section>
    <SidePanelSkeleton />
  </div>
);

const OrderLoadingMoreState = () => (
  <>
    <TableSkeleton columns={8} rows={2} />
    <div className="grid grid-cols-1 gap-3 lg:hidden">
      {Array.from({ length: 2 }).map((_, index) => (
        <OrderCardSkeleton key={index} />
      ))}
    </div>
  </>
);

const OrderEmptyState = ({
  title,
  description,
  onAdd,
}: {
  title: string;
  description: string;
  onAdd: () => void;
}) => (
  <div className="mt-4 flex min-h-56 flex-col items-center justify-start rounded-lg border border-dashed border-slate-300 bg-white px-6 py-6 text-center sm:min-h-80 sm:justify-center sm:p-8">
    <DocumentIcon className="h-8 w-8 text-slate-400 sm:h-10 sm:w-10" />
    <h2 className="mt-3 text-lg font-semibold text-slate-950 sm:mt-4">{title}</h2>
    <p className="mt-1 max-w-sm text-sm text-slate-500 sm:mt-2">{description}</p>
    <button
      type="button"
      onClick={onAdd}
      className="mt-4 inline-flex h-10 items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700 sm:mt-5"
    >
      Нове замовлення
    </button>
  </div>
);

const SearchIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.197 5.197a7.5 7.5 0 0 0 10.606 10.606Z" />
  </svg>
);

const PlusIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.5v15m7.5-7.5h-15" />
  </svg>
);

const DocumentIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414A1 1 0 0 1 19 8.414V19a2 2 0 0 1-2 2Z" />
  </svg>
);

const MapPinIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />
  </svg>
);

const ClockIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);

const CheckIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="m4.5 12.75 6 6 9-13.5" />
  </svg>
);

const MoreIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.75h.008v.008H12zm0 5.25h.008v.008H12zm0 5.25h.008v.008H12z" />
  </svg>
);
