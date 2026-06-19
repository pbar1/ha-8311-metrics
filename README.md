# 8311 Metrics

Minimal Home Assistant custom integration for the unauthenticated 8311 firmware metrics endpoint on WAS-110 and compatible ONUs.

This integration polls only:

```text
GET /cgi-bin/luci/8311/metrics
```

It does not use SSH, MQTT, shell commands, or any write-capable WAS-110 API.

## Installation

### HACS Custom Repository

1. Open HACS in Home Assistant.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/pbar1/ha-8311-metrics`.
4. Select repository type **Integration**.
5. Install **8311 Metrics**.
6. Restart Home Assistant.
7. Go to **Settings** -> **Devices & services** -> **Add integration**.
8. Search for **8311 Metrics** and configure it.

### Manual Install

1. Copy `custom_components/8311_metrics` into your Home Assistant config directory under `custom_components/8311_metrics`.
2. Restart Home Assistant.
3. Go to **Settings** -> **Devices & services** -> **Add integration**.
4. Search for **8311 Metrics** and configure it.

## Requirements

- 8311 WAS-110 firmware `2.8.2` or newer
- Home Assistant `2024.6.0` or newer
- Network reachability from Home Assistant to the ONU management IP

## Sensors

- PLOAM state
- RX optical power
- TX optical power
- CPU1 temperature
- CPU2 temperature
- Optic temperature
- TX bias current
- Module voltage

## Configuration

Add the integration from Home Assistant's UI and provide:

- Host or base URL, for example `192.168.11.1`, `https://192.168.11.1`, or `http://192.168.11.1`
- Scan interval in seconds
- Whether to verify the HTTPS certificate

Certificate verification defaults to off because the 8311 web UI commonly uses a self-signed certificate.

The integration stores the configured base URL as the unique device identifier. If you later move the ONU to another management IP, remove and re-add the integration.

## HACS Repository Requirements

This repository is structured as a HACS integration repository:

- `hacs.json` exists at the repository root.
- Exactly one integration exists under `custom_components/8311_metrics`.
- `manifest.json` includes the required custom-integration metadata.
- A brand icon exists under `custom_components/8311_metrics/brand/icon.png`.
- English translation strings exist under `custom_components/8311_metrics/translations/en.json`.

Before submitting this repository as a HACS default repository, configure the GitHub repository description and topics. Suggested topics: `home-assistant`, `hacs`, `8311`, `was-110`, `xgs-pon`, `monitoring`.

## Development Container

Run local helper tests through `uv`:

```sh
scripts/test.sh
```

This runs `compileall` and the stdlib `unittest` suite in a `uv`-managed environment.

Use the repeatable Podman dev environment to run an isolated Home Assistant instance with a mock metrics endpoint:

```sh
scripts/ha_dev.sh start
```

This starts:

- Home Assistant at `http://127.0.0.1:8311`
- A mock endpoint at `http://ha8311metrics-mock:8000/cgi-bin/luci/8311/metrics` inside the private Podman network

The Home Assistant container mounts only this repository's `custom_components` directory and a generated `.ha-dev/config` directory. It does not mount or read any real Home Assistant configuration.

Run the container validation:

```sh
scripts/ha_dev.sh validate
```

Useful commands:

```sh
scripts/ha_dev.sh status
scripts/ha_dev.sh logs
scripts/ha_dev.sh stop
scripts/ha_dev.sh clean
```

`stop` preserves `.ha-dev/config`. `clean` removes the dev containers, network, and generated isolated config.
