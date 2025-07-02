# custom_components/socalgas_monitor/sensor.py

import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import DEVICE_CLASS_GAS, STATE_CLASS_MEASUREMENT
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)
from .playwright_grabber import fetch_therms
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_INTERVAL, DEFAULT_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up two SoCalGas sensors: usage and cost."""
    conf = hass.data.get(DOMAIN)
    if not conf:
        _LOGGER.error("No configuration for %s found", DOMAIN)
        return

    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    interval = conf.get(CONF_INTERVAL, DEFAULT_INTERVAL)

    # Create a coordinator that calls fetch_therms() every `interval` minutes
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="SoCalGas",
        update_method=lambda: fetch_therms(username, password),
        update_interval=timedelta(minutes=interval),
    )

    # Do the first refresh now
    await coordinator.async_config_entry_first_refresh()

    # Create and register two sensors
    async_add_entities([
        SoCalGasUsageSensor(coordinator),
        SoCalGasCostSensor(coordinator),
    ], update_before_add=False)


class SoCalGasUsageSensor(CoordinatorEntity, SensorEntity):
    """SensorEntity for hourly usage in therms."""

    _attr_device_class = DEVICE_CLASS_GAS
    _attr_state_class = STATE_CLASS_MEASUREMENT
    _attr_native_unit_of_measurement = "therm"
    _attr_name = "SoCalGas Usage"
    _attr_unique_id = "socalgas_usage"

    def __init__(self, coordinator: DataUpdateCoordinator):
        """Initialize with a shared coordinator."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> float:
        """Return the latest usage (therms)."""
        return self.coordinator.data["usage"]

    @property
    def extra_state_attributes(self) -> dict:
        """Return the rest of the data as attributes."""
        data = self.coordinator.data
        return {
            "date":      data["date"],
            "time":      data["time"],
            "avg_temp":  data["avg_temp"],
            "timestamp": data["timestamp"].isoformat(),
        }


class SoCalGasCostSensor(CoordinatorEntity, SensorEntity):
    """SensorEntity for the cost of that usage."""

    _attr_state_class = STATE_CLASS_MEASUREMENT
    _attr_native_unit_of_measurement = "$"
    _attr_name = "SoCalGas Cost"
    _attr_unique_id = "socalgas_cost"

    def __init__(self, coordinator: DataUpdateCoordinator):
        """Initialize with a shared coordinator."""
        super().__init__(coordinator)

    @property
    def native_value(self) -> float:
        """Return the cost in dollars."""
        return round(self.coordinator.data["cost"], 2)

    @property
    def extra_state_attributes(self) -> dict:
        """Expose usage and timestamp alongside cost."""
        data = self.coordinator.data
        return {
            "usage":     data["usage"],
            "date":      data["date"],
            "time":      data["time"],
            "avg_temp":  data["avg_temp"],
            "timestamp": data["timestamp"].isoformat(),
        }
