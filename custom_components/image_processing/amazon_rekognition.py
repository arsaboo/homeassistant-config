"""
Platform that will perform object and label recognition.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing/amazon_rekognition
"""
import base64
import json
import logging

import voluptuous as vol

from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.components.image_processing import (
    PLATFORM_SCHEMA, ImageProcessingEntity, CONF_SOURCE, CONF_ENTITY_ID,
    CONF_NAME)


_LOGGER = logging.getLogger(__name__)

CONF_REGION = 'region_name'
CONF_ACCESS_KEY_ID = 'aws_access_key_id'
CONF_SECRET_ACCESS_KEY = 'aws_secret_access_key'
DEFAULT_TARGET = 'Person'

DEFAULT_REGION = 'us-east-1'
SUPPORTED_REGIONS = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
                     'ca-central-1', 'eu-west-1', 'eu-central-1', 'eu-west-2',
                     'eu-west-3', 'ap-southeast-1', 'ap-southeast-2',
                     'ap-northeast-2', 'ap-northeast-1', 'ap-south-1',
                     'sa-east-1']

REQUIREMENTS = ['boto3 == 1.9.16']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_REGION, default=DEFAULT_REGION):
        vol.In(SUPPORTED_REGIONS),
    vol.Required(CONF_ACCESS_KEY_ID): cv.string,
    vol.Required(CONF_SECRET_ACCESS_KEY): cv.string,
})


def get_label_data(response, label_string='Person'):
    """Get label data."""
    for label in response['Labels']:
        if label['Name'] == label_string:
            data = {}
            data['Confidence'] = round(label['Confidence'], 2)
            data['Instances'] = len(label['Instances'])

            bounding_boxes = []
            for instance in label['Instances']:
                bounding_boxes.append(instance['BoundingBox'])

            data['bounding_boxes'] = bounding_boxes
            return data
    return {'Instances': 0, 'Confidence': None, 'bounding_boxes': None}


def parse_labels(response):
    """Parse the response and return labels data."""
    return {label['Name']: round(label['Confidence'], 2)
            for label in response['Labels']}


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up Rekognition."""

    import boto3
    aws_config = {
        CONF_REGION: config.get(CONF_REGION),
        CONF_ACCESS_KEY_ID: config.get(CONF_ACCESS_KEY_ID),
        CONF_SECRET_ACCESS_KEY: config.get(CONF_SECRET_ACCESS_KEY),
        }
    try:
        client = boto3.client('rekognition', **aws_config)
    except Exception as exc:
        _LOGGER.error(exc)
        return

    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(Rekognition(
            client,
            DEFAULT_TARGET,
            camera[CONF_ENTITY_ID],
            camera.get(CONF_NAME),
        ))
    add_devices(entities)


class Rekognition(ImageProcessingEntity):
    """Perform object and label recognition."""

    def __init__(self, client, target, camera_entity, name=None):
        """Init with the client."""
        self._client = client
        self._target = target
        if name:  # Since name is optional.
            self._name = name
        else:
            entity_name = split_entity_id(camera_entity)[1]
            self._name = "{} {}".format('rekognition', entity_name)
        self._camera_entity = camera_entity
        self._state = None  # The number of instances of interest
        self._attributes = {}

    def process_image(self, image):
        """Process an image."""
        self._state = None
        self._attributes = {}

        try:
            response = self._client.detect_labels(Image={'Bytes': image})
            data = get_label_data(response, label_string=self._target)
            self._state = data['Instances']
            self._attributes = parse_labels(response)
        except Exception as exc:
            _LOGGER.error(exc)
            return

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera_entity

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attr = self._attributes
        attr['target'] = self._target
        return attr

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
