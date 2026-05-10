export const BALANCE_PAYMENT_METHOD_NAME = "Баланс";

export const isBalancePaymentMethodName = (name: string) => name === BALANCE_PAYMENT_METHOD_NAME;

export const resolveAvailablePaymentMethodName = (
  requestedName: string | null | undefined,
  availableNames: string[],
) => {
  if (requestedName && availableNames.includes(requestedName)) {
    return requestedName;
  }

  return availableNames[0] ?? "";
};
