import { Navigate } from "react-router-dom";
import { useUserShopStore } from "../context/useUserShopStore";
import { UserRole } from "../constants/roles";
import { getDefaultRouteForRole } from "../config/roles.config";
import { usePlatform } from "../platforms/usePlatform";

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const user = useUserShopStore((s) => s.user);
  const shop = useUserShopStore((s) => s.shop);
  const { unauthorizedRedirect } = usePlatform();

  if (!user) {
    return <Navigate to={unauthorizedRedirect} replace />;
  }

  if (!shop) {
    return <Navigate to="/create-shop" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    const defaultRoute = getDefaultRouteForRole(user.role);
    return <Navigate to={defaultRoute} replace />;
  }

  return <>{children}</>;
};
