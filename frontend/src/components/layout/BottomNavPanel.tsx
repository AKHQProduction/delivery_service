import { useUserStore } from "../../context/useUserStore";
import { useNavigate, useLocation } from "react-router-dom";
import { getRoutesForRole } from "../../config/roles.config";

export const BottomNavPanel = () => {
  const user = useUserStore((s) => s.user);
  const navigate = useNavigate();
  const location = useLocation();

  if (!user) return null;
  const userRoutes = getRoutesForRole(user.role).filter(
    (route) => route.showInNav !== false
  );

  return (
    <div className="flex items-center justify-center fixed bottom-0 w-full">
      <div className="w-full max-w-md">
        <nav className="bg-white shadow-lg px-4 py-4 border border-gray-200 rounded-lg">
          <div className="flex items-center justify-around w-full">
            {userRoutes?.map((route) => {
              const isActive = location.pathname === route.path;

              return (
                <button
                  key={route.path}
                  onClick={() => navigate(route.path)}
                  className="
                    flex flex-col items-center justify-center
                    gap-1 py-1 px-2
                    transition
                  "
                >
                  <img
                    src={route.icon}
                    alt={route.label}
                    className={`w-6 h-6 object-contain ${
                      isActive ? "opacity-100" : "opacity-70"
                    }`}
                  />
                  <span
                    className={`text-xs ${
                      isActive ? "text-blue-600 font-medium" : "text-gray-600"
                    }`}
                  >
                    {route.label}
                  </span>
                </button>
              );
            })}
          </div>
        </nav>
      </div>
    </div>
  );
};
