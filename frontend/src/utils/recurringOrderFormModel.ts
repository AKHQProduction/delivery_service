import {
  type CreateRecurringOrderPayload,
  type RecurringOrderDetail,
  type ScheduleType,
  type UpdateRecurringOrderPayload,
} from "../types/entities/RecurringOrder";
import { type Order } from "../types/entities/Order";

export interface RecurringTemplateSeed {
  product_id?: string;
  quantity?: number;
  items?: Array<{ product_id: string; quantity: number }>;
  payment_method?: string;
  comment?: string;
}

export interface RecurringOrderFormItemDraft {
  id: string;
  productId: string;
  quantity: number;
}

export interface RecurringOrderFormDraft {
  scheduleType: ScheduleType;
  weekdays: number[];
  monthDays: string;
  phoneId: number | "";
  addressId: number | "";
  timeSlotId: string;
  paymentMethod: string;
  items: RecurringOrderFormItemDraft[];
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
  | { type: "addItem"; productId?: string }
  | { type: "removeItem"; itemId: string }
  | { type: "setItemProduct"; itemId: string; productId: string }
  | { type: "setItemQuantity"; itemId: string; quantity: number }
  | { type: "applySeed"; seed: RecurringTemplateSeed }
  | { type: "applyDetail"; detail: RecurringOrderDetail };

let itemDraftId = 0;

const createItemDraft = (productId = "", quantity = 1): RecurringOrderFormItemDraft => ({
  id: `recurring-item-${itemDraftId++}`,
  productId,
  quantity,
});

export const createRecurringOrderFormDraft = (): RecurringOrderFormDraft => ({
  scheduleType: "WEEKLY",
  weekdays: [1],
  monthDays: "1",
  phoneId: "",
  addressId: "",
  timeSlotId: "",
  paymentMethod: "",
  items: [createItemDraft()],
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
      return state.timeSlotId ? state : { ...state, timeSlotId: action.timeSlotId };
    case "setPaymentMethodDefault":
      return state.paymentMethod ? state : { ...state, paymentMethod: action.paymentMethod };
    case "setProductDefault":
      return state.items.some((item) => item.productId)
        ? state
        : {
            ...state,
            items: state.items.map((item, index) =>
              index === 0 ? { ...item, productId: action.productId } : item,
            ),
          };
    case "addItem":
      return {
        ...state,
        items: [...state.items, createItemDraft(action.productId ?? "")],
      };
    case "removeItem":
      return state.items.length <= 1
        ? state
        : {
            ...state,
            items: state.items.filter((item) => item.id !== action.itemId),
          };
    case "setItemProduct":
      return {
        ...state,
        items: state.items.map((item) =>
          item.id === action.itemId ? { ...item, productId: action.productId } : item,
        ),
      };
    case "setItemQuantity":
      return {
        ...state,
        items: state.items.map((item) =>
          item.id === action.itemId ? { ...item, quantity: Math.max(1, action.quantity) } : item,
        ),
      };
    case "applySeed": {
      const seedItems = action.seed.items?.length
        ? action.seed.items
        : action.seed.product_id
          ? [
              {
                product_id: action.seed.product_id,
                quantity: action.seed.quantity ?? 1,
              },
            ]
          : null;

      return {
        ...state,
        scheduleType: "WEEKLY",
        weekdays: [1],
        items: seedItems
          ? seedItems.map((item) => createItemDraft(item.product_id, item.quantity))
          : [createItemDraft(state.items[0]?.productId ?? "", state.items[0]?.quantity ?? 1)],
        paymentMethod: action.seed.payment_method ?? state.paymentMethod,
        comment: action.seed.comment ?? "",
      };
    }
    case "applyDetail":
      return {
        ...state,
        scheduleType: action.detail.schedule_type,
        weekdays: action.detail.weekdays ?? [],
        monthDays: action.detail.month_days?.join(", ") ?? "",
        phoneId: action.detail.phone_id ?? "",
        addressId: action.detail.address_id ?? "",
        timeSlotId: action.detail.time_slot_id ?? "",
        paymentMethod: action.detail.payment_method,
        items: action.detail.items.map((item) => createItemDraft(item.product_id, item.quantity)),
        comment: action.detail.comment ?? "",
      };
  }
};

export const buildRecurringTemplateSeed = (order: Order): RecurringTemplateSeed => {
  const seedItem = order.items.find((item) => item.product_id);
  const items = order.items.flatMap((item) =>
    item.product_id
      ? [
          {
            product_id: item.product_id,
            quantity: item.quantity,
          },
        ]
      : [],
  );

  return {
    product_id: seedItem?.product_id ?? undefined,
    quantity: seedItem?.quantity,
    items,
    payment_method: order.payment_method,
    comment: order.comment || order.note || "",
  };
};

export const buildCreateRecurringOrderPayload = (
  clientId: string,
  draft: RecurringOrderFormDraft,
): CreateRecurringOrderPayload | null => {
  const templatePayload = buildUpdateRecurringOrderPayload(draft);
  if (!templatePayload) {
    return null;
  }

  return {
    client_id: clientId,
    ...templatePayload,
  };
};

export const buildUpdateRecurringOrderPayload = (
  draft: RecurringOrderFormDraft,
): UpdateRecurringOrderPayload | null => {
  const items = draft.items.map((item) => ({
    product_id: item.productId,
    quantity: item.quantity,
  }));

  if (
    !draft.phoneId ||
    !draft.addressId ||
    !draft.timeSlotId ||
    !draft.paymentMethod ||
    items.length === 0 ||
    items.some((item) => !item.product_id || item.quantity <= 0)
  ) {
    return null;
  }

  return {
    address_id: draft.addressId,
    phone_id: draft.phoneId,
    time_slot_id: draft.timeSlotId,
    items,
    payment_method: draft.paymentMethod,
    comment: draft.comment.trim() || null,
    schedule_type: draft.scheduleType,
    weekdays: draft.scheduleType === "WEEKLY" ? draft.weekdays : null,
    month_days: draft.scheduleType === "MONTHLY_BY_DAY" ? parseMonthDays(draft.monthDays) : null,
  };
};

const parseMonthDays = (monthDays: string) =>
  monthDays
    .split(",")
    .map((value) => Number(value.trim()))
    .filter((value) => Number.isInteger(value));
