"""
Component that will perform facial detection and identification via deepstack.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.deepstack_object
"""
import base64
import logging

import requests
import voluptuous as vol

from homeassistant.const import (
    ATTR_ENTITY_ID, ATTR_NAME)
from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.components.image_processing import (
    PLATFORM_SCHEMA, ImageProcessingEntity, CONF_SOURCE,
    CONF_ENTITY_ID, CONF_NAME, DOMAIN)
from homeassistant.const import (
    CONF_IP_ADDRESS, CONF_PORT,
    HTTP_BAD_REQUEST, HTTP_OK, HTTP_UNAUTHORIZED)

_LOGGER = logging.getLogger(__name__)

CLASSIFIER = 'deepstack_object'
CONF_TARGET = 'target'
DEFAULT_TARGET = 'person'


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_PORT): cv.port,
    vol.Optional(CONF_TARGET, default=DEFAULT_TARGET): cv.string,
})


def get_object_classes(predictions):
    """
    Get a list of the unique object classes predicted.
    """
    classes = [pred['label'] for pred in predictions]
    return set(classes)


def get_object_instances(predictions, target):
    """
    Return the number of instances of a target class.
    """
    targets_identified = [
        pred for pred in predictions if pred['label'] == target]
    return len(targets_identified)


def get_objects_summary(predictions):
    """
    Get a summary of the objects detected.
    """
    classes = get_object_classes(predictions)
    return {class_cat: get_object_instances(predictions, target=class_cat)
            for class_cat in classes}


def post_image(url, image):
    """Post an image to the classifier."""
    try:
        response = requests.post(
            url,
            files={"image": image},
            )
        return response
    except requests.exceptions.ConnectionError:
        _LOGGER.error("ConnectionError: Is %s running?", CLASSIFIER)
        return None


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    ip_address = config[CONF_IP_ADDRESS]
    port = config[CONF_PORT]
    target = config[CONF_TARGET]
    entities = []
    for camera in config[CONF_SOURCE]:
        object_entity = ObjectClassifyEntity(
            ip_address, port, target,
            camera[CONF_ENTITY_ID], camera.get(CONF_NAME))
        entities.append(object_entity)
    add_devices(entities)


class ObjectClassifyEntity(ImageProcessingEntity):
    """Perform a face classification."""

    def __init__(self, ip_address, port, target, camera_entity, name=None):
        """Init with the API key and model id."""
        super().__init__()
        self._url_check = "http://{}:{}/v1/vision/detection".format(
            ip_address, port)
        self._target = target
        self._camera = camera_entity
        if name:
            self._name = name
        else:
            camera_name = split_entity_id(camera_entity)[1]
            self._name = "{} {}".format(CLASSIFIER, camera_name)
        self._state = None
        self._predictions = {}

    def process_image(self, image):
        """Process an image."""
        response = post_image(
            self._url_check, image)
        if response:
            if response.status_code == HTTP_OK:
                predictions_json = response.json()["predictions"]
                self._state = get_object_instances(
                    predictions_json, self._target)
                self._predictions = get_objects_summary(predictions_json)

        else:
            self._state = None
            self._predictions = {}

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attr = {}
        attr['target'] = self._target
        attr['predictions'] = self._predictions
        return attr
