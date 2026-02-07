import api from "../../config/api.config";

export const updateEmployeeById = async (user_id: string, name: string, role: string) => {
  const response = await api.patch(`v1/employee/${user_id}`, {
    name,
    role,
  });
  return response.data;
};

export const deleteEmployeeById = async (user_id: string) => {
  const response = await api.delete(`v1/employee/${user_id}`);
  return response.data;
};

export const getEmployeeById = async (user_id: string) => {
  const response = await api.get(`v1/employee/${user_id}`);
  return response.data;
};

export const getAllEmployees = async (
  employeeName: string,
  employeeLimit: number,
  offset: number,
  order: string,
) => {
  const params: Record<string, string | number> = {
    limit: employeeLimit,
    offset: offset,
    order: order,
  };

  if (employeeName) params.name = employeeName;

  const response = await api.get(`v1/employee/all`, { params });
  return response.data;
};
