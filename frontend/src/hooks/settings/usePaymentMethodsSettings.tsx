import { useState, useEffect } from "react";
import {
  getAllPaymentMethods,
  createPaymentMethod,
  updatePaymentMethod,
  deletePaymentMethod,
} from "../../services/api/settingsApi";

interface PaymentMethod {
  payment_method_id: string;
  name: string;
}

export const usePaymentMethodsSettings = () => {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchPaymentMethods = async () => {
    try {
      setIsLoading(true);
      const data = (await getAllPaymentMethods()) as PaymentMethod[];
      setPaymentMethods(data);
    } catch (error) {
      console.error("Error fetching payment methods:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPaymentMethods();
  }, []);

  const addPaymentMethod = async (name: string) => {
    try {
      await createPaymentMethod(name);
      await fetchPaymentMethods();
    } catch (error) {
      console.error("Error adding payment method:", error);
      throw error;
    }
  };

  const updatePaymentMethodById = async (id: string, name: string) => {
    try {
      await updatePaymentMethod(id, name);
      await fetchPaymentMethods();
    } catch (error) {
      console.error("Error updating payment method:", error);
      throw error;
    }
  };

  const deletePaymentMethodById = async (id: string) => {
    try {
      await deletePaymentMethod(id);
      await fetchPaymentMethods();
    } catch (error) {
      console.error("Error deleting payment method:", error);
      throw error;
    }
  };

  return {
    paymentMethods,
    addPaymentMethod,
    updatePaymentMethodById,
    deletePaymentMethodById,
    isLoading,
    refetch: fetchPaymentMethods,
  };
};
