import React from "react";
import { type Client } from "../../../../types/entities/Client";
import { type Product } from "../../../../types/entities/Product";
import { Tooltip } from "../../../ui/Tooltip";
import { DateInput } from "../../../shared/DateInput";
import { FormSelect } from "../../../shared/FormSelect";

interface SelectedProduct {
  product: Product;
  quantity: number;
}

interface DeliveryDateStepProps {
  client: Client | null;
  selectedPhone: string;
  selectedAddress: string;
  selectedProducts: SelectedProduct[];
  deliveryDate: string;
  timeSlotId: string;
  timeSlots: {
    time_slot_id: string;
    start_time: string;
    end_time: string;
    label?: string;
  }[];
  paymentMethod: string;
  note: string;
  onDateChange: (date: string) => void;
  onTimeChange: (time: string) => void;
  onPaymentMethodChange: (paymentMethod: string) => void;
  onNoteChange: (note: string) => void;
}

export const DeliveryDateStep: React.FC<DeliveryDateStepProps> = ({
  client,
  selectedPhone,
  selectedAddress,
  selectedProducts,
  deliveryDate,
  timeSlotId,
  timeSlots,
  paymentMethod,
  note,
  onDateChange,
  onTimeChange,
  onPaymentMethodChange,
  onNoteChange,
}) => {
  const totalAmount = selectedProducts.reduce((sum, p) => sum + p.product.price * p.quantity, 0);

  const totalItems = selectedProducts.reduce((sum, p) => sum + p.quantity, 0);

  const formatDate = (dateString: string) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString("uk-UA", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  const selectedSlot = timeSlots.find((slot) => slot.time_slot_id === timeSlotId);
  return (
    <div className="space-y-6">
      <h3 className="text-xl font-bold text-gray-900">Дата доставки та підсумок</h3>

      <DateInput
        label="Дата доставки"
        value={deliveryDate}
        onChange={onDateChange}
        required
        minDate={new Date().toISOString().split("T")[0]}
        icon={
          <svg
            className="w-5 h-5 text-indigo-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        }
      />

      <FormSelect
        label="Час доставки"
        name="deliveryTime"
        value={timeSlotId}
        required={true}
        onChange={(e) => onTimeChange(e.target.value)}
        options={timeSlots.map((slot) => ({
          value: slot.time_slot_id,
          label: slot.label
            ? `${slot.label} (${slot.start_time} - ${slot.end_time})`
            : `${slot.start_time} - ${slot.end_time}`,
        }))}
      />

      <FormSelect
        label="Спосіб оплати"
        name="paymentMethod"
        value={paymentMethod}
        required={true}
        onChange={(e) => onPaymentMethodChange(e.target.value)}
        options={[
          { value: "CASH", label: "Готівка" },
          { value: "BANK_TRANSFER", label: "На рахунок" },
          { value: "OTHER", label: "Інше" },
        ]}
      />

      <div>
        {deliveryDate && (
          <div className="flex items-center gap-2 text-sm text-indigo-600 mt-2">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="font-medium">
              Доставка: {formatDate(deliveryDate)} <br />
              {selectedSlot
                ? `${selectedSlot.label} (${selectedSlot.start_time} - ${selectedSlot.end_time})`
                : ""}
            </span>
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 pt-4">
        <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg
            className="w-5 h-5 text-indigo-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Підсумок замовлення
        </h4>

        <div className="space-y-4">
          <div className="p-4 bg-linear-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
            <div className="flex items-start gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold shrink-0">
                {(client?.full_name || "")
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase()
                  .slice(0, 2)}
              </div>
              <div className="flex-1">
                <div className="text-xs text-gray-600 mb-0.5">Клієнт</div>
                <div className="font-semibold text-gray-900">{client?.full_name}</div>
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-gray-700">
                <svg
                  className="w-4 h-4 text-indigo-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                  />
                </svg>
                <span className="font-medium">{selectedPhone}</span>
              </div>
              <div className="flex items-start gap-2 text-gray-700">
                <svg
                  className="w-4 h-4 text-indigo-600 mt-0.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <span className="font-medium flex-1">{selectedAddress}</span>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-sm font-medium text-gray-700 mb-2">
              Товари ({selectedProducts.length})
            </div>
            {selectedProducts.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{item.product.name}</div>
                  <div className="text-sm text-gray-600">
                    {item.product.price} ₴ × {item.quantity} шт.
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900">
                    {item.product.price * item.quantity} ₴
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 bg-linear-to-r from-indigo-600 to-purple-600 rounded-xl text-white">
            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="text-sm opacity-90">Всього товарів</div>
                <div className="text-2xl font-bold">{totalItems} шт.</div>
              </div>
              <div className="text-right">
                <div className="text-sm opacity-90">До сплати</div>
                <div className="text-3xl font-bold">{totalAmount} ₴</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <textarea
        value={note}
        onChange={(e) => onNoteChange(e.target.value)}
        placeholder="Примітка до замовлення..."
        rows={2}
        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none text-sm"
      />

      <div>
        <Tooltip
          type="success"
          message="Перевірте всі деталі замовлення та натисніть кнопку 'Створити замовлення' для завершення."
        />
      </div>
    </div>
  );
};
