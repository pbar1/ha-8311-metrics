#!/usr/bin/env python3
"""Serve a static 8311 metrics response for local validation."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

METRICS = {
    "cpu1_tempC": 52.68,
    "cpu2_tempC": 50.48,
    "module_voltage": 3.27,
    "optic_tempC": 34.04,
    "ploam_state": 51,
    "rx_power_dBm": -21.49,
    "tx_bias_mA": 35.48,
    "tx_power_dBm": 5.96,
}


class MetricsHandler(BaseHTTPRequestHandler):
    """Handle mock metrics requests."""

    def do_GET(self) -> None:
        """Serve the metrics endpoint."""
        if self.path != "/cgi-bin/luci/8311/metrics":
            self.send_error(404)
            return

        body = json.dumps(METRICS).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        """Silence request logging."""


def main() -> None:
    """Run the mock server."""
    server = ThreadingHTTPServer(("0.0.0.0", 8000), MetricsHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
