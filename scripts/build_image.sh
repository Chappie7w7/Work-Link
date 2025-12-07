#!/usr/bin/env bash
set -e

# Construye la imagen Docker de la aplicación WorkLink.
# Uso:
#   ./scripts/build_image.sh [IMAGE_NAME] [TAG]
# Ejemplo:
#   ./scripts/build_image.sh chappie420/work-link v1

IMAGE_NAME="${1:-chappie420/work-link}"
TAG="${2:-v1}"

echo "Construyendo imagen ${IMAGE_NAME}:${TAG} ..."
docker build -t "${IMAGE_NAME}:${TAG}" .
