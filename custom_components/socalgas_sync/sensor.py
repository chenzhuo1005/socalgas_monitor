# custom_components/socalgas_sync/sensor.py

import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import DEVICE_CLASS_GAS, STATE_CLASS_MEASUREMENT
from .playwright_grabber import fetch_therms
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_INTERVAL, DEFAULT_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the SoCalGas sensor platform."""
    conf = hass.data.get(DOMAIN)
    if not conf:
        _LOGGER.error("No configuration for %s found", DOMAIN)
        return

    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    update_interval = conf.get(CONF_INTERVAL, DEFAULT_INTERVAL)

    async_add_entities([SoCalGasThermsSensor(username, password, update_interval)], True)


class SoCalGasThermsSensor(SensorEntity):
    """Sensor that reports your latest hourly SoCalGas usage."""

    # These class attributes tell HA how to treat our sensor
    _attr_device_class = DEVICE_CLASS_GAS
    _attr_state_class = STATE_CLASS_MEASUREMENT
    _attr_native_unit_of_measurement = "therm"

    def __init__(self, username: str, password: str, interval: int):
        """Initialize the sensor with credentials and scan interval."""
        self._username = username
        self._password = password
        self._attr_name = "SoCalGas Therms"
        self._attr_unique_id = f"socalgas_therms_{username}"
        # Tell HA to call async_update() every `interval` minutes
        self._attr_scan_interval = timedelta(minutes=interval)
        # Will hold the numeric therms value
        self._attr_native_value = None
        # Will hold date, time, cost, avg_temp and timestamp
        self._attr_extra_state_attributes = {}

    async def async_update(self):
        """
        Fetch new data from SoCalGas and update state + attributes.

        fetch_therms returns a dict:
          - date (str): 'MM/DD/YYYY'
          - time (str): 'HH:MM AM/PM'
          - usage (float): Usage in therms
          - cost (float): Cost in $
          - avg_temp (float): Average temperature in °F
          - timestamp (datetime): full timestamp
        """
        try:
            data = await fetch_therms(self._username, self._password)
        except Exception as exc:
            _LOGGER.error("Error fetching SoCalGas data: %s", exc)
            return

        # Primary sensor state: hourly usage in therms
        self._attr_native_value = data["usage"]

        # Expose the rest as extra attributes
        self._attr_extra_state_attributes = {
            "date":      data["date"],
            "time":      data["time"],
            "cost":      round(data["cost"], 2),
            "avg_temp":  round(data["avg_temp"], 1),
            "timestamp": data["timestamp"].isoformat(),
        }

        _LOGGER.debug(
            "SoCalGas sensor updated: %s therms at %s",
            data["usage"], data["timestamp"]
        )
