"""
Search images for faces and people using sighthound.com cloud service.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.sighthound
"""
import base64
import json
import requests
import logging
import voluptuous as vol

from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.components.image_processing import (
    PLATFORM_SCHEMA, ImageProcessingEntity, CONF_SOURCE, CONF_ENTITY_ID,
    CONF_NAME)
from homeassistant.const import CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://dev.sighthoundapi.com/v1/detections"
CLASSIFIER = 'sighthound'
TIMEOUT = 9

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
})


def encode_image(image):
    """base64 encode an image stream."""
    base64_img = base64.b64encode(image).decode('ascii')
    return base64_img


def parse_api_response(response):
    """Parse the response from the API. """
    faces = []
    persons = []
    for obj in response.json()['objects']:
        if obj['type'] == 'face':
            faces.append(obj)
        if obj['type'] == 'person':
            persons.append(obj)
    return faces, persons


def post_image(url, headers, params, image):
    """Post an image to the classifier."""
    try:
        response = requests.post(
            url,
            headers=headers,
            params=params,
            data=json.dumps({"image": encode_image(image)}),
            timeout=TIMEOUT
            )
        return response
    except requests.exceptions.ConnectionError:
        _LOGGER.error("ConnectionError: Is %s reachable?", CLASSIFIER)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    entities = []
    for camera in config[CONF_SOURCE]:
        sighthound = SighthoundEntity(
            config[CONF_API_KEY],
            camera[CONF_ENTITY_ID],
            camera.get(CONF_NAME))
        entities.append(sighthound)
    add_devices(entities)


class SighthoundEntity(ImageProcessingEntity):
    """Create a sighthound entity."""

    def __init__(self, api_key, camera_entity, name):
        """Init with the IP and PORT."""
        super().__init__()
        self._url = BASE_URL
        self._headers = {"Content-type": "application/json",
                         "X-Access-Token": api_key}
        self._params = (
            ('type', 'face,person'),
            ('faceOption', 'landmark,gender'),
            )

        self._camera = camera_entity
        if name:
            self._name = name
        else:
            camera_name = split_entity_id(camera_entity)[1]
            self._name = "{} {}".format(
                CLASSIFIER, camera_name)
        self._state = None
        self.total_faces = None
        self.faces = []
        self.total_persons = None
        self.persons = []

    def process_image(self, image):
        """Process an image."""
        response = post_image(self._url,
                              self._headers,
                              self._params,
                              image)
        if response is not None:
            self.faces, self.persons = parse_api_response(response)
            self.total_faces = len(self.faces)
            self.total_persons = len(self.persons)
            self._state = self.total_persons

        else:
            self.total_faces = None
            self.faces = []
            self.total_persons = None
            self.persons = []

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the classifier attributes."""
        attr = {
            'faces': self.faces,
            'total_faces': self.total_faces,
            'persons': self.persons,
            'total_persons': self.total_persons,
            }
        return attr
