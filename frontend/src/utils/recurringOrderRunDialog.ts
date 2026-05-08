import {
  type RecurringOrder,
  type RunRecurringOrderResult,
} from "../types/entities/RecurringOrder";

export type RunDialogState =
  | { step: "activate"; order: RecurringOrder }
  | { step: "today"; order: RecurringOrder; activate: boolean }
  | {
      step: "summary";
      order: RecurringOrder;
      result: RunRecurringOrderResult;
    };

export const startRunDialog = (order: RecurringOrder): RunDialogState =>
  order.status === "PAUSED"
    ? { step: "activate", order }
    : { step: "today", order, activate: false };

export const continueRunDialogAfterActivation = (
  state: RunDialogState,
): RunDialogState =>
  state.step === "activate"
    ? { step: "today", order: state.order, activate: true }
    : state;

export const completeRunDialog = (
  order: RecurringOrder,
  result: RunRecurringOrderResult,
): RunDialogState => ({
  step: "summary",
  order,
  result,
});
