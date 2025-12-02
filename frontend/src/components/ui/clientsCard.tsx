import React from "react";

interface Client {
  client_id: string;
  full_name: string;
  number: string[];
  adress: string[];
}

interface ClientCardProps {
  client: Client;
  onClick: (employee: Client) => void;
}

export const ClientCard: React.FC<ClientCardProps> = ({ client, onClick }) => {
  return (
    <div
      onClick={() => onClick(client)}
      className="group relative bg-white rounded-2xl p-5 shadow-sm cursor-pointer
        hover:shadow-2xl hover:-translate-y-2 transition-all duration-300
        border border-gray-100 overflow-hidden"
    >
      <div className="relative flex items-start gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
              {client.full_name}
            </h3>
            <span className="px-2.5 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
              #{client.client_id}
            </span>
          </div>

          <div className="space-y-2">
            <div className="flex items-start gap-2">
              <svg
                className="w-4 h-4 text-indigo-500 mt-0.5 shrink-0"
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
              <div className="flex flex-wrap gap-1.5">
                <span
                  className="text-sm text-gray-700 bg-indigo-50 px-2.5 py-0.5 rounded-lg font-medium
                      group-hover:bg-indigo-100 transition-colors"
                >
                  {client.number[0]}
                </span>
              </div>
            </div>

            {client.adress.length > 0 && client.adress[0] && (
              <div className="flex items-start gap-2">
                <svg
                  className="w-4 h-4 text-purple-500 mt-0.5 shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <div className="flex flex-wrap gap-1.5">
                  <span
                    className="text-sm text-gray-700 bg-purple-50 px-2.5 py-0.5 rounded-lg font-medium
                        group-hover:bg-purple-100 transition-colors"
                  >
                    {client.adress[0]}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
