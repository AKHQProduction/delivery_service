import React from "react";
import { roleMap } from "../../utils/dataMap";
import { type Employee } from "../../types/entities/Employee";

interface EmployeeCardProps {
  employee: Employee;
  onClick: (employee: Employee) => void;
}

export const EmployeeCard: React.FC<EmployeeCardProps> = ({ employee, onClick }) => {
  return (
    <div
      onClick={() => onClick(employee)}
      className="
    bg-white rounded-2xl p-5 shadow-sm cursor-pointer
    hover:shadow-2xl hover:-translate-y-2 transition-all duration-300
    border border-gray-100 flex items-center gap-4
  "
    >
      <div className="w-12 h-12 shrink-0 rounded-full bg-linear-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold text-lg">
        {employee.full_name[0]}
      </div>

      <div>
        <h3 className="text-lg font-semibold leading-tight">{employee.full_name}</h3>

        <p className="text-sm text-gray-500">{roleMap[employee.role]}</p>
      </div>
    </div>
  );
};
