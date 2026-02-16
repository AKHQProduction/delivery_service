#!/bin/bash
set -e

echo "Pulling latest changes..."
PULL_OUTPUT=$(git pull)
echo "$PULL_OUTPUT"

if [ "$PULL_OUTPUT" = "Already up to date." ]; then
  echo "No changes found. Exiting."
  exit 0
fi

DUMPS_DIR="$(cd "$(dirname "$0")/.." && pwd)/dumps"
mkdir -p "$DUMPS_DIR"

echo "Creating database dump..."
DUMP_FILE="$DUMPS_DIR/dump_$(date +%Y%m%d_%H%M%S).sql.gz"
docker exec water_delivery-postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "$DUMP_FILE"
echo "Dump created: $DUMP_FILE"

echo "Removing previous dumps..."
for old_dump in "$DUMPS_DIR"/dump_*.sql.gz; do
  [ "$old_dump" != "$DUMP_FILE" ] && rm -f "$old_dump"
done

echo "Building images without cache..."
docker compose -f docker-compose-prod.yml build --no-cache

echo "Restarting containers..."
docker compose -f docker-compose-prod.yml up -d --force-recreate

echo "Cleaning up old images..."
docker image prune -a -f

echo "Cleaning up build cache..."
docker builder prune -f

echo "Deploy completed!"