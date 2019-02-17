"""
Support for Netgear Arlo IP cameras.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/camera.arlo/
"""
import logging
import voluptuous as vol

from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.components.camera import (
        Camera, ATTR_ENTITY_ID, CAMERA_SERVICE_SCHEMA, DOMAIN, PLATFORM_SCHEMA,
        STATE_IDLE, STATE_RECORDING, STATE_STREAMING )
from homeassistant.components.ffmpeg import DATA_FFMPEG
from homeassistant.helpers.aiohttp_client import async_aiohttp_proxy_stream
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.const import (
        ATTR_ATTRIBUTION, ATTR_BATTERY_LEVEL )

from custom_components.aarlo import (
        CONF_ATTRIBUTION, DEFAULT_BRAND, DATA_ARLO )

_LOGGER = logging.getLogger(__name__)

ARLO_MODE_ARMED = 'armed'
ARLO_MODE_DISARMED = 'disarmed'

ATTR_BRIGHTNESS = 'brightness'
ATTR_FLIPPED = 'flipped'
ATTR_MIRRORED = 'mirrored'
ATTR_MOTION = 'motion_detection_sensitivity'
ATTR_POWERSAVE = 'power_save_mode'
ATTR_SIGNAL_STRENGTH = 'signal_strength'
ATTR_UNSEEN_VIDEOS = 'unseen_videos'
ATTR_RECENT_ACTIVITY = 'recent_activity'

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


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up an Arlo IP Camera."""
    arlo = hass.data[DATA_ARLO]

    cameras = []
    for camera in arlo.cameras:
        cameras.append( ArloCam(hass, camera, config) )

    async_add_entities(cameras)

    async def service_handler(service):
        entity_ids = service.data.get(ATTR_ENTITY_ID)
        if entity_ids:
            target_devices = [dev for dev in cameras if dev.entity_id in entity_ids]
        else:
            target_devices = cameras
        for target_device in target_devices:
            target_device.take_snapshot()

    #  hass.data[DOMAIN].async_register_entity_service(
        #  SERVICE_REQUEST_SNAPSHOT, CAMERA_SERVICE_SCHEMA, service_handler )
    hass.services.async_register(
        DOMAIN, SERVICE_REQUEST_SNAPSHOT, service_handler,
        schema=CAMERA_SERVICE_SCHEMA)


class ArloCam(Camera):
    """An implementation of a Netgear Arlo IP camera."""

    def __init__(self, hass, camera, device_info):
        """Initialize an Arlo camera."""
        super().__init__()
        self._name          = camera.name
        self._unique_id     = self._name.lower().replace(' ','_')
        self._camera        = camera
        self._state         = None
        self._recent        = False
        self._motion_status = False
        self._ffmpeg           = hass.data[DATA_FFMPEG]
        self._ffmpeg_arguments = device_info.get(CONF_FFMPEG_ARGUMENTS)

    def camera_image(self):
        """Return a still image response from the camera."""
        return self._camera.last_image_from_cache

    async def async_added_to_hass(self):
        """Register callbacks."""
        @callback
        def update_state( device,attr,value ):
            _LOGGER.info( 'callback:' + self._name + ':' + attr + ':' + str(value)[:80])

            # set state 
            if attr == 'activityState' or attr == 'connectionState':
                if value == 'thermalShutdownCold':
                    self._state = 'Offline, Too Cold'
                elif value == 'userStreamActive':
                    self._state = STATE_STREAMING
                elif value == 'alertStreamActive':
                    self._state = STATE_RECORDING
                else:
                    self._state = STATE_IDLE
            if attr == 'recentActivity':
                self._recent = value

            self.async_schedule_update_ha_state()

        self._camera.add_attr_callback( 'privacyActive',update_state )
        self._camera.add_attr_callback( 'recentActivity',update_state )
        self._camera.add_attr_callback( 'activityState',update_state )
        self._camera.add_attr_callback( 'connectionState',update_state )
        self._camera.add_attr_callback( 'presignedLastImageData',update_state )
        self._camera.add_attr_callback( 'mediaUploadNotification',update_state )

    async def handle_async_mjpeg_stream(self, request):
        """Generate an HTTP MJPEG stream from the camera."""
        from haffmpeg import CameraMjpeg
        video = self._camera.last_video
        if not video:
            error_msg = \
                'Video not found for {0}. Is it older than {1} days?'.format(
                    self.name, self._camera.min_days_vdo_cache)
            _LOGGER.error(error_msg)
            return

        stream = CameraMjpeg(self._ffmpeg.binary, loop=self.hass.loop)
        await stream.open_camera(
            video.video_url, extra_cmd=self._ffmpeg_arguments)

        try:
            return await async_aiohttp_proxy_stream(
                self.hass, request, stream,
                'multipart/x-mixed-replace;boundary=ffserver')
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

    def turn_off( self ):
        self._camera.turn_off()
        return True

    def turn_on( self ):
        self._camera.turn_on()
        return True

    @property
    def state(self):
        return self._camera.state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs= {
            name: value for name, value in (
                (ATTR_BATTERY_LEVEL, self._camera.battery_level),
                (ATTR_BRIGHTNESS, self._camera.brightness),
                (ATTR_FLIPPED, self._camera.flip_state),
                (ATTR_MIRRORED, self._camera.mirror_state),
                (ATTR_MOTION, self._camera.motion_detection_sensitivity),
                (ATTR_POWERSAVE, POWERSAVE_MODE_MAPPING.get( self._camera.powersave_mode )),
                (ATTR_SIGNAL_STRENGTH, self._camera.signal_strength),
                (ATTR_UNSEEN_VIDEOS, self._camera.unseen_videos),
                (ATTR_RECENT_ACTIVITY, self._camera.recent),
            ) if value is not None
        }

        attrs[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
        attrs['brand']          = DEFAULT_BRAND
        attrs['friendly_name']  = self._name

        video = self._camera.last_video
        if video:
            attrs['video_url'] = video.video_url

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

    def set_base_station_mode(self, mode):
        """Set the mode in the base station."""
        # Get the list of base stations identified by library
        base_stations = self.hass.data[DATA_ARLO].base_stations

        # Some Arlo cameras does not have base station
        # So check if there is base station detected first
        # if yes, then choose the primary base station
        # Set the mode on the chosen base station
        if base_stations:
            primary_base_station = base_stations[0]
            primary_base_station.mode = mode

    def enable_motion_detection(self):
        """Enable the Motion detection in base station (Arm)."""
        self._motion_status = True
        self.set_base_station_mode(ARLO_MODE_ARMED)

    def disable_motion_detection(self):
        """Disable the motion detection in base station (Disarm)."""
        self._motion_status = False
        self.set_base_station_mode(ARLO_MODE_DISARMED)

    def take_snapshot(self):
        self._camera.take_snapshot()
