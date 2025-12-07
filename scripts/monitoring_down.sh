#!/usr/bin/env bash
set -e

# Detiene el stack de monitoreo (WorkLink + Prometheus + Node Exporter + Grafana).
# Uso:
#   ./scripts/monitoring_down.sh

docker compose -f docker-compose.monitoring.yml down
