"""8311 Metrics integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MetricsApiClient, MetricsError, normalize_base_url
from .const import CONF_VERIFY_SSL, DEFAULT_HOST, DEFAULT_SCAN_INTERVAL, DEFAULT_VERIFY_SSL, DOMAIN, LOGGER

PLATFORMS: list[Platform] = [Platform.SENSOR]


class MetricsCoordinator(DataUpdateCoordinator[dict[str, float | int | None]]):
    """Coordinate metric polling."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MetricsApiClient,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
            always_update=False,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, float | int | None]:
        """Fetch metrics from the ONU."""
        try:
            return await self.client.async_get_metrics()
        except MetricsError as err:
            raise UpdateFailed(str(err)) from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up 8311 Metrics from a config entry."""
    data = {**entry.data, **entry.options}
    base_url = normalize_base_url(data.get(CONF_HOST) or DEFAULT_HOST)
    verify_ssl = bool(data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL))
    scan_interval = int(data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    session = async_get_clientsession(hass, verify_ssl=verify_ssl)
    client = MetricsApiClient(session, base_url)
    coordinator = MetricsCoordinator(hass, client, scan_interval)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
