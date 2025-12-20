import { useState } from "react";
import {
  updateEmployeeById,
  deleteEmployeeById,
  getAllEmployees,
} from "../services/api/employeeApi";
import { createInviteUserLink } from "../services/api/userApi";

export const useEmployees = () => {
  const [employees, setEmployees] = useState<Array<any>>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getEmployees = async (search: string = "") => {
    setLoading(true);
    setError(null);
    try {
      const fetchedEmployees = await getAllEmployees(search, 100, 0, "ASC");
      setEmployees(fetchedEmployees);
      return fetchedEmployees;
    } catch (err) {
      setError("Не вдалося завантажити працівників.");
      return [];
    } finally {
      setLoading(false);
    }
  };

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
    deleteEmployees,
    updateEmployee,
    createInviteLink,
    error,
    loading,
  };
};
