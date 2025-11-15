import { useUserStore } from "../hooks/useUserStore";
import { UserRole } from "../types/roles";

export const BottomNavPannel = () => {
  const user = useUserStore((s) => s.user);
  const hasRole = useUserStore((s) => s.hasRole);
  //const hasAnyRole = useUserStore((s) => s.hasAnyRole);

  if (!user) return null;

  return (
    <div className="flex items-center justify-center fixed bottom-0 w-full">
      <div className="w-full max-w-md">
        <nav className="bg-white shadow-lg px-4 py-6 border border-gray-200 rounded-lg">
          <div className="flex items-center justify-around">

            {hasRole(UserRole.COURIER) && (
              <>
                <button>Home</button>
                <button>Profile</button>
              </>
            )}

            {hasRole(UserRole.MANAGER) && (
              <>
                <button>Home</button>
                <button>Manage users</button>
                <button>Analytics</button>
              </>
            )}

            {hasRole(UserRole.OWNER) && (
              <>
                <button>Dashboard</button>
                <button>Admin Tools</button>
                <button>Settings</button>
              </>
            )}
            
          </div>
        </nav>
      </div>
    </div>
  );
};
