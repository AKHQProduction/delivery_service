import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FormWrapper } from "../components/shared/FormWrapper";
import { FormInput } from "../components/shared/FormInput";
import { createNewShop, getUserShopData } from "../services/api/userApi";
import { useUserShopStore } from "../context/useUserShopStore";
import { getDefaultRouteForRole } from "../config/roles.config";

export const CreateShopPage = () => {
  const navigate = useNavigate();
  const user = useUserShopStore((s) => s.user);

  const [formData, setFormData] = useState({
    name: "",
    owner_full_name: user?.full_name ?? "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await createNewShop(formData.name, formData.owner_full_name);
      const data = await getUserShopData();
      const store = useUserShopStore.getState();
      store.setUserAndShop(data.user, data.shop);
      store.setAuthStatus("authenticated");
      navigate(getDefaultRouteForRole(data.user.role), { replace: true });
    } catch {
      setError("Не вдалося створити магазин. Спробуйте ще раз.");
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Новий магазин</h1>
          <p className="text-gray-400 mt-2">Заповніть дані для створення</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <FormWrapper
            onSubmit={handleSubmit}
            onClose={() => navigate("/login")}
            submitLabel={submitting ? "Створення..." : "Створити"}
          >
            <FormInput
              label="Назва магазину"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Введіть назву"
              required
            />
            <FormInput
              label="Ім'я власника"
              name="owner_full_name"
              value={formData.owner_full_name}
              onChange={handleChange}
              placeholder="Введіть ім'я власника"
              required
            />
          </FormWrapper>

          {error && (
            <div className="flex items-center gap-2 mt-4 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl">
              <svg
                className="w-4 h-4 text-red-500 shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
