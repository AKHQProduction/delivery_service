import {
  type CreateRecurringOrderPayload,
  type ScheduleType,
} from "../types/entities/RecurringOrder";
import { type Order } from "../types/entities/Order";

export interface RecurringTemplateSeed {
  product_id?: string;
  quantity?: number;
  payment_method?: string;
  comment?: string;
}

export interface RecurringOrderFormDraft {
  scheduleType: ScheduleType;
  weekdays: number[];
  monthDays: string;
  phoneId: number | "";
  addressId: number | "";
  timeSlotId: string;
  paymentMethod: string;
  productId: string;
  quantity: number;
  comment: string;
}

export type RecurringOrderFormAction =
  | {
      type: "setField";
      field: keyof RecurringOrderFormDraft;
      value: RecurringOrderFormDraft[keyof RecurringOrderFormDraft];
    }
  | { type: "toggleWeekday"; day: number }
  | { type: "setDefaults"; phoneId?: number; addressId?: number }
  | { type: "setTimeSlotDefault"; timeSlotId: string }
  | { type: "setPaymentMethodDefault"; paymentMethod: string }
  | { type: "setProductDefault"; productId: string }
  | { type: "applySeed"; seed: RecurringTemplateSeed };

export const createRecurringOrderFormDraft = (): RecurringOrderFormDraft => ({
  scheduleType: "WEEKLY",
  weekdays: [1],
  monthDays: "1",
  phoneId: "",
  addressId: "",
  timeSlotId: "",
  paymentMethod: "",
  productId: "",
  quantity: 1,
  comment: "",
});

export const recurringOrderFormReducer = (
  state: RecurringOrderFormDraft,
  action: RecurringOrderFormAction,
): RecurringOrderFormDraft => {
  switch (action.type) {
    case "setField":
      return { ...state, [action.field]: action.value };
    case "toggleWeekday":
      return {
        ...state,
        weekdays: state.weekdays.includes(action.day)
          ? state.weekdays.filter((value) => value !== action.day)
          : [...state.weekdays, action.day].sort((a, b) => a - b),
      };
    case "setDefaults":
      return {
        ...state,
        phoneId: action.phoneId ?? "",
        addressId: action.addressId ?? "",
      };
    case "setTimeSlotDefault":
      return state.timeSlotId
        ? state
        : { ...state, timeSlotId: action.timeSlotId };
    case "setPaymentMethodDefault":
      return state.paymentMethod
        ? state
        : { ...state, paymentMethod: action.paymentMethod };
    case "setProductDefault":
      return state.productId ? state : { ...state, productId: action.productId };
    case "applySeed":
      return {
        ...state,
        scheduleType: "WEEKLY",
        weekdays: [1],
        productId: action.seed.product_id ?? state.productId,
        quantity: action.seed.quantity ?? state.quantity,
        paymentMethod: action.seed.payment_method ?? state.paymentMethod,
        comment: action.seed.comment ?? "",
      };
  }
};

export const buildRecurringTemplateSeed = (
  order: Order,
): RecurringTemplateSeed => {
  const seedItem = order.items.find((item) => item.product_id);
  return {
    product_id: seedItem?.product_id ?? undefined,
    quantity: seedItem?.quantity,
    payment_method: order.payment_method,
    comment: order.comment || order.note || "",
  };
};

export const buildCreateRecurringOrderPayload = (
  clientId: string,
  draft: RecurringOrderFormDraft,
): CreateRecurringOrderPayload | null => {
  if (
    !draft.phoneId ||
    !draft.addressId ||
    !draft.timeSlotId ||
    !draft.paymentMethod ||
    !draft.productId
  ) {
    return null;
  }

  return {
    client_id: clientId,
    address_id: draft.addressId,
    phone_id: draft.phoneId,
    time_slot_id: draft.timeSlotId,
    items: [{ product_id: draft.productId, quantity: draft.quantity }],
    payment_method: draft.paymentMethod,
    comment: draft.comment.trim() || null,
    schedule_type: draft.scheduleType,
    weekdays: draft.scheduleType === "WEEKLY" ? draft.weekdays : null,
    month_days:
      draft.scheduleType === "MONTHLY_BY_DAY"
        ? parseMonthDays(draft.monthDays)
        : null,
  };
};

const parseMonthDays = (monthDays: string) =>
  monthDays
    .split(",")
    .map((value) => Number(value.trim()))
    .filter((value) => Number.isInteger(value));
