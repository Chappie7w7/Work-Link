#!/usr/bin/env bash
set -e

# Levanta el stack de monitoreo (WorkLink + Prometheus + Node Exporter + Grafana).
# Uso:
#   ./scripts/monitoring_up.sh

docker compose -f docker-compose.monitoring.yml up -d
