"""Config flow for Wyze Home Assistant Integration integration."""

from __future__ import annotations

import logging
from typing import Any, Dict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_ACCESS_TOKEN
from homeassistant.exceptions import HomeAssistantError
from wyzeapy import Wyzeapy, exceptions

from .const import DOMAIN, ACCESS_TOKEN, REFRESH_TOKEN, REFRESH_TIME

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({CONF_USERNAME: str, CONF_PASSWORD: str})
STEP_2FA_DATA_SCHEMA = vol.Schema({CONF_ACCESS_TOKEN: str})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wyze Home Assistant Integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    client: Wyzeapy = None
    user_params = {}

    def __init__(self):
        """Initialize."""
        self.email = None
        self.password = None

    async def get_client(self):
        if not self.client:
            self.client = await Wyzeapy.create()

    async def async_step_user(
            self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle the initial step."""
        await self.get_client()

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        # noinspection PyBroadException
        try:
            await self.client.login(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except exceptions.TwoFactorAuthenticationEnabled:
            self.user_params[CONF_USERNAME] = user_input[CONF_USERNAME]
            self.user_params[CONF_PASSWORD] = user_input[CONF_PASSWORD]
            return await self.async_step_2fa()
        else:
            if self.hass.config_entries.async_entries(DOMAIN):
                for entry in self.hass.config_entries.async_entries(DOMAIN):
                    self.hass.config_entries.async_update_entry(entry, data=user_input)
                    await self.hass.config_entries.async_reload(entry.entry_id)
                    return self.async_abort(reason="reauth_successful")
            else:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_2fa(self, user_input: Dict[str, Any] = None) -> Dict[str, Any]:
        if user_input is None:
            return self.async_show_form(step_id="2fa", data_schema=STEP_2FA_DATA_SCHEMA)

        errors = {}

        try:
            token = await self.client.login_with_2fa(
                user_input[CONF_ACCESS_TOKEN],
            )
        except exceptions.LoginError:
            errors["base"] = "invalid_auth"
        else:
            self.user_params[ACCESS_TOKEN] = token.access_token
            self.user_params[REFRESH_TOKEN] = token.refresh_token
            self.user_params[REFRESH_TIME] = token.refresh_time
            if self.hass.config_entries.async_entries(DOMAIN):
                for entry in self.hass.config_entries.async_entries(DOMAIN):
                    self.hass.config_entries.async_update_entry(entry, data=self.user_params)
                    await self.hass.config_entries.async_reload(entry.entry_id)
                    return self.async_abort(reason="reauth_successful")
            else:
                return self.async_create_entry(title="", data=self.user_params)

        return self.async_show_form(
            step_id="2fa", data_schema=STEP_2FA_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)

    async def async_step_reauth(self, user_input=None):
        """Perform reauth upon an API authentication error."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
