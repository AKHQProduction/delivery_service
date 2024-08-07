import L from 'leaflet';
import { getUserCoordinates } from './getUserLocation';

export const generateRoute = async (map: L.Map, setRouteControl: (control: L.Routing.Control) => void) => {
  const userCordinates = await getUserCoordinates();
  console.log(userCordinates)
  try {
    const response = await fetch('/geocode', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    const routeData = await response.json();

    if (routeData.error) {
      alert('Address not found');
      return;
    }

    const startCoords = [routeData.customer.latitude, routeData.customer.longitude];
    const endCoords = [userCordinates.latitude, userCordinates.longitude];

    // Create new route
    const newRouteControl = L.Routing.control({
      waypoints: [
        L.latLng(startCoords[0], startCoords[1]),
        L.latLng(endCoords[0], endCoords[1]),
      ],
      routeWhileDragging: true,
    }).addTo(map);

    // Set new route
    setRouteControl(newRouteControl);
  } catch (error) {
    console.error('Error generating route:', error);
  }
};
