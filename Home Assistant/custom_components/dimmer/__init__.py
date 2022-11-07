import logging
import voluptuous as vol
import datetime

from datetime import timedelta
from typing import Any, Optional

from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON, SERVICE_TOGGLE
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA, PLATFORM_SCHEMA_BASE

logger = logging.getLogger(__name__)

DOMAIN = "dimmer"
SCAN_INTERVAL = timedelta(seconds=30)

DEVICE_CLASS_LIGHT = "light"

DEVICE_CLASSES = [DEVICE_CLASS_LIGHT]

async def async_setup(hass, config):
    component = hass.data[DOMAIN] = EntityComponent(logger, DOMAIN, hass, SCAN_INTERVAL)
    await component.async_setup(config)

    #component.async_register_entity_service(SERVICE_TURN_OFF, {}, "async_turn_off")
    #component.async_register_entity_service(SERVICE_TURN_ON, {}, "async_turn_on")
    #component.async_register_entity_service(SERVICE_TOGGLE, {}, "async_toggle")

    return True


async def async_setup_entry(hass, entry):
    return await hass.data[DOMAIN].async_setup_entry(entry)


async def async_unload_entry(hass, entry):
    return await hass.data[DOMAIN].async_unload_entry(entry)


class DimmerEntity(ToggleEntity):
    @property
    def level(self):
        return None

    async def async_set_level(self, **kwargs):
        return None
