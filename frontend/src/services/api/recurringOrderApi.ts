import api from "../../config/api.config";
import {
  type CreateRecurringOrderPayload,
  type RecurringOrder,
  type RecurringOrderDetail,
  type RecurringOrderStatus,
  type RunRecurringOrderPayload,
  type RunRecurringOrderResult,
  type ScheduleType,
  type UpdateRecurringOrderOptions,
  type UpdateRecurringOrderPayload,
} from "../../types/entities/RecurringOrder";

export interface RecurringOrderFilters {
  client_id?: string;
  client_name?: string;
  status?: RecurringOrderStatus;
  schedule_type?: ScheduleType;
  weekday?: number;
  month_day?: number;
}

export const listRecurringOrders = async (
  filters: RecurringOrderFilters = {},
): Promise<RecurringOrder[]> => {
  const response = await api.get("v1/recurring-orders", { params: filters });
  return response.data;
};

export const getRecurringOrderById = async (
  recurringOrderId: string,
): Promise<RecurringOrderDetail> => {
  const response = await api.get(`v1/recurring-orders/${recurringOrderId}`);
  return response.data;
};

export const createRecurringOrderTemplate = async (
  payload: CreateRecurringOrderPayload,
): Promise<string> => {
  const response = await api.post("v1/recurring-orders", payload);
  return response.data;
};

export const updateRecurringOrderTemplate = async (
  recurringOrderId: string,
  payload: UpdateRecurringOrderPayload,
  options: UpdateRecurringOrderOptions = {},
) => {
  const response = await api.patch(`v1/recurring-orders/${recurringOrderId}`, payload, {
    params: options,
  });
  return response.data;
};

export const pauseRecurringOrder = async (
  recurringOrderId: string,
  options: { cancel_future_orders?: boolean } = {},
) => {
  const response = await api.post(`v1/recurring-orders/${recurringOrderId}/pause`, null, {
    params: options,
  });
  return response.data;
};

export const resumeRecurringOrder = async (recurringOrderId: string) => {
  const response = await api.post(`v1/recurring-orders/${recurringOrderId}/resume`);
  return response.data;
};

export const runRecurringOrderWithPolicy = async (
  recurringOrderId: string,
  payload: RunRecurringOrderPayload,
): Promise<RunRecurringOrderResult> => {
  const response = await api.post(`v1/recurring-orders/${recurringOrderId}/run`, payload);
  return response.data;
};

export const deleteRecurringOrder = async (
  recurringOrderId: string,
  options: { delete_future_orders?: boolean } = {},
) => {
  const response = await api.delete(`v1/recurring-orders/${recurringOrderId}`, {
    params: options,
  });
  return response.data;
};
