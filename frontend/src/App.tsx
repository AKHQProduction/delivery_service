import { BrowserRouter, Routes, Route } from "react-router-dom";
import { BottomNavPanel } from "./components/layout/BottomNavPanel";
import { routeConfig } from "./config/roles.config";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DevPage } from "./pages/DevPage";
import { AddItemComponent } from "./components/features/AddItemComponent";
import { getUserShopData } from "./services/api/userApi";
import { useEffect } from "react";
import { useUserShopStore } from "./context/useUserShopStore";
import { MenuModal } from "./components/modals/MenuModal";
import { ErrorProvider } from "./context/ErrorContext";
import { ErrorBoundary } from "./components/ErrorBoundary";

const isDev = import.meta.env.MODE === "development";

function App() {
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await getUserShopData();
        useUserShopStore.getState().setUserAndShop(data.user, data.shop);
      } catch (error) {
        console.error("Failed to fetch user:", error);
      }
    };
    fetchUser();
  }, []);

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <ErrorProvider>
          <Routes>
            {isDev && <Route path="/dev" element={<DevPage />} />}
            {routeConfig.map((route) => (
              <Route
                key={route.path}
                path={route.path}
                element={
                  <ProtectedRoute allowedRoles={route.allowedRoles}>
                    <route.component />
                  </ProtectedRoute>
                }
              />
            ))}
          </Routes>
          <MenuModal />
          <AddItemComponent />
          <BottomNavPanel />
        </ErrorProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
