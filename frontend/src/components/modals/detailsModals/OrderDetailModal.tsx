import { useState } from "react";
import { type ReactNode } from "react";
import { useDistrictsSettings } from "../../../hooks/settings/useDistrictsSettings";
import { isBalancePaymentMethodName } from "../../../shared/paymentMethod";
import { type Order } from "../../../types/entities/Order";
import { EditOrderForm } from "../../forms/orders/EditOrderForm";

export interface OrderDetailModalProps {
  order: Order;
  onClose: () => void;
  onDelete: () => void;
  onSave?: () => void;
  onPayFromBalance: (orderId: string) => Promise<void> | void;
  paymentError?: string;
  initialEditing?: boolean;
  initialEditReturnTarget?: "view" | "close";
}

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

export const OrderDetailModal = ({
  order,
  onClose,
  onDelete,
  onSave,
  onPayFromBalance,
  paymentError = "",
  initialEditing = false,
  initialEditReturnTarget = "view",
}: OrderDetailModalProps) => {
  const [isEditing, setIsEditing] = useState(initialEditing);
  const [editReturnTarget, setEditReturnTarget] = useState<"view" | "close">(initialEditReturnTarget);
  const [isPaying, setIsPaying] = useState(false);
  const [balanceChargedInSession, setBalanceChargedInSession] = useState(false);
  const { districts } = useDistrictsSettings();
  const isBalancePaymentMethod = isBalancePaymentMethodName(order.payment_method || "");

  const getOrderTotal = () =>
    (order.items ?? []).reduce((sum, item) => {
      const quantity = Number(item.quantity) || 0;
      const price = Number(item.price_per_item) || 0;
      return sum + quantity * price;
    }, 0);

  const getDistrictName = (districtId: string | null | undefined) => {
    if (!districtId) return null;
    const district = districts.find((item) => item.district_id === districtId);
    return district?.name || null;
  };

  const handleSaveEdit = () => {
    if (editReturnTarget === "close") {
      onSave?.();
      onClose();
      return;
    }
    setIsEditing(false);
    onSave?.();
  };

  const handleCancelEdit = () => {
    if (editReturnTarget === "close") {
      onClose();
      return;
    }
    setIsEditing(false);
  };

  const handlePayFromBalance = async () => {
    setIsPaying(true);
    try {
      await onPayFromBalance(order.order_id);
      setBalanceChargedInSession(true);
    } finally {
      setIsPaying(false);
    }
  };

  if (isEditing) {
    return (
      <div className="flex h-full flex-col bg-white">
        <div className="flex shrink-0 items-start justify-between border-b border-slate-200 px-6 py-5">
          <div>
            <p className="text-sm font-medium text-slate-500">Замовлення</p>
            <h1 className="mt-1 text-2xl font-semibold leading-8 text-slate-950">
              Редагувати замовлення
            </h1>
          </div>
          <button
            type="button"
            onClick={handleCancelEdit}
            aria-label="Закрити редагування"
            className="flex h-9 w-9 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-900"
          >
            <CloseIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 pt-6">
          <EditOrderForm order={order} onClose={handleCancelEdit} onSave={handleSaveEdit} />
        </div>
      </div>
    );
  }

  const districtName = getDistrictName(order.delivery_address?.district_id);
  const canPayFromBalance =
    !isPaying && !balanceChargedInSession && !order.is_paid && !isBalancePaymentMethod;

  return (
    <div className="flex h-full flex-col bg-white">
      <div className="flex shrink-0 items-start justify-between border-b border-slate-200 px-6 py-5">
        <div className="flex min-w-0 items-start gap-3">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700">
            {getInitials(order.client_name)}
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="truncate text-2xl font-semibold leading-8 text-slate-950">
                Замовлення
              </h1>
            </div>
            <p className="text-sm text-slate-500">{order.client_name}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Закрити деталі замовлення"
          className="flex h-9 w-9 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-900"
        >
          <CloseIcon className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <span className="text-sm font-medium text-slate-600">Товарів</span>
            <span className="font-semibold text-slate-950">{order.items?.length ?? 0}</span>
          </div>
          <div className="flex items-center justify-between pt-3">
            <span className="text-base font-semibold text-slate-950">Разом</span>
            <span className="text-2xl font-semibold text-slate-950">{formatMoney(getOrderTotal())}</span>
          </div>
        </div>

        <section className="mt-4 rounded-lg border border-slate-200 bg-white">
          <SectionHeader title="Клієнт і доставка" />
          <div className="divide-y divide-slate-200">
            <DetailRow label="Телефон" value={order.delivery_phone || "Не вказано"} icon={<PhoneIcon className="h-4 w-4" />} />
            <DetailRow label="Адреса" value={getAddressText(order)} icon={<MapPinIcon className="h-4 w-4" />} />
            {districtName && <DetailRow label="Район" value={districtName} />}
            <DetailRow label="Дата" value={formatDate(order.date)} icon={<CalendarIcon className="h-4 w-4" />} />
            <DetailRow label="Час" value={order.time_slot || order.time_preference || "Не вказано"} icon={<ClockIcon className="h-4 w-4" />} />
            <DetailRow label="Спосіб оплати" value={order.payment_method || "Не вказано"} />
          </div>
        </section>

        {(order.note || order.comment) && (
          <section className="mt-4 rounded-lg border border-slate-200 bg-white">
            <SectionHeader title="Коментар" />
            <div className="px-4 py-3 text-sm leading-6 text-slate-700">
              {order.note || order.comment}
            </div>
          </section>
        )}

        <section className="mt-4 rounded-lg border border-slate-200 bg-white">
          <SectionHeader title="Товари" badge={`${order.items?.length ?? 0}`} />
          <div className="divide-y divide-slate-200">
            {(order.items ?? []).map((item) => (
              <div key={`${item.product_id ?? item.name}-${item.id}`} className="grid grid-cols-[1fr_auto_auto] gap-3 px-4 py-3 text-sm">
                <div className="min-w-0">
                  <p className="truncate font-medium text-slate-950">{item.name}</p>
                  <p className="mt-1 text-xs text-slate-500">{formatMoney(Number(item.price_per_item) || 0)} за шт.</p>
                </div>
                <span className="text-slate-600">{item.quantity} шт.</span>
                <span className="font-semibold text-slate-950">
                  {formatMoney((Number(item.quantity) || 0) * (Number(item.price_per_item) || 0))}
                </span>
              </div>
            ))}
          </div>
        </section>

        {paymentError && (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <p className="font-semibold">Не вдалося оплатити з балансу</p>
            <p className="mt-1">{paymentError}</p>
          </div>
        )}
      </div>

      <div className="shrink-0 border-t border-slate-200 bg-white px-6 py-4">
        <button
          type="button"
          onClick={handlePayFromBalance}
          disabled={!canPayFromBalance}
          className="mb-3 h-12 w-full rounded-md bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
        >
          {isPaying ? "Оплата..." : "Оплатити з балансу"}
        </button>
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => {
              setEditReturnTarget("view");
              setIsEditing(true);
            }}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-md border border-slate-300 bg-white text-sm font-medium text-slate-950 hover:bg-slate-100"
          >
            <EditIcon className="h-4 w-4" />
            Редагувати
          </button>
          <button
            type="button"
            onClick={onDelete}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-md border border-red-200 bg-white text-sm font-medium text-red-600 hover:bg-red-50"
          >
            <TrashIcon className="h-4 w-4" />
            Видалити
          </button>
        </div>
      </div>
    </div>
  );
};

