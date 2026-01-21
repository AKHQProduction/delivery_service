import { BrowserRouter, Routes, Route } from "react-router-dom";
import { BottomNavPanel } from "./components/layout/bottomNavPanel";
import { routeConfig } from "./config/roles.config";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DevPage } from "./pages/DevPage";
import { AddItemComponent } from "./components/features/addItemComponent";
import { getUser } from "./services/api/userApi";
import { useEffect } from "react";
import { useUserStore } from "./context/useUserStore";
import { MenuModal } from "./components/modals/MenuModal";

const isDev = import.meta.env.MODE === "development";

function App() {
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await getUser();
        useUserStore.getState().setUser({
          user_id: data.user_id,
          role: data.role,
        });
      } catch (error) {
        console.error("Failed to fetch user:", error);
      }
    };
    fetchUser();
  }, []);

  return (
    <>
      <BrowserRouter>
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
      </BrowserRouter>
    </>
  );
}

export default App;
