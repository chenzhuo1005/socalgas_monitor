# """The socalgas_sync integration."""
# import logging

# from homeassistant.helpers import discovery
# from .const import (
#     DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_INTERVAL, DEFAULT_INTERVAL
# )

# _LOGGER = logging.getLogger(__name__)

# async def async_setup(hass, config):
#     """Set up the socalgas_sync component from YAML configuration."""
#     conf = config.get(DOMAIN)
#     if conf is None:
#         _LOGGER.debug("No %s configuration found, skipping setup", DOMAIN)
#         return True

#     hass.data[DOMAIN] = {
#         CONF_USERNAME: conf[CONF_USERNAME],
#         CONF_PASSWORD: conf[CONF_PASSWORD],
#         CONF_INTERVAL: conf.get(CONF_INTERVAL, DEFAULT_INTERVAL),
#     }

#     # Load the sensor platform
#     discovery.load_platform(hass, "sensor", DOMAIN, {}, config)
#     _LOGGER.info("SoCalGas Sync integration loaded")
#     return True