const SectionHeader = ({ title, badge }: { title: string; badge?: string }) => (
  <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
    <h2 className="text-sm font-semibold text-slate-950">{title}</h2>
    {badge && <span className="rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500">{badge}</span>}
  </div>
);

const DetailRow = ({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon?: ReactNode;
}) => (
  <div className="grid grid-cols-[1fr_1.4fr] gap-4 px-4 py-3 text-sm">
    <div className="flex items-center gap-2 text-slate-500">
      {icon}
      <span>{label}</span>
    </div>
    <p className="font-medium text-slate-950">{value}</p>
  </div>
);

const CloseIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18 18 6M6 6l12 12" />
  </svg>
);

const EditIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Z" />
  </svg>
);

const TrashIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673A2.25 2.25 0 0 1 15.916 21H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
  </svg>
);

const PhoneIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 0 1-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102A1.125 1.125 0 0 0 5.872 2.25H4.5A2.25 2.25 0 0 0 2.25 4.5v2.25Z" />
  </svg>
);

const MapPinIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />
  </svg>
);

const CalendarIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6.75 3v2.25m10.5-2.25v2.25M3.75 8.25h16.5m-15 12h13.5A1.5 1.5 0 0 0 20.25 18.75V6.75a1.5 1.5 0 0 0-1.5-1.5H5.25a1.5 1.5 0 0 0-1.5 1.5v12a1.5 1.5 0 0 0 1.5 1.5Z" />
  </svg>
);

const ClockIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);
