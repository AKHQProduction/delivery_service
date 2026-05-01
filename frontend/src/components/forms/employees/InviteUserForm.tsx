import React, { useState } from "react";
import { FormWrapper } from "../../shared/FormWrapper";
import { FormInput } from "../../shared/FormInput";
import { useEmployees } from "../../../hooks/useEmployees";

export const InviteUserForm: React.FC<{
  onClose: () => void;
  onInviteCreated: (link: string) => void;
}> = ({ onClose, onInviteCreated }) => {
  const [formData, setFormData] = useState({
    name: "",
    role: "",
  });

  const { createInviteLink } = useEmployees();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const link = await createInviteLink(formData.role, formData.name);

    if (link) {
      onInviteCreated(link);
    }
  };

  const roleOptions = [
    { value: "MANAGER", label: "Менеджер" },
    { value: "COURIER", label: "Кур'єр" },
  ];

  return (
    <FormWrapper onSubmit={handleSubmit} onClose={onClose} submitLabel="Запросити">
      <FormInput
        label="Ім'я співробітника"
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Введіть ім'я..."
        required
      />

      <div>
        <label htmlFor="role" className="mb-2 block text-sm font-medium text-slate-700">
          Посада
        </label>
        <div className="relative">
          <select
            id="role"
            name="role"
            value={formData.role}
            onChange={(e) => setFormData((prev) => ({ ...prev, role: e.target.value }))}
            required
            className="h-12 w-full appearance-none rounded-md border border-slate-300 bg-white px-4 pr-10 text-slate-950 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            <option value="">Оберіть...</option>
            {roleOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <svg
            className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m19 9-7 7-7-7" />
          </svg>
        </div>
      </div>
    </FormWrapper>
  );
};
