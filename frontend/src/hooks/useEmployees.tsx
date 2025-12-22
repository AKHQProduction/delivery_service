import { useState, useCallback } from "react";
import {
  updateEmployeeById,
  deleteEmployeeById,
  getAllEmployees,
} from "../services/api/employeeApi";
import { createInviteUserLink } from "../services/api/userApi";

const PAGE_SIZE = 20;

export const useEmployees = () => {
  const [employees, setEmployees] = useState<Array<any>>([]);
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
      const fetchedEmployees = await getAllEmployees(search, PAGE_SIZE, 0, "ASC");
      setEmployees(fetchedEmployees);
      setHasMore(fetchedEmployees.length >= PAGE_SIZE);
      setOffset(PAGE_SIZE);
      return fetchedEmployees;
    } catch (err) {
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
    } catch (err) {
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
    } catch (err) {
      setError("Не вдалося видалити працівника.");
    }
    setLoading(false);
  };

  const updateEmployee = async (
    user_id: string,
    name: string,
    role: string
  ) => {
    setLoading(true);
    setError(null);
    try {
      const updatedProduct = await updateEmployeeById(user_id, name, role);

      setEmployees((prevEmployee) =>
        prevEmployee.map((employee) =>
          employee.id === user_id ? updatedProduct : employee
        )
      );
    } catch (err) {
      setError("Не вдалося оновити працівника.");
    }
  };

  const createInviteLink = async (role: string, full_name: string) => {
    setLoading(true);
    setError(null);
    try {
      const link = await createInviteUserLink(role, full_name);
      setLoading(false);
      return link;
    } catch (err) {
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