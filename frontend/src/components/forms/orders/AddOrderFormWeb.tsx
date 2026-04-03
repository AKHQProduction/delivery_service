import React, { useState } from "react";
import { useOrderForm } from "../../../hooks/orders/useOrdersForm";
import { useOrders } from "../../../hooks/orders/useOrders";
import { SearchBar } from "../../ui/SearchBar";
import { DateInput } from "../../shared/DateInput";
import { FormSelect } from "../../shared/FormSelect";
import { AddClientForm } from "../client/AddClientForm";
import { type Client } from "../../../types/entities/Client";

interface AddOrderFormWebProps {
  onClose: () => void;
  onSave?: (order?: unknown) => void;
}

export const AddOrderFormWeb: React.FC<AddOrderFormWebProps> = ({ onClose, onSave }) => {
  const { createNewOrder } = useOrders();
  const [showAddClient, setShowAddClient] = useState(false);
  const [isChangingClient, setIsChangingClient] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    formData,
    searchClient,
    searchProduct,
    clients,
    products,
    timeSlots,
    paymentMethods,
    loadMoreClients,
    clientsLoadingMore,
    clientsHasMore,
    loadMoreProducts,
    productsLoadingMore,
    productsHasMore,
    setSearchClient,
    setSearchProduct,
    handleClientSelect,
    handleProductToggle,
    handleQuantityChange,
    handlePhoneChange,
    handleAddressChange,
    handleDateChange,
    handleTimeSlotChange,
    handlePaymentMethodChange,
    handleNoteChange,
    getPhoneString,
    getAddressId,
    addAndSelectNewClient,
  } = useOrderForm();

  const isFormValid =
    formData.client !== null &&
    formData.products.length > 0 &&
    formData.deliveryPhone !== null &&
    formData.deliveryAddress !== null &&
    formData.deliveryDate !== "" &&
    formData.timeSlotId !== "" &&
    formData.paymentMethod !== "";

  const totalAmount = formData.products.reduce(
    (sum, p) => sum + p.product.price * p.quantity,
    0,
  );

  const totalItems = formData.products.reduce((sum, p) => sum + p.quantity, 0);

  const handleSubmit = async () => {
    if (isSubmitting || !isFormValid) return;

    setIsSubmitting(true);
    try {
      const newOrder = await createNewOrder({
        client_id: formData.client?.client_id,
        products: formData.products.map((p) => ({
          product_id: p.product.product_id,
          quantity: p.quantity,
        })),
        phone_id: formData.deliveryPhone?.id,
        address_id: formData.deliveryAddress?.id,
        delivery_date: formData.deliveryDate,
        time_slot_id: formData.timeSlotId,
        payment_method: formData.paymentMethod,
        comment: formData.note,
      });
      if (onSave) {
        onSave(newOrder);
      } else {
        onClose();
      }
    } catch (error) {
      console.error("Error creating order:", error);
      alert("Помилка при створенні замовлення");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClientCreated = (newClient?: Client) => {
    setShowAddClient(false);
    if (newClient) {
      addAndSelectNewClient(newClient);
    }
  };

  if (showAddClient) {
    return (
      <AddClientForm onClose={() => setShowAddClient(false)} onSuccess={handleClientCreated} />
    );
  }

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Top-left: Client */}
        <div className="space-y-5">
          <section className="bg-gray-50 rounded-2xl p-4 border border-gray-200">
            <div className="flex items-center gap-2.5 mb-3">
              <span className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold shrink-0">
                1
              </span>
              <h3 className="text-sm font-bold text-gray-900">Клієнт</h3>
              {formData.client && !isChangingClient && (
                <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              )}
            </div>

            {formData.client && !isChangingClient ? (
              <div className="p-3 rounded-xl border-2 border-indigo-600 bg-white flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">
                    {(formData.client.full_name || "")
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .toUpperCase()
                      .slice(0, 2)}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 text-sm">
                      {formData.client.full_name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formData.client.phones?.[0]?.number || ""}
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setIsChangingClient(true)}
                  className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  Змінити
                </button>
              </div>
            ) : (
              <>
                <SearchBar
                  searchTerm={searchClient}
                  setSearchTerm={setSearchClient}
                  placeholder="Пошук за ім'ям або телефоном..."
                />
                <div className="mt-2 space-y-1.5 max-h-48 overflow-y-auto">
                  {clients.length === 0 ? (
                    <p className="text-sm text-gray-400 text-center py-4">Клієнтів не знайдено</p>
                  ) : (
                    clients.map((client) => (
                      <div
                        key={client.client_id}
                        onClick={() => {
                          handleClientSelect(client);
                          setIsChangingClient(false);
                        }}
                        className="p-3 rounded-xl border border-gray-200 hover:border-indigo-300 bg-white cursor-pointer transition-colors flex items-center gap-3"
                      >
                        <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-xs">
                          {(client.full_name || "")
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .toUpperCase()
                            .slice(0, 2)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900 text-sm truncate">
                            {client.full_name || "Unknown"}
                          </div>
                          <div className="text-xs text-gray-500">
                            {client.phones?.[0]?.number || "—"}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  {clientsHasMore && (
                    <button
                      type="button"
                      onClick={loadMoreClients}
                      disabled={clientsLoadingMore}
                      className="w-full py-2 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                      {clientsLoadingMore ? "Завантаження..." : "Показати більше"}
                    </button>
                  )}
                </div>
                <button
                  onClick={() => setShowAddClient(true)}
                  type="button"
                  className="mt-2 w-full py-2.5 border-2 border-dashed border-gray-300 rounded-xl text-gray-600 hover:border-indigo-400 hover:text-indigo-600 transition-all font-medium text-sm flex items-center justify-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Додати нового клієнта
                </button>
              </>
            )}
          </section>

          {formData.client && (
            <section className="bg-gray-50 rounded-2xl p-4 border border-gray-200">
              <div className="flex items-center gap-2.5 mb-3">
                <h3 className="text-sm font-bold text-gray-900">Контактна інформація</h3>
                {formData.deliveryPhone && formData.deliveryAddress && (
                  <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                )}
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Телефон <span className="text-red-500">*</span>
                  </label>
                  {formData.client.phones && formData.client.phones.length > 1 ? (
                    <select
                      title="Phone select"
                      value={getPhoneString()}
                      onChange={(e) => handlePhoneChange(e.target.value)}
                      className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-white"
                    >
                      <option value="">Оберіть телефон...</option>
                      {formData.client.phones.map((phone, idx) => (
                        <option key={idx} value={phone.number}>
                          {phone.number}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="px-3 py-2.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium">
                      {formData.client.phones?.[0]?.number || "—"}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Адреса доставки <span className="text-red-500">*</span>
                  </label>
                  {formData.client.addresses && formData.client.addresses.length > 1 ? (
                    <select
                      title="Select address"
                      value={getAddressId()}
                      onChange={(e) => handleAddressChange(e.target.value)}
                      className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-white"
                    >
                      <option value="">Оберіть адресу...</option>
                      {formData.client.addresses.map((addr) => (
                        <option key={addr.id} value={addr.id}>
                          {addr.street} {addr.house}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="px-3 py-2.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium">
                      {formData.client.addresses?.[0]?.street} {formData.client.addresses?.[0]?.house}
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}
        </div>

        {/* Top-right: Products */}
        <section className="bg-gray-50 rounded-2xl p-4 border border-gray-200">
          <div className="flex items-center gap-2.5 mb-3">
            <span className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold shrink-0">
              2
            </span>
            <h3 className="text-sm font-bold text-gray-900">Товари</h3>
            {formData.products.length > 0 && (
              <>
                <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-xs text-gray-500 font-medium">
                  {formData.products.length} / {totalItems} шт.
                </span>
              </>
            )}
          </div>

          <SearchBar
            searchTerm={searchProduct}
            setSearchTerm={setSearchProduct}
            placeholder="Пошук товару..."
          />

          <div className="mt-2 space-y-1.5 max-h-48 overflow-y-auto">
            {products.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">Товарів не знайдено</p>
            ) : (
              products.map((product) => {
                const selected = formData.products.find(
                  (p) => p.product.product_id === product.product_id,
                );
                return (
                  <div
                    key={product.product_id}
                    className={`p-3 rounded-xl border transition-colors ${
                      selected
                        ? "border-indigo-600 bg-white"
                        : "border-gray-200 hover:border-indigo-300 bg-white"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 text-sm truncate">
                          {product.name}
                        </div>
                        <div className="text-xs font-semibold text-indigo-600">{product.price} ₴</div>
                      </div>

                      {selected ? (
                        <div className="flex items-center shrink-0">
                          <button
                            onClick={() => {
                              if (selected.quantity <= 1) {
                                handleProductToggle(product);
                              } else {
                                handleQuantityChange(product.product_id, selected.quantity - 1);
                              }
                            }}
                            type="button"
                            className="w-7 h-7 rounded-lg bg-gray-200 hover:bg-gray-300 flex items-center justify-center transition-colors font-bold text-sm"
                          >
                            −
                          </button>
                          <span className="w-10 text-center text-sm font-bold text-gray-900">
                            {selected.quantity}
                          </span>
                          <button
                            onClick={() =>
                              handleQuantityChange(product.product_id, selected.quantity + 1)
                            }
                            type="button"
                            className="w-7 h-7 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center transition-colors font-bold text-sm"
                          >
                            +
                          </button>
                          <button
                            title="remove"
                            onClick={() => handleProductToggle(product)}
                            type="button"
                            className="ml-1.5 w-7 h-7 rounded-lg bg-red-100 hover:bg-red-200 text-red-600 flex items-center justify-center transition-colors"
                          >
                            <svg
                              className="w-4 h-4"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                              />
                            </svg>
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleProductToggle(product)}
                          type="button"
                          className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors text-xs"
                        >
                          Додати
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
            {productsHasMore && (
              <button
                type="button"
                onClick={loadMoreProducts}
                disabled={productsLoadingMore}
                className="w-full py-2 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
              >
                {productsLoadingMore ? "Завантаження..." : "Показати більше"}
              </button>
            )}
          </div>

          {formData.products.length > 0 && (
            <div className="mt-3 p-3 bg-indigo-100 rounded-xl flex items-center justify-between">
              <div>
                <div className="text-xs text-gray-600">Всього до сплати</div>
                <div className="text-lg font-bold text-indigo-600">{totalAmount} ₴</div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-600">Кількість</div>
                <div className="text-base font-bold text-gray-900">{totalItems} шт.</div>
              </div>
            </div>
          )}
        </section>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Bottom-left: Delivery date & time */}
        <section className="bg-gray-50 rounded-2xl p-4 border border-gray-200">
          <div className="flex items-center gap-2.5 mb-3">
            <span className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold shrink-0">
              3
            </span>
            <h3 className="text-sm font-bold text-gray-900">Дата доставки</h3>
            {formData.deliveryDate && formData.timeSlotId && (
              <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
          </div>

          <div className="space-y-3">
            <DateInput
              label="Дата доставки"
              value={formData.deliveryDate}
              onChange={handleDateChange}
              required
              minDate={new Date().toISOString().split("T")[0]}
            />

            <FormSelect
              label="Час доставки"
              name="deliveryTime"
              value={formData.timeSlotId}
              required={true}
              onChange={(e) => handleTimeSlotChange(e.target.value)}
              options={timeSlots.map((slot) => ({
                value: slot.time_slot_id,
                label: slot.label
                  ? `${slot.label} (${slot.start_time} - ${slot.end_time})`
                  : `${slot.start_time} - ${slot.end_time}`,
              }))}
            />
          </div>
        </section>

        {/* Bottom-right: Payment & note */}
        <section className="bg-gray-50 rounded-2xl p-4 border border-gray-200">
          <div className="flex items-center gap-2.5 mb-3">
            <span className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold shrink-0">
              4
            </span>
            <h3 className="text-sm font-bold text-gray-900">Оплата</h3>
            {formData.paymentMethod && (
              <svg className="w-5 h-5 text-green-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
          </div>

          <div className="space-y-3">
            <FormSelect
              label="Спосіб оплати"
              name="paymentMethod"
              value={formData.paymentMethod}
              required={true}
              onChange={(e) => handlePaymentMethodChange(e.target.value)}
              options={paymentMethods.map((m) => ({
                value: m.name,
                label: m.name,
              }))}
            />

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Примітка</label>
              <textarea
                value={formData.note || ""}
                onChange={(e) => handleNoteChange(e.target.value)}
                placeholder="Примітка до замовлення..."
                rows={2}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none text-sm bg-white"
              />
            </div>
          </div>
        </section>
      </div>

      {/* Submit */}
      <div className="sticky bottom-0 bg-white pt-4 pb-4">
        <button
          onClick={handleSubmit}
          disabled={!isFormValid || isSubmitting}
          type="button"
          className={`w-full py-3.5 rounded-xl font-semibold text-white transition-colors ${
            isFormValid && !isSubmitting
              ? "bg-indigo-600 hover:bg-indigo-700"
              : "bg-gray-300 cursor-not-allowed"
          }`}
        >
          {isSubmitting ? "Створення..." : "Створити замовлення"}
        </button>
      </div>
    </div>
  );
};
