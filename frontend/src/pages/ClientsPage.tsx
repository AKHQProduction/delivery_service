import { useEffect, useMemo, useRef, useState } from "react";
import { AddClientForm } from "../components/forms/client/AddClientForm";
import { ImportClientsModal } from "../components/features/ImportClientsModal";
import { Modal } from "../components/modals/Modal";
import { DetailModal } from "../components/modals/DetailModal";
import { ClientDetailModal } from "../components/modals/detailsModals/ClientDetailModal";
import { ClientCard } from "../components/ui/ClientsCard";
import { ClientCardSkeleton, SidePanelSkeleton, TableSkeleton } from "../components/ui/Skeleton";
import { ConfirmDeleteModal } from "../components/ui/ConfirmDeleteModal";
import { FloatingAddButton } from "../components/ui/FloatingAddButton";
import { useClient } from "../hooks/clients/useClients";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";
import { getClientById } from "../services/api/clientApi";
import { type Client } from "../types/entities/Client";

type ClientFilter = "all" | "debt" | "positive";

const formatBalance = (balance: Client["balance"] | null | undefined) => {
  const numericBalance = Number(balance ?? 0);
  return Number.isFinite(numericBalance) ? `${numericBalance.toLocaleString("uk-UA")} ₴` : "0 ₴";
};

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

