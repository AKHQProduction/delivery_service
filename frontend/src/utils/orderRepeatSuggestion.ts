import { type Client } from "../types/entities/Client";
import { type Order, type OrderItem } from "../types/entities/Order";
import { type Product } from "../types/entities/Product";
import { addDaysToDateKey } from "./dateUtils";

export interface RepeatOrderFormProduct {
  product: Product;
  quantity: number;
}

export interface RepeatOrderDraft {
  client: Client;
  products: RepeatOrderFormProduct[];
  deliveryPhone: NonNullable<Client["phones"]>[number] | null;
  deliveryAddress: NonNullable<Client["addresses"]>[number] | null;
  deliveryDate: string;
  timeSlotId: string;
  paymentMethod: string;
  note: string;
}

export type MissingRepeatOrderField =
  | "phone"
  | "address"
  | "deliveryDate"
  | "timeSlot"
  | "paymentMethod"
  | "products";

export interface AvailableOrderRepeatSuggestion {
  kind: "available";
  order: Order;
  draft: RepeatOrderDraft;
  skippedItems: OrderItem[];
  missingRequiredFields: MissingRepeatOrderField[];
}

export interface NoOrderRepeatSuggestion {
  kind: "none";
}

export type OrderRepeatSuggestion = AvailableOrderRepeatSuggestion | NoOrderRepeatSuggestion;

interface BuildOrderRepeatSuggestionOptions {
  client: Client;
  lastOrder: Order | null | undefined;
  products: Product[];
  todayKey: string;
  paymentMethodNames: string[];
}

const normalize = (value: string | undefined | null) =>
  (value || "").trim().toLocaleLowerCase("uk-UA");

const findPhone = (client: Client, order: Order) => {
  const phones = client.phones || [];
  return (
    phones.find((phone) => phone.number === order.delivery_phone) ||
    phones.find((phone) => phone.is_primary) ||
    phones[0] ||
    null
  );
};

const findAddress = (client: Client, order: Order) => {
  const addresses = client.addresses || [];
  const orderAddress = order.delivery_address;

  return (
    addresses.find(
      (address) =>
        normalize(address.street) === normalize(orderAddress?.street) &&
        normalize(address.house) === normalize(orderAddress?.house) &&
        normalize(address.apartment) === normalize(orderAddress?.apartment),
    ) ||
    addresses.find((address) => address.is_primary) ||
    addresses[0] ||
    null
  );
};

export const buildOrderRepeatSuggestion = ({
  client,
  lastOrder,
  products,
  todayKey,
  paymentMethodNames,
}: BuildOrderRepeatSuggestionOptions): OrderRepeatSuggestion => {
  if (!lastOrder) {
    return { kind: "none" };
  }

  const availableItems: RepeatOrderFormProduct[] = [];
  const skippedItems: OrderItem[] = [];

  for (const item of lastOrder.items || []) {
    const product = products.find((candidate) => candidate.product_id === item.product_id);
    if (product) {
      availableItems.push({ product, quantity: item.quantity });
    } else {
      skippedItems.push(item);
    }
  }

  if (availableItems.length === 0) {
    return { kind: "none" };
  }

  const deliveryPhone = findPhone(client, lastOrder);
  const deliveryAddress = findAddress(client, lastOrder);
  const previousPaymentMethod = lastOrder.payment_method || "";
  const paymentMethod = paymentMethodNames.includes(previousPaymentMethod)
    ? previousPaymentMethod
    : "";
  const deliveryDate = addDaysToDateKey(todayKey, 1);
  const timeSlotId = deliveryAddress?.preferred_time_slot_id || "";
  const missingRequiredFields: MissingRepeatOrderField[] = [];

  if (!deliveryPhone) missingRequiredFields.push("phone");
  if (!deliveryAddress) missingRequiredFields.push("address");
  if (!deliveryDate) missingRequiredFields.push("deliveryDate");
  if (!timeSlotId) missingRequiredFields.push("timeSlot");
  if (!paymentMethod) missingRequiredFields.push("paymentMethod");
  if (availableItems.length === 0) missingRequiredFields.push("products");

  return {
    kind: "available",
    order: lastOrder,
    skippedItems,
    missingRequiredFields,
    draft: {
      client,
      products: availableItems,
      deliveryPhone,
      deliveryAddress,
      deliveryDate,
      timeSlotId,
      paymentMethod,
      note: lastOrder.comment || lastOrder.note || "",
    },
  };
};
