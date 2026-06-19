"""Constants for 8311 Metrics."""

from __future__ import annotations

import logging

DOMAIN = "8311_metrics"
LOGGER = logging.getLogger(__package__)

ENDPOINT = "/cgi-bin/luci/8311/metrics"

CONF_VERIFY_SSL = "verify_ssl"

DEFAULT_HOST = "192.168.11.1"
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_VERIFY_SSL = False

METRIC_FLOAT_KEYS = (
    "rx_power_dBm",
    "tx_power_dBm",
    "cpu1_tempC",
    "cpu2_tempC",
    "optic_tempC",
    "tx_bias_mA",
    "module_voltage",
)

METRIC_INT_KEYS = ("ploam_state",)
