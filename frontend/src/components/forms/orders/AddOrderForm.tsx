import React from "react";
import { AddOrderFormWeb } from "./AddOrderFormWeb";

export interface InitialOrderFormData {
  client_id?: string;
  phone_id?: number;
  address_id?: number;
  delivery_date?: string;
  date?: string;
  time_slot_id?: string;
  payment_method?: string;
  comment?: string;
  note?: string;
  items?: Array<{
    id: number;
    product_id: string;
    name?: string;
    price_per_item?: number;
    quantity: number;
  }>;
}

interface AddOrderFormProps {
  onClose: () => void;
  onSave?: (order?: unknown) => void;
  initialOrder?: InitialOrderFormData;
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
