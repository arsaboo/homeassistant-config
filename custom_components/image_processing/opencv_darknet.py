"""
Component that performs OpenCV classification on images using DNN.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.opencv_darknet/
"""
from datetime import timedelta
import logging

import requests
import voluptuous as vol

from homeassistant.components.image_processing import (
    CONF_ENTITY_ID, CONF_NAME, CONF_SOURCE, PLATFORM_SCHEMA,
    ImageProcessingEntity)
from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['numpy==1.15.1']

_LOGGER = logging.getLogger(__name__)

ATTR_MATCHES = 'matches'
ATTR_TOTAL_MATCHES = 'total_matches'

ATTR_MATCHES = 'matches'
ATTR_TOTAL_MATCHES = 'total_matches'

CONF_OPTIONS = 'options'
CONF_MODEL = 'detect_model'
CONF_WEIGHTS = 'weights'
CONF_LABELS = 'labels'
CONF_CONFIDENCE = 'confidence'
CONF_CROP = 'crop'
CONF_X1 = 'x1'
CONF_X2 = 'x2'
CONF_Y1 = 'y1'
CONF_Y2 = 'y2'

DEFAULT_TIMEOUT = 10
DEFAULT_CONFIDENCE = 0.55
DEFAULT_CROP = {'x1': None, 'x2': None, 'y1': None, 'y2': None}

SCAN_INTERVAL = timedelta(seconds=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_OPTIONS): {
        vol.Required(CONF_MODEL): cv.isfile,
        vol.Required(CONF_WEIGHTS): cv.isfile,
        vol.Required(CONF_LABELS): cv.isfile,
        vol.Optional(CONF_CROP, DEFAULT_CROP): {
            vol.Required(CONF_X1): vol.All(vol.Coerce(int), vol.Range(min=0)),
            vol.Required(CONF_Y1): vol.All(vol.Coerce(int), vol.Range(min=0)),
            vol.Required(CONF_X2): vol.All(vol.Coerce(int), vol.Range(min=0)),
            vol.Required(CONF_Y2): vol.All(vol.Coerce(int), vol.Range(min=0))
        },
        vol.Optional(CONF_CONFIDENCE, DEFAULT_CONFIDENCE):
            vol.All(vol.Coerce(float), vol.Range(
                min=0, max=1, max_included=True))
    }
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the OpenCV image processing platform."""
    try:
        # Verify that the OpenCV python package is pre-installed
        # pylint: disable=unused-import,unused-variable
        import cv2  # noqa
    except ImportError:
        _LOGGER.error(
            "No OpenCV library found! Install or compile for your system "
            "following instructions here: http://opencv.org/releases.html")
        return

    options = {"model": config[CONF_OPTIONS][CONF_MODEL], "weights": config[CONF_OPTIONS][CONF_WEIGHTS],
               "threshold": config[CONF_OPTIONS][CONF_CONFIDENCE], "labels": config[CONF_OPTIONS][CONF_LABELS]}
    entities = []
    if CONF_CROP not in config[CONF_OPTIONS].keys():
        config[CONF_OPTIONS][CONF_CROP] = False
    for camera in config[CONF_SOURCE]:
        entities.append(OpenCVImageProcessor(
            hass, camera[CONF_ENTITY_ID], camera.get(CONF_NAME), options, config[CONF_OPTIONS][CONF_CROP]))

    add_entities(entities)


class OpenCVImageProcessor(ImageProcessingEntity):
    """Representation of an OpenCV image processor."""

    def __init__(self, hass, camera_entity, name, options, crop):
        """Initialize the OpenCV entity."""
        self.hass = hass
        self._camera_entity = camera_entity
        if name:
            self._name = name
        else:
            self._name = "OpenCV {0}".format(split_entity_id(camera_entity)[1])
        
        self.confThreshold = options["threshold"]  #Confidence threshold
        self.nmsThreshold = 0.4   #Non-maximum suppression threshold
        self.inpWidth = 416       #Width of network's input image
        self.inpHeight = 416      #Height of network's input image
        self.classes = None
        with open(options["labels"], 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

        # Give the configuration and weight files for the model and load the network using them.
        self.modelConfiguration = options["model"]
        self.modelWeights = options["weights"]
        self._crop = crop
        self._matches = {}
        self._total_matches = 0
        self._last_image = None

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera_entity

    @property
    def name(self):
        """Return the name of the image processor."""
        return self._name

    @property
    def state(self):
        """Return the state of the entity."""
        return self._total_matches

    @property
    def state_attributes(self):
        """Return device specific state attributes."""
        return {
            ATTR_MATCHES: self._matches,
            ATTR_TOTAL_MATCHES: self._total_matches
        }

    def process_image(self, image):
        """Process the image."""
        import cv2  # pylint: disable=import-error
        import numpy
        cv_image = cv2.imdecode(
            numpy.asarray(bytearray(image)), cv2.IMREAD_UNCHANGED)
        # If there are parameters for cropping, split the image using numpy array splitting
        if self._crop:
            frame = cv_image[self._crop[CONF_Y1]:self._crop[CONF_Y2],
                             self._crop[CONF_X1]:self._crop[CONF_X2]]
        else:
            frame = cv_image

        net = cv2.dnn.readNetFromDarknet(self.modelConfiguration, self.modelWeights) # pylint:disable=E1101
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV) # pylint:disable=E1101
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU) # pylint:disable=E1101
        # Create a 4D blob from an image.
        blob = cv2.dnn.blobFromImage(frame, 1/255, (self.inpWidth, self.inpHeight), [0,0,0], 1, crop=False) # pylint:disable=E1101
        net.setInput(blob)
        # Get the names of all the layers in the network
        layersNames = net.getLayerNames()
        # Runs the forward pass to get output of the output layers
        outs = net.forward([layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()])
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]

        classIds = []
        confidences = []
        boxes = []
        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = numpy.argmax(scores)
                confidence = scores[classId]
                if confidence > self.confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])
        
        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold) # pylint:disable=E1101
        total_matches = 0
        matches = {}

        for i in indices:
            i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            regions = matches.get(self.classes[classIds[i]],[])
            regions.append((int(left), int(top), int(width), int(height)))
            total_matches += 1
            matches[self.classes[classIds[i]]] = regions

        self._matches = matches
        self._total_matches = total_matches
