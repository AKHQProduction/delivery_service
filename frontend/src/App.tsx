import GeoMapPage from "./pages/geoMapPage";
import { UserPositionQueryParam } from "./url/queryParamUserPosition";
import "./App.css";
import { BrowserRouter } from "react-router-dom";

function App() {
  return (
    <>
      <BrowserRouter>
        <UserPositionQueryParam />
      </BrowserRouter>

      <GeoMapPage />
    </>
  );
}

export default App;
