import React from "react";
import { type Client } from "../../../../types/entities/Client";
import { SearchBar } from "../../../ui/searchBar";

interface ClientSelectionStepProps {
  clients: Client[];
  selectedClient: Client | null;
  searchValue: string;
  onSearchChange: (value: string) => void;
  onClientSelect: (client: Client) => void;
  onAddNewClient?: () => void;
}

export const ClientSelectionStep: React.FC<ClientSelectionStepProps> = ({
  clients,
  selectedClient,
  searchValue,
  onSearchChange,
  onClientSelect,
  onAddNewClient,
}) => {
  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold text-gray-900">Вибір клієнта</h3>

      <SearchBar
        searchTerm={searchValue}
        setSearchTerm={onSearchChange}
        placeholder="Пошук за ім'ям або телефоном..."
      />

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {clients.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <svg
              className="w-12 h-12 mx-auto mb-3 text-gray-300"
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
            <p className="font-medium">Клієнтів не знайдено</p>
            <p className="text-sm">Спробуйте інший пошуковий запит</p>
          </div>
        ) : (
          clients.map((client) => (
            <div
              key={client.client_id}
              onClick={() => onClientSelect(client)}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                selectedClient?.client_id === client.client_id
                  ? "border-indigo-600 bg-indigo-50"
                  : "border-gray-200 hover:border-indigo-300 bg-white"
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
                    selectedClient?.client_id === client.client_id
                      ? "bg-indigo-600 text-white"
                      : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {client.full_name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .toUpperCase()
                    .slice(0, 2)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-gray-900">
                    {client.full_name}
                  </div>
                  <div className="text-sm text-gray-600 flex items-center gap-1">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                      />
                    </svg>
                    {client.number[0]}
                  </div>
                </div>

                {selectedClient?.client_id === client.client_id && (
                  <svg
                    className="w-6 h-6 text-indigo-600"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {onAddNewClient && (
        <button
          onClick={onAddNewClient}
          type="button"
          className="w-full py-3 border-2 border-dashed border-gray-300 rounded-xl text-gray-600 hover:border-indigo-400 hover:text-indigo-600 transition-all font-medium flex items-center justify-center gap-2"
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          Додати нового клієнта
        </button>
      )}
    </div>
  );
};
