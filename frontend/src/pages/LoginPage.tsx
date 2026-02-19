import { useEffect, useRef, useCallback, useState } from "react";
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

    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.setAttribute("data-telegram-login", TELEGRAM_BOT_NAME);
    script.setAttribute("data-size", "large");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");
    script.setAttribute("data-request-access", "write");

    if (widgetContainerRef.current) {
      widgetContainerRef.current.appendChild(script);
    }

    return () => {
      delete window.onTelegramAuth;
      if (widgetContainerRef.current && script.parentNode) {
        widgetContainerRef.current.removeChild(script);
      }
    };
  }, [handleTelegramAuth]);

  if (authStatus === "loading") return null;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 rounded-2xl bg-indigo-600 flex items-center justify-center mx-auto mb-5 shadow-lg">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Water Delivery</h1>
          <p className="text-gray-400 mt-2">Увійдіть, щоб продовжити</p>
        </div>

        {/* Login card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <p className="text-sm font-medium text-gray-500 text-center mb-5">Оберіть спосіб входу</p>

          {/* Telegram auth option */}
          <div className="space-y-3">
            <div className="relative rounded-xl border border-gray-200 bg-gray-50 p-4 transition-colors hover:border-indigo-200 hover:bg-indigo-50/30">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-full bg-sky-100 flex items-center justify-center shrink-0">
                  <svg className="w-5 h-5 text-sky-500" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-800">Telegram</p>
                  <p className="text-xs text-gray-400">Швидкий вхід через акаунт</p>
                </div>
              </div>

              {loggingIn ? (
                <div className="flex items-center justify-center gap-2 text-gray-500 py-3">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
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
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  <span className="text-sm">Вхід...</span>
                </div>
              ) : (
                <div ref={widgetContainerRef} className="flex justify-center" />
              )}
            </div>
          </div>

          {/* Create shop link */}
          <button
            type="button"
            onClick={() => navigate("/create-shop")}
            className="w-full mt-4 py-3 text-sm font-medium text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-xl transition-colors"
          >
            Створити новий магазин
          </button>

          {/* Error */}
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
