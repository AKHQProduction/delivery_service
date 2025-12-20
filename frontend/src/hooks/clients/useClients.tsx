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
  deleteClientById,
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
      return fetchedClients;
    } catch {
      setError("Не вдалося завантажити клієнтів.");
      return [];
    } finally {
      setLoading(false);
    }
  };

  const deleteClient = async (clientId: string) => {
    setLoading(true);
    setError(null);
    try {
      await deleteClientById(clientId);
    } catch (err) {
      setError("Не вдалося видалити працівника.");
    }
    setLoading(false);
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
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail || "Не вдалося додати клієнта.";
      setError(errorMessage);
      throw new Error(errorMessage);
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
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail || "Не вдалося оновити клієнта.";
      setError(errorMessage);
      throw new Error(errorMessage);
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
    deleteClient,
  };
};
