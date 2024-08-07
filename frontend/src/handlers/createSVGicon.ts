import L from "leaflet";

export const createCustomIcon = (url: string) => {
    return new L.Icon({
      iconUrl: url,
      iconSize: [32, 32],
      iconAnchor: [16, 32], 
      popupAnchor: [0, -32],
    });
  };
