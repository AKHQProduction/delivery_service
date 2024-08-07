import React, { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';
import 'leaflet-routing-machine';
import { generateRoute } from '../api/generateRoute';

export const MapComponent: React.FC = () => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const [routeControl, setRouteControl] = useState<L.Routing.Control | null>(null);

  useEffect(() => {
    if (mapRef.current && !mapInstance.current) {
      mapInstance.current = L.map(mapRef.current).setView([51.505, -0.09], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(mapInstance.current);
    }
  }, []);

  const handleGenerateRoute = useCallback(() => {
    if (mapInstance.current) {
      if (routeControl) {
        mapInstance.current.removeControl(routeControl);
      }
      generateRoute(mapInstance.current, setRouteControl);
    }
  }, [routeControl]);

  return (
    <div>
      <button title="Click" onClick={handleGenerateRoute}>Generate Route</button>
      <div
        ref={mapRef}
        style={{
          height: '500px',
          width: '100%',
          marginBottom: '20px',
        }}
      />
    </div>
  );
};
