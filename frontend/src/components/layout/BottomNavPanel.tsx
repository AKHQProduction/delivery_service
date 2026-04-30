import { useUserShopStore } from "../../context/useUserShopStore";
import { useNavigate, useLocation } from "react-router-dom";
import { getBottomNavRoutesForRole } from "../../config/roles.config";

export const BottomNavPanel = () => {
  const user = useUserShopStore((s) => s.user);
  const navigate = useNavigate();
  const location = useLocation();

  if (!user) return null;
  const userRoutes = getBottomNavRoutesForRole(user.role);

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 md:hidden">
      <div className="border-t border-slate-200 bg-white/95 px-2 pb-[calc(env(safe-area-inset-bottom)+0.5rem)] pt-2 shadow-[0_-8px_24px_rgba(15,23,42,0.08)] backdrop-blur">
        <nav aria-label="Основна навігація">
          <div className="mx-auto grid max-w-md grid-cols-4 gap-1">
            {userRoutes?.map((route) => {
              const isActive =
                location.pathname === route.path ||
                (route.path !== "/" && location.pathname.startsWith(route.path));

              return (
                <button
                  key={route.path}
                  type="button"
                  onClick={() => navigate(route.path)}
                  className={`flex min-h-14 flex-col items-center justify-center gap-1 rounded-md px-1 py-1.5 text-xs leading-4 transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-700"
                      : "text-slate-500 hover:bg-slate-100 hover:text-slate-950"
                  }`}
                >
                  <img
                    src={route.icon}
                    alt={route.label}
                    className={`h-5 w-5 object-contain ${isActive ? "opacity-100" : "opacity-65"}`}
                  />
                  <span className={isActive ? "font-semibold" : "font-medium"}>{route.label}</span>
                </button>
              );
            })}
          </div>
        </nav>
      </div>
    </div>
  );
};
