"""Tests for the 8311 metrics API helpers."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
import types
import unittest


def _load_api_module():
    """Load api.py without importing the Home Assistant package __init__."""
    root = Path(__file__).parents[1] / "custom_components" / "8311_metrics"
    package_name = "custom_components.8311_metrics"

    aiohttp = types.ModuleType("aiohttp")
    aiohttp.ClientError = Exception
    aiohttp.ClientResponseError = Exception
    aiohttp.ClientSession = object
    sys.modules.setdefault("aiohttp", aiohttp)

    sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
    package = types.ModuleType(package_name)
    package.__path__ = [str(root)]
    sys.modules[package_name] = package

    importlib.import_module(f"{package_name}.const")
    spec = importlib.util.spec_from_file_location(f"{package_name}.api", root / "api.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


api = _load_api_module()


class TestApiHelpers(unittest.TestCase):
    """Tests for API helper behavior."""

    def test_normalize_base_url_defaults_to_https(self) -> None:
        """Host names become HTTPS base URLs."""
        self.assertEqual(api.normalize_base_url("192.168.11.1"), "https://192.168.11.1")

    def test_parse_metrics_uses_numeric_endpoint_shape(self) -> None:
        """Known numeric metrics are parsed from the endpoint shape."""
        parsed = api.parse_metrics(
            {
                "cpu1_tempC": 52.68,
                "cpu2_tempC": 50.48,
                "module_voltage": 3.27,
                "optic_tempC": 34.04,
                "ploam_state": 51,
                "rx_power_dBm": -21.49,
                "tx_bias_mA": 35.48,
                "tx_power_dBm": 5.96,
            }
        )

        self.assertEqual(parsed["cpu1_tempC"], 52.68)
        self.assertEqual(parsed["cpu2_tempC"], 50.48)
        self.assertEqual(parsed["module_voltage"], 3.27)
        self.assertEqual(parsed["optic_tempC"], 34.04)
        self.assertEqual(parsed["ploam_state"], 51)
        self.assertEqual(parsed["rx_power_dBm"], -21.49)
        self.assertEqual(parsed["tx_bias_mA"], 35.48)
        self.assertEqual(parsed["tx_power_dBm"], 5.96)

    def test_parse_metrics_rejects_non_finite_values(self) -> None:
        """NaN and infinity are ignored."""
        parsed = api.parse_metrics({"rx_power_dBm": "nan", "tx_power_dBm": "-inf"})

        self.assertIsNone(parsed["rx_power_dBm"])
        self.assertIsNone(parsed["tx_power_dBm"])


if __name__ == "__main__":
    unittest.main()