export const ClientsPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailEditing, setIsDetailEditing] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [clientPendingDelete, setClientPendingDelete] = useState<Client | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<ClientFilter>("all");
  const {
    clients,
    summary,
    getClients,
    deleteClient,
    loadMoreClients,
    loading,
    loadingMore,
    hasMore,
  } = useClient();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const initialLoadRef = useRef(false);

  const { sentinelRef } = useInfiniteScroll({
    onLoadMore: loadMoreClients,
    hasMore,
    isLoading: loadingMore,
  });

  useEffect(() => {
    if (initialLoadRef.current) return;
    initialLoadRef.current = true;

    const initClients = async () => {
      await getClients("", selectedFilter);

      const openClientId = sessionStorage.getItem("openClientId");
      if (openClientId) {
        try {
          const client = await getClientById(openClientId);
          setSelectedClient(client);
          setIsModalOpen(true);
        } catch {
          console.error("Failed to fetch client by ID");
        }
        sessionStorage.removeItem("openClientId");
      }
    };
    initClients();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      getClients(searchTerm, selectedFilter);
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, selectedFilter]);

  const filterChips = useMemo(() => {
    return [
      { id: "all" as const, label: "Усі", count: summary.total_count },
      { id: "debt" as const, label: "З боргом", count: summary.debt_count },
      {
        id: "positive" as const,
        label: "З балансом",
        count: summary.positive_balance_count,
      },
    ];
  }, [summary]);

  const visibleClients = clients;
  const selectedClientTotal =
    selectedFilter === "debt"
      ? summary.debt_count
      : selectedFilter === "positive"
        ? summary.positive_balance_count
        : summary.total_count;

  useEffect(() => {
    if (selectedClient) {
      const updatedSelection = clients.find((client) => client.client_id === selectedClient.client_id);
      if (updatedSelection) {
        setSelectedClient(updatedSelection);
      }
    } else if (visibleClients.length > 0) {
      setSelectedClient(visibleClients[0]);
    }
  }, [clients, selectedClient, visibleClients]);

  const handleClientClick = (client: Client, edit = false) => {
    setSelectedClient(client);
    setIsDetailEditing(edit);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setIsDetailEditing(false);
  };

  const handleSave = async () => {
    const updatedClients = await getClients(searchTerm, selectedFilter);
    if (selectedClient) {
      const updated = updatedClients.find((client: Client) => client.client_id === selectedClient.client_id);
      if (updated) {
        setSelectedClient(updated);
      }
    }
  };

  const handleClientCreated = async (client?: Client) => {
    setIsAddModalOpen(false);
    const refreshedClients = await getClients(searchTerm, selectedFilter);
    const createdClient = client?.client_id
      ? refreshedClients.find((item: Client) => item.client_id === client.client_id)
      : null;
    setSelectedClient(createdClient ?? refreshedClients[0] ?? null);
  };

  const requestDeleteClient = (client: Client) => {
    setClientPendingDelete(client);
  };

  const confirmDeleteClient = async () => {
    if (!clientPendingDelete) return;

    const client = clientPendingDelete;
    await deleteClient(client.client_id);
    if (selectedClient?.client_id === client.client_id) {
      setSelectedClient(null);
      setIsModalOpen(false);
    }
    setClientPendingDelete(null);
    await getClients(searchTerm, selectedFilter);
  };

  const emptyTitle = searchTerm ? "Клієнтів не знайдено" : "Клієнтів поки немає";
  const emptyDescription = searchTerm
    ? "Спробуйте інший пошуковий запит або змініть швидкий фільтр."
    : "Додайте першого клієнта або імпортуйте список з Excel.";

  return (
    <div className="min-h-screen bg-slate-50 px-4 pb-28 pt-6 sm:px-6 md:px-8 md:pb-10">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-semibold leading-8 text-slate-950">Клієнти</h1>
          <span className="rounded bg-slate-100 px-2 py-1 text-sm font-medium leading-5 text-slate-500">
            {selectedClientTotal}
          </span>
        </div>

        <div className="grid grid-cols-[auto_auto] gap-2 md:flex md:min-w-[640px] md:justify-end">
          <div className="hidden md:block md:w-80 lg:w-[420px]">
            <ClientSearchInput searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
          </div>
          <button
            type="button"
            aria-label="Імпорт клієнтів"
            onClick={() => setIsImportModalOpen(true)}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 text-sm font-medium text-slate-950 hover:bg-slate-100 md:px-4"
          >
            <ImportIcon className="h-5 w-5 text-slate-700" />
            <span className="hidden sm:inline">Імпорт</span>
          </button>
          <button
            type="button"
            aria-label="Додати клієнта"
            onClick={() => setIsAddModalOpen(true)}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-blue-600 px-3 text-sm font-medium text-white hover:bg-blue-700 md:px-4"
          >
            <PlusIcon className="h-5 w-5" />
            <span className="hidden sm:inline">Додати клієнта</span>
            <span className="sm:hidden">Додати</span>
          </button>
        </div>
      </div>

      <div className="mt-4 md:hidden">
        <ClientSearchInput searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
      </div>

      <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
        {filterChips.map((filter) => {
          const isActive = selectedFilter === filter.id;
          return (
            <button
              key={filter.id}
              type="button"
              onClick={() => setSelectedFilter(filter.id)}
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

      {loading && clients.length === 0 ? (
        <ClientLoadingState />
      ) : visibleClients.length === 0 ? (
        <ClientEmptyState
          title={emptyTitle}
          description={emptyDescription}
          onAdd={() => setIsAddModalOpen(true)}
        />
      ) : (
        <div className="mt-4 grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_25rem]">
          <section className="hidden overflow-hidden rounded-lg border border-slate-200 bg-white lg:block">
            <ClientTable
              clients={visibleClients}
              selectedClient={selectedClient}
              onSelect={setSelectedClient}
            />
            <ClientTableFooter shown={visibleClients.length} total={selectedClientTotal} />
          </section>

          <section className="grid grid-cols-1 gap-3 lg:hidden">
            {visibleClients.map((client) => (
              <ClientCard
                key={client.client_id}
                client={client}
                onClick={() => handleClientClick(client)}
              />
            ))}
          </section>

          <aside className="hidden max-h-[calc(100vh-3rem)] overflow-y-auto rounded-lg border border-slate-200 bg-white p-6 xl:sticky xl:top-6 xl:block xl:self-start">
            {selectedClient ? (
              <ClientSidePanel
                client={selectedClient}
                onClose={() => setSelectedClient(null)}
                onEdit={() => handleClientClick(selectedClient, true)}
                onDelete={() => requestDeleteClient(selectedClient)}
              />
            ) : (
              <div className="flex h-full min-h-64 items-center justify-center text-center text-sm text-slate-500">
                Оберіть клієнта у таблиці, щоб переглянути деталі.
              </div>
            )}
          </aside>

          <div ref={sentinelRef} className="py-4 xl:col-span-2">
            {loadingMore && <ClientLoadingMoreState />}
          </div>
        </div>
      )}

      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Додати клієнта"
        size="2xl"
      >
        <AddClientForm onClose={() => setIsAddModalOpen(false)} onSuccess={handleClientCreated} />
      </Modal>

      <FloatingAddButton label="Додати клієнта" onClick={() => setIsAddModalOpen(true)} />

      <DetailModal isOpen={isModalOpen} onClose={handleCloseModal}>
        {selectedClient && (
          <ClientDetailModal
            key={`${selectedClient.client_id}-${isDetailEditing ? "edit" : "view"}`}
            client={selectedClient}
            onClose={handleCloseModal}
            onDelete={() => requestDeleteClient(selectedClient)}
            onSave={handleSave}
            initialEditing={isDetailEditing}
            initialEditReturnTarget={isDetailEditing ? "close" : "view"}
          />
        )}
      </DetailModal>

      <ImportClientsModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        onSuccess={() => getClients(searchTerm)}
      />

      <ConfirmDeleteModal
        isOpen={!!clientPendingDelete}
        title="Підтвердити видалення"
        message={clientPendingDelete ? `Видалити клієнта "${clientPendingDelete.full_name}"?` : ""}
        warning="Цю дію не можна скасувати."
        confirmLabel="Видалити клієнта"
        onCancel={() => setClientPendingDelete(null)}
        onConfirm={confirmDeleteClient}
      />
    </div>
  );
};

const ClientSearchInput = ({
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
      placeholder="Пошук клієнтів, телефону, адреси..."
      value={searchTerm}
      onChange={(event) => setSearchTerm(event.target.value)}
      className="h-10 w-full rounded-md border border-slate-300 bg-white pl-10 pr-3 text-sm leading-5 text-slate-950 placeholder:text-slate-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
    />
  </div>
);

const ClientTable = ({
  clients,
  selectedClient,
  onSelect,
}: {
  clients: Client[];
  selectedClient: Client | null;
  onSelect: (client: Client) => void;
}) => (
  <div className="overflow-x-auto">
    <table className="min-w-full table-fixed divide-y divide-slate-200 text-sm">
      <colgroup>
        <col className="w-12" />
        <col className="w-[26%]" />
        <col className="w-[18%]" />
        <col className="w-[27%]" />
        <col className="w-[14%]" />
        <col className="w-[10%]" />
        <col className="w-16" />
      </colgroup>
      <thead className="bg-white text-left text-xs font-medium uppercase tracking-normal text-slate-500">
        <tr>
          <th className="px-5 py-4">
            <span className="block h-4 w-4 rounded border border-slate-300 bg-white" />
          </th>
          <th className="px-4 py-4 font-medium normal-case">Клієнт</th>
          <th className="px-4 py-4 font-medium normal-case">Телефон</th>
          <th className="px-4 py-4 font-medium normal-case">Адреса</th>
          <th className="px-4 py-4 font-medium normal-case">Баланс</th>
          <th className="px-4 py-4 font-medium normal-case">Замовлень</th>
          <th className="px-4 py-4 text-center font-medium normal-case">Дії</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-200">
        {clients.map((client) => {
          const isSelected = selectedClient?.client_id === client.client_id;
          const balance = Number(client.balance ?? 0);

          return (
            <tr
              key={client.client_id}
              onClick={() => onSelect(client)}
              className={`cursor-pointer transition-colors ${
                isSelected ? "bg-blue-50/70" : "bg-white hover:bg-slate-50"
              }`}
            >
              <td className="px-5 py-4">
                <span
                  className={`flex h-4 w-4 items-center justify-center rounded border ${
                    isSelected ? "border-blue-600 bg-blue-600" : "border-slate-300 bg-white"
                  }`}
                >
                  {isSelected && (
                    <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 16 16">
                      <path
                        d="m3.5 8 3 3 6-6"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                      />
                    </svg>
                  )}
                </span>
              </td>
              <td className="px-4 py-4">
                <div className="flex items-center gap-3">
                  <ClientAvatar name={client.full_name} />
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-950">
                      {client.full_name || "Без імені"}
                    </p>
                  </div>
                </div>
              </td>
              <td className="px-4 py-4 text-slate-700">{getPrimaryPhone(client)?.number || "—"}</td>
              <td className="px-4 py-4 text-slate-700">
                <span className="line-clamp-2">{getAddressText(client)}</span>
              </td>
              <td
                className={`px-4 py-4 font-medium ${
                  balance < 0 ? "text-red-600" : balance > 0 ? "text-emerald-600" : "text-slate-700"
                }`}
              >
                {formatBalance(client.balance)}
              </td>
              <td className="px-4 py-4 text-slate-700">—</td>
              <td className="px-4 py-4 text-center">
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    onSelect(client);
                  }}
                  className="rounded-md p-2 text-slate-700 hover:bg-slate-100"
                  aria-label="Відкрити клієнта"
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

const ClientTableFooter = ({ shown, total }: { shown: number; total: number }) => (
  <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3 text-sm text-slate-500">
    <span>
      Всього: {shown} з {total} клієнтів
    </span>
    <span className="rounded-md border border-slate-200 bg-white px-3 py-2 text-slate-700">
      20 / сторінка
    </span>
  </div>
);

const ClientSidePanel = ({
  client,
  onClose,
  onEdit,
  onDelete,
}: {
  client: Client;
  onClose: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) => (
  <div className="flex h-full flex-col">
    <div className="flex items-start justify-between gap-4">
      <div className="flex items-center gap-3">
        <ClientAvatar name={client.full_name} size="lg" />
        <div>
          <h2 className="text-xl font-semibold leading-7 text-slate-950">
            {client.full_name || "Без імені"}
          </h2>
        </div>
      </div>
      <button
        type="button"
        onClick={onClose}
        className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-950"
        aria-label="Закрити деталі клієнта"
      >
        <CloseIcon className="h-5 w-5" />
      </button>
    </div>

    <div className="mt-6 rounded-lg border border-emerald-100 bg-emerald-50 px-4 py-3">
      <p className="text-sm font-medium text-emerald-700">Баланс</p>
      <p className="mt-1 text-2xl font-semibold text-emerald-700">{formatBalance(client.balance)}</p>
    </div>

    <dl className="mt-5 divide-y divide-slate-200 text-sm">
      <div className="flex items-center justify-between gap-4 py-4">
        <dt className="text-slate-500">Телефон</dt>
        <dd className="font-medium text-slate-950">{getPrimaryPhone(client)?.number || "Не вказано"}</dd>
      </div>
      <div className="flex items-center justify-between gap-4 py-4">
        <dt className="text-slate-500">Адреса</dt>
        <dd className="max-w-52 text-right font-medium text-slate-950">{getAddressText(client)}</dd>
      </div>
      <div className="flex items-center justify-between gap-4 py-4">
        <dt className="text-slate-500">Телефонів</dt>
        <dd className="font-medium text-slate-950">{client.phones?.length ?? 0}</dd>
      </div>
      <div className="flex items-center justify-between gap-4 py-4">
        <dt className="text-slate-500">Адрес</dt>
        <dd className="font-medium text-slate-950">{client.addresses?.length ?? 0}</dd>
      </div>
    </dl>

    <div className="mt-7 space-y-3">
      <button
        type="button"
        onClick={onEdit}
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

const ClientLoadingState = () => (
  <div className="mt-4 grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_25rem]">
    <TableSkeleton columns={7} rows={6} />
    <section className="grid grid-cols-1 gap-3 lg:hidden">
      {Array.from({ length: 5 }).map((_, index) => (
        <ClientCardSkeleton key={index} />
      ))}
    </section>
    <SidePanelSkeleton />
  </div>
);

const ClientLoadingMoreState = () => (
  <>
    <TableSkeleton columns={7} rows={2} />
    <div className="grid grid-cols-1 gap-3 lg:hidden">
      {Array.from({ length: 2 }).map((_, index) => (
        <ClientCardSkeleton key={index} />
      ))}
    </div>
  </>
);

const ClientEmptyState = ({
  title,
  description,
  onAdd,
}: {
  title: string;
  description: string;
  onAdd: () => void;
}) => (
  <div className="mt-4 flex min-h-80 flex-col items-center justify-center rounded-lg border border-slate-200 bg-white px-6 text-center">
    <UsersIcon className="h-14 w-14 text-slate-400" />
    <h2 className="mt-5 text-lg font-semibold text-slate-950">{title}</h2>
    <p className="mt-2 max-w-sm text-sm leading-5 text-slate-500">{description}</p>
    <button
      type="button"
      onClick={onAdd}
      className="mt-6 inline-flex h-10 items-center justify-center rounded-md bg-blue-600 px-5 text-sm font-medium text-white hover:bg-blue-700"
    >
      Додати клієнта
    </button>
  </div>
);

const ClientAvatar = ({ name, size = "md" }: { name?: string; size?: "md" | "lg" }) => (
  <span
    className={`flex shrink-0 items-center justify-center rounded-full bg-blue-100 font-semibold text-blue-700 ${
      size === "lg" ? "h-12 w-12 text-base" : "h-8 w-8 text-xs"
    }`}
  >
    {getClientInitials(name)}
  </span>
);

const SearchIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.197 5.197a7.5 7.5 0 0 0 10.606 10.606Z"
    />
  </svg>
);

const PlusIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.5v15m7.5-7.5h-15" />
  </svg>
);

const ImportIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 3v12m0 0 4-4m-4 4-4-4M4 17v1.5A2.5 2.5 0 0 0 6.5 21h11a2.5 2.5 0 0 0 2.5-2.5V17"
    />
  </svg>
);

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

const UsersIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={1.8}
      d="M15 19.128A9.38 9.38 0 0 0 12 18.75c-2.3 0-4.4.82-6.036 2.184M15 19.128A3.75 3.75 0 0 0 21 16.125c0-2.071-1.679-3.75-3.75-3.75-.825 0-1.588.267-2.208.72M15 19.128V19.5M9 10.5a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm0 3.75c-2.071 0-3.75 1.679-3.75 3.75"
    />
  </svg>
);
