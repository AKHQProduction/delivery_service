import { BrowserRouter, Routes, Route } from "react-router-dom";
import { BottomNavPannel } from "./components/bottomNavPannel";
// import { getUser } from "./api/user";
// import { useEffect } from "react";
import { DevPage } from "./pages/DevPage";

const isDev = import.meta.env.MODE === "development";

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>{isDev && <Route path="/dev" element={<DevPage />} />}</Routes>
      </BrowserRouter>
      <BottomNavPannel />
    </>
  );
}

export default App;
