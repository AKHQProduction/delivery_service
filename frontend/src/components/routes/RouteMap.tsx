import React, { useMemo, useEffect, useCallback, useRef } from "react";
import { MapContainer, TileLayer, Marker, Polyline, Tooltip, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { type RoutePoint } from "../../types/entities/Route";

const MAP_TILE_URL =
  import.meta.env.VITE_MAP_TILE_URL || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const MAP_TILE_SUBDOMAINS = import.meta.env.VITE_MAP_TILE_URL
  ? ["mt0", "mt1", "mt2", "mt3"]
  : ["a", "b", "c"];

const hasValidCoordinates = (point: RoutePoint) =>
  Number.isFinite(point.coordinates?.latitude) && Number.isFinite(point.coordinates?.longitude);

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

const FitBounds: React.FC<{ points: RoutePoint[] }> = ({ points }) => {
  const map = useMap();
  const hasFitted = useRef(false);

  const fitBounds = useCallback(() => {
    if (points.length === 0) return;
    const bounds = L.latLngBounds(
      points.map((p) => [p.coordinates.latitude, p.coordinates.longitude] as [number, number]),
    );
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [30, 30], maxZoom: 15 });
    }
  }, [map, points]);

  useEffect(() => {
    if (!hasFitted.current && points.length > 0) {
      hasFitted.current = true;
      fitBounds();
    }
  }, [points, fitBounds]);

  useEffect(() => {
    map.on("resize", fitBounds);
    return () => { map.off("resize", fitBounds); };
  }, [map, fitBounds]);

  return null;
};

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

const InvalidateSize: React.FC = () => {
  const map = useMap();
  useEffect(() => {
    map.invalidateSize();
  });
  return null;
};

const OFFSET = 0.00015;

function spreadDuplicates(points: RoutePoint[]): Map<string, [number, number]> {
  const groups = new Map<string, number[]>();
  points.forEach((p, i) => {
    const key = `${p.coordinates.latitude},${p.coordinates.longitude}`;
    const list = groups.get(key);
    if (list) list.push(i);
    else groups.set(key, [i]);
  });

  const result = new Map<string, [number, number]>();
  for (const indices of groups.values()) {
    if (indices.length === 1) {
      const p = points[indices[0]];
      result.set(p.order_id, [p.coordinates.latitude, p.coordinates.longitude]);
      continue;
    }
    const base = points[indices[0]].coordinates;
    for (let j = 0; j < indices.length; j++) {
      const angle = (2 * Math.PI * j) / indices.length - Math.PI / 2;
      const p = points[indices[j]];
      result.set(p.order_id, [
        base.latitude + OFFSET * Math.sin(angle),
        base.longitude + OFFSET * Math.cos(angle),
      ]);
    }
  }
  return result;
}

interface RouteMapProps {
  points: RoutePoint[];
  editingOrderId: string | null;
  onMarkerMove: (orderId: string, lat: number, lng: number) => void;
}

export const RouteMap: React.FC<RouteMapProps> = ({ points, editingOrderId, onMarkerMove }) => {
  const validPoints = useMemo(() => points.filter(hasValidCoordinates), [points]);
  const polylinePositions = useMemo(
    () => validPoints.map((p) => [p.coordinates.latitude, p.coordinates.longitude] as [number, number]),
    [validPoints],
  );

  const markerPositions = useMemo(() => spreadDuplicates(validPoints), [validPoints]);

  const defaultCenter: [number, number] =
    validPoints.length > 0
      ? [validPoints[0].coordinates.latitude, validPoints[0].coordinates.longitude]
      : [50.4501, 30.5234];

  return (
    <MapContainer
      center={defaultCenter}
      zoom={13}
      style={{ height: "100%", width: "100%" }}
      scrollWheelZoom={true}
    >
      <TileLayer
        url={MAP_TILE_URL}
        subdomains={MAP_TILE_SUBDOMAINS}
        maxZoom={21}
      />
      <InvalidateSize />
      <FitBounds points={validPoints} />
      <MapClickHandler editingOrderId={editingOrderId} onMarkerMove={onMarkerMove} />

      {polylinePositions.length >= 2 && (
        <Polyline
          positions={polylinePositions}
          pathOptions={{
            color: "#4f46e5",
            weight: 4,
            opacity: 0.8,
            dashArray: "12, 8",
          }}
        />
      )}

      {validPoints.map((point, index) => {
        const pos = markerPositions.get(point.order_id) ?? [
          point.coordinates.latitude,
          point.coordinates.longitude,
        ];
        return (
          <Marker
            key={point.order_id}
            position={pos as [number, number]}
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
