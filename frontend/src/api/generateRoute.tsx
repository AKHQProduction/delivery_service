import L from "leaflet";
import { watchUserCoordinates, getCustomerPosition } from "./getUserLocation";

export const generateRoute = async (
  map: L.Map,
  setRouteControl: (control: L.Routing.Control) => void
) => {
  try {
    const customerPosition = await getCustomerPosition();
    if (!customerPosition) {
      throw new Error("Customer position could not be determined");
    }

    let routeControl: L.Routing.Control | null = null;

    const updateRoute = (position: GeolocationPosition) => {
      const driverCoordinates = [position.coords.latitude, position.coords.longitude];
      const startCoords = driverCoordinates;
      const endCoords = customerPosition;

      console.log("Driver coordinates:", startCoords);

      if (routeControl) {
        map.removeControl(routeControl);
      }

      // Create new route
      routeControl = L.Routing.control({
        waypoints: [
          L.latLng(startCoords[0], startCoords[1]),
          L.latLng(endCoords[0], endCoords[1]),
        ],
        routeWhileDragging: true,
      }).addTo(map);

      // Set new route
      setRouteControl(routeControl);
    };

    watchUserCoordinates(updateRoute, (error) => {
      console.error("Geolocation error:", error);
    });
  } catch (error) {
    console.error("Error generating route:", error);
  }
};