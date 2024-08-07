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
    let driverMarker: L.Marker | null = null;

    const updateRoute = (position: GeolocationPosition) => {
      const driverCoordinates: [number, number] = [position.coords.latitude, position.coords.longitude];
      const startCoords: [number, number] = driverCoordinates;
      const endCoords: [number, number] = customerPosition as [number, number];

      // Log the coordinates to verify they are updating
      console.log("Driver coordinates:", startCoords);

      // Create or update the driver marker
      if (driverMarker) {
        driverMarker.setLatLng(startCoords);
      } else {
        driverMarker = L.marker(startCoords).addTo(map);
      }

      map.setView(startCoords, 15)

      // Update the route control waypoints or create a new route control
      if (routeControl) {
        routeControl.setWaypoints([
          L.latLng(startCoords[0], startCoords[1]),
          L.latLng(endCoords[0], endCoords[1]),
        ]);
      } else {
        routeControl = L.Routing.control({
          waypoints: [
            L.latLng(startCoords[0], startCoords[1]),
            L.latLng(endCoords[0], endCoords[1]),
          ],
          show: false,
          routeWhileDragging: true,
        }).addTo(map);
        setRouteControl(routeControl);
      }
    };

    watchUserCoordinates(updateRoute, (error) => {
      console.error("Geolocation error:", error);
    });
  } catch (error) {
    console.error("Error generating route:", error);
  }
};
