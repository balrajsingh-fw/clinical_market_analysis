#!/bin/bash
set -e

echo "🔹 Stop and remove existing container (if any)..."
docker stop clinical_analysis_container 2>/dev/null || true
docker rm clinical_analysis_container 2>/dev/null || true

echo "🔹 Build Docker image..."
docker build -t clinical_analysis_app .

echo "🔹 Run Docker container..."
docker run -d --name clinical_analysis_container -p 8042:8042 clinical_analysis_app
