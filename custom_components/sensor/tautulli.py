"""
Support for getting statistical data from a Tautulli system.


"""
import logging
import json
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, CONF_HOST, CONF_SSL, CONF_VERIFY_SSL, CONF_TOKEN, CONF_MONITORED_CONDITIONS)

_LOGGER = logging.getLogger(__name__)
_ENDPOINT = '/api/v2'

DEFAULT_HOST = 'localhost'
DEFAULT_NAME = 'Tautulli'
DEFAULT_SSL = False
DEFAULT_VERIFY_SSL = True

SCAN_INTERVAL = timedelta(minutes=1)

MONITORED_CONDITIONS = {
    'stream_count': ['Total',
                     'streams', 'mdi:basket-unfill'],
    'stream_count_transcode': ['Transcode',
                               'streams', 'mdi:basket-unfill'],
    'stream_count_direct_play': ['Direct Play',
                                 'streams', 'mdi:basket-unfill'],
    'stream_count_direct_stream': ['Direct Stream',
                                   'streams', 'mdi:basket-unfill'],
    'total_bandwidth': ['Total Bandwidth',
                        'Mbps', 'mdi:basket-unfill'],


}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
    vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): cv.boolean,
    vol.Optional(CONF_TOKEN): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=MONITORED_CONDITIONS):
    vol.All(cv.ensure_list, [vol.In(MONITORED_CONDITIONS)]),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Tautulli sensor."""
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    use_ssl = config.get(CONF_SSL)
    token = config.get(CONF_TOKEN)
    verify_ssl = config.get(CONF_VERIFY_SSL)

    api = TautulliAPI('{}'.format(host), use_ssl, verify_ssl, token)

    sensors = [TautulliSensor(hass, api, name, condition)
               for condition in config[CONF_MONITORED_CONDITIONS]]

    add_devices(sensors, True)


class TautulliSensor(Entity):
    """Representation of a Tautulli sensor."""

    def __init__(self, hass, api, name, variable):
        """Initialize a Tautulli sensor."""
        self._hass = hass
        self._api = api
        self._name = name
        self._var_id = variable

        variable_info = MONITORED_CONDITIONS[variable]
        self._var_name = variable_info[0]
        self._var_units = variable_info[1]
        self._var_icon = variable_info[2]

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{} {}".format(self._name, self._var_name)

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._var_icon

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._var_units

    # pylint: disable=no-member
    @property
    def state(self):
        """Return the state of the device."""
        try:
            return_value = self._api.data['response']['data'][self._var_id]
            if self._var_id == 'total_bandwidth':
                return_value = round((return_value / 1000), 2)

            return return_value
        except TypeError:
            return self._api.data['response']['data'][self._var_id]

    # pylint: disable=no-member
    @property
    def device_state_attributes(self):
        """Return the state attributes of the Tautulli."""
        attributes = {}

        if self._var_id == 'total_bandwidth':
            attributes['wan_bandwidth'] = round(
                (self._api.data['response']['data']['wan_bandwidth'] / 1000), 2)
            attributes['lan_bandwidth'] = round(
                (self._api.data['response']['data']['lan_bandwidth'] / 1000), 2)
            # attributes[ATTR_TOTAL_BANDWIDTH] = self._api.data['response']['data']['total_bandwidth']
        else:
            for session in self._api.data['response']['data']['sessions']:
                if self._var_id == 'stream_count':
                    attributes[session['friendly_name']
                               ] = session['full_title']
                elif self._var_id == 'stream_count_transcode' and session['transcode_decision'] == "transcode":
                    attributes[session['friendly_name']
                               ] = session['full_title']
                elif self._var_id == 'stream_count_direct_stream' and session['transcode_decision'] == "copy":
                    attributes[session['friendly_name']
                               ] = session['full_title']
                elif self._var_id == 'stream_count_direct_play' and session['transcode_decision'] == "direct play":
                    attributes[session['friendly_name']
                               ] = session['full_title']

        return attributes

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._api.available

    def update(self):
        """Get the latest data from the Tautulli API."""
        self._api.update()


class TautulliAPI(object):
    """Get the latest data and update the states."""

    def __init__(self, host, use_ssl, verify_ssl, token):
        """Initialize the data object."""
        from homeassistant.components.sensor.rest import RestData

        uri_scheme = 'https://' if use_ssl else 'http://'
        resource = "{}{}{}?cmd=get_activity&apikey={}".format(
            uri_scheme, host, _ENDPOINT, token)

        self._rest = RestData('GET', resource, None, None, None, verify_ssl)
        self.data = None
        self.available = True
        self.update()

    def update(self):
        """Get the latest data from the Tautulli."""
        try:
            self._rest.update()
            self.data = json.loads(self._rest.data)
            self.available = True
        except TypeError:
            _LOGGER.error("Unable to fetch data from Tautulli")
            self.available = False
