import { useState } from "react";
import {
  type Client,
  type Address,
  type Phone,
} from "../../types/entities/Client";
import {
  getAllClients,
  createNewClient,
  updateExistingClientById,
} from "../../services/api/clientApi";

export const useClient = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getClients = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedClients = await getAllClients("", "", "", 100, 0, "ASC");
      setClients(fetchedClients);
    } catch {
      setError("Не вдалося завантажити клієнтів.");
    } finally {
      setLoading(false);
    }
  };

  const createClient = async (clientData: {
    full_name: string;
    phones: Phone[];
    addresses: Address[];
    custom_id?: string;
  }) => {
    setLoading(true);
    setError(null);
    try {
      const newClient = await createNewClient({
        full_name: clientData.full_name,
        phones: clientData.phones.filter((p) => p.number.trim() !== ""),
        addresses: clientData.addresses.filter((a) => a.street.trim() !== ""),
        custom_id: clientData?.custom_id,
      });

      setClients((prev) => [...prev, newClient]);
      return newClient;
    } catch {
      setError("Не вдалося додати клієнта.");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateClient = async (
    clientId: string,
    clientData: {
      full_name: string;
      phones: Phone[];
      addresses: Address[];
      custom_id?: string;
    }
  ) => {
    setLoading(true);
    setError(null);
    try {
      const updatedClient = await updateExistingClientById(clientId, {
        full_name: clientData.full_name,
        phones: clientData.phones.filter((p) => p.number.trim() !== ""),
        addresses: clientData.addresses.filter((a) => a.street.trim() !== ""),
        custom_id: clientData?.custom_id,
      });

      setClients((prev) =>
        prev.map((c) => (c.client_id === clientId ? updatedClient : c))
      );
      return updatedClient;
    } catch {
      setError("Не вдалося оновити клієнта.");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    clients,
    loading,
    error,
    createClient,
    getClients,
    updateClient,
  };
};
