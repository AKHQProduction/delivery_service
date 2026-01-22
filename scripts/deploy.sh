#!/bin/bash
set -e

echo "Pulling latest changes..."
git pull

echo "Building images without cache..."
docker compose -f docker-compose-prod.yml build --no-cache

echo "Restarting containers..."
docker compose -f docker-compose-prod.yml up -d --force-recreate

echo "Cleaning up old images..."
docker image prune -a -f

echo "Cleaning up build cache..."
docker builder prune -f

echo "Deploy completed!"