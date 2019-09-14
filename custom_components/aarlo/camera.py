"""
Support for Netgear Arlo IP cameras.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/camera.arlo/
"""
import base64
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components import websocket_api
from homeassistant.components.camera import (ATTR_FILENAME,
                                             CAMERA_SERVICE_SCHEMA,
                                             CAMERA_SERVICE_SNAPSHOT,
                                             DOMAIN,
                                             STATE_IDLE,
                                             STATE_RECORDING,
                                             STATE_STREAMING,
                                             Camera)
from homeassistant.components.ffmpeg import DATA_FFMPEG
from homeassistant.const import (ATTR_ATTRIBUTION,
                                 ATTR_BATTERY_LEVEL,
                                 ATTR_ENTITY_ID)
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_aiohttp_proxy_stream
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from . import CONF_ATTRIBUTION, DATA_ARLO, DEFAULT_BRAND

_LOGGER = logging.getLogger(__name__)

ARLO_MODE_ARMED = 'armed'
ARLO_MODE_DISARMED = 'disarmed'

ATTR_BATTERY_TECH = 'battery_tech'
ATTR_BRIGHTNESS = 'brightness'
ATTR_FLIPPED = 'flipped'
ATTR_MIRRORED = 'mirrored'
ATTR_MOTION = 'motion_detection_sensitivity'
ATTR_POWERSAVE = 'power_save_mode'
ATTR_SIGNAL_STRENGTH = 'signal_strength'
ATTR_UNSEEN_VIDEOS = 'unseen_videos'
ATTR_RECENT_ACTIVITY = 'recent_activity'
ATTR_IMAGE_SRC = 'image_source'
ATTR_CHARGING = 'charging'
ATTR_CHARGER_TYPE = 'charger_type'
ATTR_WIRED = 'wired'
ATTR_WIRED_ONLY = 'wired_only'
ATTR_LAST_VIDEO = 'last_video'

CONF_FFMPEG_ARGUMENTS = 'ffmpeg_arguments'

DEPENDENCIES = ['aarlo', 'ffmpeg']

POWERSAVE_MODE_MAPPING = {
    1: 'best_battery_life',
    2: 'optimized',
    3: 'best_video'
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_FFMPEG_ARGUMENTS): cv.string,
})

SERVICE_REQUEST_SNAPSHOT = 'aarlo_request_snapshot'
SERVICE_REQUEST_SNAPSHOT_TO_FILE = 'aarlo_request_snapshot_to_file'
SERVICE_REQUEST_VIDEO_TO_FILE = 'aarlo_request_video_to_file'
SERVICE_STOP_ACTIVITY = 'aarlo_stop_activity'

