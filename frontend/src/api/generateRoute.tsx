import L from "leaflet";
import { watchUserCoordinates, getCustomerPosition } from "./getUserLocation";
import {createCustomMarker } from "../handlers/createMarker";

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
      const driverCoordinates: [number, number] = [
        position.coords.latitude,
        position.coords.longitude,
      ];
      const startCoords: [number, number] = driverCoordinates;
      const endCoords: [number, number] = customerPosition as [number, number];

      // Remove existing markers if they exist
      if (driverMarker) {
        map.removeLayer(driverMarker);
      }
      if (customerMarker) {
        map.removeLayer(customerMarker);
      }

      // Create driver and customer markers
      createCustomMarker(driverMarker, startCoords, map, "/icons/car-water.svg");
      createCustomMarker(customerMarker, endCoords, map, "/icons/map-pin.svg");

      map.setView(startCoords, map.getZoom());

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
          plan: new (L.Routing as any).Plan(
            [
              L.latLng(startCoords[0], startCoords[1]),
              L.latLng(endCoords[0], endCoords[1]),
            ],
            {
              createMarker: () => null,
              extendToWaypoints: false,
              missingRouteTolerance: 0,
            }
          ),
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
