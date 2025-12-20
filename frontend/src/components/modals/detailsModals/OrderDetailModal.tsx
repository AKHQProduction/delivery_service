import { ModalButtons } from "../../ui/modalButtons";
import leftArrowIcon from "../../../assets/icons/left_arrow.svg";
import { timeMap } from "../../../utils/dataMap";
import { useState } from "react";
import { EditOrderForm } from "../../forms/orders/EditOrderForm";

export const OrderDetailModal = ({ order, onClose, onDelete, onSave }) => {
  const [isEditing, setIsEditing] = useState(false);

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleSaveEdit = () => {
    setIsEditing(false);
    onSave?.();
  };

  const getOrderTotal = () => {
    return (order.items ?? []).reduce((sum, item) => {
      const quantity = Number(item.quantity) || 0;
      const price = Number(item.price_per_item) || 0;
      return sum + quantity * price;
    }, 0);
  };

  const getTotalItems = () => {
    return (order.items ?? []).reduce(
      (sum, item) => sum + (Number(item.quantity) || 0),
      0
    );
  };

  if (isEditing) {
    return (
      <div className="h-full flex flex-col">
        <div className="bg-linear-to-br from-indigo-600 to-indigo-700 px-6 pt-12 pb-8">
          <button
            onClick={handleCancelEdit}
            type="button"
            title="cancel"
            className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center mb-6 hover:bg-white/30 transition-colors"
          >
            <img src={leftArrowIcon} alt="Back" className="w-8 h-8" />
          </button>
          <h1 className="text-3xl font-bold text-white mb-2">
            Редагувати замовлення
          </h1>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6">
          <EditOrderForm
            order={order}
            onClose={handleCancelEdit}
            onSave={handleSaveEdit}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="bg-linear-to-br from-indigo-600 to-indigo-700 px-6 pt-12 pb-8">
        <button
          onClick={onClose}
          type="button"
          title="close"
          className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center mb-6 hover:bg-white/30 transition-colors"
        >
          <img src={leftArrowIcon} alt="Back" className="w-8 h-8" />
        </button>
        <h1 className="text-3xl font-bold text-white mb-2">
          Замовлення: {order.order_id}
        </h1>
        <p className="text-indigo-100">{order.client_name}</p>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 pb-24">
        {/* Items List */}
        <div className="space-y-3">
          {order.items?.map((item, index) => (
            <div
              key={index}
              className="bg-white rounded-xl p-4 border border-gray-200"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-gray-900 flex-1">
                  {item.name}
                </h3>
                <span className="text-lg font-bold text-indigo-600 ml-3">
                  ₴{item.price_per_item}
                </span>
              </div>
              <p className="text-sm text-gray-500">
                ₴{item.price_per_item} за шт
              </p>
            </div>
          ))}
        </div>

        <div className="bg-indigo-50 rounded-2xl p-4 border-2 border-indigo-200">
          <div className="flex items-center justify-between mb-3 pb-3 border-b border-indigo-200">
            <span className="text-gray-700">Кількість товарів:</span>
            <span className="font-semibold text-gray-900">
              {getTotalItems()}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-gray-900">Всього:</span>
            <span className="text-2xl font-bold text-indigo-600">
              ₴{getOrderTotal()}
            </span>
          </div>
        </div>

        <div>
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">
            Клієнт і доставка
          </h2>

          <div className="bg-white rounded-2xl p-5 border border-gray-200 space-y-4">
            <div>
              <p className="text-xs text-gray-500 mb-1">Клієнт</p>
              <p className="font-semibold text-gray-900 text-lg">
                {order.client_name}
              </p>
              <p className="text-sm text-gray-400">
                {order.client_name} (Custom ID{" "}
                {order.custom_id ? order.custom_id : "N/A"})
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center shrink-0">
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
              </div>
              <span className="text-gray-700">
                {order.delivery_phone || ""}
              </span>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-pink-100 flex items-center justify-center shrink-0 mt-0.5">
                <svg
                  className="w-4 h-4 text-pink-600"
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
              </div>
              <span className="text-gray-700 flex-1 leading-relaxed">
                {order.address ||
                  `вул. ${order.delivery_address.street}, ${order.delivery_address.house}, ${order.delivery_address.apartment}, ${order.delivery_address.floor}, ${order.delivery_address.intercom}`}
              </span>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">
            Час доставки
          </h2>

          <div className="bg-white rounded-2xl p-5 border border-gray-200 space-y-4">
            <div>
              <p className="text-xs text-gray-500 mb-1">Дата</p>
              <p className="font-semibold text-gray-900">{order.date}</p>
            </div>

            <div>
              <p className="text-xs text-gray-500 mb-1">Час</p>
              <p className="font-semibold text-gray-900">
                {timeMap[order.time_preference]}
              </p>
            </div>

            {order.note && (
              <div>
                <p className="text-xs text-gray-500 mb-1">
                  Примітка для кур'єра
                </p>
                <p className="text-gray-700">{order.note}</p>
              </div>
            )}
          </div>
        </div>

        <ModalButtons
          firstButtonText={"Редагувати"}
          handleEditClick={handleEditClick}
          secondButtonText="Видалити"
          onDelete={onDelete}
        />
      </div>
    </div>
  );
};
