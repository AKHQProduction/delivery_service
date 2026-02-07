import { useState, useCallback } from "react";
import {
  updateEmployeeById,
  deleteEmployeeById,
  getAllEmployees,
} from "../services/api/employeeApi";
import { createInviteUserLink } from "../services/api/userApi";
import { type Employee } from "../types/entities/Employee";

const PAGE_SIZE = 20;

export const useEmployees = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [offset, setOffset] = useState<number>(0);
  const [currentSearch, setCurrentSearch] = useState<string>("");

  const getEmployees = async (search: string = "") => {
    setLoading(true);
    setError(null);
    setCurrentSearch(search);
    setOffset(0);
    try {
      const fetchedEmployees = (await getAllEmployees(search, PAGE_SIZE, 0, "ASC")) as Employee[];
      setEmployees(fetchedEmployees);
      setHasMore(fetchedEmployees.length >= PAGE_SIZE);
      setOffset(PAGE_SIZE);
      return fetchedEmployees;
    } catch {
      setError("Не вдалося завантажити працівників.");
      return [];
    } finally {
      setLoading(false);
    }
  };

  const loadMoreEmployees = useCallback(async () => {
    if (loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      const fetchedEmployees = await getAllEmployees(currentSearch, PAGE_SIZE, offset, "ASC");
      setEmployees((prev) => [...prev, ...fetchedEmployees]);
      setHasMore(fetchedEmployees.length >= PAGE_SIZE);
      setOffset((prev) => prev + PAGE_SIZE);
    } catch {
      setError("Не вдалося завантажити більше працівників.");
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, hasMore, offset, currentSearch]);

  const deleteEmployees = async (productId: string) => {
    setLoading(true);
    setError(null);
    try {
      await deleteEmployeeById(productId);
    } catch {
      setError("Не вдалося видалити працівника.");
    }
    setLoading(false);
  };

  const updateEmployee = async (user_id: string, name: string, role: string) => {
    setLoading(true);
    setError(null);
    try {
      const updatedEmployee = (await updateEmployeeById(user_id, name, role)) as Employee;

      if (updatedEmployee) {
        setEmployees((prevEmployee) =>
          prevEmployee.map((employee) =>
            employee?.user_id === user_id ? updatedEmployee : employee,
          ),
        );
      }
      return updatedEmployee;
    } catch {
      setError("Не вдалося оновити працівника.");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const createInviteLink = async (role: string, full_name: string) => {
    setLoading(true);
    setError(null);
    try {
      const link = (await createInviteUserLink(role, full_name)) as string;
      setLoading(false);
      return link;
    } catch {
      setError("Не вдалося створити запрошення для працівника.");
      setLoading(false);
    }
  };

  return {
    employees,
    getEmployees,
    loadMoreEmployees,
    deleteEmployees,
    updateEmployee,
    createInviteLink,
    error,
    loading,
    loadingMore,
    hasMore,
  };
};
