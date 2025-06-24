#!/bin/bash
set -e

echo "🔹 Bringing up containers with docker-compose..."
docker-compose down
docker-compose up --build -d
