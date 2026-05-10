import { useEffect, useMemo, useReducer, useState } from "react";
import { usePaymentMethodsSettings } from "../settings/usePaymentMethodsSettings";
import { useTimeSlotsSettings } from "../settings/useTimeSlotsSettings";
import { useProducts } from "../products/useProducts";
import {
  createRecurringOrderTemplate,
  type RecurringOrderFilters,
  updateRecurringOrderTemplate,
} from "../../services/api/recurringOrderApi";
import { fetchRecurringOrdersForClient } from "../../services/clientPlanningData";
import { type Client } from "../../types/entities/Client";
import {
  type RecurringOrder,
  type RecurringOrderDetail,
} from "../../types/entities/RecurringOrder";
import { resolveAvailablePaymentMethodName } from "../../shared/paymentMethod";
import {
  buildCreateRecurringOrderPayload,
  buildUpdateRecurringOrderPayload,
  createRecurringOrderFormDraft,
  recurringOrderFormReducer,
  type RecurringTemplateSeed,
} from "../../utils/recurringOrderFormModel";
import { useRecurringOrderPlanningWorkflow } from "./useRecurringOrderPlanningWorkflow";

const getPrimaryPhone = (client: Client) =>
  client.phones?.find((phone) => phone.is_primary) ?? client.phones?.[0];

const getPrimaryAddress = (client: Client) =>
  client.addresses?.find((address) => address.is_primary) ?? client.addresses?.[0];

export const useRecurringOrderPlanning = (
  client: Client,
  seed: RecurringTemplateSeed | null,
  onSeedConsumed?: () => void,
  filters: Omit<RecurringOrderFilters, "client_id" | "client_name"> = {},
) => {
  const [orders, setOrders] = useState<RecurringOrder[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingOrderId, setEditingOrderId] = useState<string | null>(null);
  const [form, dispatchForm] = useReducer(
    recurringOrderFormReducer,
    undefined,
    createRecurringOrderFormDraft,
  );

  const { timeSlots } = useTimeSlotsSettings();
  const { paymentMethods } = usePaymentMethodsSettings();
  const { products, getProducts } = useProducts();

  const clientOrders = useMemo(
    () => orders.filter((order) => order.client_id === client.client_id),
    [client.client_id, orders],
  );
  const paymentMethodNames = useMemo(
    () => paymentMethods.map((method) => method.name),
    [paymentMethods],
  );
  const canSubmit = useMemo(
    () =>
      Boolean(
        form.phoneId &&
        form.addressId &&
        form.timeSlotId &&
        form.paymentMethod &&
        paymentMethodNames.includes(form.paymentMethod) &&
        form.items.length > 0 &&
        form.items.every((item) => item.productId && item.quantity > 0) &&
        (form.scheduleType === "WEEKLY"
          ? form.weekdays.length > 0
          : form.monthDays.trim().length > 0),
      ),
    [form, paymentMethodNames],
  );

  const refresh = async () => {
    setIsLoading(true);
    try {
      const nextOrders = await fetchRecurringOrdersForClient(client, filters);
      setOrders(nextOrders);
      return nextOrders;
    } finally {
      setIsLoading(false);
    }
  };

  const workflow = useRecurringOrderPlanningWorkflow({ refresh });

  const toggleWeekday = (day: number) => {
    dispatchForm({ type: "toggleWeekday", day });
  };

  const handleCreate = async () => {
    if (editingOrderId) {
      const payload = buildUpdateRecurringOrderPayload(form);
      if (!payload) {
        return;
      }

      await updateRecurringOrderTemplate(editingOrderId, payload);
      setIsFormOpen(false);
      setEditingOrderId(null);
      await refresh();
      return;
    }

    const payload = buildCreateRecurringOrderPayload(client.client_id, form);
    if (!payload) {
      return;
    }

    const recurringOrderId = await createRecurringOrderTemplate(payload);

    setIsFormOpen(false);
    const nextOrders = await refresh();
    const createdOrder = nextOrders.find((order) => order.recurring_order_id === recurringOrderId);
    if (createdOrder) {
      workflow.requestRun(createdOrder);
    }
  };

  useEffect(() => {
    refresh();
    getProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [client.client_id, filters.month_day, filters.schedule_type, filters.status, filters.weekday]);

  useEffect(() => {
    dispatchForm({
      type: "setDefaults",
      phoneId: getPrimaryPhone(client)?.id,
      addressId: getPrimaryAddress(client)?.id,
    });
  }, [client]);

  useEffect(() => {
    if (timeSlots[0]) {
      dispatchForm({
        type: "setTimeSlotDefault",
        timeSlotId: timeSlots[0].time_slot_id,
      });
    }
  }, [timeSlots]);

  useEffect(() => {
    const paymentMethod = resolveAvailablePaymentMethodName(form.paymentMethod, paymentMethodNames);
    if (paymentMethod && paymentMethod !== form.paymentMethod) {
      dispatchForm({ type: "setField", field: "paymentMethod", value: paymentMethod });
    }
  }, [form.paymentMethod, paymentMethodNames]);

  useEffect(() => {
    if (products[0]) {
      dispatchForm({
        type: "setProductDefault",
        productId: products[0].product_id,
      });
    }
  }, [products]);

  useEffect(() => {
    if (!seed) return;

    dispatchForm({ type: "applySeed", seed });
    setIsFormOpen(true);
    onSeedConsumed?.();
  }, [onSeedConsumed, seed]);

  return {
    clientOrders,
    form: {
      draft: form,
      mode: editingOrderId ? "edit" : "create",
      isOpen: isFormOpen,
      canSubmit,
    },
    formActions: {
      create: handleCreate,
      close: () => {
        setIsFormOpen(false);
        setEditingOrderId(null);
      },
      open: () => {
        setEditingOrderId(null);
        setIsFormOpen(true);
      },
      startEdit: (detail: RecurringOrderDetail) => {
        dispatchForm({ type: "applyDetail", detail });
        setEditingOrderId(detail.recurring_order_id);
        setIsFormOpen(true);
      },
      toggleOpen: () => setIsFormOpen((value) => !value),
      applySeed: (nextSeed: RecurringTemplateSeed) =>
        dispatchForm({ type: "applySeed", seed: nextSeed }),
      selectAddress: (value: number | "") =>
        dispatchForm({ type: "setField", field: "addressId", value }),
      selectPhone: (value: number | "") =>
        dispatchForm({ type: "setField", field: "phoneId", value }),
      selectTimeSlot: (value: string) =>
        dispatchForm({ type: "setField", field: "timeSlotId", value }),
      selectPaymentMethod: (value: string) =>
        dispatchForm({ type: "setField", field: "paymentMethod", value }),
      addItem: () => dispatchForm({ type: "addItem", productId: products[0]?.product_id }),
      removeItem: (itemId: string) => dispatchForm({ type: "removeItem", itemId }),
      selectItemProduct: (itemId: string, productId: string) =>
        dispatchForm({ type: "setItemProduct", itemId, productId }),
      setComment: (value: string) => dispatchForm({ type: "setField", field: "comment", value }),
      setMonthDays: (value: string) =>
        dispatchForm({ type: "setField", field: "monthDays", value }),
      setItemQuantity: (itemId: string, quantity: number) =>
        dispatchForm({ type: "setItemQuantity", itemId, quantity }),
      setScheduleType: (value: typeof form.scheduleType) =>
        dispatchForm({ type: "setField", field: "scheduleType", value }),
      toggleWeekday,
    },
    isLoading,
    options: {
      paymentMethods,
      products,
      timeSlots,
    },
    workflow,
  };
};
