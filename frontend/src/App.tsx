import { BrowserRouter, Routes, Route } from "react-router-dom";
import { BottomNavPannel } from "./components/bottomNavPannel";
// import { getUser } from "./api/user";
// import { useEffect } from "react";
import { DevPage } from "./pages/DevPage";
import { AddItemComponent } from "./components/addItemComponent";

const isDev = import.meta.env.MODE === "development";

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>{isDev && <Route path="/dev" element={<DevPage />} />}</Routes>
        <AddItemComponent />
        <BottomNavPannel />
      </BrowserRouter>
    </>
  );
}

export default App;
