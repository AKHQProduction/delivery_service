import L from "leaflet";
import { watchUserCoordinates, getCustomerPosition } from "./getUserLocation";
import { createCustomMarker } from "../handlers/createMarker";

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
    let customerMarker: L.Marker | null = null;

    const updateRoute = (position: GeolocationPosition) => {
      //get start and end coordinates, driver is updating, customer is const
      const startCoords: [number, number] = [
        position.coords.latitude,
        position.coords.longitude,
      ];
      const endCoords: [number, number] = customerPosition as [number, number];

      // Remove existing markers if they exist
      if (driverMarker && customerMarker) {
        map.removeLayer(driverMarker);
        map.removeLayer(customerMarker);
      }

      // Create driver and customer markers
      driverMarker = createCustomMarker(
        driverMarker,
        startCoords,
        map,
        "/icons/car-water.svg"
      );
      customerMarker = createCustomMarker(
        customerMarker,
        endCoords,
        map,
        "/icons/map-pin.svg"
      );

      // set view to start coordinates with zoom allowed
      map.setView(startCoords, map.getZoom());

      // set waypoints(markers)
      const waypoints = [
        L.latLng(startCoords[0], startCoords[1]),
        L.latLng(endCoords[0], endCoords[1]),
      ];

      // Update the route control waypoints or create a new route control
      if (routeControl) {
        routeControl.setWaypoints(waypoints);
      } else {
        routeControl = L.Routing.control({
          waypoints: waypoints,
          show: false,
          routeWhileDragging: true,
          plan: new (L.Routing as any).Plan(waypoints, {
            createMarker: () => null,
          }),
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
