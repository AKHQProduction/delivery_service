import api from "../config/api.config";

export const updateEmployeeById = async (
  user_id: string,
  name: string,
  role: string
) => {
  try {
    const response = await api.patch(`v1/employee/${user_id}`, {
      name,
      role,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteEmployeeById = async (user_id: string) => {
  try {
    const response = await api.delete(`v1/employee/${user_id}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getEmployeeById = async (user_id: string) => {
  try {
    const response = await api.get(`v1/employee/${user_id}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getAllEmployees = async (
  employeeName: string,
  employeeLimit: number,
  offset: number,
  order: string
) => {
  try {
    const response = await api.get(`v1/employee/all`, {
      params: {
        name: employeeName,
        limit: employeeLimit,
        offset: offset,
        order: order,
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};
