import { BrowserRouter, Routes, Route } from "react-router-dom";
import { BottomNavPanel } from "./components/layout/BottomNavPanel";
import { AppLayout } from "./components/layout/AppLayout";
import { routeConfig } from "./config/roles.config";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DevPage } from "./pages/DevPage";
import { LoginPage } from "./pages/LoginPage";
import { AddItemComponent } from "./components/features/AddItemComponent";
import { getUserShopData } from "./services/api/userApi";
import { useEffect } from "react";
import { useUserShopStore } from "./context/useUserShopStore";
import { MenuModal } from "./components/modals/MenuModal";
import { ErrorProvider } from "./context/ErrorContext";
import { ErrorBoundary } from "./components/ErrorBoundary";
import initDataTG from "./services/tgInitData";

const isDev = import.meta.env.MODE === "development";

function App() {
  const authStatus = useUserShopStore((s) => s.authStatus);

  useEffect(() => {
    const store = useUserShopStore.getState();
    const isTG = !!initDataTG?.initData;
    store.setIsTGWebApp(isTG);
    store.setAuthStatus("loading");

    const fetchUser = async () => {
      try {
        const data = await getUserShopData();
        store.setUserAndShop(data.user, data.shop);
        store.setAuthStatus("authenticated");
      } catch (error) {
        console.error("Failed to fetch user:", error);
        store.setAuthStatus("unauthenticated");
      }
    };
    fetchUser();
  }, []);

  if (authStatus === "idle" || authStatus === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <ErrorProvider>
          <AppLayout>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
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
          </AppLayout>
          <MenuModal />
          <AddItemComponent />
          <BottomNavPanel />
        </ErrorProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
