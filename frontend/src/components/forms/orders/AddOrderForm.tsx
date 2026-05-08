import React from "react";
import { AddOrderFormWeb } from "./AddOrderFormWeb";
import { type RegularOrderDraft } from "../../../utils/orderDraft";

interface AddOrderFormProps {
  onClose: () => void;
  onSave?: (order?: unknown) => void;
  initialOrder?: RegularOrderDraft;
}

export const AddOrderForm: React.FC<AddOrderFormProps> = ({
  onClose,
  onSave,
  initialOrder,
}) => {
  return (
    <AddOrderFormWeb
      onClose={onClose}
      onSave={onSave}
      initialOrder={initialOrder}
    />
  );
};
