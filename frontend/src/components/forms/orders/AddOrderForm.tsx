import React from "react";
import { AddOrderFormWeb } from "./AddOrderFormWeb";

interface AddOrderFormProps {
  onClose: () => void;
  onSave?: (order?: unknown) => void;
}

export const AddOrderForm: React.FC<AddOrderFormProps> = ({ onClose, onSave }) => {
  return <AddOrderFormWeb onClose={onClose} onSave={onSave} />;
};
