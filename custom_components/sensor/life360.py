"""
@ Author      : Suresh Kalavala
@ Date        : 05/24/2017
@ Description : Life360 Sensor - It queries Life360 API and retrieves
                data at a specified interval and dumpt into MQTT

@ Notes:        Copy this file and place it in your
                "Home Assistant Config folder\custom_components\sensor\" folder
                Copy corresponding Life360 Package frommy repo,
                and make sure you have MQTT installed and Configured
                Make sure the life360 password don't contain '#' or '$' symbols
"""

from datetime import timedelta
import logging
import subprocess
import json

import voluptuous as vol
import homeassistant.components.mqtt as mqtt

from io import StringIO
from homeassistant.components.mqtt import (CONF_STATE_TOPIC, CONF_COMMAND_TOPIC, CONF_QOS, CONF_RETAIN)
from homeassistant.helpers import template
from homeassistant.exceptions import TemplateError
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, CONF_VALUE_TEMPLATE, CONF_UNIT_OF_MEASUREMENT,
    STATE_UNKNOWN)
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['mqtt']

DEFAULT_NAME = 'Life360 Sensor'
CONST_MQTT_TOPIC = "mqtt_topic"
CONST_STATE_ERROR = "error"
CONST_STATE_RUNNING = "running"
CONST_USERNAME = "username"
CONST_PASSWORD = "password"

COMMAND1 = "curl -s -X POST -H \"Authorization: Basic cFJFcXVnYWJSZXRyZTRFc3RldGhlcnVmcmVQdW1hbUV4dWNyRUh1YzptM2ZydXBSZXRSZXN3ZXJFQ2hBUHJFOTZxYWtFZHI0Vg==\" -F \"grant_type=password\" -F \"username=USERNAME360\" -F \"password=PASSWORD360\" https://api.life360.com/v3/oauth2/token.json | grep -Po '(?<=\"access_token\":\")\\w*'"
COMMAND2 = "curl -s -X GET -H \"Authorization: Bearer ACCESS_TOKEN\" https://api.life360.com/v3/circles.json | grep -Po '(?<=\"id\":\")[\\w-]*'"
COMMAND3 = "curl -s -X GET -H \"Authorization: Bearer ACCESS_TOKEN\" https://api.life360.com/v3/circles/ID"

SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONST_USERNAME): cv.string,
    vol.Required(CONST_PASSWORD): cv.string,
    vol.Required(CONST_MQTT_TOPIC): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string,
    vol.Optional(CONF_VALUE_TEMPLATE): cv.template,
})

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Life360 Sensor."""
    name = config.get(CONF_NAME)
    username = config.get(CONST_USERNAME)
    password = config.get(CONST_PASSWORD)
    mqtt_topic = config.get(CONST_MQTT_TOPIC)

    unit = config.get(CONF_UNIT_OF_MEASUREMENT)
    value_template = config.get(CONF_VALUE_TEMPLATE)
    if value_template is not None:
        value_template.hass = hass

    data = Life360SensorData(username, password, COMMAND1, COMMAND2, COMMAND3, mqtt_topic, hass)

    add_devices([Life360Sensor(hass, data, name, unit, value_template)])


class Life360Sensor(Entity):
    """Representation of a sensor."""

    def __init__(self, hass, data, name, unit_of_measurement, value_template):
        """Initialize the sensor."""
        self._hass = hass
        self.data = data
        self._name = name
        self._state = STATE_UNKNOWN
        self._unit_of_measurement = unit_of_measurement
        self._value_template = value_template
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    def update(self):
        """Get the latest data and updates the state."""
        self.data.update()
        value = self.data.value

        if value is None:
            value = STATE_UNKNOWN
        elif self._value_template is not None:
            self._state = self._value_template.render_with_possible_json_value(
                value, STATE_UNKNOWN)
        else:
            self._state = value


class Life360SensorData(object):
    """The class for handling the data retrieval."""

    def __init__(self, username, password, command1, command2, command3, mqtt_topic, hass):
        """Initialize the data object."""
        self.username = username
        self.password = password
        self.COMMAND_ACCESS_TOKEN = command1
        self.COMMAND_ID = command2
        self.COMMAND_MEMBERS = command3
        self.hass = hass
        self.value = None
        self.mqtt_topic = mqtt_topic
        self.mqtt_retain = True
        self.mqtt_qos = 0

    def update(self):

        try:
            """ Prepare and Execute Commands """
            self.COMMAND_ACCESS_TOKEN = self.COMMAND_ACCESS_TOKEN.replace("USERNAME360", self.username)
            self.COMMAND_ACCESS_TOKEN = self.COMMAND_ACCESS_TOKEN.replace("PASSWORD360", self.password)
            access_token = self.exec_shell_command( self.COMMAND_ACCESS_TOKEN )

            if access_token == None:
                self.value = CONST_STATE_ERROR
                return None

            self.COMMAND_ID = self.COMMAND_ID.replace("ACCESS_TOKEN", access_token)
            id = self.exec_shell_command( self.COMMAND_ID )

            if id == None:
                self.value = CONST_STATE_ERROR
                return None

            self.COMMAND_MEMBERS = self.COMMAND_MEMBERS.replace("ACCESS_TOKEN", access_token)
            self.COMMAND_MEMBERS = self.COMMAND_MEMBERS.replace("ID", id)
            payload = self.exec_shell_command( self.COMMAND_MEMBERS )

            if payload != None:
                self.save_payload_to_mqtt ( self.mqtt_topic, payload )
                data = json.loads ( payload )
                for member in data["members"]:
                    topic = StringBuilder()
                    topic.Append("owntracks/")
                    topic.Append(member["firstName"].lower())
                    topic.Append("/")
                    topic.Append(member["firstName"].lower())
                    topic = topic

                    msgPayload = StringBuilder()
                    msgPayload.Append("{")
                    msgPayload.Append("\"t\":\"p\"")
                    msgPayload.Append(",")

                    msgPayload.Append("\"tst\":")
                    msgPayload.Append(member['location']['timestamp'])
                    msgPayload.Append(",")

                    msgPayload.Append("\"acc\":")
                    msgPayload.Append(member['location']['accuracy'])
                    msgPayload.Append(",")

                    msgPayload.Append("\"_type\":\"location\"")
                    msgPayload.Append(",")

                    msgPayload.Append("\"alt\":\"0\"")
                    msgPayload.Append(",")

                    msgPayload.Append("\"_cp\":\"false\"")
                    msgPayload.Append(",")

                    msgPayload.Append("\"lon\":")
                    msgPayload.Append(member['location']['longitude'])
                    msgPayload.Append(",")

                    msgPayload.Append("\"lat\":")
                    msgPayload.Append(member['location']['latitude'])
                    msgPayload.Append(",")

                    msgPayload.Append("\"batt\":")
                    msgPayload.Append(member['location']['battery'])
                    msgPayload.Append(",")

                    if str(member['location']['wifiState']) == "1":
                        msgPayload.Append("\"conn\":\"w\"")
                        msgPayload.Append(",")

                    msgPayload.Append("\"vel\":")
                    msgPayload.Append(str(member['location']['speed']))
                    msgPayload.Append(",")

                    msgPayload.Append("\"charging\":")
                    msgPayload.Append(member['location']['charge'])
                    msgPayload.Append("}")

                    self.save_payload_to_mqtt ( str(topic), str(msgPayload) )
                self.value = CONST_STATE_RUNNING
            else:
                self.value = CONST_STATE_ERROR

        except Exception as e:
            self.value = CONST_STATE_ERROR

    def exec_shell_command( self, command ):

        output = None
        try:
            output = subprocess.check_output( command, shell=True, timeout=60 )
            output = output.strip().decode('utf-8')

        except subprocess.CalledProcessError:
            """ _LOGGER.error("Command failed: %s", command)"""
            self.value = CONST_STATE_ERROR
            output = None
        except subprocess.TimeoutExpired:
            """ _LOGGER.error("Timeout for command: %s", command)"""
            self.value = CONST_STATE_ERROR
            output = None

        if output == None:
            _LOGGER.error( "Life360 has not responsed well. Nothing to worry, will try again!" )
            self.value = CONST_STATE_ERROR
            return None
        else:
            return output

    def save_payload_to_mqtt( self, topic, payload ):

        try:
            """mqtt.async_publish ( self.hass, topic, payload, self.mqtt_qos, self.mqtt_retain )"""
            _LOGGER.info("topic: %s", topic)
            _LOGGER.info("payload: %s", payload)
            mqtt.publish ( self.hass, topic, payload, self.mqtt_qos, self.mqtt_retain )

        except:
            _LOGGER.error( "Error saving Life360 data to mqtt." )

class StringBuilder:
     _file_str = None

     def __init__(self):
         self._file_str = StringIO()

     def Append(self, str):
         self._file_str.write(str)

     def __str__(self):
         return self._file_str.getvalue()
