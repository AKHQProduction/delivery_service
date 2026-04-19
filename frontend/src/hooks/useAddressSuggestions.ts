import { useCallback, useEffect, useRef, useState } from "react";
import { suggestAddresses, type AddressSuggestion } from "../services/api/geocodingApi";

export interface UseAddressSuggestionsOptions {
  city: string;
  enabled?: boolean;
  limit?: number;
  debounceMs?: number;
}

export const useAddressSuggestions = (
  query: string,
  { city, enabled = true, limit = 5, debounceMs = 300 }: UseAddressSuggestionsOptions,
) => {
  const [items, setItems] = useState<AddressSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpenRequested, setIsOpenRequested] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const requestIdRef = useRef(0);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const normalizedQuery = query.trim();
  const normalizedCity = city.trim();
  const canFetch = enabled && normalizedQuery.length > 0 && normalizedCity.length > 0;

  const invalidatePendingRequest = useCallback(() => {
    requestIdRef.current += 1;

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }
  }, []);

  const clear = useCallback(() => {
    invalidatePendingRequest();
    setItems([]);
    setIsLoading(false);
    setIsOpenRequested(false);
    setError(null);
  }, [invalidatePendingRequest]);

  const open = useCallback(() => {
    setIsOpenRequested(true);
  }, []);

  const close = useCallback(() => {
    setIsOpenRequested(false);
  }, []);

  useEffect(() => {
    invalidatePendingRequest();
    const currentRequestId = requestIdRef.current;

    if (!canFetch) {
      setItems([]);
      setIsLoading(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    setItems([]);
    setError(null);

    const timer = setTimeout(async () => {
      try {
        const data = await suggestAddresses(normalizedQuery, normalizedCity, limit);

        if (requestIdRef.current !== currentRequestId) {
          return;
        }

        setItems(data);
        setError(null);
      } catch (error) {
        if (requestIdRef.current !== currentRequestId) {
          return;
        }

        setItems([]);
        setError(error instanceof Error ? error.message : "Failed to load address suggestions");
      } finally {
        if (requestIdRef.current === currentRequestId) {
          setIsLoading(false);
        }
      }
    }, debounceMs);

    debounceTimerRef.current = timer;

    return () => {
      invalidatePendingRequest();
    };
  }, [normalizedQuery, normalizedCity, canFetch, limit, debounceMs, invalidatePendingRequest]);

  const isOpen = isOpenRequested && canFetch;

  return {
    items,
    isLoading,
    isOpen,
    error,
    open,
    close,
    clear,
  };
};
