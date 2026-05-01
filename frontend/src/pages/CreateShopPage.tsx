import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createNewShop, getUserShopData } from "../services/api/userApi";
import { logout } from "../services/api/authApi";
import { useUserShopStore } from "../context/useUserShopStore";
import { getDefaultRouteForRole } from "../config/roles.config";

export const CreateShopPage = () => {
  const navigate = useNavigate();
  const user = useUserShopStore((s) => s.user);

  const [formData, setFormData] = useState({
    name: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    if (error) setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setSubmitting(true);
    setError("");

    if (!formData.name.trim()) {
      setSubmitting(false);
      return;
    }

    try {
      await createNewShop(formData.name.trim());
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

  const handleCancel = async () => {
    try {
      await logout();
    } catch {
      // Ignore logout transport errors; local state still needs to be cleared.
    }
    useUserShopStore.getState().logout();
    navigate("/login", { replace: true });
  };

  const nameError = submitted && !formData.name.trim() ? "Поле є обов'язковим" : "";
  const hasFormError = Boolean(nameError);

  return (
    <div className="min-h-screen bg-white px-4 py-5 text-slate-950 sm:px-6 md:bg-slate-50">
      <div className="mx-auto flex min-h-[calc(100vh-2.5rem)] w-full max-w-[1400px] flex-col rounded-none border-slate-200 bg-white md:rounded-lg md:border md:bg-slate-50">
        <header className="flex items-center px-2 py-2 sm:px-5 sm:py-4">
          <BrandMark />
        </header>

        <main className="flex flex-1 items-start justify-center pb-8 pt-8 sm:items-center sm:pt-4 md:pb-14">
          <div className="w-full max-w-[36rem]">
            <section className="rounded-none border-0 bg-transparent p-0 shadow-none sm:rounded-lg sm:border sm:border-slate-200 sm:bg-white sm:p-8 sm:shadow-sm">
              <div className="text-center">
                <ShopIcon className="mx-auto h-16 w-16 text-blue-600 sm:h-20 sm:w-20" />
                <h1 className="mt-4 text-2xl font-semibold leading-8 text-slate-950">
                  Створити магазин
                </h1>
                <p className="mx-auto mt-2 max-w-[18rem] text-sm leading-5 text-slate-500">
                  Заповніть інформацію для створення магазину
                </p>
              </div>

              {(error || hasFormError) && (
                <div className="mt-6 flex gap-3 rounded-md border border-red-200 bg-red-50 px-4 py-3">
                  <AlertIcon className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-600" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-slate-950">
                      Будь ласка, виправте помилки у формі
                    </p>
                    <p className="mt-1 text-sm leading-5 text-slate-500">
                      {error || "Є поле, яке потрібно виправити."}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setError("")}
                    className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-md text-slate-500 hover:bg-red-100 hover:text-slate-700"
                    aria-label="Закрити повідомлення"
                  >
                    <CloseIcon className="h-4 w-4" />
                  </button>
                </div>
              )}

              <form onSubmit={handleSubmit} className="mt-7 space-y-5" noValidate>
                <div>
                  <label
                    htmlFor="shop-name"
                    className="mb-2 block text-sm font-medium text-slate-700"
                  >
                    Назва магазину <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="shop-name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Введіть назву магазину"
                    aria-invalid={Boolean(nameError)}
                    aria-describedby={nameError ? "shop-name-error" : undefined}
                    className={`h-12 w-full rounded-md border bg-white px-4 text-sm text-slate-950 outline-none transition-colors placeholder:text-slate-400 focus:ring-2 ${
                      nameError
                        ? "border-red-400 focus:border-red-500 focus:ring-red-100"
                        : "border-slate-300 focus:border-blue-600 focus:ring-blue-100"
                    }`}
                  />
                  {nameError && (
                    <p id="shop-name-error" className="mt-1.5 text-sm text-red-600">
                      {nameError}
                    </p>
                  )}
                </div>

                <div className="grid gap-3 pt-2 sm:grid-cols-[auto_1fr] sm:justify-end">
                  <button
                    type="button"
                    onClick={handleCancel}
                    disabled={submitting}
                    className="h-12 rounded-md border border-slate-200 bg-white px-6 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Скасувати
                  </button>
                  <button
                    type="submit"
                    disabled={submitting || (submitted && !formData.name.trim())}
                    className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-blue-600 px-6 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-200"
                  >
                    {submitting && <SpinnerIcon className="h-5 w-5 animate-spin" />}
                    {submitting ? "Створення..." : "Створити магазин"}
                  </button>
                </div>
              </form>

              {user?.full_name && (
                <p className="mt-5 text-center text-xs leading-5 text-slate-500">
                  Магазин буде створено для користувача{" "}
                  <span className="font-medium text-slate-700">{user.full_name}</span>.
                </p>
              )}
            </section>
          </div>
        </main>
      </div>
    </div>
  );
};

const BrandMark = () => (
  <div className="flex items-center gap-2">
    <WaterDropIcon className="h-8 w-8 text-blue-600" />
    <span className="text-lg font-semibold text-slate-950 sm:text-xl">Water Delivery</span>
  </div>
);

const WaterDropIcon = ({ className = "" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 40 40" fill="none" aria-hidden="true">
    <path
      d="M20 4.5c2.2 5.1 9.5 12.1 9.5 21.1 0 6.1-4.2 10.4-9.5 10.4s-9.5-4.3-9.5-10.4C10.5 16.6 17.8 9.6 20 4.5Z"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinejoin="round"
    />
    <path
      d="M20 4.5c1.3 3 4.4 6.5 6.7 10.7"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
    />
    <path d="M17.4 7.5h5.2" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
  </svg>
);

const ShopIcon = ({ className = "" }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 48 48"
    aria-hidden="true"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={3}
      d="M10 20h28l-2.4-10.5A2 2 0 0 0 33.7 8H14.3a2 2 0 0 0-1.9 1.5L10 20Z"
    />
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={3}
      d="M10 20c0 3.3 2.7 6 6 6 2.2 0 4.1-1.2 5.2-3 1.1 1.8 3 3 5.2 3s4.1-1.2 5.2-3c1.1 1.8 3 3 5.2 3 3.3 0 6-2.7 6-6M14 26v12h20V26M21 38v-9h6v9"
    />
  </svg>
);

const AlertIcon = ({ className = "" }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 9v4m0 4h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"
    />
  </svg>
);

const CloseIcon = ({ className = "" }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18 18 6M6 6l12 12" />
  </svg>
);

const SpinnerIcon = ({ className = "" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
      fill="none"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 0 1 8-8V0C5.37 0 0 5.37 0 12h4zm2 5.29A7.96 7.96 0 0 1 4 12H0c0 3.04 1.13 5.82 3 7.94l3-2.65z"
    />
  </svg>
);
