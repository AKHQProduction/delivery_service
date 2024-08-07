import React, { useEffect, useRef, useState, useCallback } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-routing-machine/dist/leaflet-routing-machine.css";
import "leaflet-routing-machine";
import { generateRoute } from "../api/generateRoute";

export const MapComponent: React.FC = () => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const [routeControl, setRouteControl] = useState<L.Routing.Control | null>(null);

  useEffect(() => {
    if (mapRef.current && !mapInstance.current) {
      mapInstance.current = L.map(mapRef.current).setView([49.44443300,32.05976700], 13);
      L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      }).addTo(mapInstance.current);
    }
  }, []);

  const handleGenerateRoute = useCallback(() => {
    if (mapInstance.current) {
      generateRoute(mapInstance.current, setRouteControl);
    }
  }, [routeControl]);

  return (
    <div className="relative h-screen w-screen">
      <button
        id="testBtn"
        className="absolute top-5 left-1/2 -translate-x-1/2 bg-blue-500 text-white w-32 h-12 rounded"
        title="Click"
        onClick={handleGenerateRoute}
      >
        Generate Route
      </button>
      <div className="absolute inset-0" id="mapElement" ref={mapRef} />
    </div>
  );
};
