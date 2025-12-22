import { useEffect, useState, useRef, useCallback } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { ClientCard } from "../components/ui/clientsCard";
import { ClientDetailModal } from "../components/modals/detailsModals/ClientDetailModal";
import { RightModal } from "../components/modals/RightModal";
import { type Client } from "../types/entities/Client";
import { useClient } from "../hooks/clients/useClients";
import { getClientById } from "../services/api/clientApi";

export const ClientsPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { clients, getClients, deleteClient, loadMoreClients, loadingMore, hasMore } = useClient();
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const initClients = async () => {
      await getClients();

      const openClientId = sessionStorage.getItem("openClientId");
      if (openClientId) {
        try {
          const client = await getClientById(openClientId);
          setSelectedClient(client);
          setIsModalOpen(true);
        } catch (e) {
          console.error("Failed to fetch client by ID");
        }
        sessionStorage.removeItem("openClientId");
      }
    };
    initClients();
  }, []);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      getClients(searchTerm);
    }, 100);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [searchTerm]);

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      if (entry.isIntersecting && hasMore && !loadingMore) {
        loadMoreClients();
      }
    },
    [hasMore, loadingMore, loadMoreClients]
  );

  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: "100px",
      threshold: 0,
    });

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [handleObserver]);

  const handleClientClick = (client: Client) => {
    setSelectedClient(client);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedClient(null), 300);
  };

  const handleSave = async () => {
    const updatedClients = await getClients(searchTerm);
    if (selectedClient) {
      const updated = updatedClients.find(
        (c: Client) => c.client_id === selectedClient.client_id
      );
      if (updated) {
        setSelectedClient(updated);
      }
    }
  };

  const handleDelete = async () => {
    if (selectedClient) {
      await deleteClient(selectedClient.client_id);
      handleCloseModal();
      getClients(searchTerm);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <PageHeader title="Клієнти" />

      <div className="px-6 pb-4">
        <SearchBar
          placeholder="Пошук клієнтів"
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
        />
      </div>

      {clients.length === 0 ? (
        <div className="flex flex-col items-center justify-center mt-20">
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
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
          <p className="text-gray-500 text-lg font-medium">
            {searchTerm ? "Клієнтів не знайдено" : "Клієнти відсутні"}
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
            {clients.map((client) => (
              <ClientCard
                key={client.client_id}
                client={client}
                onClick={() => handleClientClick(client)}
              />
            ))}
          </div>

          <div ref={loadMoreRef} className="py-4 flex justify-center">
            {loadingMore && (
              <div className="flex items-center gap-2 text-gray-500">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Завантаження...</span>
              </div>
            )}
          </div>
        </div>
      )}

      <RightModal isOpen={isModalOpen} onClose={handleCloseModal}>
        {selectedClient && (
          <ClientDetailModal
            client={selectedClient}
            onClose={handleCloseModal}
            onDelete={handleDelete}
            onSave={handleSave}
          />
        )}
      </RightModal>
    </div>
  );
};