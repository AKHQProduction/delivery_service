import { useEffect, useState } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { ClientCard } from "../components/ui/clientsCard";
import { ClientDetailModal } from "../components/modals/detailsModals/ClientDetailModal";
import { RightModal } from "../components/modals/RightModal";
import { type Client } from "../types/entities/Client";
import { useClient } from "../hooks/clients/useClients";

export const ClientsPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { clients, getClients, deleteClient } = useClient();

  useEffect(() => {
    getClients();
  }, []);

  const clientsList = clients.filter(
    (client) =>
      client.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ??
      false
  );

  const handleClientClick = (client: Client) => {
    setSelectedClient(client);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedClient(null), 300);
  };

  const handleSave = async () => {
    const updatedClients = await getClients();
    if (selectedClient) {
      const updated = updatedClients.find(
        (c: Client) => c.client_id === selectedClient.client_id
      );
      if (updated) {
        setSelectedClient(updated);
      }
    }
  };

  const handleDelete = () => {
    if (selectedClient) {
      deleteClient(selectedClient.client_id);
    }
    window.location.reload(); //TEMPORARY SOLUTION
    handleCloseModal();
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

      {clientsList.length === 0 ? (
        <div className="flex flex-col items-center justify-center mt-20">
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
