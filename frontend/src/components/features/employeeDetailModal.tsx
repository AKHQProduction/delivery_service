import React, { useState } from "react";
import { EditEmployeeForm } from "../forms/editEmployeeForm";
import { ItemElement } from "../ui/itemElement";
import { ModalButtons } from "../ui/modalButtons";
import leftArrowIcon from "../../assets/icons/left_arrow.svg";
import { roleMap } from "../../utils/dataMap";

interface Employee {
  user_id: string;
  full_name: string;
  role: string;
}

interface EmployeeDetailModalProps {
  employee: Employee;
  onClose: () => void;
  onDelete: () => void;
  onSave: (updatedProduct: Employee) => void;
}

export const EmployeeDetailModal: React.FC<EmployeeDetailModalProps> = ({
  employee,
  onClose,
  onDelete,
  onSave,
}) => {
  const [isEditing, setIsEditing] = useState(false);

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleSaveEdit = (updatedEmployee: Employee) => {
    onSave(updatedEmployee);
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
            Редагувати працівника {employee.full_name}
          </h1>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6">
          <EditEmployeeForm
            employee={employee}
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

        <h1 className="text-3xl font-bold text-white mb-2">{employee.full_name}</h1>
        <p className="text-indigo-100">
          {roleMap[employee.role]}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 pb-24">
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
            Основна інформація
          </h2>
          <ItemElement
            descriptionText={"Ім'я працівника"}
            elementText={employee.full_name}
          />
          <ItemElement
            descriptionText={"Роль працівника"}
            elementText={roleMap[employee.role]}
          />
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
