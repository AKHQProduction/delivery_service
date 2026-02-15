#!/bin/bash
set -e

OSRM_IMAGE="osrm/osrm-backend"
DATA_DIR="$(cd "$(dirname "$0")/.." && pwd)/osrm-data"
REGION_URL="${1:-https://download.geofabrik.de/europe/ukraine-latest.osm.pbf}"
PBF_FILE="$DATA_DIR/$(basename "$REGION_URL")"
OSRM_FILE="${PBF_FILE%.osm.pbf}.osrm"

echo "=== OSRM Setup ==="
echo "Data directory: $DATA_DIR"
echo "Region: $REGION_URL"
echo ""

mkdir -p "$DATA_DIR"

if [ -f "$OSRM_FILE" ]; then
    echo "Processed OSRM files already exist: $OSRM_FILE"
    read -rp "Re-process? (y/N): " answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        echo "Skipped. Run 'docker compose --profile map up -d osrm' to start."
        exit 0
    fi
fi

if [ ! -f "$PBF_FILE" ]; then
    echo "[1/4] Downloading map data..."
    curl -L -o "$PBF_FILE" "$REGION_URL"
else
    echo "[1/4] Map file already exists, skipping download."
fi

echo ""
echo "[2/4] Extracting road network (osrm-extract)..."
docker run --rm --platform linux/amd64 -v "$DATA_DIR:/data" "$OSRM_IMAGE" \
    osrm-extract -p /opt/car.lua "/data/$(basename "$PBF_FILE")"

echo ""
echo "[3/4] Partitioning graph (osrm-partition)..."
docker run --rm --platform linux/amd64 -v "$DATA_DIR:/data" "$OSRM_IMAGE" \
    osrm-partition "/data/$(basename "$OSRM_FILE")"

echo ""
echo "[4/4] Computing weights (osrm-customize)..."
docker run --rm --platform linux/amd64 -v "$DATA_DIR:/data" "$OSRM_IMAGE" \
    osrm-customize "/data/$(basename "$OSRM_FILE")"

echo ""
echo "=== Done ==="
echo "PBF file kept at: $PBF_FILE"
echo "Start OSRM + Nominatim: docker compose --profile map up -d"
echo "Test OSRM:              curl http://localhost:5050/trip/v1/driving/30.52,50.45;30.53,50.46"
echo "Test Nominatim:         curl 'http://localhost:8088/search?q=Kyiv&format=json'"