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
            className="w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
          />
          <span className="text-sm text-gray-700">Перший рядок — заголовки</span>
        </label>
        <span className="text-xs text-gray-400">~{totalRows} рядків</span>
      </div>

      {/* Desktop table */}
      <div className="hidden md:block max-h-[50vh] overflow-y-auto rounded-xl border border-gray-200">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 w-16">Стовпець</th>
              {firstRowIsHeader && (
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Заголовок</th>
              )}
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Приклади</th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 w-52">Поле системи</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {columns.map((col) => {
              const currentField = mapping[col.index] ?? "";
              const fieldDef = SYSTEM_FIELDS.find((f) => f.value === currentField);
              const isRequired = fieldDef?.required;

              return (
                <tr key={col.index} className="hover:bg-gray-50">
                  <td className="px-3 py-2 text-gray-500 font-mono text-xs">
                    {getColumnLetter(col.index)}
                  </td>
                  {firstRowIsHeader && (
                    <td className="px-3 py-2 text-gray-900 font-medium truncate max-w-[200px]">
                      {col.header || "—"}
                    </td>
                  )}
                  <td className="px-3 py-2 text-gray-400 text-xs truncate max-w-[250px]">
                    {(firstRowIsHeader ? col.sample_values : [col.header, ...col.sample_values].filter(Boolean))
                      .slice(0, 3)
                      .join(", ") || "—"}
                  </td>
                  <td className="px-3 py-2">
                    <select
                      title="Поле системи"
                      value={currentField}
                      onChange={(e) => handleFieldChange(col.index, e.target.value)}
                      className={`w-full px-2 py-1.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                        isRequired
                          ? "border-indigo-300 bg-indigo-50"
                          : "border-gray-200 bg-white"
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
      <div className="md:hidden max-h-[50vh] overflow-y-auto space-y-2">
        {columns.map((col) => {
          const currentField = mapping[col.index] ?? "";
          const fieldDef = SYSTEM_FIELDS.find((f) => f.value === currentField);
          const isRequired = fieldDef?.required;

          return (
            <div
              key={col.index}
              className={`p-3 rounded-xl border ${
                isRequired ? "border-indigo-200 bg-indigo-50/50" : "border-gray-200 bg-gray-50"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono text-gray-400">
                  {getColumnLetter(col.index)}
                </span>
                {firstRowIsHeader && col.header && (
                  <span className="text-sm font-medium text-gray-900 truncate">
                    {col.header}
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-400 mb-2 truncate">
                {(firstRowIsHeader ? col.sample_values : [col.header, ...col.sample_values].filter(Boolean))
                  .slice(0, 3)
                  .join(", ") || "—"}
              </p>
              <select
                title="Поле системи"
                value={currentField}
                onChange={(e) => handleFieldChange(col.index, e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                  isRequired
                    ? "border-indigo-300 bg-white"
                    : "border-gray-200 bg-white"
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
        <div className="px-3 py-2 bg-red-50 border border-red-100 rounded-xl">
          <p className="text-xs text-red-600 font-medium">
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
