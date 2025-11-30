import { useState } from "react";
import {
  updateEmployeeById,
  deleteEmployeeById,
  getAllEmployees,
} from "../services/employeeService";

export const useProducts = () => {
  const [employees, setEmployees] = useState<Array<any>>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getEmployees = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedProducts = await getAllEmployees("", 100, 0, "ASC");
      setEmployees(fetchedProducts);
    } catch (err) {
      setError("Не вдалося завантажити працівників.");
    }
    setLoading(false);
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

  return {
    employees,
    getEmployees,
    deleteEmployees,
    updateEmployee,
    error,
    loading,
  };
};
