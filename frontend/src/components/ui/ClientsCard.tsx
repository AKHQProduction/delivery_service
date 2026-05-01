import React from "react";
import { type Client } from "../../types/entities/Client";

interface ClientCardProps {
  client: Client;
  onClick: (employee: Client) => void;
}

const getPrimaryPhone = (client: Client) =>
  client.phones?.find((phone) => phone.is_primary) ?? client.phones?.[0];

const getPrimaryAddress = (client: Client) =>
  client.addresses?.find((address) => address.is_primary) ?? client.addresses?.[0];

const getAddressText = (client: Client) => {
  const address = getPrimaryAddress(client);
  if (!address) return "Адресу не вказано";

  return [address.street, address.house, address.apartment ? `кв. ${address.apartment}` : ""]
    .filter(Boolean)
    .join(", ");
};

const getClientInitials = (name?: string) => {
  const parts = (name || "Клієнт").trim().split(/\s+/).filter(Boolean);
  return parts
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toLocaleUpperCase("uk-UA");
};

const formatBalance = (balance: Client["balance"] | null | undefined) => {
  const numericBalance = Number(balance ?? 0);
  return Number.isFinite(numericBalance) ? `${numericBalance.toLocaleString("uk-UA")} ₴` : "0 ₴";
};

export const ClientCard: React.FC<ClientCardProps> = ({ client, onClick }) => {
  const balance = Number(client.balance ?? 0);

  return (
    <button
      type="button"
      onClick={() => onClick(client)}
      className="w-full rounded-lg border border-slate-200 bg-white p-4 text-left shadow-sm transition-colors hover:bg-slate-50"
    >
      <div className="flex items-start gap-3">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700">
          {getClientInitials(client.full_name)}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="truncate text-base font-semibold text-slate-950">
                  {client.full_name || "Без імені"}
                </h3>
                <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
                  Постійний
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-600">
                {getPrimaryPhone(client)?.number || "Телефон не вказано"}
              </p>
            </div>
            <span
              className={`shrink-0 text-sm font-semibold ${
                balance < 0 ? "text-red-600" : balance > 0 ? "text-emerald-600" : "text-slate-700"
              }`}
            >
              {formatBalance(client.balance)}
            </span>
          </div>
          <div className="mt-2 flex items-end justify-between gap-3">
            <p className="line-clamp-2 text-sm leading-5 text-slate-500">{getAddressText(client)}</p>
            <span className="shrink-0 text-xs text-slate-500">— замовлень</span>
          </div>
        </div>
        <MoreIcon className="mt-1 h-5 w-5 shrink-0 text-slate-500" />
      </div>
    </button>
  );
};

const MoreIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 6.75h.008v.008H12zm0 5.25h.008v.008H12zm0 5.25h.008v.008H12z"
    />
  </svg>
);
