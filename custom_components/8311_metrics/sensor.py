"""Sensors for 8311 Metrics."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricPotential, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MetricsCoordinator
from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class MetricsSensorEntityDescription(SensorEntityDescription):
    """Describe an 8311 metric sensor."""

    value_key: str


SENSOR_DESCRIPTIONS: tuple[MetricsSensorEntityDescription, ...] = (
    MetricsSensorEntityDescription(
        key="ploam_state",
        value_key="ploam_state",
        name="PLOAM State",
        icon="mdi:state-machine",
    ),
    MetricsSensorEntityDescription(
        key="rx_power",
        value_key="rx_power_dBm",
        name="RX Power",
        native_unit_of_measurement="dBm",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    MetricsSensorEntityDescription(
        key="tx_power",
        value_key="tx_power_dBm",
        name="TX Power",
        native_unit_of_measurement="dBm",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    MetricsSensorEntityDescription(
        key="cpu1_temperature",
        value_key="cpu1_tempC",
        name="CPU1 Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    MetricsSensorEntityDescription(
        key="cpu2_temperature",
        value_key="cpu2_tempC",
        name="CPU2 Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    MetricsSensorEntityDescription(
        key="optic_temperature",
        value_key="optic_tempC",
        name="Optic Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    MetricsSensorEntityDescription(
        key="tx_bias",
        value_key="tx_bias_mA",
        name="TX Bias Current",
        native_unit_of_measurement="mA",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    MetricsSensorEntityDescription(
        key="module_voltage",
        value_key="module_voltage",
        name="Module Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 8311 metric sensors."""
    coordinator: MetricsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MetricsSensor(coordinator, entry, description) for description in SENSOR_DESCRIPTIONS)


class MetricsSensor(CoordinatorEntity[MetricsCoordinator], SensorEntity):
    """A sensor backed by the metrics coordinator."""

    entity_description: MetricsSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MetricsCoordinator,
        entry: ConfigEntry,
        description: MetricsSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        device_id = entry.unique_id or entry.entry_id
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "manufacturer": "8311 Community",
            "model": "Unauthenticated metrics endpoint",
            "name": entry.title,
        }

    @property
    def native_value(self) -> float | int | None:
        """Return the current metric value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.value_key)
