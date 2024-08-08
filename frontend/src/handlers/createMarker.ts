import L from "leaflet";

export const createCustomIcon = (url: string) => {
  return new L.Icon({
    iconUrl: url,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
};

export const createCustomMarker = (
  marker: L.Marker<any> | null,
  coordinates: [number, number],
  map: L.Map,
  url: string
) => {
  marker = L.marker(coordinates, {
    icon: createCustomIcon(url),
  }).addTo(map);

  return marker;
};
