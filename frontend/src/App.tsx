import { BrowserRouter, Routes, Route } from "react-router-dom";
import { BottomNavPanel } from "./components/layout/bottomNavPanel";
import { routeConfig } from "./config/roles.config";
//import { useUserStore } from "./context/useUserStore";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DevPage } from "./pages/DevPage";
import { AddItemComponent } from "./components/features/addItemComponent";

const isDev = import.meta.env.MODE === "development";

function App() {
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
        <AddItemComponent />
        <BottomNavPanel />
      </BrowserRouter>
    </>
  );
}

export default App;
