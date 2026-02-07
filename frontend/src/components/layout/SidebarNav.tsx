import { useUserShopStore } from "../../context/useUserShopStore";
import { useNavigate, useLocation } from "react-router-dom";
import { getRoutesForRole } from "../../config/roles.config";

export const SidebarNav = () => {
  const user = useUserShopStore((s) => s.user);
  const navigate = useNavigate();
  const location = useLocation();

  if (!user) return null;

  const allRoutes = getRoutesForRole(user.role);

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 lg:left-0 bg-white border-r border-gray-200 z-40">
      {/* Logo / Brand */}
      <div className="px-6 py-6 border-b border-gray-100">
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">Water Delivery</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {allRoutes.map((route) => {
          const isActive = location.pathname === route.path;

          return (
            <button
              key={route.path}
              type="button"
              onClick={() => navigate(route.path)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-150 ${
                isActive
                  ? "bg-indigo-50 text-indigo-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              <img
                src={route.icon}
                alt={route.label}
                className={`w-5 h-5 object-contain ${isActive ? "opacity-100" : "opacity-60"}`}
              />
              <span className={`text-sm ${isActive ? "font-semibold" : "font-medium"}`}>
                {route.label}
              </span>
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-gray-100">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-sm">
            {user.full_name[0]}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{user.full_name}</p>
            <p className="text-xs text-gray-500">{user.role}</p>
          </div>
        </div>
      </div>
    </aside>
  );
};
