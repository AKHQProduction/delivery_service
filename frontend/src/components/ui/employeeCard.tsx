import React from "react";
import { roleMap } from "../../utils/dataMap";

interface Employee {
  user_id: string;
  full_name: string;
  role: string;
}

interface EmployeeCardProps {
  employee: Employee;
  onClick: (employee: Employee) => void;
}

export const EmployeeCard: React.FC<EmployeeCardProps> = ({
  employee,
  onClick,
}) => {
  return (
    <div
  onClick={() => onClick(employee)}
  className="
    bg-white rounded-2xl p-5 shadow-sm cursor-pointer
    hover:shadow-lg hover:-translate-y-1 transition-all
    border border-gray-100 flex items-center gap-4
  "
>
  <div className="w-12 h-12 rounded-full bg-linear-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold text-lg">
    {employee.full_name[0]}
  </div>

  <div>
    <h3 className="text-lg font-semibold leading-tight">
      {employee.full_name}
    </h3>

    <p className="text-sm text-gray-500">
      {roleMap[employee.role]}
    </p>
  </div>
</div>

  );
};
