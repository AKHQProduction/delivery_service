import React from "react";
import { roleMap } from "../../utils/dataMap";
import { type Employee } from "../../types/entities/Employee";

interface EmployeeCardProps {
  employee: Employee;
  onClick: (employee: Employee) => void;
}

const roleClasses: Record<string, string> = {
  OWNER: "bg-blue-50 text-blue-700",
  MANAGER: "bg-emerald-50 text-emerald-700",
  COURIER: "bg-amber-50 text-amber-700",
};

export const EmployeeCard: React.FC<EmployeeCardProps> = ({ employee, onClick }) => {
  const initials = employee.full_name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  return (
    <button
      type="button"
      onClick={() => onClick(employee)}
      className="group w-full rounded-lg border border-slate-200 bg-white p-4 text-left transition-colors hover:border-blue-300 hover:bg-blue-50/30"
    >
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700">
          {initials || "?"}
        </div>

        <div className="min-w-0 flex-1">
          <h3 className="truncate text-base font-semibold text-slate-950">{employee.full_name}</h3>
          <div className="mt-2 flex items-center gap-2">
            <span
              className={`rounded px-2 py-1 text-xs font-medium ${roleClasses[employee.role] ?? "bg-slate-100 text-slate-600"}`}
            >
              {roleMap[employee.role] ?? employee.role}
            </span>
          </div>
        </div>

        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="m9 5 7 7-7 7" />
          </svg>
        </span>
      </div>
    </button>
  );
};
