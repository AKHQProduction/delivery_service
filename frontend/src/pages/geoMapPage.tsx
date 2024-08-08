import { MapComponent } from "../components/mapComponent";
import { generateRoute as driver } from "../services/generateRouteDriver";

const GeoMapPage = () => {
  return (
    <>
      <MapComponent generateRoute = {driver} />
    </>
  );
};

export default GeoMapPage;
