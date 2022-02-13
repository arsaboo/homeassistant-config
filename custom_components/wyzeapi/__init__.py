"""The Wyze Home Assistant Integration."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.check_config import HomeAssistantConfig
from wyzeapy import Wyzeapy
from wyzeapy.wyze_auth_lib import Token

from .const import DOMAIN, CONF_CLIENT, ACCESS_TOKEN, REFRESH_TOKEN, REFRESH_TIME, WYZE_NOTIFICATION_TOGGLE
from .token_manager import TokenManager

PLATFORMS = [
    "light",
    "switch",
    "lock",
    "climate",
    "alarm_control_panel",
    "sensor"
]  # Fixme: Re add scene
_LOGGER = logging.getLogger(__name__)


# noinspection PyUnusedLocal
async def async_setup(
        hass: HomeAssistant, config: HomeAssistantConfig, discovery_info=None
):
    # pylint: disable=unused-argument
    """Set up the WyzeApi domain."""
    if hass.config_entries.async_entries(DOMAIN):
        _LOGGER.debug(
            "Nothing to import from configuration.yaml, loading from Integrations",
        )
        return True

    # noinspection SpellCheckingInspection
    domainconfig = config.get(DOMAIN)
    # pylint: disable=logging-not-lazy
    _LOGGER.debug(
        "Importing config information for %s from configuration.yml"
        % domainconfig[CONF_USERNAME]
    )
    if hass.config_entries.async_entries(DOMAIN):
        _LOGGER.debug("Found existing config entries")
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry:
                entry_data = entry.as_dict().get("data")
                hass.config_entries.async_update_entry(
                    entry,
                    data=entry_data,
                )
                break
    else:
        _LOGGER.debug("Creating new config entry")
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data={
                    CONF_USERNAME: domainconfig[CONF_USERNAME],
                    CONF_PASSWORD: domainconfig[CONF_PASSWORD],
                    ACCESS_TOKEN: domainconfig[ACCESS_TOKEN],
                    REFRESH_TOKEN: domainconfig[REFRESH_TOKEN],
                    REFRESH_TIME: domainconfig[REFRESH_TIME],
                },
            )
        )
    return True


# noinspection DuplicatedCode
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Wyze Home Assistant Integration from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    client = await Wyzeapy.create()
    token = None
    if config_entry.data.get(ACCESS_TOKEN):
        token = Token(
            config_entry.data.get(ACCESS_TOKEN),
            config_entry.data.get(REFRESH_TOKEN),
            float(config_entry.data.get(REFRESH_TIME)),
        )
    a_tkn_manager = TokenManager(hass, config_entry)
    client.register_for_token_callback(a_tkn_manager.token_callback)
    # We should probably try/catch here to invalidate the login credentials and throw a notification if we cannot get
    # a login with the token
    try:
        await client.login(
            config_entry.data.get(CONF_USERNAME),
            config_entry.data.get(CONF_PASSWORD),
            token,
        )
    except Exception as e:
        _LOGGER.error("Wyzeapi: Could not login. Please re-login through integration configuration")
        _LOGGER.error(e)
        raise ConfigEntryAuthFailed("Unable to login, please re-login.") from None

    hass.data[DOMAIN][config_entry.entry_id] = {CONF_CLIENT: client}

    for platform in PLATFORMS:
        hass.create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    mac_addresses = await client.unique_device_ids

    mac_addresses.add(WYZE_NOTIFICATION_TOGGLE)

    hms_service = await client.hms_service
    hms_id = hms_service.hms_id
    if hms_id is not None:
        mac_addresses.add(hms_id)

    device_registry = await dr.async_get_registry(hass)
    for device in dr.async_entries_for_config_entry(
            device_registry, config_entry.entry_id
    ):
        for identifier in device.identifiers:
            # domain has to remain here. If it is removed the integration will remove all entities for not being in
            # the mac address list each boot.
            domain, mac = identifier
            if mac not in mac_addresses:
                _LOGGER.warning(
                    '%s is not in the mac_addresses list, removing the entry', mac
                )
                device_registry.async_remove_device(device.id)
    return True


async def options_update_listener(
        hass: HomeAssistant, config_entry: ConfigEntry
):
    """Handle options update."""
    _LOGGER.debug("Updated options")
    entry_data = config_entry.as_dict().get("data")
    hass.config_entries.async_update_entry(
        config_entry,
        data=entry_data,
    )
    _LOGGER.debug("Reload entry: " + config_entry.entry_id)
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
