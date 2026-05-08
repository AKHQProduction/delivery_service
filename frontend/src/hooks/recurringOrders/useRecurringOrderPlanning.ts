import { useEffect, useMemo, useReducer, useState } from "react";
import { usePaymentMethodsSettings } from "../settings/usePaymentMethodsSettings";
import { useTimeSlotsSettings } from "../settings/useTimeSlotsSettings";
import { useProducts } from "../products/useProducts";
import {
  createRecurringOrderTemplate,
  deleteRecurringOrder,
  pauseRecurringOrder,
  resumeRecurringOrder,
  runRecurringOrderWithPolicy,
} from "../../services/api/recurringOrderApi";
import { fetchRecurringOrdersForClient } from "../../services/clientPlanningData";
import { type Client } from "../../types/entities/Client";
import {
  type RecurringOrder,
} from "../../types/entities/RecurringOrder";
import {
  buildCreateRecurringOrderPayload,
  createRecurringOrderFormDraft,
  recurringOrderFormReducer,
  type RecurringTemplateSeed,
} from "../../utils/recurringOrderFormModel";
import {
  continueRunDialogAfterActivation,
  completeRunDialog,
  startRunDialog,
  type RunDialogState,
} from "../../utils/recurringOrderRunDialog";

const getPrimaryPhone = (client: Client) =>
  client.phones?.find((phone) => phone.is_primary) ?? client.phones?.[0];

const getPrimaryAddress = (client: Client) =>
  client.addresses?.find((address) => address.is_primary) ??
  client.addresses?.[0];

export const useRecurringOrderPlanning = (
  client: Client,
  seed: RecurringTemplateSeed | null,
  onSeedConsumed?: () => void,
) => {
  const [orders, setOrders] = useState<RecurringOrder[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [form, dispatchForm] = useReducer(
    recurringOrderFormReducer,
    undefined,
    createRecurringOrderFormDraft,
  );
  const [runDialog, setRunDialog] = useState<RunDialogState | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const { timeSlots } = useTimeSlotsSettings();
  const { paymentMethods } = usePaymentMethodsSettings();
  const { products, getProducts } = useProducts();

  const clientOrders = useMemo(
    () => orders.filter((order) => order.client_id === client.client_id),
    [client.client_id, orders],
  );

  const refresh = async () => {
    setIsLoading(true);
    try {
      setOrders(await fetchRecurringOrdersForClient(client));
    } finally {
      setIsLoading(false);
    }
  };

  const toggleWeekday = (day: number) => {
    dispatchForm({ type: "toggleWeekday", day });
  };

  const handleCreate = async () => {
    const payload = buildCreateRecurringOrderPayload(client.client_id, form);
    if (!payload) {
      return;
    }

    await createRecurringOrderTemplate(payload);

    setIsFormOpen(false);
    await refresh();
  };

  const handleRunClick = (order: RecurringOrder) => {
    setRunDialog(startRunDialog(order));
  };

  const executeRun = async (
    order: RecurringOrder,
    options: { includeToday: boolean; activate: boolean },
  ) => {
    setIsRunning(true);
    try {
      const result = await runRecurringOrderWithPolicy(order.recurring_order_id, {
        include_today: options.includeToday,
        activate: options.activate,
      });
      await refresh();
      setRunDialog(completeRunDialog(order, result));
    } finally {
      setIsRunning(false);
    }
  };

  const toggleStatus = async (order: RecurringOrder) => {
    if (order.status === "ACTIVE") {
      await pauseRecurringOrder(order.recurring_order_id);
    } else {
      await resumeRecurringOrder(order.recurring_order_id);
    }
    await refresh();
  };

  const deleteOrder = async (order: RecurringOrder) => {
    await deleteRecurringOrder(order.recurring_order_id);
    await refresh();
  };

  const closeRunDialog = () => {
    if (!isRunning) {
      setRunDialog(null);
    }
  };

  const continueAfterActivation = () => {
    setRunDialog((current) =>
      current ? continueRunDialogAfterActivation(current) : current,
    );
  };

  useEffect(() => {
    refresh();
    getProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [client.client_id]);

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
    if (paymentMethods[0]) {
      dispatchForm({
        type: "setPaymentMethodDefault",
        paymentMethod: paymentMethods[0].name,
      });
    }
  }, [paymentMethods]);

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
    addressId: form.addressId,
    clientOrders,
    comment: form.comment,
    deleteOrder,
    executeRun,
    handleCreate,
    handleRunClick,
    isFormOpen,
    isLoading,
    isRunning,
    monthDays: form.monthDays,
    paymentMethod: form.paymentMethod,
    paymentMethods,
    phoneId: form.phoneId,
    productId: form.productId,
    products,
    quantity: form.quantity,
    runDialog,
    scheduleType: form.scheduleType,
    setAddressId: (value: number | "") =>
      dispatchForm({ type: "setField", field: "addressId", value }),
    setComment: (value: string) =>
      dispatchForm({ type: "setField", field: "comment", value }),
    setIsFormOpen,
    setMonthDays: (value: string) =>
      dispatchForm({ type: "setField", field: "monthDays", value }),
    setPaymentMethod: (value: string) =>
      dispatchForm({ type: "setField", field: "paymentMethod", value }),
    setPhoneId: (value: number | "") =>
      dispatchForm({ type: "setField", field: "phoneId", value }),
    setProductId: (value: string) =>
      dispatchForm({ type: "setField", field: "productId", value }),
    setQuantity: (value: number) =>
      dispatchForm({ type: "setField", field: "quantity", value }),
    continueAfterActivation,
    setScheduleType: (value: typeof form.scheduleType) =>
      dispatchForm({ type: "setField", field: "scheduleType", value }),
    setTimeSlotId: (value: string) =>
      dispatchForm({ type: "setField", field: "timeSlotId", value }),
    timeSlotId: form.timeSlotId,
    timeSlots,
    toggleStatus,
    toggleWeekday,
    weekdays: form.weekdays,
    closeRunDialog,
  };
};
