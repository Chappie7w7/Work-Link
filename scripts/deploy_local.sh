#!/usr/bin/env bash
set -e

# Actualiza la imagen de WorkLink desde Docker Hub y levanta el stack de monitoreo.
# Uso:
#   ./scripts/deploy_local.sh [IMAGE_NAME] [TAG]
# Ejemplo:
#   ./scripts/deploy_local.sh chappie420/work-link v1

IMAGE_NAME="${1:-chappie420/work-link}"
TAG="${2:-v1}"

FULL_IMAGE="${IMAGE_NAME}:${TAG}"

echo "Haciendo pull de ${FULL_IMAGE} ..."
docker pull "${FULL_IMAGE}" || true

echo "Levantando stack local de monitoreo..."
docker compose -f docker-compose.monitoring.yml up -d
