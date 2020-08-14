"""
Support for Netgear Arlo IP cameras.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/camera.arlo/
"""
import base64
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
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
from homeassistant.components.stream.const import (
    CONF_DURATION,
    CONF_LOOKBACK,
    CONF_STREAM_SOURCE,
    DOMAIN as DOMAIN_STREAM,
    SERVICE_RECORD,
)
from homeassistant.const import (ATTR_ATTRIBUTION,
                                 ATTR_BATTERY_LEVEL,
                                 ATTR_ENTITY_ID,
                                 CONF_FILENAME)
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_aiohttp_proxy_stream
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)

from . import COMPONENT_ATTRIBUTION, COMPONENT_DATA, COMPONENT_BRAND, COMPONENT_DOMAIN, COMPONENT_SERVICES, \
    get_entity_from_domain, is_homekit
from .pyaarlo.constant import (ACTIVITY_STATE_KEY,
                               CHARGER_KEY,
                               CHARGING_KEY,
                               CONNECTION_KEY,
                               LAST_IMAGE_KEY,
                               LAST_IMAGE_DATA_KEY,
                               LAST_IMAGE_SRC_KEY,
                               MEDIA_UPLOAD_KEYS,
                               PRIVACY_KEY,
                               RECENT_ACTIVITY_KEY,
                               SIREN_STATE_KEY)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [COMPONENT_DOMAIN, 'ffmpeg']

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
ATTR_VOLUME = 'volume'
ATTR_LAST_THUMBNAIL = 'last_thumbnail'
ATTR_DURATION = 'duration'
ATTR_TIME_ZONE = 'time_zone'

CONF_FFMPEG_ARGUMENTS = 'ffmpeg_arguments'

POWERSAVE_MODE_MAPPING = {
    1: 'best_battery_life',
    2: 'optimized',
    3: 'best_video'
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_FFMPEG_ARGUMENTS): cv.string,
})

SERVICE_REQUEST_SNAPSHOT = 'camera_request_snapshot'
SERVICE_REQUEST_SNAPSHOT_TO_FILE = 'camera_request_snapshot_to_file'
SERVICE_REQUEST_VIDEO_TO_FILE = 'camera_request_video_to_file'
SERVICE_STOP_ACTIVITY = 'camera_stop_activity'
SERVICE_RECORD_START = 'camera_start_recording'
SERVICE_RECORD_STOP = 'camera_stop_recording'
OLD_SERVICE_REQUEST_SNAPSHOT = 'aarlo_request_snapshot'
OLD_SERVICE_REQUEST_SNAPSHOT_TO_FILE = 'aarlo_request_snapshot_to_file'
OLD_SERVICE_REQUEST_VIDEO_TO_FILE = 'aarlo_request_video_to_file'
OLD_SERVICE_STOP_ACTIVITY = 'aarlo_stop_activity'
OLD_SERVICE_SIREN_ON = 'aarlo_siren_on'
OLD_SERVICE_SIREN_OFF = 'aarlo_siren_off'
OLD_SERVICE_RECORD_START = 'aarlo_start_recording'
OLD_SERVICE_RECORD_STOP = 'aarlo_stop_recording'
SIREN_ON_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required(ATTR_DURATION): cv.positive_int,
    vol.Required(ATTR_VOLUME): cv.positive_int,
})
SIREN_OFF_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
})
RECORD_START_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required(ATTR_DURATION): cv.positive_int,
})

