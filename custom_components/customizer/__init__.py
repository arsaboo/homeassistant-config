"""Customizer component. Bring extra customize features to home-assistant."""

import asyncio
import logging
import os

import homeassistant.components.frontend as frontend
import homeassistant.helpers.config_validation as cv
from homeassistant.config import load_yaml_config_file, DATA_CUSTOMIZE
from homeassistant.core import callback

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.const import CONF_ENTITY_ID, MINOR_VERSION

import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'customizer'
DEPENDENCIES = ['frontend']

CONF_PANEL = 'panel'
CONF_CUSTOM_UI = 'custom_ui'

LOCAL = 'local'
HOSTED = 'hosted'

CONF_HIDE_CUSTOMUI_ATTRIBUTES = 'hide_customui_attributes'
CONF_HIDE_ATTRIBUTES = 'hide_attributes'

CONF_ATTRIBUTE = 'attribute'
CONF_VALUE = 'value'

SERVICE_SET_ATTRIBUTE = 'set_attribute'
SERVICE_SET_ATTRIBUTE_SCHEMA = vol.Schema({
    vol.Required(CONF_ENTITY_ID): cv.entity_id,
    vol.Required(CONF_ATTRIBUTE): cv.string,
    vol.Optional(CONF_VALUE): cv.match_all,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_PANEL): cv.boolean,
        vol.Optional(CONF_CUSTOM_UI): cv.string,
        vol.Optional(CONF_HIDE_CUSTOMUI_ATTRIBUTES, default=True): cv.boolean,
        vol.Optional(CONF_HIDE_ATTRIBUTES):
            vol.All(cv.ensure_list, [cv.string]),
    })
}, extra=vol.ALLOW_EXTRA)


@callback
def maybe_load_panel(hass, conf_panel):
    """Maybe load CustomUI panel. Async friendly."""
    if conf_panel is True and MINOR_VERSION <= 52:
        frontend.register_panel(
            hass,
            "custom-ui",
            hass.config.path('panels/ha-panel-custom-ui.html'),
            sidebar_title="Custom UI",
            sidebar_icon="mdi:domain"
        )
    elif conf_panel is not None:
        _LOGGER.error('%s setting is deprecated.'
                      'Starting from HA 0.53 it is auto-added to config panel',
                      CONF_PANEL)


@asyncio.coroutine
def async_setup(hass, config):
    """Set up customizer."""
    maybe_load_panel(hass, config[DOMAIN].get(CONF_PANEL))

    custom_ui = config[DOMAIN].get(CONF_CUSTOM_UI)
    if MINOR_VERSION < 53 and custom_ui is not None:
        _LOGGER.warning('%s is only supported from Home Assistant 0.53',
                        CONF_CUSTOM_UI)
    elif custom_ui is not None:
        if custom_ui == LOCAL:
            frontend.add_extra_html_url(
                hass,
                '/local/custom_ui/state-card-custom-ui.html')
        elif custom_ui == HOSTED:
            frontend.add_extra_html_url(
                hass,
                'https://raw.githubusercontent.com/andrey-git/'
                'home-assistant-custom-ui/master/state-card-custom-ui.html')
        else:
            frontend.add_extra_html_url(
                hass,
                'https://github.com/andrey-git/home-assistant-custom-ui/'
                'releases/download/{}/state-card-custom-ui.html'
                .format(custom_ui))

    component = EntityComponent(_LOGGER, DOMAIN, hass)
    if not config[DOMAIN][CONF_HIDE_CUSTOMUI_ATTRIBUTES]:
        if MINOR_VERSION >= 53:
            _LOGGER.error(
                '%s is deprecated. '
                'Starting from HA 0.53 it is always treated as True',
                CONF_HIDE_CUSTOMUI_ATTRIBUTES)
    yield from component.async_add_entity(CustomizerEntity(config[DOMAIN]))

    descriptions = yield from hass.async_add_job(
        load_yaml_config_file, os.path.join(
            os.path.dirname(__file__), 'services.yaml'))

    @callback
    def set_attribute(call):
        """Set attribute override."""
        data = call.data
        entity_id = data[CONF_ENTITY_ID]
        attribute = data[CONF_ATTRIBUTE]
        value = data.get(CONF_VALUE)
        overrides = hass.data[DATA_CUSTOMIZE].get(entity_id)
        state = hass.states.get(entity_id)
        state_attributes = dict(state.attributes)
        if value is None:
            if attribute in overrides:
                overrides.pop(attribute)
            if attribute in state_attributes:
                state_attributes.pop(attribute)
        else:
            overrides[attribute] = value
            state_attributes[attribute] = value
        hass.states.async_set(entity_id, state.state, state_attributes)

    hass.services.async_register(DOMAIN, SERVICE_SET_ATTRIBUTE,
                                 set_attribute,
                                 descriptions[SERVICE_SET_ATTRIBUTE],
                                 SERVICE_SET_ATTRIBUTE_SCHEMA)

    return True


class CustomizerEntity(Entity):
    """Customizer entity class."""

    def __init__(self, config):
        """Constructor that parses the config."""
        self.hide_customui_attributes = config.get(
            CONF_HIDE_CUSTOMUI_ATTRIBUTES)
        self.hide_attributes = config.get(CONF_HIDE_ATTRIBUTES)

    @property
    def hidden(self):
        """Don't show the entity."""
        return True

    @property
    def name(self):
        """Singleton name."""
        return DOMAIN

    @property
    def state_attributes(self):
        """Return the state attributes."""
        result = {}
        if self.hide_customui_attributes:
            result[CONF_HIDE_CUSTOMUI_ATTRIBUTES] = True
        if self.hide_attributes:
            result[CONF_HIDE_ATTRIBUTES] = self.hide_attributes
        return result
