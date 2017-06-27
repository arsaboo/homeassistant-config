"""
Camera that highlights the detected regions from the opencv image processor
"""
import asyncio
import io
import logging
import os

import voluptuous as vol

from homeassistant.const import CONF_NAME
from homeassistant.components.camera import Camera, PLATFORM_SCHEMA
from homeassistant.helpers import config_validation as cv
from homeassistant.components.image_processing.opencv import ATTR_MATCHES
from homeassistant.loader import get_component

_LOGGER = logging.getLogger(__name__)

ATTR_CAMERA = 'camera_entity'
ATTR_PROCESSOR = 'processor_entity'

CONF_CAMERA = 'camera'
CONF_COLOR = 'color'
CONF_PROCESSOR = 'processor'
CONF_CLASSIFIER = 'classifier'

DEFAULT_COLOR = (255, 255, 0)
DEFAULT_NAME = 'OpenCV'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_CAMERA): cv.entity_id,
    vol.Required(CONF_PROCESSOR): cv.entity_id,
    vol.Optional(CONF_CLASSIFIER, default=None): cv.string,
    vol.Optional(CONF_COLOR, default=DEFAULT_COLOR): (int, int, int)
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the OpenCV camera platform."""
    add_devices([OpenCVCamera(hass, config.get(CONF_NAME, DEFAULT_NAME),
                             config[CONF_CAMERA], config[CONF_PROCESSOR],
                             config[CONF_CLASSIFIER], config[CONF_COLOR])])


class OpenCVCamera(Camera):
    """Visual representation of opencv matched regions."""
    def __init__(self, hass, name, camera, processor, classifier, color):
        """Initialize the opencv camera."""
        super().__init__()
        self._hass = hass
        self._camera = camera
        self._processor = processor
        self._color = color
        self._name = name
        self._classifier = classifier

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name

    @property
    def state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_CAMERA: self._camera,
            ATTR_PROCESSOR: self._processor
        }

    @asyncio.coroutine
    def async_camera_image(self):
        """Return the camera image still."""
        from PIL import Image, ImageDraw

        camera = get_component('camera')
        image = None
        processor = self._hass.states.get(self._processor)

        try:
            image = yield from camera.async_get_image(
                self._hass, self._camera, timeout=2)

        except HomeAssistantError as err:
            _LOGGER.error("Error on receive image from entity: %s", err)
            return

        matches = processor.attributes.get(ATTR_MATCHES)
        regions = []
        if self._classifier is None:
            for key, value in matches.items():
                for region in value:
                    regions.append(region)
        elif self._classifier in matches:
            for region in matches[self._classifier]:
                regions.append(region)
        else:
            _LOGGER.error("Cannot locate classifier %s", self._classifier)
            return
        if len(regions) == 0:
            return image


        stream = io.BytesIO(image)
        im = Image.open(stream)
        annotated_image = ImageDraw.Draw(im)
        for region in regions:
            x0 = region[0]
            y0 = region[1]
            x1 = x0 + region[2]
            y1 = y0 + region[2]
            annotated_image.rectangle([x0, y0, x1, y1],
                                      outline=self._color)

        image_bytes = io.BytesIO()
        im.save(image_bytes, format='PNG')
        return image_bytes.getvalue()
