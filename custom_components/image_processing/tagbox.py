"""
Search images for tagged objects via a local Tagbox instance.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.tagbox
"""
import base64
import requests
import logging
import voluptuous as vol

from homeassistant.core import (
    callback, split_entity_id)
import homeassistant.helpers.config_validation as cv
from homeassistant.components.image_processing import (
    PLATFORM_SCHEMA, ImageProcessingEntity, ATTR_CONFIDENCE, CONF_CONFIDENCE,
    CONF_SOURCE, CONF_ENTITY_ID, CONF_NAME)
from homeassistant.const import (
    ATTR_ENTITY_ID, ATTR_NAME, CONF_IP_ADDRESS, CONF_PORT)
from homeassistant.util.async_ import run_callback_threadsafe

_LOGGER = logging.getLogger(__name__)

CLASSIFIER = 'tagbox'
EVENT_DETECT_TAG = 'image_processing.detect_tag'
TIMEOUT = 9

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_PORT): cv.port,
})


def encode_image(image):
    """base64 encode an image stream."""
    base64_img = base64.b64encode(image).decode('ascii')
    return base64_img


def get_matched_tags(tags, confidence):
    """Return the name and rounded confidence of matched tags."""
    return {tag['name']: tag['confidence']
            for tag in tags if tag['confidence'] > confidence}


def parse_tags(api_tags):
    """Parse the API tag data into the format required."""
    parsed_tags = []
    for entry in api_tags:
        tag = {}
        tag[ATTR_NAME] = entry['tag']
        tag[ATTR_CONFIDENCE] = round(100.0*entry['confidence'], 2)
        parsed_tags.append(tag)
    return parsed_tags


def post_image(url, image):
    """Post an image to the classifier."""
    try:
        response = requests.post(
            url,
            json={"base64": encode_image(image)},
            timeout=TIMEOUT
            )
        return response
    except requests.exceptions.ConnectionError:
        _LOGGER.error("ConnectionError: Is %s running?", CLASSIFIER)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(ImageProcessingTagEntity(
            config[CONF_IP_ADDRESS],
            config[CONF_PORT],
            camera[CONF_ENTITY_ID],
            camera.get(CONF_NAME),
            config[CONF_CONFIDENCE],
        ))
    add_devices(entities)


class ImageProcessingTagEntity(ImageProcessingEntity):
    """Perform a tag search via a Tagbox."""

    def __init__(self, ip, port, camera_entity, name, confidence):
        """Init with the IP and PORT"""
        super().__init__()
        self._url_check = "http://{}:{}/{}/check".format(ip, port, CLASSIFIER)
        self._camera = camera_entity
        if name:
            self._name = name
        else:
            camera_name = split_entity_id(camera_entity)[1]
            self._name = "{} {}".format(
                CLASSIFIER, camera_name)
        self._confidence = confidence
        self.tags = []
        self._matched = {}

    def process_image(self, image):
        """Process an image."""
        response = post_image(self._url_check, image)
        if response is not None:
            response_json = response.json()
            if response_json['success']:
                api_tags = response_json['tags'] + response_json['custom_tags']
                tags = parse_tags(api_tags)
                self.process_tags(tags)
                self._matched = get_matched_tags(tags, self.confidence)
        else:
            self.tags = []
            self._matched = {}

    @property
    def confidence(self):
        """Return minimum confidence for send events."""
        return self._confidence

    @property
    def state(self):
        """Return the state of the entity."""
        state = None

        if len(self._matched) > 0:
            return self.tags[0][ATTR_NAME]

        return state

    def process_tags(self, tags):
        """Send event with detected tags and store data."""
        run_callback_threadsafe(
            self.hass.loop, self.async_process_tags, tags).result()

    @callback
    def async_process_tags(self, tags):
        """Send event with detected tags and store data.
        Tags are a dict in follow format:
         [
           {
              ATTR_CONFIDENCE: 80,
              ATTR_NAME: 'people',
           },
         ]
        This method must be run in the event loop.
        """
        # Send events
        for tag in tags:
            tag.update({ATTR_ENTITY_ID: self.entity_id})
            if tag[ATTR_CONFIDENCE] > self.confidence:
                self.hass.async_add_job(
                    self.hass.bus.async_fire, EVENT_DETECT_TAG, tag
                )

        # Update entity store
        self.tags = tags

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return other details about the sensor state."""
        return {
            'tags': self.tags,
            'total_tags': len(self.tags),
            'matched_tags': self._matched,
            'total_matched_tags': len(self._matched),
            }