WS_TYPE_VIDEO_URL = 'aarlo_video_url'
WS_TYPE_LIBRARY = 'aarlo_library'
WS_TYPE_STREAM_URL = 'aarlo_stream_url'
WS_TYPE_SNAPSHOT_IMAGE = 'aarlo_snapshot_image'
WS_TYPE_REQUEST_SNAPSHOT = 'aarlo_request_snapshot'
WS_TYPE_VIDEO_DATA = 'aarlo_video_data'
WS_TYPE_STOP_ACTIVITY = 'aarlo_stop_activity'
WS_TYPE_SIREN_ON = 'aarlo_camera_siren_on'
WS_TYPE_SIREN_OFF = 'aarlo_camera_siren_off'
SCHEMA_WS_VIDEO_URL = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_VIDEO_URL,
    vol.Required('entity_id'): cv.entity_id,
    vol.Required('index'): cv.positive_int
})
SCHEMA_WS_LIBRARY = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_LIBRARY,
    vol.Required('entity_id'): cv.entity_id,
    vol.Required('at_most'): cv.positive_int
})
SCHEMA_WS_STREAM_URL = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_STREAM_URL,
    vol.Required('entity_id'): cv.entity_id
})
SCHEMA_WS_SNAPSHOT_IMAGE = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_SNAPSHOT_IMAGE,
    vol.Required('entity_id'): cv.entity_id
})
SCHEMA_WS_REQUEST_SNAPSHOT = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_REQUEST_SNAPSHOT,
    vol.Required('entity_id'): cv.entity_id
})
SCHEMA_WS_VIDEO_DATA = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_VIDEO_DATA,
    vol.Required('entity_id'): cv.entity_id
})
SCHEMA_WS_STOP_ACTIVITY = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_STOP_ACTIVITY,
    vol.Required('entity_id'): cv.entity_id
})
SCHEMA_WS_SIREN_ON = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_SIREN_ON,
    vol.Required('entity_id'): cv.entity_id,
    vol.Required(ATTR_DURATION): cv.positive_int,
    vol.Required(ATTR_VOLUME): cv.positive_int
})
SCHEMA_WS_SIREN_OFF = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_SIREN_OFF,
    vol.Required('entity_id'): cv.entity_id
})


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Arlo IP Camera."""
    arlo = hass.data[COMPONENT_DATA]

    cameras = []
    cameras_with_siren = False
    for camera in arlo.cameras:
        cameras.append(ArloCam(camera, config, arlo))
        if camera.has_capability(SIREN_STATE_KEY):
            cameras_with_siren = True

    async_add_entities(cameras)

    # Component Services
    async def async_camera_service(call):
        """Call aarlo service handler."""
        _LOGGER.info("{} service called".format(call.service))
        if call.service == SERVICE_REQUEST_SNAPSHOT:
            await async_camera_snapshot_service(hass, call)
        if call.service == SERVICE_REQUEST_SNAPSHOT_TO_FILE:
            await async_camera_snapshot_to_file_service(hass, call)
        if call.service == SERVICE_REQUEST_VIDEO_TO_FILE:
            await async_camera_video_to_file_service(hass, call)
        if call.service == SERVICE_STOP_ACTIVITY:
            await async_camera_stop_activity_service(hass, call)
        if call.service == SERVICE_RECORD_START:
            await async_camera_start_recording_service(hass, call)
        if call.service == SERVICE_RECORD_STOP:
            await async_camera_stop_recording_service(hass, call)

    if not hasattr(hass.data[COMPONENT_SERVICES], DOMAIN):
        _LOGGER.info("installing handlers")
        hass.data[COMPONENT_SERVICES][DOMAIN] = 'installed'

        hass.services.async_register(
            COMPONENT_DOMAIN, SERVICE_REQUEST_SNAPSHOT, async_camera_service, schema=CAMERA_SERVICE_SCHEMA,
        )
        hass.services.async_register(
            COMPONENT_DOMAIN, SERVICE_REQUEST_SNAPSHOT_TO_FILE, async_camera_service, schema=CAMERA_SERVICE_SNAPSHOT,
        )
        hass.services.async_register(
            COMPONENT_DOMAIN, SERVICE_REQUEST_VIDEO_TO_FILE, async_camera_service, schema=CAMERA_SERVICE_SNAPSHOT,
        )
        hass.services.async_register(
            COMPONENT_DOMAIN, SERVICE_STOP_ACTIVITY, async_camera_service, schema=CAMERA_SERVICE_SCHEMA,
        )
        hass.services.async_register(
            COMPONENT_DOMAIN, SERVICE_RECORD_START, async_camera_service, schema=RECORD_START_SCHEMA,
        )
        hass.services.async_register(
            COMPONENT_DOMAIN, SERVICE_RECORD_STOP, async_camera_service, schema=CAMERA_SERVICE_SCHEMA,
        )

    # Deprecated Services.
    if not arlo.cfg.hide_deprecated_services:
        component = hass.data[DOMAIN]
        component.async_register_entity_service(
            OLD_SERVICE_REQUEST_SNAPSHOT, CAMERA_SERVICE_SCHEMA,
            aarlo_snapshot_service_handler
        )
        component.async_register_entity_service(
            OLD_SERVICE_REQUEST_SNAPSHOT_TO_FILE, CAMERA_SERVICE_SNAPSHOT,
            aarlo_snapshot_to_file_service_handler
        )
        component.async_register_entity_service(
            OLD_SERVICE_REQUEST_VIDEO_TO_FILE, CAMERA_SERVICE_SNAPSHOT,
            aarlo_video_to_file_service_handler
        )
        component.async_register_entity_service(
            OLD_SERVICE_STOP_ACTIVITY, CAMERA_SERVICE_SCHEMA,
            aarlo_stop_activity_handler
        )
        if cameras_with_siren:
            component.async_register_entity_service(
                OLD_SERVICE_SIREN_ON, SIREN_ON_SCHEMA,
                aarlo_siren_on_service_handler
            )
            component.async_register_entity_service(
                OLD_SERVICE_SIREN_OFF, SIREN_OFF_SCHEMA,
                aarlo_siren_off_service_handler
            )
        component.async_register_entity_service(
            OLD_SERVICE_RECORD_START, RECORD_START_SCHEMA,
            aarlo_start_recording_handler
        )
        component.async_register_entity_service(
            OLD_SERVICE_RECORD_STOP, CAMERA_SERVICE_SCHEMA,
            aarlo_stop_recording_handler
        )

    # Websockets
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
        WS_TYPE_REQUEST_SNAPSHOT, websocket_request_snapshot,
        SCHEMA_WS_REQUEST_SNAPSHOT
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_VIDEO_DATA, websocket_video_data,
        SCHEMA_WS_VIDEO_DATA
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_STOP_ACTIVITY, websocket_stop_activity,
        SCHEMA_WS_STOP_ACTIVITY
    )
    if cameras_with_siren:
        hass.components.websocket_api.async_register_command(
            WS_TYPE_SIREN_ON, websocket_siren_on,
            SCHEMA_WS_SIREN_ON
        )
        hass.components.websocket_api.async_register_command(
            WS_TYPE_SIREN_OFF, websocket_siren_off,
            SCHEMA_WS_SIREN_OFF
        )


class ArloCam(Camera):
    """An implementation of a Netgear Arlo IP camera."""

    def __init__(self, camera, config, arlo):
        """Initialize an Arlo camera."""
        super().__init__()
        self._name = camera.name
        self._unique_id = camera.entity_id
        self._camera = camera
        self._state = None
        self._recent = False
        self._last_image_source_ = None
        self._motion_status = False
        self._stream_snapshot = arlo.cfg.stream_snapshot
        self._save_updates_to = arlo.cfg.save_updates_to
        self._ffmpeg_arguments = config.get(CONF_FFMPEG_ARGUMENTS)
        _LOGGER.info('ArloCam: %s created', self._name)

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_device, attr, value):
            _LOGGER.debug('callback:' + self._name + ':' + attr + ':' + str(value)[:80])

            # set state 
            if attr == ACTIVITY_STATE_KEY or attr == CONNECTION_KEY:
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
            if attr == RECENT_ACTIVITY_KEY:
                self._recent = value

            # Trigger snapshot/capture/image updated events
            if attr == LAST_IMAGE_SRC_KEY:
                if self._last_image_source_ is not None and self._last_image_source_ != value:
                    if value.startswith("snapshot/"):
                        _LOGGER.debug("{0} snapshot updated".format(self._unique_id))
                        self.hass.bus.fire('aarlo_snapshot_updated', {
                            'entity_id': 'aarlo.' + self._unique_id
                        })
                    else:
                        _LOGGER.debug("{0} capture updated".format(self._unique_id))
                        self.hass.bus.fire('aarlo_capture_updated', {
                            'entity_id': 'aarlo.' + self._unique_id
                        })
                    self.hass.bus.fire('aarlo_image_updated', {
                        'entity_id': 'aarlo.' + self._unique_id
                    })
                self._last_image_source_ = value

            # Save image if asked to
            if attr == LAST_IMAGE_DATA_KEY and self._save_updates_to != '':
                filename = "{}/{}.jpg".format(self._save_updates_to,self._unique_id)
                _LOGGER.debug("saving to {}".format(filename))
                if not self.hass.config.is_allowed_path(filename):
                    _LOGGER.error("Can't write %s, no access to path!", filename)
                else:
                    with open(filename, 'wb') as img_file:
                        img_file.write(value)

            # Signal changes.
            self.async_schedule_update_ha_state()

        self._camera.add_attr_callback(ACTIVITY_STATE_KEY, update_state)
        self._camera.add_attr_callback(CHARGER_KEY, update_state)
        self._camera.add_attr_callback(CHARGING_KEY, update_state)
        self._camera.add_attr_callback(CONNECTION_KEY, update_state)
        self._camera.add_attr_callback(LAST_IMAGE_KEY, update_state)
        self._camera.add_attr_callback(LAST_IMAGE_SRC_KEY, update_state)
        self._camera.add_attr_callback(LAST_IMAGE_DATA_KEY, update_state)
        self._camera.add_attr_callback(MEDIA_UPLOAD_KEYS, update_state)
        self._camera.add_attr_callback(PRIVACY_KEY, update_state)
        self._camera.add_attr_callback(RECENT_ACTIVITY_KEY, update_state)

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
                (ATTR_RECENT_ACTIVITY, self._camera.was_recently_active),
                (ATTR_IMAGE_SRC, self._camera.last_image_source),
                (ATTR_CHARGING, self._camera.charging),
                (ATTR_CHARGER_TYPE, self._camera.charger_type),
                (ATTR_WIRED, self._camera.wired),
                (ATTR_WIRED_ONLY, self._camera.wired_only),
                (ATTR_LAST_THUMBNAIL, self.last_thumbnail_url),
                (ATTR_LAST_VIDEO, self.last_video_url),
                (ATTR_TIME_ZONE, self._camera.timezone),
            ) if value is not None
        }

        attrs[ATTR_ATTRIBUTION] = COMPONENT_ATTRIBUTION
        attrs['brand'] = COMPONENT_BRAND
        attrs['device_id'] = self._camera.device_id
        attrs['model_id'] = self._camera.model_id
        attrs['parent_id'] = self._camera.parent_id
        attrs['friendly_name'] = self._name
        attrs['siren'] = self._camera.has_capability(SIREN_STATE_KEY)

        return attrs

    @property
    def model(self):
        """Return the camera model."""
        return self._camera.model_id

    @property
    def brand(self):
        """Return the camera brand."""
        return COMPONENT_BRAND

    async def stream_source(self):
        """Return the source of the stream."""
        if is_homekit():
            return self._camera.get_stream()
        else:
            return await self.hass.async_add_executor_job(self._camera.get_stream)

    async def async_stream_source(self):
        return await self.hass.async_add_executor_job(self._camera.get_stream)

    def camera_image(self):
        """Return a still image response from the camera."""
        return self._camera.last_image_from_cache

    @property
    def motion_detection_enabled(self):
        """Return the camera motion detection status."""
        return self._motion_status

    @property
    def last_video(self):
        return self._camera.last_video

    @property
    def last_thumbnail_url(self):
        # prefer video or what arlo says?
        #  video = self._camera.last_video
        #  if video is None:
        #  thumbnail =  self._camera.last_image
        #  else:
        #  thumbnail = video.thumbnail_url
        #  return thumbnail
        return self._camera.last_image

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

    def _attach_hidden_stream(self, source, duration):
        _LOGGER.info("{} attaching hidden stream for duration {}".format(self._unique_id, 15))

        video_path = "/tmp/aarlo-hidden-{}.mp4".format(self._unique_id)

        data = {
            CONF_STREAM_SOURCE: source,
            CONF_FILENAME: video_path,
            CONF_DURATION: duration,
            CONF_LOOKBACK: 0,
        }
        self.hass.services.call(
            DOMAIN_STREAM, SERVICE_RECORD, data, blocking=True
        )

        _LOGGER.debug("waiting on stream connect")
        return self._camera.wait_for_user_stream()

    def _start_snapshot_stream(self):
        if self._stream_snapshot:
            source = self._camera.start_snapshot_stream()
            if source is not None:
                self._camera.wait_for_user_stream()
            return source
        return None

    def request_snapshot(self):
        self._start_snapshot_stream()
        self._camera.request_snapshot()

    async def async_request_snapshot(self):
        return await self.hass.async_add_executor_job(self.request_snapshot)

    def get_snapshot(self):
        self._start_snapshot_stream()
        return self._camera.get_snapshot()

    async def async_get_snapshot(self):
        return await self.hass.async_add_executor_job(self.get_snapshot)

    def get_video(self):
        return self._camera.get_video()

    async def async_get_video(self):
        return await self.hass.async_add_executor_job(self.get_video)

    def stop_activity(self):
        return self._camera.stop_activity()

    async def async_stop_activity(self):
        return await self.hass.async_add_executor_job(self.stop_activity)

    def siren_on(self, duration=30, volume=10):
        if self._camera.has_capability(SIREN_STATE_KEY):
            _LOGGER.debug("{0} siren on {1}/{2}".format(self.unique_id, volume, duration))
            self._camera.siren_on(duration=duration, volume=volume)
            return True
        return False

    def siren_off(self):
        if self._camera.has_capability(SIREN_STATE_KEY):
            _LOGGER.debug("{0} siren off".format(self.unique_id))
            self._camera.siren_off()
            return True
        return False

    async def async_siren_on(self, duration, volume):
        return await self.hass.async_add_executor_job(self.siren_on, duration, volume)

    async def async_siren_off(self):
        return await self.hass.async_add_executor_job(self.siren_off)

    def start_recording(self, duration=30):
        source = self._camera.start_recording_stream()
        if source is not None:
            self._attach_hidden_stream(source, duration + 10)
            self._camera.start_recording(duration=duration)
            return source
        _LOGGER.warning("failed to start recording for {}".format(self._camera.name))
        return None

    def stop_recording(self):
        self._camera.stop_recording_stream()

    async def async_start_recording(self, duration):
        return await self.hass.async_add_executor_job(self.start_recording, duration)

    async def async_stop_recording(self):
        return await self.hass.async_add_executor_job(self.stop_recording)


@websocket_api.async_response
async def websocket_video_url(hass, connection, msg):
    try:
        camera = get_entity_from_domain(hass, DOMAIN, msg['entity_id'])
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
    except HomeAssistantError as error:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'video_url_ws', "Unable to fetch url ({})".format(str(error))))
        _LOGGER.warning("{} video url websocket failed".format(msg['entity_id']))


@websocket_api.async_response
async def websocket_library(hass, connection, msg):
    try:
        camera = get_entity_from_domain(hass, DOMAIN, msg['entity_id'])
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
    except HomeAssistantError as error:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'library_ws', "Unable to fetch library ({})".format(str(error))))
        _LOGGER.warning("{} library websocket failed".format(msg['entity_id']))


@websocket_api.async_response
async def websocket_stream_url(hass, connection, msg):
    try:
        camera = get_entity_from_domain(hass, DOMAIN, msg['entity_id'])
        _LOGGER.debug('stream_url for ' + str(camera.unique_id))

        stream = await camera.async_stream_source()
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'url': stream
            }
        ))
    except HomeAssistantError as error:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'stream_url_ws', "Unable to fetch stream ({})".format(str(error))))
        _LOGGER.warning("{} stream url websocket failed".format(msg['entity_id']))


@websocket_api.async_response
async def websocket_snapshot_image(hass, connection, msg):
    try:
        camera = get_entity_from_domain(hass, DOMAIN, msg['entity_id'])
        _LOGGER.debug('snapshot_image for ' + str(camera.unique_id))

        image = await camera.async_get_snapshot()
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'content_type': camera.content_type,
                'content': base64.b64encode(image).decode('utf-8')
            }
        ))
    except HomeAssistantError as error:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'snapshot_image_ws', "Unable to take snapshot ({})".format(str(error))))
        _LOGGER.warning("{} snapshot image websocket failed".format(msg['entity_id']))


@websocket_api.async_response
async def websocket_request_snapshot(hass, connection, msg):
    try:
        camera = get_entity_from_domain(hass, DOMAIN, msg['entity_id'])
        _LOGGER.debug('request_snapshot_image for ' + str(camera.unique_id))

        await camera.async_request_snapshot()
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'snapshot requested'
            }
        ))
    except HomeAssistantError as error:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'requst_snapshot_ws', "Unable to request snapshot ({})".format(str(error))))
        _LOGGER.warning("{} snapshot request websocket failed".format(msg['entity_id']))


@websocket_api.async_response
async def websocket_video_data(hass, connection, msg):
    try:
        camera = get_entity_from_domain(hass, DOMAIN, msg['entity_id'])
        _LOGGER.debug('video_data for ' + str(camera.unique_id))

        video = await camera.async_get_video()
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'content_type': 'video/mp4',
                'content': base64.b64encode(video).decode('utf-8')
            }
        ))
    except HomeAssistantError as error:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'video_data_ws', "Unable to get video data ({})".format(str(error))))
        _LOGGER.warning("{} video data websocket failed".format(msg['entity_id']))


@websocket_api.async_response
async def websocket_stop_activity(hass, connection, msg):
    try:
        camera = get_entity_from_domain(hass, DOMAIN, msg['entity_id'])
        _LOGGER.debug('stop_activity for ' + str(camera.unique_id))

        stopped = await camera.async_stop_activity()
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'stopped': stopped
            }
        ))
    except HomeAssistantError as error:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'stop_activity_ws', "Unable to stop activity ({})".format(str(error))))
        _LOGGER.warning("{} stop activity websocket failed".format(msg['entity_id']))


@websocket_api.async_response
async def websocket_siren_on(hass, connection, msg):
    try:
        camera = get_entity_from_domain(hass, DOMAIN, msg['entity_id'])
        _LOGGER.debug('stop_activity for ' + str(camera.unique_id))

        await camera.async_siren_on(duration=msg['duration'], volume=msg['volume'])
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'siren': 'on'
            }
        ))
    except HomeAssistantError as error:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'siren_on_ws', "Unable to turn siren on ({})".format(str(error))))
        _LOGGER.warning("{} siren on websocket failed".format(msg['entity_id']))


@websocket_api.async_response
async def websocket_siren_off(hass, connection, msg):
    try:
        camera = get_entity_from_domain(hass, DOMAIN, msg['entity_id'])
        _LOGGER.debug('stop_activity for ' + str(camera.unique_id))

        await camera.async_siren_off()
        connection.send_message(websocket_api.result_message(
            msg['id'], {
                'siren': 'off'
            }
        ))
    except HomeAssistantError as error:
        connection.send_message(websocket_api.error_message(
            msg['id'], 'siren_off_ws', "Unable to turn siren off ({})".format(str(error))))
        _LOGGER.warning("{} siren off websocket failed".format(msg['entity_id']))


async def aarlo_snapshot_service_handler(camera, _service):
    _LOGGER.debug("{0} snapshot".format(camera.unique_id))
    await camera.async_get_snapshot()
    hass = camera.hass
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


async def aarlo_siren_on_service_handler(camera, service):
    volume = service.data[ATTR_VOLUME]
    duration = service.data[ATTR_DURATION]
    camera.siren_on(duration=duration, volume=volume)


async def aarlo_siren_off_service_handler(camera, _service):
    camera.siren_off()


async def aarlo_start_recording_handler(camera, service):
    duration = service.data[ATTR_DURATION]
    camera.start_recording(duration=duration)


async def aarlo_stop_recording_handler(camera, _service):
    camera.stop_recording()


async def async_camera_snapshot_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            _LOGGER.info("{} snapshot".format(entity_id))
            camera = get_entity_from_domain(hass, DOMAIN, entity_id)
            await camera.async_get_snapshot()
            hass.bus.fire('aarlo_snapshot_ready', {
                'entity_id': entity_id,
            })
        except HomeAssistantError:
            _LOGGER.warning("{} snapshot service failed".format(entity_id))


async def async_camera_snapshot_to_file_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            camera = get_entity_from_domain(hass, DOMAIN, entity_id)
            filename = call.data[ATTR_FILENAME]
            filename.hass = hass
            snapshot_file = filename.async_render(variables={ATTR_ENTITY_ID: camera})
            _LOGGER.info("{} snapshot(filename={})".format(entity_id, filename))

            # check if we allow to access to that file
            if not hass.config.is_allowed_path(snapshot_file):
                _LOGGER.error("Can't write %s, no access to path!", snapshot_file)
                return

            image = await camera.async_get_snapshot()

            def _write_image(to_file, image_data):
                with open(to_file, 'wb') as img_file:
                    img_file.write(image_data)

            await hass.async_add_executor_job(_write_image, snapshot_file, image)
            hass.bus.fire('aarlo_snapshot_ready', {
                'entity_id': entity_id,
                'file': snapshot_file
            })
        except OSError as err:
            _LOGGER.error("Can't write image to file: %s", err)
        except HomeAssistantError:
            _LOGGER.warning("{} snapshot to file service failed".format(entity_id))


async def async_camera_video_to_file_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            camera = get_entity_from_domain(hass, DOMAIN, entity_id)
            filename = call.data[ATTR_FILENAME]
            filename.hass = hass
            video_file = filename.async_render(variables={ATTR_ENTITY_ID: camera})
            _LOGGER.info("{} video to file {}".format(entity_id, filename))

            # check if we allow to access to that file
            if not hass.config.is_allowed_path(video_file):
                _LOGGER.error("Can't write %s, no access to path!", video_file)
                return

            image = await camera.async_get_video()

            def _write_image(to_file, image_data):
                with open(to_file, 'wb') as img_file:
                    img_file.write(image_data)

            await hass.async_add_executor_job(_write_image, video_file, image)
            hass.bus.fire('aarlo_video_ready', {
                'entity_id': entity_id,
                'file': video_file
            })
        except OSError as err:
            _LOGGER.error("Can't write image to file: %s", err)
        except HomeAssistantError:
            _LOGGER.warning("{} video to file service failed".format(entity_id))
        _LOGGER.debug("{0} video to file finished".format(entity_id))


async def async_camera_stop_activity_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            _LOGGER.info("{} stop activity".format(entity_id))
            get_entity_from_domain(hass, DOMAIN, entity_id).stop_activity()
        except HomeAssistantError:
            _LOGGER.warning("{} stop activity service failed".format(entity_id))


async def async_camera_siren_on_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            volume = call.data[ATTR_VOLUME]
            duration = call.data[ATTR_DURATION]
            _LOGGER.info("{} start siren(volume={}/duration={})".format(entity_id, volume, duration))
            get_entity_from_domain(hass, DOMAIN, entity_id).siren_on(duration=duration, volume=volume)
        except HomeAssistantError:
            _LOGGER.warning("{} siren on service failed".format(entity_id))


async def async_camera_siren_off_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            _LOGGER.info("{} stop siren".format(entity_id))
            get_entity_from_domain(hass, DOMAIN, entity_id).siren_off()
        except HomeAssistantError:
            _LOGGER.warning("{} siren off service failed".format(entity_id))


async def async_camera_start_recording_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            duration = call.data[ATTR_DURATION]
            _LOGGER.info("{} start recording(duration={})".format(entity_id, duration))
            camera = get_entity_from_domain(hass, DOMAIN, entity_id)
            await camera.async_start_recording(duration=duration)
        except HomeAssistantError:
            _LOGGER.warning("{} start recording service failed".format(entity_id))


async def async_camera_stop_recording_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            _LOGGER.info("{} stop recording".format(entity_id))
            get_entity_from_domain(hass, DOMAIN, entity_id).stop_recording()
        except HomeAssistantError:
            _LOGGER.warning("{} stop recording service failed".format(entity_id))
