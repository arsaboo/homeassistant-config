"""
Component that performs TensorFlow classification on images.

For a quick start, pick a pre-trained COCO model from:
https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.tensorflow/
"""
import logging

import voluptuous as vol

from homeassistant.components.image_processing import (
    CONF_ENTITY_ID, CONF_NAME, CONF_SOURCE, CONF_CONFIDENCE, PLATFORM_SCHEMA,
    ImageProcessingEntity)
from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import template

REQUIREMENTS = ['numpy==1.15.2', 'pillow==5.2.0', 'protobuf==3.6.1']

_LOGGER = logging.getLogger(__name__)

ATTR_MATCHES = 'matches'
ATTR_TOTAL_MATCHES = 'total_matches'

CONF_FILE_OUT = 'file_out'
CONF_MODEL = 'model'
CONF_GRAPH = 'graph'
CONF_LABELS = 'labels'
CONF_MODEL_DIR = 'model_dir'
CONF_CATEGORIES = 'categories'

DEFAULT_MODEL_DIR = '/usr/src/app/tensorflow'
DEFAULT_LABELS = ("{0}/object_detection/data/mscoco_label_map.pbtxt"
                  .format(DEFAULT_MODEL_DIR))

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_FILE_OUT, default=[]):
        vol.All(cv.ensure_list, [cv.template]),
    vol.Required(CONF_MODEL): vol.Schema({
        vol.Required(CONF_GRAPH): cv.isfile,
        vol.Optional(CONF_LABELS, default=DEFAULT_LABELS): cv.isfile,
        vol.Optional(CONF_MODEL_DIR, default=DEFAULT_MODEL_DIR): cv.isdir,
        vol.Optional(CONF_CATEGORIES, default=[]):
            vol.All(cv.ensure_list, [cv.string])
    })
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the TensorFlow image processing platform."""
    import sys

    model_config = config.get(CONF_MODEL)
    model_dir = model_config.get(CONF_MODEL_DIR)

    # append custom model path to sys.path
    sys.path.append(model_dir)

    try:
        # Verify that the TensorFlow Object Detection API is pre-installed
        # pylint: disable=unused-import,unused-variable
        import tensorflow as tf # noqa
        from object_detection.utils import label_map_util # noqa
    except ImportError:
        # pylint: disable=line-too-long
        _LOGGER.error(
            "No TensorFlow Object Detection library found! Install or compile for your system "
            "following instructions here: "
            "https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md")
        return

    try:
        # Display warning that PIL will be used if no OpenCV is found.
        # pylint: disable=unused-import,unused-variable
        import cv2 # noqa
    except ImportError:
        _LOGGER.warning("No OpenCV library found. "
                        "TensorFlow will process image with PIL at reduced resolution.")

    # setup tensorflow graph, session, and label map to pass to processor
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(model_config.get(CONF_GRAPH), 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    session = tf.Session(graph=detection_graph)
    label_map = label_map_util.load_labelmap(model_config.get(CONF_LABELS))
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=90, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    min_confidence = config.get(CONF_CONFIDENCE)

    include_categories = model_config.get(CONF_CATEGORIES)

    file_out = config.get(CONF_FILE_OUT)

    entities = []

    for camera in config[CONF_SOURCE]:
        entities.append(TensorFlowImageProcessor(
            hass, camera[CONF_ENTITY_ID], camera.get(CONF_NAME),
            session, detection_graph, category_index,
            min_confidence, include_categories, file_out))

    add_entities(entities)


class TensorFlowImageProcessor(ImageProcessingEntity):
    """Representation of an TensorFlow image processor."""

    def __init__(self, hass, camera_entity, name, session, detection_graph,
                 category_index, min_confidence, include_categories, file_out):
        """Initialize the TensorFlow entity."""

        self.hass = hass
        self._camera_entity = camera_entity
        if name:
            self._name = name
        else:
            self._name = "TensorFlow {0}".format(split_entity_id(camera_entity)[1])
        self._session = session
        self._detection_graph = detection_graph
        self._category_index = category_index
        self._min_confidence = min_confidence
        self._include_categories = include_categories
        self._file_out = file_out
        template.attach(hass, self._file_out)

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

    def _save_image(self, image, matches, paths):
        from PIL import Image, ImageDraw
        import io
        img = Image.open(io.BytesIO(bytearray(image))).convert('RGB')
        img_width, img_height = img.size
        draw = ImageDraw.Draw(img)

        for label, values in matches.items():
            for instance in values:
                score = "{0:.1f}".format(instance["score"])
                ymin, xmin, ymax, xmax = instance["box"]
                (left, right, top, bottom) = (xmin * img_width, xmax * img_width,
                                                ymin * img_height, ymax * img_height)
                draw.line([(left, top), (left, bottom), (right, bottom),
                            (right, top), (left, top)], width=5, fill=(255, 255, 0))
                draw.text((left, top-15), "{0} {1}%".format(label, score), fill=(255, 255, 0))

        for path in paths:
            _LOGGER.info("Saving results image to {}".format(path))
            img.save(path)

    def process_image(self, image):
        """Process the image."""
        import numpy as np

        try:
            import cv2  # pylint: disable=import-error
            img = cv2.imdecode(np.asarray(bytearray(image)), cv2.IMREAD_UNCHANGED)
            inp = img[:, :, [2, 1, 0]]  # BGR->RGB
            inp_expanded = inp.reshape(1, inp.shape[0], inp.shape[1], 3)
        except ImportError:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(bytearray(image))).convert('RGB')
            img.thumbnail((460, 460), Image.ANTIALIAS)
            img_width, img_height = img.size
            inp = np.array(img.getdata()).reshape(
                (img_height, img_width, 3)).astype(np.uint8)
            inp_expanded = np.expand_dims(inp, axis=0)

        image_tensor = self._detection_graph.get_tensor_by_name('image_tensor:0')
        boxes = self._detection_graph.get_tensor_by_name('detection_boxes:0')
        scores = self._detection_graph.get_tensor_by_name('detection_scores:0')
        classes = self._detection_graph.get_tensor_by_name('detection_classes:0')
        boxes, scores, classes = self._session.run(
            [boxes, scores, classes],
            feed_dict={image_tensor: inp_expanded})
        boxes, scores, classes = map(np.squeeze, [boxes, scores, classes])
        classes = classes.astype(int)

        matches = {}
        total_matches = 0
        for box, score, obj_class in zip(boxes, scores, classes):
            score = score * 100
            if score < self._min_confidence:
                continue
            category = self._category_index[obj_class]['name']
            if self._include_categories and category not in self._include_categories:
                continue
            if category not in matches.keys():
                matches[category] = []
            matches[category].append({
                'score': float(score),
                'box': box.tolist()
            })
            total_matches += 1

        # Save Images
        if total_matches and self._file_out:
            paths = []
            for path_template in self._file_out:
                if isinstance(path_template, template.Template):
                    paths.append(path_template.render(camera_entity=self._camera_entity))
                else:
                    paths.append(path_template)
            self._save_image(image, matches, paths)

        self._matches = matches
        self._total_matches = total_matches
