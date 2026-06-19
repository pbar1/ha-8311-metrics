#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NETWORK_NAME="${NETWORK_NAME:-ha8311metrics-dev}"
HA_CONTAINER="${HA_CONTAINER:-ha8311metrics-ha}"
MOCK_CONTAINER="${MOCK_CONTAINER:-ha8311metrics-mock}"
HA_IMAGE="${HA_IMAGE:-ghcr.io/home-assistant/home-assistant:stable}"
HA_CONFIG_DIR="${HA_CONFIG_DIR:-$ROOT_DIR/.ha-dev/config}"
HA_PORT="${HA_PORT:-8311}"

usage() {
  printf 'Usage: %s {start|stop|clean|status|logs|validate}\n' "$0"
}

ensure_podman() {
  if ! podman info >/dev/null 2>&1; then
    podman machine start
  fi
}

ensure_network() {
  if ! podman network exists "$NETWORK_NAME" >/dev/null 2>&1; then
    podman network create "$NETWORK_NAME" >/dev/null
  fi
}

start_container() {
  local name="$1"
  shift

  if podman container exists "$name"; then
    podman start "$name" >/dev/null
    return
  fi

  podman run -d --name "$name" "$@" >/dev/null
}

start() {
  ensure_podman
  ensure_network
  mkdir -p "$HA_CONFIG_DIR"

  start_container "$MOCK_CONTAINER" \
    --network "$NETWORK_NAME" \
    --volume "$ROOT_DIR/scripts:/work/scripts:ro,Z" \
    "$HA_IMAGE" \
    python "/work/scripts/mock_metrics_server.py"

  start_container "$HA_CONTAINER" \
    --network "$NETWORK_NAME" \
    --publish "127.0.0.1:$HA_PORT:8123" \
    --volume "$HA_CONFIG_DIR:/config:Z" \
    --volume "$ROOT_DIR/custom_components:/config/custom_components:ro,Z" \
    "$HA_IMAGE"

  printf 'Home Assistant: http://127.0.0.1:%s\n' "$HA_PORT"
  printf 'Mock metrics URL inside HA: http://%s:8000/cgi-bin/luci/8311/metrics\n' "$MOCK_CONTAINER"
}

stop() {
  ensure_podman
  podman stop "$HA_CONTAINER" "$MOCK_CONTAINER" >/dev/null 2>&1 || true
}

clean() {
  ensure_podman
  podman rm -f "$HA_CONTAINER" "$MOCK_CONTAINER" >/dev/null 2>&1 || true
  podman network rm "$NETWORK_NAME" >/dev/null 2>&1 || true
  rm -rf "$ROOT_DIR/.ha-dev"
}

status() {
  ensure_podman
  podman ps --all --filter "name=ha8311metrics"
}

logs() {
  ensure_podman
  podman logs "$HA_CONTAINER"
}

validate() {
  start
  podman exec --workdir "/config" "$HA_CONTAINER" python -c '
import asyncio
import importlib
import aiohttp

api = importlib.import_module("custom_components.8311_metrics.api")
sensor = importlib.import_module("custom_components.8311_metrics.sensor")

async def main():
    async with aiohttp.ClientSession() as session:
        client = api.MetricsApiClient(session, "http://ha8311metrics-mock:8000")
        metrics = await client.async_get_metrics()
        assert metrics["cpu1_tempC"] == 52.68
        assert metrics["cpu2_tempC"] == 50.48
        assert metrics["module_voltage"] == 3.27
        assert metrics["optic_tempC"] == 34.04
        assert metrics["ploam_state"] == 51
        assert metrics["rx_power_dBm"] == -21.49
        assert metrics["tx_bias_mA"] == 35.48
        assert metrics["tx_power_dBm"] == 5.96
        assert len(sensor.SENSOR_DESCRIPTIONS) == 8
        print("HA container validation passed")

asyncio.run(main())
'
}

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  clean) clean ;;
  status) status ;;
  logs) logs ;;
  validate) validate ;;
  *) usage; exit 2 ;;
esac
