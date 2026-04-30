import { useUserShopStore } from "../../context/useUserShopStore";
import { useNavigate, useLocation } from "react-router-dom";
import { getShellRoutesForRole } from "../../config/roles.config";
import { logout } from "../../services/api/authApi";
import { usePlatform } from "../../platforms/usePlatform";

export const SidebarNav = () => {
  const user = useUserShopStore((s) => s.user);
  const { type } = usePlatform();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      console.error("Logout failed");
    } finally {
      useUserShopStore.getState().logout();
      navigate("/login", { replace: true });
    }
  };

  if (!user) return null;

  const allRoutes = getShellRoutesForRole(user.role);

  return (
    <aside className="hidden md:fixed md:inset-y-0 md:left-0 md:z-40 md:flex md:w-[17rem] md:flex-col border-r border-slate-200 bg-white">
      <div
        className="border-b border-slate-200 px-5 py-5 cursor-pointer"
        onClick={() => navigate("/")}
      >
        <h1 className="text-[18px] font-semibold leading-7 text-slate-950">Water Delivery</h1>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {allRoutes.map((route) => {
          const isActive =
            location.pathname === route.path ||
            (route.path !== "/" && location.pathname.startsWith(route.path));

          return (
            <button
              key={route.path}
              type="button"
              onClick={() => navigate(route.path)}
              className={`w-full flex items-center gap-3 rounded-md px-3 py-2.5 text-left text-sm leading-5 transition-colors ${
                isActive
                  ? "bg-blue-50 text-blue-700"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
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
      </nav>

      <div className="border-t border-slate-200 px-4 py-4">
        <div className="flex items-center gap-3 rounded-md px-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-blue-100 text-sm font-semibold text-blue-700">
            {user.full_name?.[0] ?? "?"}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium leading-5 text-slate-950">
              {user.full_name}
            </p>
            <p className="text-xs leading-4 text-slate-500">{user.role}</p>
          </div>
          {type === "web" && (
            <button
              type="button"
              onClick={handleLogout}
              className="shrink-0 rounded-md p-1.5 text-slate-400 transition-colors hover:bg-red-50 hover:text-red-600"
              title="Вийти"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
            </button>
          )}
        </div>
      </div>
    </aside>
  );
};
