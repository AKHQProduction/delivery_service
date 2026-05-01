import React, { useState } from "react";
import { EditClientForm } from "../../forms/client/EditClientForm";
import { type Client } from "../../../types/entities/Client";
import { useDistrictsSettings } from "../../../hooks/settings/useDistrictsSettings";
import { useTimeSlotsSettings } from "../../../hooks/settings/useTimeSlotsSettings";

interface ClientDetailModalProps {
  client: Client;
  onClose: () => void;
  onDelete: () => void;
  onSave: () => Promise<void> | void;
  initialEditing?: boolean;
  initialEditReturnTarget?: "view" | "close";
}

const formatBalance = (balance: Client["balance"] | null | undefined) => {
  const numericBalance = Number(balance ?? 0);
  return Number.isFinite(numericBalance) ? `${numericBalance.toLocaleString("uk-UA")} ₴` : "0 ₴";
};

const getClientInitials = (name?: string) => {
  const parts = (name || "Клієнт").trim().split(/\s+/).filter(Boolean);
  return parts
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toLocaleUpperCase("uk-UA");
};

export const ClientDetailModal: React.FC<ClientDetailModalProps> = ({
  client,
  onClose,
  onDelete,
  onSave,
  initialEditing = false,
  initialEditReturnTarget = "view",
}) => {
  const [isEditing, setIsEditing] = useState(initialEditing);
  const [editReturnTarget, setEditReturnTarget] = useState<"view" | "close">(initialEditReturnTarget);
  const { districts } = useDistrictsSettings();
  const { timeSlots, isLoading: timeSlotsLoading } = useTimeSlotsSettings();

  const getDistrictName = (districtId: string | null | undefined) => {
    if (!districtId) return null;
    const district = districts.find((item) => item.district_id === districtId);
    return district?.name || null;
  };

  const getPreferredTimeSlotLabel = () => {
    if (!client.preferred_time_slot_id) {
      return "Не вказано";
    }

    const timeSlot = timeSlots.find((slot) => slot.time_slot_id === client.preferred_time_slot_id);
    if (!timeSlot) {
      return timeSlotsLoading ? "Завантаження..." : "Не знайдено";
    }

    return timeSlot.label
      ? `${timeSlot.label} (${timeSlot.start_time} - ${timeSlot.end_time})`
      : `${timeSlot.start_time} - ${timeSlot.end_time}`;
  };

  const handleSaveEdit = async () => {
    await onSave();
    if (editReturnTarget === "close") {
      onClose();
      return;
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    if (editReturnTarget === "close") {
      onClose();
      return;
    }
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="flex h-full flex-col bg-white">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5">
          <div>
            <p className="text-sm font-medium text-slate-500">Клієнт</p>
            <h1 className="text-xl font-semibold text-slate-950">Редагувати клієнта</h1>
          </div>
          <button
            onClick={handleCancelEdit}
            type="button"
            className="rounded-md p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-950"
            aria-label="Закрити редагування"
          >
            <CloseIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 pt-5">
          <EditClientForm client={client} onClose={handleCancelEdit} onSave={handleSaveEdit} />
        </div>
      </div>
    );
  }

  const balance = Number(client.balance ?? 0);

  return (
    <div className="flex h-full flex-col bg-white">
      <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-5">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-100 text-base font-semibold text-blue-700">
            {getClientInitials(client.full_name)}
          </span>
          <div className="min-w-0">
            <h1 className="truncate text-xl font-semibold text-slate-950">
              {client.full_name || "Без імені"}
            </h1>
          </div>
        </div>
        <button
          onClick={onClose}
          type="button"
          className="rounded-md p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-950"
          aria-label="Закрити"
        >
          <CloseIcon className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
        <div
          className={`rounded-lg border px-4 py-3 ${
            balance < 0
              ? "border-red-100 bg-red-50"
              : balance > 0
                ? "border-emerald-100 bg-emerald-50"
                : "border-slate-200 bg-slate-50"
          }`}
        >
          <p
            className={`text-sm font-medium ${
              balance < 0 ? "text-red-700" : balance > 0 ? "text-emerald-700" : "text-slate-600"
            }`}
          >
            Баланс
          </p>
          <p
            className={`mt-1 text-2xl font-semibold ${
              balance < 0 ? "text-red-700" : balance > 0 ? "text-emerald-700" : "text-slate-950"
            }`}
          >
            {formatBalance(client.balance)}
          </p>
        </div>

        <dl className="divide-y divide-slate-200 rounded-lg border border-slate-200 text-sm">
          <DetailRow label="Бажаний час доставки" value={getPreferredTimeSlotLabel()} />
          <DetailRow label="Телефонів" value={String(client.phones?.length ?? 0)} />
          <DetailRow label="Адрес" value={String(client.addresses?.length ?? 0)} />
        </dl>

        <section className="rounded-lg border border-slate-200">
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
            <h2 className="text-sm font-semibold text-slate-950">Телефони</h2>
            <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
              {client.phones?.length ?? 0}
            </span>
          </div>
          <div className="divide-y divide-slate-200">
            {client.phones?.length ? (
              client.phones.map((phone, index) => (
                <div key={`${phone.number}-${index}`} className="flex items-center justify-between gap-4 px-4 py-3 text-sm">
                  <span className="font-medium text-slate-950">{phone.number}</span>
                  {phone.is_primary && (
                    <span className="rounded bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
                      Основний
                    </span>
                  )}
                </div>
              ))
            ) : (
              <p className="px-4 py-3 text-sm text-slate-500">Телефони не вказано.</p>
            )}
          </div>
        </section>

        <section className="rounded-lg border border-slate-200">
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
            <h2 className="text-sm font-semibold text-slate-950">Адреси</h2>
            <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
              {client.addresses?.length ?? 0}
            </span>
          </div>
          <div className="divide-y divide-slate-200">
            {client.addresses?.length ? (
              client.addresses.map((address, index) => {
                const districtName = getDistrictName(address.district_id);
                return (
                  <div key={`${address.street}-${address.house}-${index}`} className="px-4 py-3">
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-sm font-medium leading-5 text-slate-950">
                        {address.street} {address.house}
                        {address.apartment ? `, кв. ${address.apartment}` : ""}
                      </p>
                      {address.is_primary && (
                        <span className="shrink-0 rounded bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
                          Основна
                        </span>
                      )}
                    </div>
                    {districtName && <p className="mt-1 text-sm text-slate-500">{districtName}</p>}
                    {address.comment && (
                      <p className="mt-2 rounded-md bg-slate-50 px-3 py-2 text-sm leading-5 text-slate-600">
                        {address.comment}
                      </p>
                    )}
                  </div>
                );
              })
            ) : (
              <p className="px-4 py-3 text-sm text-slate-500">Адреси не вказано.</p>
            )}
          </div>
        </section>
      </div>

      <div className="space-y-3 border-t border-slate-200 px-6 py-5">
        <button
          type="button"
          onClick={() => {
            setEditReturnTarget("view");
            setIsEditing(true);
          }}
          className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-md border border-slate-300 bg-white text-sm font-medium text-slate-950 hover:bg-slate-100"
        >
          <EditIcon className="h-5 w-5" />
          Редагувати
        </button>
        <button
          type="button"
          onClick={onDelete}
          className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-md border border-red-300 bg-white text-sm font-medium text-red-600 hover:bg-red-50"
        >
          <TrashIcon className="h-5 w-5" />
          Видалити
        </button>
      </div>
    </div>
  );
};

const DetailRow = ({ label, value }: { label: string; value: string }) => (
  <div className="flex items-center justify-between gap-4 px-4 py-4">
    <dt className="text-slate-500">{label}</dt>
    <dd className="text-right font-medium text-slate-950">{value}</dd>
  </div>
);

const CloseIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18 18 6M6 6l12 12" />
  </svg>
);

const EditIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125"
    />
  </svg>
);

const TrashIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.68.107 1.022.166m-1.022-.165L18.16 19.673A2.25 2.25 0 0 1 15.916 21H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
    />
  </svg>
);
