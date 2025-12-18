import api from "../../config/api.config";

interface Phone {
  id?: number;
  number: string;
  is_primary: boolean;
}

interface Address {
  id?: number;
  street: string;
  house: string;
  address_type: "APARTMENT" | "PRIVATE_HOUSE";
  apartment?: string;
  entrance?: string;
  floor?: string;
  intercom?: string;
  is_primary: boolean;
}

interface UpdateClientPayload {
  full_name?: string;
  custom_id?: string;
  phones?: Phone[];
  addresses?: Address[];
}

interface CreateClientPayload {
  full_name: string;
  phones: Phone[];
  addresses: Address[];
  custom_id?: string;
}

export const createNewClient = async (
  body: CreateClientPayload
) => {
  try {
    const response = await api.post(`v1/clients`, 
      body
    );
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateExistingClientById = async (
  clientId: string,
  payload: UpdateClientPayload
) => {
  try {
    const response = await api.patch(`v1/clients/${clientId}`, payload);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// export const deleteProductById = async (productId: string) => {
//   try {
//     const response = await api.delete(`v1/products/${productId}`);
//     return response.data;
//   } catch (error) {
//     throw error;
//   }
// };

// export const getProductById = async (productId: string) => {
//   try {
//     const response = await api.get(`v1/products/${productId}`);
//     return response.data;
//   } catch (error) {
//     throw error;
//   }
// };

export const getAllClients = async (
  full_name: string,
  custom_id: string,
  phone: string,
  clientsLimit: number,
  offset: number,
  order: string
) => {
  try {
    const response = await api.get(`v1/clients/all`, {
      params: {
        full_name: full_name,
        custom_id: custom_id,
        phone: phone,
        limit: clientsLimit,
        offset: offset,
        order: order,
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};
