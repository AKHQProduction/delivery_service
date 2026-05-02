import { useState, useCallback } from "react";
import { type Client, type Address, type Phone } from "../../types/entities/Client";
import {
  getAllClients,
  createNewClient,
  getClientById,
  getClientSummary,
  type ClientSummary,
  updateExistingClientById,
  deleteClientById,
  setClientBalance as setClientBalanceApi,
} from "../../services/api/clientApi";

const PAGE_SIZE = 20;
type ClientFilter = "all" | "debt" | "positive";

export const useClient = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const [currentSearch, setCurrentSearch] = useState("");
  const [currentFilter, setCurrentFilter] = useState<ClientFilter>("all");
  const [summary, setSummary] = useState<ClientSummary>({
    total_count: 0,
    debt_count: 0,
    positive_balance_count: 0,
  });

  const getClients = async (search: string = "", filter: ClientFilter = "all") => {
    setLoading(true);
    setError(null);
    setCurrentSearch(search);
    setCurrentFilter(filter);
    setOffset(0);
    try {
      const [fetchedClients, fetchedSummary] = await Promise.all([
        getAllClients(
          search,
          search,
          PAGE_SIZE,
          0,
          "ASC",
          filter === "debt" ? true : undefined,
          filter === "positive" ? true : undefined,
        ),
        getClientSummary(search, search),
      ]);
      setClients(fetchedClients);
      setSummary(fetchedSummary);
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
    if (loadingMore || loading || !hasMore) return;

    setLoadingMore(true);
    try {
      const fetchedClients = await getAllClients(
        currentSearch,
        currentSearch,
        PAGE_SIZE,
        offset,
        "ASC",
        currentFilter === "debt" ? true : undefined,
        currentFilter === "positive" ? true : undefined,
      );
      setClients((prev) => [...prev, ...fetchedClients]);
      setHasMore(fetchedClients.length >= PAGE_SIZE);
      setOffset((prev) => prev + PAGE_SIZE);
    } catch {
      setError("Не вдалося завантажити більше клієнтів.");
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, loading, hasMore, offset, currentSearch, currentFilter]);

  const deleteClient = async (clientId: string) => {
    setLoading(true);
    setError(null);
    try {
      await deleteClientById(clientId);
    } catch {
      setError("Не вдалося видалити працівника.");
    }
    setLoading(false);
  };

  const createClient = async (
    clientData: {
      full_name: string;
      phones: Phone[];
      addresses: Address[];
    },
    confirmDuplicate: boolean = false,
  ) => {
    setLoading(true);
    setError(null);
    try {
      const newClient = await createNewClient(
        {
          full_name: clientData.full_name,
          phones: clientData.phones.filter((p) => p.number.trim() !== ""),
          addresses: clientData.addresses.filter((a) => a.street.trim() !== ""),
        },
        confirmDuplicate,
      );

      setClients((prev) => [...prev, newClient]);
      return newClient;
    } catch (err: unknown) {
      const error = err as {
        response?: { status?: number; data?: { code?: string; detail?: string } };
      };
      if (error?.response?.status === 409 && error?.response?.data?.code === "duplicate_phones") {
        throw err;
      }

      const errorMessage = error?.response?.data?.detail || "Не вдалося додати клієнта.";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateClient = async (
    clientId: string,
    clientData: {
      full_name: string;
      balance?: number;
      phones: Phone[];
      addresses: Address[];
    },
    confirmDuplicate: boolean = false,
  ) => {
    setLoading(true);
    setError(null);
    try {
      const updatedClient = await updateExistingClientById(
        clientId,
        {
          full_name: clientData.full_name,
          balance: clientData.balance,
          phones: clientData.phones.filter((p) => p.number.trim() !== ""),
          addresses: clientData.addresses.filter((a) => a.street.trim() !== ""),
        },
        confirmDuplicate,
      );

      setClients((prev) => prev.map((c) => (c.client_id === clientId ? updatedClient : c)));
      return updatedClient;
    } catch (err: unknown) {
      const error = err as {
        response?: { status?: number; data?: { code?: string; detail?: string } };
      };
      if (error?.response?.status === 409 && error?.response?.data?.code === "duplicate_phones") {
        throw err;
      }
      const errorMessage = error?.response?.data?.detail || "Не вдалося оновити клієнта.";
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const setClientBalance = async (clientId: string, balance: number) => {
    setLoading(true);
    setError(null);
    try {
      await setClientBalanceApi(clientId, balance);
      const updatedClient = (await getClientById(clientId)) as Client;
      setClients((prev) =>
        prev.map((client) => (client.client_id === clientId ? updatedClient : client)),
      );
      return updatedClient;
    } catch (err: unknown) {
      const error = err as {
        response?: { data?: { detail?: string } };
      };
      const errorMessage = error?.response?.data?.detail || "Не вдалося оновити баланс клієнта.";
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    clients,
    summary,
    loading,
    loadingMore,
    error,
    hasMore,
    createClient,
    getClients,
    loadMoreClients,
    updateClient,
    deleteClient,
    setClientBalance,
  };
};
