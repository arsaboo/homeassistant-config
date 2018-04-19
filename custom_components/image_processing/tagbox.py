"""
Component that will search images for tagged objects via a local
machinebox instance.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.tagbox
"""
import base64
import requests
import logging
import time
import voluptuous as vol

from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.components.image_processing import (
    PLATFORM_SCHEMA, ImageProcessingEntity, CONF_SOURCE, CONF_ENTITY_ID,
    CONF_NAME, DOMAIN)

_LOGGER = logging.getLogger(__name__)

CONF_ENDPOINT = 'endpoint'
CONF_TAGS = 'tags'
ROUNDING_DECIMALS = 2

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ENDPOINT): cv.string,
    vol.Optional(CONF_TAGS, default=[]):
        vol.All(cv.ensure_list, [cv.string]),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(Tagbox(
            camera.get(CONF_NAME),
            config[CONF_ENDPOINT],
            camera[CONF_ENTITY_ID],
            config[CONF_TAGS],
        ))
    add_devices(entities)


class Tagbox(ImageProcessingEntity):
    """Perform a tag search via a Tagbox."""

    def __init__(self, name, endpoint, camera_entity, tags):
        """Init with the API key and model id"""
        super().__init__()
        if name:  # Since name is optional.
            self._name = name
        else:
            self._name = "Tagbox {0}".format(
                split_entity_id(camera_entity)[1])
        self._camera = camera_entity
        self._default_tags = {tag: 0.0 for tag in tags}
        self._tags = self._default_tags
        self._url = "http://{}/tagbox/check".format(endpoint)
        self._state = "no_processing_performed"
        self._response_time = None

    def process_image(self, image):
        """Process an image."""
        timer_start = time.perf_counter()
        try:
            response = requests.post(
                self._url,
                json=self.encode_image(image)
                ).json()
        except:
            response = {'success': False}

        if response['success']:
            elapsed_time = time.perf_counter() - timer_start
            self._response_time = round(elapsed_time, ROUNDING_DECIMALS)
            self._tags, self._state = self.process_response(response)
        else:
            self._state = "Request_failed"
            self._tags = self._default_tags

    def encode_image(self, image):
        """base64 encode an image stream."""
        base64_img = base64.b64encode(image).decode('ascii')
        return {"base64": base64_img}

    def process_response(self, response):
        """Process response data, returning the processed tags and state."""
        tags = self._default_tags.copy()
        tags.update(self.process_tags(response['tags']))
        if response['custom_tags']:
            tags.update(self.process_tags(response['custom_tags']))
        # Default tags have probability 0.0 and cause an exception.
        try:
            state = max(tags.keys(), key=(lambda k: tags[k]))
        except:
            state = "No_tags_identified"
        return tags, state

    def process_tags(self, tags_data):
        """Process tags data, returning the tag and rounded confidence."""
        processed_tags = {
            tag['tag'].lower(): round(tag['confidence'], ROUNDING_DECIMALS)
            for tag in tags_data
            }
        return processed_tags

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def device_state_attributes(self):
        """Return other details about the sensor state."""
        attr = self._tags.copy()
        attr.update({'response_time': self._response_time})
        return attr

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
