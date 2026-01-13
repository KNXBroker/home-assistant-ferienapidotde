"""
Utilizes the api `ferien-api.de` to provide a binary sensor to indicate if
today is a german vacational day or not - based on your configured state.

For more details about this platform, please refer to the documentation at
https://github.com/HazardDede/home-assistant-ferienapidotde
"""

import logging
from datetime import datetime, timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.exceptions import PlatformNotReady
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

ALL_STATE_CODES = [
    "BW",
    "BY",
    "BE",
    "BB",
    "HB",
    "HH",
    "HE",
    "MV",
    "NI",
    "NW",
    "RP",
    "SL",
    "SN",
    "ST",
    "SH",
    "TH",
]

ATTR_DAYS_OFFSET = "days_offset"
ATTR_START = "start"
ATTR_END = "end"
ATTR_NEXT_START = "next_start"
ATTR_NEXT_END = "next_end"
ATTR_VACATION_NAME = "vacation_name"

CONF_DAYS_OFFSET = "days_offset"
CONF_STATE = "state_code"

DEFAULT_DAYS_OFFSET = 0
DEFAULT_NAME = "Vacation Sensor"

ICON_OFF_DEFAULT = "mdi:calendar-remove"
ICON_ON_DEFAULT = "mdi:calendar-check"

# Don't rush the api. Every 12h should suffice.
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=12)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_DAYS_OFFSET, default=DEFAULT_DAYS_OFFSET):
            vol.Coerce(int),
        vol.Required(CONF_STATE): vol.In(ALL_STATE_CODES),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_platform(
        hass, config, async_add_entities, discovery_info=None
):
    """Setups the ferienapidotde platform."""
    _, _ = hass, discovery_info  # Fake usage
    days_offset = config.get(CONF_DAYS_OFFSET)
    state_code = config.get(CONF_STATE)
    name = config.get(CONF_NAME)

    try:
        # GEÄNDERT: hass wird nun an VacationData übergeben
        data_object = VacationData(hass, state_code)
        await data_object.async_update()
    except Exception as ex:
        import traceback

        _LOGGER.warning(traceback.format_exc())
        raise PlatformNotReady() from ex

    async_add_entities([VacationSensor(name, days_
