"""HTTP client for the 8311 metrics endpoint."""

from __future__ import annotations

import asyncio
import math
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import ENDPOINT, METRIC_FLOAT_KEYS, METRIC_INT_KEYS


class MetricsError(Exception):
    """Base metrics client error."""


class CannotConnect(MetricsError):
    """Raised when the endpoint cannot be reached."""


class InvalidResponse(MetricsError):
    """Raised when the endpoint response is not usable metrics JSON."""


def normalize_base_url(host: str) -> str:
    """Return a normalized base URL from a host or URL."""
    host = host.strip()
    if not host:
        raise InvalidResponse("Host is required")
    if "://" not in host:
        host = f"https://{host}"
    return host.rstrip("/")


def parse_metrics(raw: dict[str, Any]) -> dict[str, float | int | None]:
    """Parse endpoint JSON into typed metric values."""
    metrics: dict[str, float | int | None] = {}

    for key in METRIC_FLOAT_KEYS:
        metrics[key] = _as_finite_float(raw.get(key))

    for key in METRIC_INT_KEYS:
        metrics[key] = _as_int(raw.get(key))

    return metrics


class MetricsApiClient:
    """Client for the unauthenticated metrics endpoint."""

    def __init__(self, session: ClientSession, base_url: str) -> None:
        """Initialize the client."""
        self._session = session
        self._base_url = normalize_base_url(base_url)

    async def async_get_metrics(self) -> dict[str, float | int | None]:
        """Fetch and parse metrics."""
        try:
            async with asyncio.timeout(10):
                async with self._session.get(f"{self._base_url}{ENDPOINT}") as response:
                    response.raise_for_status()
                    raw = await response.json(content_type=None)
        except (TimeoutError, ClientResponseError, ClientError) as err:
            raise CannotConnect(f"Failed to fetch metrics: {err}") from err
        except ValueError as err:
            raise InvalidResponse("Metrics endpoint did not return JSON") from err

        if not isinstance(raw, dict):
            raise InvalidResponse("Metrics endpoint did not return a JSON object")

        metrics = parse_metrics(raw)
        if not any(value is not None for value in metrics.values()):
            raise InvalidResponse("Metrics endpoint did not include known metrics")

        return metrics


def _as_finite_float(value: Any) -> float | None:
    """Convert a value to a finite float."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numeric):
        return None
    return numeric


def _as_int(value: Any) -> int | None:
    """Convert a value to an int."""
    numeric = _as_finite_float(value)
    if numeric is None:
        return None
    return int(numeric)
