import api from "../../config/api.config";
import { type Phone, type Address } from "../../types/entities/Client";

interface UpdateClientPayload {
  full_name?: string;
  balance?: number;
  phones?: Phone[];
  addresses?: Address[];
}

interface CreateClientPayload {
  full_name: string;
  phones: Phone[];
  addresses: Address[];
}

const normalizeOptionalUuid = (value: string | null | undefined) => {
  if (value === undefined || value === null || value.trim() === "") {
    return null;
  }

  return value;
};

const normalizeAddresses = (addresses: Address[]) =>
  addresses.map((address) => ({
    ...address,
    district_id: normalizeOptionalUuid(address.district_id),
    preferred_time_slot_id: normalizeOptionalUuid(address.preferred_time_slot_id),
  }));

const normalizeCreateClientPayload = (body: CreateClientPayload): CreateClientPayload => ({
  ...body,
  addresses: normalizeAddresses(body.addresses),
});

const normalizeUpdateClientPayload = (payload: UpdateClientPayload): UpdateClientPayload => ({
  ...payload,
  addresses: payload.addresses ? normalizeAddresses(payload.addresses) : undefined,
});

export interface ImportResult {
  imported: number;
  skipped: number;
  error_file_id: string | null;
  error_filename: string | null;
}

export interface ColumnPreview {
  index: number;
  header: string | null;
  sample_values: string[];
}

export interface PreviewResult {
  columns: ColumnPreview[];
  total_rows: number;
}

export type ColumnMapping = Record<number, string>;

export interface ClientSummary {
  total_count: number;
  debt_count: number;
  positive_balance_count: number;
}

export const createNewClient = async (
  body: CreateClientPayload,
  confirmDuplicate: boolean = false,
) => {
  const payload = normalizeCreateClientPayload(body);
  const response = await api.post(`v1/clients`, {
    ...payload,
    ...(confirmDuplicate && { confirm_duplicate_phones: true }),
  });
  return response.data;
};

export const updateExistingClientById = async (
  clientId: string,
  payload: UpdateClientPayload,
  confirmDuplicate: boolean = false,
) => {
  const normalizedPayload = normalizeUpdateClientPayload(payload);
  const response = await api.patch(`v1/clients/${clientId}`, {
    ...normalizedPayload,
    ...(confirmDuplicate && { confirm_duplicate_phones: true }),
  });
  return response.data;
};

export const deleteClientById = async (clientId: string) => {
  const response = await api.delete(`v1/clients/${clientId}`);
  return response.data;
};

export const getClientById = async (clientId: string) => {
  const response = await api.get(`v1/clients/${clientId}`);
  return response.data;
};

export const setClientBalance = async (clientId: string, balance: number) => {
  const response = await api.patch(`v1/clients/${clientId}/balance`, {
    balance,
  });
  return response.data;
};

export const previewImportXlsx = async (file: File): Promise<PreviewResult> => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post(`v1/clients/import/preview`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data as PreviewResult;
};

export const importClientsFromXlsx = async (
  file: File,
  columnMapping?: ColumnMapping,
  firstRowIsHeader?: boolean,
  originalHeaders?: string[],
): Promise<ImportResult> => {
  const formData = new FormData();
  formData.append("file", file);
  if (columnMapping) {
    formData.append("column_mapping", JSON.stringify(columnMapping));
    formData.append("first_row_is_header", String(firstRowIsHeader ?? true));
    if (originalHeaders) {
      formData.append("original_headers", JSON.stringify(originalHeaders));
    }
  }
  const response = await api.post(`v1/clients/import`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data as ImportResult;
};

export const getAllClients = async (
  full_name: string,
  phone: string,
  clientsLimit: number,
  offset: number,
  order: string,
  hasDebt?: boolean,
  hasPositiveBalance?: boolean,
) => {
  const params: Record<string, string | number> = {
    limit: clientsLimit,
    offset: offset,
    order: order,
  };

  if (full_name) params.full_name = full_name;
  if (phone) params.phone = phone;
  if (hasDebt !== undefined) params.has_debt = String(hasDebt);
  if (hasPositiveBalance !== undefined) {
    params.has_positive_balance = String(hasPositiveBalance);
  }

  const response = await api.get(`v1/clients/all`, { params });
  return response.data;
};

export const getClientSummary = async (
  full_name: string,
  phone: string,
): Promise<ClientSummary> => {
  const params: Record<string, string> = {};

  if (full_name) params.full_name = full_name;
  if (phone) params.phone = phone;

  const response = await api.get(`v1/clients/summary`, { params });
  return response.data;
};
