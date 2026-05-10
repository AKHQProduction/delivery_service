import { useState } from "react";
import {
  deleteRecurringOrder,
  pauseRecurringOrder,
  runRecurringOrderWithPolicy,
} from "../../services/api/recurringOrderApi";
import { type RecurringOrder } from "../../types/entities/RecurringOrder";
import {
  completeRunDialog,
  continueRunDialogAfterActivation,
  startRunDialogAfterActivationRequest,
  startRunDialog,
  type RunDialogState,
} from "../../utils/recurringOrderRunDialog";

interface UseRecurringOrderPlanningWorkflowOptions {
  refresh: () => Promise<unknown>;
}

export const useRecurringOrderPlanningWorkflow = ({
  refresh,
}: UseRecurringOrderPlanningWorkflowOptions) => {
  const [runDialog, setRunDialog] = useState<RunDialogState | null>(null);
  const [pauseDialogOrder, setPauseDialogOrder] = useState<RecurringOrder | null>(null);
  const [deleteDialogOrder, setDeleteDialogOrder] = useState<RecurringOrder | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const requestRun = (order: RecurringOrder) => {
    setRunDialog(startRunDialog(order));
  };

  const requestActivationRun = (order: RecurringOrder) => {
    setRunDialog(startRunDialogAfterActivationRequest(order));
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

  const closeRunDialog = () => {
    if (!isRunning) {
      setRunDialog(null);
    }
  };

  const continueRunAfterActivation = () => {
    setRunDialog((current) => (current ? continueRunDialogAfterActivation(current) : current));
  };

  const toggleStatus = async (order: RecurringOrder) => {
    if (order.status === "ACTIVE") {
      setPauseDialogOrder(order);
      return;
    }

    requestActivationRun(order);
  };

  const confirmPause = async (cancelFutureOrders: boolean) => {
    if (!pauseDialogOrder) return;

    await pauseRecurringOrder(pauseDialogOrder.recurring_order_id, {
      cancel_future_orders: cancelFutureOrders,
    });
    setPauseDialogOrder(null);
    await refresh();
  };

  const requestDelete = (order: RecurringOrder) => {
    setDeleteDialogOrder(order);
  };

  const confirmDelete = async (deleteFutureOrders: boolean) => {
    if (!deleteDialogOrder) return;

    await deleteRecurringOrder(deleteDialogOrder.recurring_order_id, {
      delete_future_orders: deleteFutureOrders,
    });
    setDeleteDialogOrder(null);
    await refresh();
  };

  return {
    closeRunDialog,
    confirmDelete,
    confirmPause,
    continueRunAfterActivation,
    deleteDialogOrder,
    executeRun,
    isRunning,
    pauseDialogOrder,
    requestDelete,
    requestRun,
    runDialog,
    setDeleteDialogOrder,
    setPauseDialogOrder,
    toggleStatus,
  };
};