WS_TYPE_VIDEO_URL = 'aarlo_video_url'
SCHEMA_WS_VIDEO_URL = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_VIDEO_URL,
    vol.Required('entity_id'): cv.entity_id,
    vol.Required('index'): cv.positive_int
})
WS_TYPE_LIBRARY = 'aarlo_library'
SCHEMA_WS_LIBRARY = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_LIBRARY,
    vol.Required('entity_id'): cv.entity_id,
    vol.Required('at_most'): cv.positive_int
})
WS_TYPE_STREAM_URL = 'aarlo_stream_url'
SCHEMA_WS_STREAM_URL = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_STREAM_URL,
    vol.Required('entity_id'): cv.entity_id
})
WS_TYPE_SNAPSHOT_IMAGE = 'aarlo_snapshot_image'
SCHEMA_WS_SNAPSHOT_IMAGE = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_SNAPSHOT_IMAGE,
    vol.Required('entity_id'): cv.entity_id
})
WS_TYPE_VIDEO_DATA = 'aarlo_video_data'
SCHEMA_WS_VIDEO_DATA = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_VIDEO_DATA,
    vol.Required('entity_id'): cv.entity_id
})
WS_TYPE_STOP_ACTIVITY = 'aarlo_stop_activity'
SCHEMA_WS_STOP_ACTIVITY = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_STOP_ACTIVITY,
    vol.Required('entity_id'): cv.entity_id
})


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Arlo IP Camera."""
    arlo = hass.data[DATA_ARLO]
    component = hass.data[DOMAIN]

    cameras = []
    for camera in arlo.cameras:
        cameras.append(ArloCam(camera, config))

    async_add_entities(cameras)

    component.async_register_entity_service(
        SERVICE_REQUEST_SNAPSHOT, CAMERA_SERVICE_SCHEMA,
        aarlo_snapshot_service_handler
    )
    component.async_register_entity_service(
        SERVICE_REQUEST_SNAPSHOT_TO_FILE, CAMERA_SERVICE_SNAPSHOT,
        aarlo_snapshot_to_file_service_handler
    )
    component.async_register_entity_service(
        SERVICE_REQUEST_VIDEO_TO_FILE, CAMERA_SERVICE_SNAPSHOT,
        aarlo_video_to_file_service_handler
    )
    component.async_register_entity_service(
        SERVICE_STOP_ACTIVITY, CAMERA_SERVICE_SCHEMA,
        aarlo_stop_activity_handler
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_VIDEO_URL, websocket_video_url,
        SCHEMA_WS_VIDEO_URL
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_LIBRARY, websocket_library,
        SCHEMA_WS_LIBRARY
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_STREAM_URL, websocket_stream_url,
        SCHEMA_WS_STREAM_URL
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_SNAPSHOT_IMAGE, websocket_snapshot_image,
        SCHEMA_WS_SNAPSHOT_IMAGE
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_VIDEO_DATA, websocket_video_data,
        SCHEMA_WS_VIDEO_DATA
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_STOP_ACTIVITY, websocket_stop_activity,
        SCHEMA_WS_STOP_ACTIVITY
    )


class ArloCam(Camera):
    """An implementation of a Netgear Arlo IP camera."""

    def __init__(self, camera, config):
        """Initialize an Arlo camera."""
        super().__init__()
        self._name = camera.name
        self._unique_id = self._name.lower().replace(' ', '_')
        self._camera = camera
        self._state = None
        self._recent = False
        self._motion_status = False
        self._ffmpeg_arguments = config.get(CONF_FFMPEG_ARGUMENTS)
        _LOGGER.info('ArloCam: %s created', self._name)

    async def stream_source(self):
        """Return the source of the stream."""
        return self._camera.get_stream()

    def async_stream_source(self):
        return self.hass.async_add_job(self._camera.stream_source)

    def camera_image(self):
        """Return a still image response from the camera."""
        return self._camera.last_image_from_cache

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_device, attr, value):
            _LOGGER.debug('callback:' + self._name + ':' + attr + ':' + str(value)[:80])

            # set state 
            if attr == 'activityState' or attr == 'connectionState':
                if value == 'thermalShutdownCold':
                    self._state = 'Offline, Too Cold'
                elif value == 'userStreamActive':
                    self._state = STATE_STREAMING
                elif value == 'alertStreamActive':
                    self._state = STATE_RECORDING
                elif value == 'unavailable':
                    self._state = 'Unavailable'
                else:
                    self._state = STATE_IDLE
            if attr == 'recentActivity':
                self._recent = value

            self.async_schedule_update_ha_state()

        self._camera.add_attr_callback('privacyActive', update_state)
        self._camera.add_attr_callback('recentActivity', update_state)
        self._camera.add_attr_callback('activityState', update_state)
        self._camera.add_attr_callback('connectionState', update_state)
        self._camera.add_attr_callback('presignedLastImageData', update_state)
        self._camera.add_attr_callback('mediaUploadNotification', update_state)
        self._camera.add_attr_callback('chargingState', update_state)
        self._camera.add_attr_callback('chargingTech', update_state)

    async def handle_async_mjpeg_stream(self, request):
        """Generate an HTTP MJPEG stream from the camera."""
        from haffmpeg.camera import CameraMjpeg
        video = self._camera.last_video
        if not video:
            error_msg = \
                'Video not found for {0}. Is it older than {1} days?'.format(
                    self._name, self._camera.min_days_vdo_cache)
            _LOGGER.error(error_msg)
            return

        ffmpeg_manager = self.hass.data[DATA_FFMPEG]
        stream = CameraMjpeg(ffmpeg_manager.binary, loop=self.hass.loop)
        await stream.open_camera(
            video.video_url, extra_cmd=self._ffmpeg_arguments)

        try:
            stream_reader = await stream.get_reader()
            return await async_aiohttp_proxy_stream(
                self.hass, request, stream_reader,
                ffmpeg_manager.ffmpeg_stream_content_type)

        finally:
            await stream.close()

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_recording(self):
        return self._camera.is_recording

    @property
    def is_on(self):
        return self._camera.is_on

    def turn_off(self):
        self._camera.turn_off()
        return True

    def turn_on(self):
        self._camera.turn_on()
        return True

    @property
    def state(self):
        return self._camera.state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            name: value for name, value in (
                (ATTR_BATTERY_LEVEL, self._camera.battery_level),
                (ATTR_BATTERY_TECH, self._camera.battery_tech),
                (ATTR_BRIGHTNESS, self._camera.brightness),
                (ATTR_FLIPPED, self._camera.flip_state),
                (ATTR_MIRRORED, self._camera.mirror_state),
                (ATTR_MOTION, self._camera.motion_detection_sensitivity),
                (ATTR_POWERSAVE, POWERSAVE_MODE_MAPPING.get(self._camera.powersave_mode)),
                (ATTR_SIGNAL_STRENGTH, self._camera.signal_strength),
                (ATTR_UNSEEN_VIDEOS, self._camera.unseen_videos),
                (ATTR_RECENT_ACTIVITY, self._camera.recent),
                (ATTR_IMAGE_SRC, self._camera.last_image_source),
                (ATTR_CHARGING, self._camera.charging),
                (ATTR_CHARGER_TYPE, self._camera.charger_type),
                (ATTR_WIRED, self._camera.wired),
                (ATTR_WIRED_ONLY, self._camera.wired_only),
                (ATTR_LAST_VIDEO, self.last_video_url),
            ) if value is not None
        }

        attrs[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
        attrs['brand'] = DEFAULT_BRAND
        attrs['friendly_name'] = self._name

        return attrs

    @property
    def model(self):
        """Return the camera model."""
        return self._camera.model_id

    @property
    def brand(self):
        """Return the camera brand."""
        return DEFAULT_BRAND

    @property
    def motion_detection_enabled(self):
        """Return the camera motion detection status."""
        return self._motion_status

    @property
    def last_video(self):
        return self._camera.last_video

    @property
    def last_video_url(self):
        video = self._camera.last_video
        return video.video_url if video is not None else None

    def last_n_videos(self, count):
        return self._camera.last_n_videos(count)

    @property
    def last_capture_date_format(self):
        return self._camera.last_capture_date_format

    def set_base_station_mode(self, mode):
        """Set the mode in the base station."""
        self._camera.base_station.mode = mode

    def enable_motion_detection(self):
        """Enable the Motion detection in base station (Arm)."""
        self._motion_status = True
        self.set_base_station_mode(ARLO_MODE_ARMED)

    def disable_motion_detection(self):
        """Disable the motion detection in base station (Disarm)."""
        self._motion_status = False
        self.set_base_station_mode(ARLO_MODE_DISARMED)

    def request_snapshot(self):
        self._camera.request_snapshot()

    def async_request_snapshot(self):
        return self.hass.async_add_job(self.request_snapshot)

    def get_snapshot(self):
        return self._camera.get_snapshot()

    def async_get_snapshot(self):
        return self.hass.async_add_job(self.get_snapshot)

    def get_video(self):
        return self._camera.get_video()

    def async_get_video(self):
        return self.hass.async_add_job(self.get_video)

    def stop_activity(self):
        return self._camera.stop_activity()

    def async_stop_activity(self):
        return self.hass.async_add_job(self._camera.stop_activity)


def _get_camera_from_entity_id(hass, entity_id):
    component = hass.data.get(DOMAIN)
    if component is None:
        raise HomeAssistantError('Camera component not set up')

    camera = component.get_entity(entity_id)
    if camera is None:
        raise HomeAssistantError('Camera not found')

    return camera


@websocket_api.async_response
async def websocket_video_url(hass, connection, msg):
    camera = _get_camera_from_entity_id(hass, msg['entity_id'])
    video = camera.last_video
    url = video.video_url if video is not None else None
    url_type = video.content_type if video is not None else None
    thumbnail = video.thumbnail_url if video is not None else None
    connection.send_message(websocket_api.result_message(
        msg['id'], {
            'url': url,
            'url_type': url_type,
            'thumbnail': thumbnail,
            'thumbnail_type': 'image/jpeg',
        }
    ))


@websocket_api.async_response
async def websocket_library(hass, connection, msg):
    camera = _get_camera_from_entity_id(hass, msg['entity_id'])
    videos = []
    _LOGGER.debug('library+' + str(msg['at_most']))
    for v in camera.last_n_videos(msg['at_most']):
        videos.append({
            'created_at': v.created_at,
            'created_at_pretty': v.created_at_pretty(camera.last_capture_date_format),
            'url': v.video_url,
            'url_type': v.content_type,
            'thumbnail': v.thumbnail_url,
            'thumbnail_type': 'image/jpeg',
            'object': v.object_type,
            'object_region': v.object_region,
            'trigger': v.object_type,
            'trigger_region': v.object_region,
        })
    connection.send_message(websocket_api.result_message(
        msg['id'], {
            'videos': videos,
        }
    ))


@websocket_api.async_response
async def websocket_stream_url(hass, connection, msg):
    camera = _get_camera_from_entity_id(hass, msg['entity_id'])
    _LOGGER.debug('stream_url for ' + str(camera.unique_id))
    try:
        stream = await camera.async_stream_source()
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'url': stream
            }
        ))

    except HomeAssistantError:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'image_fetch_failed', 'Unable to fetch stream'))


@websocket_api.async_response
async def websocket_snapshot_image(hass, connection, msg):
    camera = _get_camera_from_entity_id(hass, msg['entity_id'])
    _LOGGER.debug('snapshot_image for ' + str(camera.unique_id))

    try:
        image = await camera.async_get_snapshot()
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'content_type': camera.content_type,
                'content': base64.b64encode(image).decode('utf-8')
            }
        ))

    except HomeAssistantError:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'image_fetch_failed', 'Unable to fetch image'))


@websocket_api.async_response
async def websocket_video_data(hass, connection, msg):
    camera = _get_camera_from_entity_id(hass, msg['entity_id'])
    _LOGGER.debug('video_data for ' + str(camera.unique_id))

    try:
        video = await camera.async_get_video()
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'content_type': 'video/mp4',
                'content': base64.b64encode(video).decode('utf-8')
            }
        ))

    except HomeAssistantError:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'video_fetch_failed', 'Unable to fetch video'))


@websocket_api.async_response
async def websocket_stop_activity(hass, connection, msg):
    camera = _get_camera_from_entity_id(hass, msg['entity_id'])
    _LOGGER.debug('stop_activity for ' + str(camera.unique_id))

    stopped = await camera.async_stop_activity()
    connection.send_message(websocket_api.result_message(
        msg['id'], {
            'stopped': stopped
        }
    ))


async def aarlo_snapshot_service_handler(camera, _service):
    _LOGGER.debug("{0} snapshot".format(camera.unique_id))
    await camera.async_get_snapshot()
    hass = camera.hass
    _LOGGER.debug("{0} snapshot event".format(camera.unique_id))
    hass.bus.fire('aarlo_snapshot_ready', {
        'entity_id': 'aarlo.' + camera.unique_id,
    })


async def aarlo_snapshot_to_file_service_handler(camera, service):
    _LOGGER.info("{0} snapshot to file".format(camera.unique_id))

    hass = camera.hass
    filename = service.data[ATTR_FILENAME]
    filename.hass = hass

    snapshot_file = filename.async_render(variables={ATTR_ENTITY_ID: camera})

    # check if we allow to access to that file
    if not hass.config.is_allowed_path(snapshot_file):
        _LOGGER.error("Can't write %s, no access to path!", snapshot_file)
        return

    image = await camera.async_get_snapshot()

    def _write_image(to_file, image_data):
        with open(to_file, 'wb') as img_file:
            img_file.write(image_data)

    try:
        await hass.async_add_executor_job(_write_image, snapshot_file, image)
        hass.bus.fire('aarlo_snapshot_ready', {
            'entity_id': 'aarlo.' + camera.unique_id,
            'file': snapshot_file
        })
    except OSError as err:
        _LOGGER.error("Can't write image to file: %s", err)


async def aarlo_video_to_file_service_handler(camera, service):
    _LOGGER.info("{0} video to file".format(camera.unique_id))

    hass = camera.hass
    filename = service.data[ATTR_FILENAME]
    filename.hass = hass

    video_file = filename.async_render(variables={ATTR_ENTITY_ID: camera})

    # check if we allow to access to that file
    if not hass.config.is_allowed_path(video_file):
        _LOGGER.error("Can't write %s, no access to path!", video_file)
        return

    image = await camera.async_get_video()

    def _write_image(to_file, image_data):
        with open(to_file, 'wb') as img_file:
            img_file.write(image_data)

    try:
        await hass.async_add_executor_job(_write_image, video_file, image)
        hass.bus.fire('aarlo_video_ready', {
            'entity_id': 'aarlo.' + camera.unique_id,
            'file': video_file
        })
    except OSError as err:
        _LOGGER.error("Can't write image to file: %s", err)

    _LOGGER.debug("{0} video to file finished".format(camera.unique_id))


async def aarlo_stop_activity_handler(camera, _service):
    _LOGGER.info("{0} stop activity".format(camera.unique_id))
    camera.stop_activity()
