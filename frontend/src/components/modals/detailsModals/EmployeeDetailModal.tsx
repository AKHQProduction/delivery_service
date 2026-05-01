import React, { useState } from "react";
import { EditEmployeeForm } from "../../forms/employees/EditEmployeeForm";
import { roleMap } from "../../../utils/dataMap";
import { type Employee } from "../../../types/entities/Employee";

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
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleSaveEdit = (updatedEmployee: Employee) => {
    if (!updatedEmployee?.user_id) {
      console.error("Cannot save: invalid employee data");
      return;
    }
    onSave(updatedEmployee);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="flex h-full flex-col">
        <div className="flex shrink-0 items-start justify-between border-b border-slate-200 px-6 py-5">
          <div>
            <p className="text-sm font-medium text-slate-500">Працівник</p>
            <h1 className="mt-1 text-2xl font-semibold text-slate-950">Редагувати працівника</h1>
          </div>
          <button
            onClick={handleCancelEdit}
            type="button"
            className="flex h-9 w-9 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-950"
            aria-label="Повернутися до картки працівника"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="m15 18-6-6 6-6"
              />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 pt-6">
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
    <div className="flex h-full flex-col">
      <div className="flex shrink-0 items-start justify-between border-b border-slate-200 px-6 py-5">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-500">Працівник</p>
          <h1 className="mt-1 truncate text-2xl font-semibold text-slate-950">
            {employee.full_name}
          </h1>
          <p className="mt-2 inline-flex rounded bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
            {roleMap[employee.role] ?? employee.role}
          </p>
        </div>
        <button
          onClick={onClose}
          type="button"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-950"
          aria-label="Закрити картку працівника"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18 18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <h2 className="text-sm font-semibold text-slate-950">Основна інформація</h2>
        <div className="mt-4 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
          <InfoRow label="Ім'я" value={employee.full_name} />
          <InfoRow label="Роль" value={roleMap[employee.role] ?? employee.role} />
        </div>

        {isConfirmingDelete && (
          <div className="mt-5 rounded-lg border border-red-200 bg-red-50 p-4">
            <p className="text-sm font-semibold text-red-700">Видалити працівника?</p>
            <p className="mt-1 text-sm text-red-700">Дію не можна буде скасувати.</p>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setIsConfirmingDelete(false)}
                className="h-10 rounded-md bg-white text-sm font-medium text-slate-700 hover:bg-red-100"
              >
                Скасувати
              </button>
              <button
                type="button"
                onClick={onDelete}
                className="h-10 rounded-md bg-red-600 text-sm font-medium text-white hover:bg-red-700"
              >
                Видалити
              </button>
            </div>
          </div>
        )}
      </div>

      {!isConfirmingDelete && (
        <div className="grid shrink-0 grid-cols-2 gap-3 border-t border-slate-200 px-6 py-4">
          <button
            type="button"
            onClick={() => setIsEditing(true)}
            className="h-12 rounded-md bg-blue-600 font-medium text-white hover:bg-blue-700"
          >
            Редагувати
          </button>
          <button
            type="button"
            onClick={() => setIsConfirmingDelete(true)}
            className="h-12 rounded-md bg-red-50 font-medium text-red-600 hover:bg-red-100"
          >
            Видалити
          </button>
        </div>
      )}
    </div>
  );
};

const InfoRow = ({ label, value }: { label: string; value: string }) => (
  <div className="flex items-center justify-between gap-4 px-4 py-3">
    <span className="text-sm text-slate-500">{label}</span>
    <span className="text-right text-sm font-medium text-slate-950">{value}</span>
  </div>
);
