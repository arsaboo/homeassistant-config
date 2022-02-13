"""Composite Device Tracker."""
import asyncio
import logging

import voluptuous as vol

from homeassistant.requirements import async_process_requirements, RequirementsNotFound
from homeassistant.components.device_tracker import DOMAIN as DT_DOMAIN
from homeassistant.const import CONF_PLATFORM
import homeassistant.helpers.config_validation as cv

from .const import CONF_TIME_AS, DOMAIN, TZ_DEVICE_LOCAL, TZ_DEVICE_UTC

CONF_TZ_FINDER = "tz_finder"
DEFAULT_TZ_FINDER = "timezonefinderL==4.0.2"
CONF_TZ_FINDER_CLASS = "tz_finder_class"
TZ_FINDER_CLASS_OPTS = ["TimezoneFinder", "TimezoneFinderL"]

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(DOMAIN, default=dict): vol.Schema(
            {
                vol.Optional(CONF_TZ_FINDER, default=DEFAULT_TZ_FINDER): cv.string,
                vol.Optional(
                    CONF_TZ_FINDER_CLASS, default=TZ_FINDER_CLASS_OPTS[0]
                ): vol.In(TZ_FINDER_CLASS_OPTS),
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    if any(
        conf[CONF_TIME_AS] in (TZ_DEVICE_UTC, TZ_DEVICE_LOCAL)
        for conf in (config.get(DT_DOMAIN) or [])
        if conf[CONF_PLATFORM] == DOMAIN
    ):
        pkg = config[DOMAIN][CONF_TZ_FINDER]
        try:
            asyncio.run_coroutine_threadsafe(
                async_process_requirements(
                    hass, "{}.{}".format(DOMAIN, DT_DOMAIN), [pkg]
                ),
                hass.loop,
            ).result()
        except RequirementsNotFound:
            _LOGGER.debug("Process requirements failed: %s", pkg)
            return False
        else:
            _LOGGER.debug("Process requirements suceeded: %s", pkg)

        if pkg.split("==")[0].strip().endswith("L"):
            from timezonefinderL import TimezoneFinder

            tf = TimezoneFinder()
        elif config[DOMAIN][CONF_TZ_FINDER_CLASS] == "TimezoneFinder":
            from timezonefinder import TimezoneFinder

            tf = TimezoneFinder()
        else:
            from timezonefinder import TimezoneFinderL

            tf = TimezoneFinderL()
        hass.data[DOMAIN] = tf

    return True
