import api from "../../config/api.config";
import { type Phone, type Address } from "../../types/entities/Client";

interface UpdateClientPayload {
  full_name?: string;
  phones?: Phone[];
  addresses?: Address[];
}

interface CreateClientPayload {
  full_name: string;
  phones: Phone[];
  addresses: Address[];
}

export const createNewClient = async (
  body: CreateClientPayload,
  confirmDuplicate: boolean = false,
) => {
  const response = await api.post(`v1/clients`, {
    ...body,
    ...(confirmDuplicate && { confirm_duplicate_phones: true }),
  });
  return response.data;
};

export const updateExistingClientById = async (
  clientId: string,
  payload: UpdateClientPayload,
  confirmDuplicate: boolean = false,
) => {
  try {
    const response = await api.patch(`v1/clients/${clientId}`, {
      ...payload,
      ...(confirmDuplicate && { confirm_duplicate_phones: true }),
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteClientById = async (clientId: string) => {
  try {
    const response = await api.delete(`v1/clients/${clientId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getClientById = async (clientId: string) => {
  try {
    const response = await api.get(`v1/clients/${clientId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getAllClients = async (
  full_name: string,
  phone: string,
  clientsLimit: number,
  offset: number,
  order: string,
) => {
  try {
    const params: Record<string, string | number> = {
      limit: clientsLimit,
      offset: offset,
      order: order,
    };

    if (full_name) params.full_name = full_name;
    if (phone) params.phone = phone;

    const response = await api.get(`v1/clients/all`, { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};
