import React from "react";
import type { ColumnMapping, ColumnPreview } from "../../../services/api/clientApi";
import { SYSTEM_FIELDS, REQUIRED_SYSTEM_FIELDS, getColumnLetter } from "./constants";

interface ColumnMappingStepProps {
  columns: ColumnPreview[];
  mapping: ColumnMapping;
  onMappingChange: (mapping: ColumnMapping) => void;
  firstRowIsHeader: boolean;
  onFirstRowIsHeaderChange: (value: boolean) => void;
  totalRows: number;
}

export const ColumnMappingStep: React.FC<ColumnMappingStepProps> = ({
  columns,
  mapping,
  onMappingChange,
  firstRowIsHeader,
  onFirstRowIsHeaderChange,
  totalRows,
}) => {
  const assignedFields = new Set(Object.values(mapping));

  const unmappedRequired = REQUIRED_SYSTEM_FIELDS.filter((f) => !assignedFields.has(f));

  const handleFieldChange = (colIndex: number, fieldValue: string) => {
    const next = { ...mapping };
    if (fieldValue === "") {
      delete next[colIndex];
    } else {
      next[colIndex] = fieldValue;
    }
    onMappingChange(next);
  };

  const getAvailableFields = (currentColIndex: number) => {
    const currentField = mapping[currentColIndex];
    return SYSTEM_FIELDS.filter(
      (f) => f.value === currentField || !assignedFields.has(f.value),
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={firstRowIsHeader}
            onChange={(e) => onFirstRowIsHeaderChange(e.target.checked)}
            className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-slate-700">Перший рядок — заголовки</span>
        </label>
        <span className="text-xs text-slate-400">~{totalRows} рядків</span>
      </div>

      {/* Desktop table */}
      <div className="hidden max-h-[50vh] overflow-y-auto rounded-md border border-slate-200 md:block">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-slate-50">
            <tr>
              <th className="w-16 px-3 py-2 text-left text-xs font-medium text-slate-500">Стовпець</th>
              {firstRowIsHeader && (
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500">Заголовок</th>
              )}
              <th className="px-3 py-2 text-left text-xs font-medium text-slate-500">Приклади</th>
              <th className="w-52 px-3 py-2 text-left text-xs font-medium text-slate-500">Поле системи</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {columns.map((col) => {
              const currentField = mapping[col.index] ?? "";
              const fieldDef = SYSTEM_FIELDS.find((f) => f.value === currentField);
              const isRequired = fieldDef?.required;

              return (
                <tr key={col.index} className="hover:bg-slate-50">
                  <td className="px-3 py-2 font-mono text-xs text-slate-500">
                    {getColumnLetter(col.index)}
                  </td>
                  {firstRowIsHeader && (
                    <td className="max-w-[200px] truncate px-3 py-2 font-medium text-slate-900">
                      {col.header || "—"}
                    </td>
                  )}
                  <td className="max-w-[250px] truncate px-3 py-2 text-xs text-slate-400">
                    {(firstRowIsHeader ? col.sample_values : [col.header, ...col.sample_values].filter(Boolean))
                      .slice(0, 3)
                      .join(", ") || "—"}
                  </td>
                  <td className="px-3 py-2">
                    <select
                      title="Поле системи"
                      value={currentField}
                      onChange={(e) => handleFieldChange(col.index, e.target.value)}
                      className={`w-full rounded-md border px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        isRequired
                          ? "border-blue-300 bg-blue-50"
                          : "border-slate-200 bg-white"
                      }`}
                    >
                      <option value="">— Пропустити</option>
                      {getAvailableFields(col.index).map((f) => (
                        <option key={f.value} value={f.value}>
                          {f.label}{f.required ? " *" : ""}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="max-h-[50vh] space-y-2 overflow-y-auto md:hidden">
        {columns.map((col) => {
          const currentField = mapping[col.index] ?? "";
          const fieldDef = SYSTEM_FIELDS.find((f) => f.value === currentField);
          const isRequired = fieldDef?.required;

          return (
            <div
              key={col.index}
              className={`rounded-md border p-3 ${
                isRequired ? "border-blue-200 bg-blue-50/50" : "border-slate-200 bg-slate-50"
              }`}
            >
              <div className="mb-1 flex items-center gap-2">
                <span className="font-mono text-xs text-slate-400">
                  {getColumnLetter(col.index)}
                </span>
                {firstRowIsHeader && col.header && (
                  <span className="truncate text-sm font-medium text-slate-900">
                    {col.header}
                  </span>
                )}
              </div>
              <p className="mb-2 truncate text-xs text-slate-400">
                {(firstRowIsHeader ? col.sample_values : [col.header, ...col.sample_values].filter(Boolean))
                  .slice(0, 3)
                  .join(", ") || "—"}
              </p>
              <select
                title="Поле системи"
                value={currentField}
                onChange={(e) => handleFieldChange(col.index, e.target.value)}
                className={`w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  isRequired
                    ? "border-blue-300 bg-white"
                    : "border-slate-200 bg-white"
                }`}
              >
                <option value="">— Пропустити</option>
                {getAvailableFields(col.index).map((f) => (
                  <option key={f.value} value={f.value}>
                    {f.label}{f.required ? " *" : ""}
                  </option>
                ))}
              </select>
            </div>
          );
        })}
      </div>

      {unmappedRequired.length > 0 && (
        <div className="rounded-md border border-red-100 bg-red-50 px-3 py-2">
          <p className="text-xs font-medium text-red-600">
            Не призначено:{" "}
            {unmappedRequired
              .map((f) => SYSTEM_FIELDS.find((sf) => sf.value === f)?.label ?? f)
              .join(", ")}
          </p>
        </div>
      )}
    </div>
  );
};
