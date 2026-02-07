import React, { useState } from "react";
import { ItemElement } from "../../ui/ItemElement";
import { ModalButtons } from "../../ui/ModalButtons";
import leftArrowIcon from "../../../assets/icons/left_arrow.svg";
import { EditClientForm } from "../../forms/client/EditClientForm";
import { type Client } from "../../../types/entities/Client";
import { useDistrictsSettings } from "../../../hooks/settings/useDistrictsSettings";

interface ClientDetailModalProps {
  client: Client;
  onClose: () => void;
  onDelete: () => void;
  onSave: () => Promise<void> | void;
}

export const ClientDetailModal: React.FC<ClientDetailModalProps> = ({
  client,
  onClose,
  onDelete,
  onSave,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const { districts } = useDistrictsSettings();

  const getDistrictName = (districtId: string | null | undefined) => {
    if (!districtId) return null;
    const district = districts.find((d) => d.district_id === districtId);
    return district?.name || null;
  };

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleSaveEdit = async () => {
    await onSave();
    setIsEditing(false);
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
            Редагувати клієнта {client.full_name}
          </h1>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6">
          <EditClientForm client={client} onClose={handleCancelEdit} onSave={handleSaveEdit} />
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

        <h1 className="text-3xl font-bold text-white mb-2">{client.full_name}</h1>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 pb-24">
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
            Основна інформація
          </h2>
          <ItemElement
            descriptionText={"Ім'я клієнта"}
            elementText={client.full_name || "Не вказано"}
          />
          {client.phones?.map((phone, index) => (
            <ItemElement
              key={index}
              descriptionText={`Телефон ${index + 1}`}
              elementText={phone.number}
            />
          ))}

          {client.addresses?.map((address, index) => {
            const districtName = getDistrictName(address.district_id);
            return (
              <ItemElement
                key={index}
                descriptionText={`Адреса ${index + 1}${districtName ? ` (${districtName})` : ""}`}
                elementText={`${address.street} ${address.house}${
                  address.apartment ? `, кв. ${address.apartment}` : ""
                }`}
                comment={address.comment}
              />
            );
          })}
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
