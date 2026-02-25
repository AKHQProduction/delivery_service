import React, { useMemo, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Polyline, Tooltip, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { type RoutePoint } from "../../types/entities/Route";

// Numbered marker icon factory
const createNumberedIcon = (num: number, isEditing: boolean) => {
  const color = isEditing ? "#f59e0b" : "#4f46e5";
  return L.divIcon({
    className: "custom-marker",
    html: `<div style="
      background: ${color};
      color: white;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 14px;
      border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">${num}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

/** Decode Google encoded polyline to array of [lat, lng] */
const decodePolyline = (encoded: string): [number, number][] => {
  const points: [number, number][] = [];
  let index = 0;
  let lat = 0;
  let lng = 0;

  while (index < encoded.length) {
    let shift = 0;
    let result = 0;
    let byte: number;
    do {
      byte = encoded.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);
    lat += result & 1 ? ~(result >> 1) : result >> 1;

    shift = 0;
    result = 0;
    do {
      byte = encoded.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);
    lng += result & 1 ? ~(result >> 1) : result >> 1;

    points.push([lat / 1e5, lng / 1e5]);
  }
  return points;
};

/** Fit map bounds to all markers */
const FitBounds: React.FC<{ points: RoutePoint[] }> = ({ points }) => {
  const map = useMap();

  useEffect(() => {
    if (points.length === 0) return;
    const bounds = L.latLngBounds(
      points.map((p) => [p.coordinates.latitude, p.coordinates.longitude] as [number, number]),
    );
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
    }
  }, [points, map]);

  return null;
};

/** Click handler for marker editing */
const MapClickHandler: React.FC<{
  editingOrderId: string | null;
  onMarkerMove: (orderId: string, lat: number, lng: number) => void;
}> = ({ editingOrderId, onMarkerMove }) => {
  useMapEvents({
    click: (e) => {
      if (editingOrderId) {
        onMarkerMove(editingOrderId, e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
};

interface RouteMapProps {
  points: RoutePoint[];
  encodedPolyline?: string;
  editingOrderId: string | null;
  onMarkerMove: (orderId: string, lat: number, lng: number) => void;
}

export const RouteMap: React.FC<RouteMapProps> = ({ points, encodedPolyline, editingOrderId, onMarkerMove }) => {
  // Use encoded polyline from geometry if available, otherwise fall back to straight lines between points
  const polylinePositions = useMemo(() => {
    if (encodedPolyline) {
      return decodePolyline(encodedPolyline);
    }
    return points.map((p) => [p.coordinates.latitude, p.coordinates.longitude] as [number, number]);
  }, [points, encodedPolyline]);

  const defaultCenter: [number, number] =
    points.length > 0
      ? [points[0].coordinates.latitude, points[0].coordinates.longitude]
      : [50.4501, 30.5234];

  return (
    <MapContainer
      center={defaultCenter}
      zoom={13}
      style={{ height: "100%", width: "100%" }}
      scrollWheelZoom={true}
    >
      <TileLayer
        url={import.meta.env.VITE_MAP_TILE_URL}
        subdomains={["mt0", "mt1", "mt2", "mt3"]}
        maxZoom={21}
      />
      <FitBounds points={points} />
      <MapClickHandler editingOrderId={editingOrderId} onMarkerMove={onMarkerMove} />

      {/* Route polyline */}
      {polylinePositions.length >= 2 && (
        <Polyline
          positions={polylinePositions}
          pathOptions={{
            color: "#4f46e5",
            weight: 4,
            opacity: 0.8,
            dashArray: encodedPolyline ? undefined : "12, 8",
          }}
        />
      )}

      {/* Markers */}
      {points.map((point, index) => {
        const pos: [number, number] = [
          point.coordinates.latitude,
          point.coordinates.longitude,
        ];
        return (
          <Marker
            key={point.order_id}
            position={pos}
            icon={createNumberedIcon(index + 1, editingOrderId === point.order_id)}
          >
            <Tooltip direction="top" offset={[0, -20]} permanent={false}>
              <div className="text-sm">
                <p className="font-semibold">{point.client_name}</p>
                <p className="text-gray-500">{point.address}</p>
              </div>
            </Tooltip>
          </Marker>
        );
      })}
    </MapContainer>
  );
};
