import { useEffect, useRef, useCallback, useState } from "react";
import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { useUserShopStore } from "../context/useUserShopStore";
import { loginViaTelegram, type TelegramLoginData } from "../services/api/authApi";
import { getUserShopData } from "../services/api/userApi";
import { getDefaultRouteForRole } from "../config/roles.config";

const TELEGRAM_BOT_NAME = import.meta.env.VITE_TELEGRAM_BOT_NAME;

export const LoginPage = () => {
  const navigate = useNavigate();
  const authStatus = useUserShopStore((s) => s.authStatus);
  const user = useUserShopStore((s) => s.user);
  const widgetContainerRef = useRef<HTMLDivElement>(null);
  const [loggingIn, setLoggingIn] = useState(false);
  const [error, setError] = useState("");

  const shop = useUserShopStore((s) => s.shop);

  useEffect(() => {
    if (authStatus === "authenticated" && user) {
      if (!shop) {
        navigate("/create-shop", { replace: true });
      } else {
        navigate(getDefaultRouteForRole(user.role), { replace: true });
      }
    }
  }, [authStatus, user, shop, navigate]);

  const handleTelegramAuth = useCallback(
    async (tgUser: TelegramLoginData) => {
      setLoggingIn(true);
      setError("");
      try {
        await loginViaTelegram(tgUser);
        const data = await getUserShopData();
        const store = useUserShopStore.getState();
        store.setUserAndShop(data.user, data.shop);
        store.setAuthStatus("authenticated");
        if (!data.shop) {
          navigate("/create-shop", { replace: true });
        } else {
          navigate(getDefaultRouteForRole(data.user.role), { replace: true });
        }
      } catch {
        setError("Не вдалося увійти. Спробуйте ще раз.");
        setLoggingIn(false);
      }
    },
    [navigate],
  );

  useEffect(() => {
    window.onTelegramAuth = (user: TelegramLoginData) => {
      handleTelegramAuth(user);
    };

    const container = widgetContainerRef.current;
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.setAttribute("data-telegram-login", TELEGRAM_BOT_NAME);
    script.setAttribute("data-size", "large");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");
    script.setAttribute("data-request-access", "write");

    if (container) {
      container.appendChild(script);
    }

    return () => {
      delete window.onTelegramAuth;
      if (container && script.parentNode === container) {
        container.removeChild(script);
      }
    };
  }, [handleTelegramAuth]);

  if (authStatus === "loading") return null;

  return (
    <div className="min-h-screen bg-white px-4 py-5 text-slate-950 sm:px-6 md:bg-slate-50">
      <div className="mx-auto flex min-h-[calc(100vh-2.5rem)] w-full max-w-[1400px] flex-col rounded-none border-slate-200 bg-white md:rounded-lg md:border md:bg-slate-50">
        <header className="flex items-center px-2 py-2 sm:px-5 sm:py-4">
          <BrandMark />
        </header>

        <main className="flex flex-1 items-center justify-center pb-8 pt-8 sm:pt-4 md:pb-14">
          <div className="w-full max-w-[36rem]">
            <section className="rounded-none border-0 bg-transparent p-0 shadow-none sm:rounded-lg sm:border sm:border-slate-200 sm:bg-white sm:p-8 sm:shadow-sm">
              <div className="text-center">
                <WaterDropIcon className="mx-auto h-16 w-16 text-blue-600 sm:h-20 sm:w-20" />
                <h1 className="mt-4 text-2xl font-semibold leading-8 text-slate-950">Увійдіть</h1>
                <p className="mx-auto mt-2 max-w-[18rem] text-sm leading-5 text-slate-500">
                  Вхід до системи управління доставкою води
                </p>
              </div>

              {error && (
                <div className="mt-5 flex gap-3 rounded-md border border-red-200 bg-red-50 px-4 py-3">
                  <AlertIcon className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-600" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-slate-950">
                      Не вдалося увійти через Telegram
                    </p>
                    <p className="mt-1 text-sm leading-5 text-slate-500">
                      Перевірте, чи встановлено Telegram та спробуйте ще раз.
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

              <div className={error ? "mt-4 grid gap-3 sm:grid-cols-2" : "mt-7"}>
                <div className="rounded-md border border-slate-200 bg-white p-3 transition-colors hover:border-blue-300">
                  <div className="mb-3 flex items-center gap-3">
                    <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-sky-100 text-sky-600">
                      <TelegramIcon className="h-5 w-5" />
                    </span>
                    <span className="flex-1 text-left text-sm font-semibold text-slate-950">
                      Telegram
                    </span>
                    <ChevronRightIcon className="h-5 w-5 text-slate-400" />
                  </div>

                  {loggingIn ? (
                    <div className="flex h-10 items-center justify-center gap-2 text-sm font-medium text-slate-500">
                      <SpinnerIcon className="h-5 w-5 animate-spin" />
                      Вхід...
                    </div>
                  ) : (
                    <div
                      ref={widgetContainerRef}
                      className="telegram-widget-host flex min-h-10 items-center justify-center"
                      aria-label="Telegram login widget"
                    />
                  )}
                </div>

                {error && (
                  <button
                    type="button"
                    onClick={() => setError("")}
                    className="inline-flex h-14 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    <RefreshIcon className="h-4 w-4" />
                    Спробувати ще раз
                  </button>
                )}
              </div>

              <DividerLabel>Єдиний спосіб входу</DividerLabel>

              <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
                <div className="flex gap-3">
                  <ShieldIcon className="mt-0.5 h-6 w-6 flex-shrink-0 text-blue-600" />
                  <div>
                    <p className="text-sm font-semibold text-slate-950">Безпечно та зручно</p>
                    <p className="mt-1 text-sm leading-5 text-slate-500">
                      Ми використовуємо Telegram для безпечного входу. Ваші дані надійно захищені.
                    </p>
                  </div>
                </div>
              </div>
            </section>

            <p className="mx-auto mt-4 max-w-[28rem] text-center text-xs leading-5 text-slate-500">
              Використовуючи вхід, ви погоджуєтесь з обробкою даних відповідно до{" "}
              <a href="#" className="font-medium text-blue-600 hover:text-blue-700">
                Політики конфіденційності.
              </a>
            </p>
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

const DividerLabel = ({ children }: { children: ReactNode }) => (
  <div className="my-5 flex items-center gap-3">
    <span className="h-px flex-1 bg-slate-200" />
    <span className="text-xs font-medium text-slate-500">{children}</span>
    <span className="h-px flex-1 bg-slate-200" />
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

const TelegramIcon = ({ className = "" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0h-.056zm4.962 7.224c.1-.002.321.023.465.14.085.068.145.18.171.325.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
  </svg>
);

const ShieldIcon = ({ className = "" }: { className?: string }) => (
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
      d="M9 12.75 11.25 15 15 9.75M12 3.75l7.5 3.25v5.2c0 4.7-3.1 7.8-7.5 9.3-4.4-1.5-7.5-4.6-7.5-9.3V7L12 3.75Z"
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

const ChevronRightIcon = ({ className = "" }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m9 18 6-6-6-6" />
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

const RefreshIcon = ({ className = "" }: { className?: string }) => (
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
      d="M16.5 6.75H21v-4.5M20 7.8A8.25 8.25 0 1 0 21 12"
    />
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
