import { useState, useCallback } from "react";
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

const PAGE_SIZE = 20;

export const useClient = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const [currentSearch, setCurrentSearch] = useState("");

  const getClients = async (search: string = "") => {
    setLoading(true);
    setError(null);
    setCurrentSearch(search);
    setOffset(0);
    try {
      const fetchedClients = await getAllClients(search, search, search, PAGE_SIZE, 0, "ASC");
      setClients(fetchedClients);
      setHasMore(fetchedClients.length >= PAGE_SIZE);
      setOffset(PAGE_SIZE);
      return fetchedClients;
    } catch {
      setError("Не вдалося завантажити клієнтів.");
      return [];
    } finally {
      setLoading(false);
    }
  };

  const loadMoreClients = useCallback(async () => {
    if (loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      const fetchedClients = await getAllClients(currentSearch, currentSearch, currentSearch, PAGE_SIZE, offset, "ASC");
      setClients((prev) => [...prev, ...fetchedClients]);
      setHasMore(fetchedClients.length >= PAGE_SIZE);
      setOffset((prev) => prev + PAGE_SIZE);
    } catch {
      setError("Не вдалося завантажити більше клієнтів.");
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, hasMore, offset, currentSearch]);

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
    loadingMore,
    error,
    hasMore,
    createClient,
    getClients,
    loadMoreClients,
    updateClient,
    deleteClient,
  };
};