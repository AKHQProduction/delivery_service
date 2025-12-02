import { useState } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { ClientCard } from "../components/ui/clientsCard";
import { ClientDetailModal } from "../components/modals/detailsModals/ClientDetailModal";
import { RightModal } from "../components/modals/RightModal";
import { type Client } from "../types/entities/Client";

const clientsData = {
  clients: [
    {
      client_id: "БИДЛ001",
      full_name: "Іван Петренко",
      number: ["+380501234567"],
      adress: ["вул. Шевченка який пасе ягнят за селом, 10, Київ"],
    },
    {
      client_id: "БИДЛ002",
      full_name: "Олена Ковальчук",
      number: ["+380671112233", "+380631112233"],
      adress: ["просп. ТЦК, 5, Львів", "вул. Грушевського, 20, Львів"],
    },
    {
      client_id: "БИДЛ003",
      full_name: "Петро Іванов",
      number: ["+380931234567"],
      adress: ["вул. Пушкіна Гандона, 15, Одеса"],
    },
  ],
};

export const ClientsPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const clientsList = clientsData.clients.filter((client) =>
    client.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleEmployeeClick = (client: Client) => {
    setSelectedClient(client);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedClient(null), 300);
  };

  const handleSave = (updatedClient: Client) => {
    console.log("Save employee:", updatedClient);
    window.location.reload();
  };

  const handleDelete = () => {
    console.log("Delete employee:", selectedClient);
    window.location.reload();
    handleCloseModal();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <PageHeader title="Клієнти" />
      <SearchBar
        placeholder="Пошук клієнтів..."
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
      />

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
            {clientsData.clients.map((client) => (
              <ClientCard
                key={client.client_id}
                client={client}
                onClick={() => handleEmployeeClick(client)}
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
