import base64
import threading
import time
import zlib
import pprint

from .constant import (
    ACTIVITY_STATE_KEY, AIR_QUALITY_KEY, AUDIO_ANALYTICS_KEY,
    AUDIO_DETECTED_KEY, AUDIO_POSITION_KEY, AUDIO_TRACK_KEY, BATTERY_KEY,
    BRIGHTNESS_KEY, CAMERA_MEDIA_DELAY, CAPTURED_TODAY_KEY, CRY_DETECTION_KEY,
    CONNECTION_KEY, FLIP_KEY, FLOODLIGHT_BRIGHTNESS1_KEY,
    FLOODLIGHT_BRIGHTNESS2_KEY, FLOODLIGHT_KEY, HUMIDITY_KEY,
    IDLE_SNAPSHOT_PATH, LAMP_STATE_KEY, LAST_CAPTURE_KEY, LAST_IMAGE_DATA_KEY,
    LAST_IMAGE_KEY, LAST_IMAGE_SRC_KEY, LIGHT_BRIGHTNESS_KEY, LIGHT_MODE_KEY,
    MEDIA_COUNT_KEY, MEDIA_PLAYER_KEY, MEDIA_PLAYER_RESOURCE_ID,
    MEDIA_UPLOAD_KEY, MEDIA_UPLOAD_KEYS, MIRROR_KEY, MOTION_DETECTED_KEY,
    MOTION_SENS_KEY, NIGHTLIGHT_KEY, POWER_SAVE_KEY, PRIVACY_KEY,
    RECENT_ACTIVITY_KEY, RECORDING_STOPPED_KEY, RECORD_START_PATH,
    RECORD_STOP_PATH, SIGNAL_STR_KEY, SIREN_STATE_KEY, SNAPSHOT_KEY,
    SPOTLIGHT_BRIGHTNESS_KEY, SPOTLIGHT_KEY, STREAM_SNAPSHOT_KEY,
    STREAM_SNAPSHOT_PATH, STREAM_START_PATH, TEMPERATURE_KEY, RECENT_ACTIVITY_KEYS,
)
from .device import ArloChildDevice
from .util import http_get, http_get_img, the_epoch


class ArloCamera(ArloChildDevice):

    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)
        self._recent = False
        self._recent_job = None
        self._cache_count = None
        self._cached_videos = None
        self._min_days_vdo_cache = self._arlo.cfg.library_days
        self._lock = threading.Condition()
        self._event = threading.Event()
        self._snapshot_time = the_epoch()
        self._stream_url = None
        self._activity_state = set()

    def _parse_statistic(self, data, scale):
        """Parse binary statistics returned from the history API"""
        i = 0
        for byte in bytearray(data):
            i = (i << 8) + byte

        if i == 32768:
            return None

        if scale == 0:
            return i

        return float(i) / (scale * 10)

    def _decode_sensor_data(self, properties):
        """Decode, decompress, and parse the data from the history API"""
        b64_input = ""
        for s in properties.get('payload', []):
            # pylint: disable=consider-using-join
            b64_input += s
        if b64_input == "":
            return None

        decoded = base64.b64decode(b64_input)
        data = zlib.decompress(decoded)
        points = []
        i = 0

        while i < len(data):
            points.append({
                'timestamp': int(1e3 * self._parse_statistic(data[i:(i + 4)], 0)),
                'temperature': self._parse_statistic(data[(i + 8):(i + 10)], 1),
                'humidity': self._parse_statistic(data[(i + 14):(i + 16)], 1),
                'airQuality': self._parse_statistic(data[(i + 20):(i + 22)], 1)
            })
            i += 22

        return points[-1]

    def _dump_activities(self, msg):
        self._arlo.debug("{}::activities={}".format(msg, pprint.pformat(self._activity_state)))

    # Media library has updated, reload todays events.
    def _update_media(self):
        self._arlo.debug('reloading cache for ' + self._name)
        count, videos = self._arlo.ml.videos_for(self)
        if videos:
            captured_today = len([video for video in videos if video.created_today])
            last_captured = videos[0].created_at_pretty(self._arlo.cfg.last_format)
            last_image = videos[0].thumbnail_url
        else:
            captured_today = 0
            last_captured = None
            last_image = None

        # update local copies
        with self._lock:
            self._cache_count = count
            self._cached_videos = videos

        # signal video up!
        self._save_and_do_callbacks(CAPTURED_TODAY_KEY, captured_today)
        if last_captured is not None:
            self._save_and_do_callbacks(LAST_CAPTURE_KEY, last_captured)
        self._do_callbacks(MEDIA_UPLOAD_KEY, True)

        # new snapshot?
        snapshot = self._arlo.ml.snapshot_for(self)
        if snapshot is not None:
            self._arlo.debug('snapshot updated from media ' + self.name)
            self._save(SNAPSHOT_KEY, snapshot.image_url)
            self._arlo.bg.run_low(self._update_snapshot)

        # new image?
        if last_image is not None:
            self._arlo.debug('image updated from media ' + self.name)
            self._save(LAST_IMAGE_KEY, last_image)
            self._arlo.bg.run_low(self._update_image)

    # Update last captured image.
    def _update_image(self):
        # Get image and date, if fails ignore
        img, date = http_get_img(self._load(LAST_IMAGE_KEY, None))
        if img is None:
            self._arlo.debug('failed to load image for ' + self.name)
            return

        # Always make this the latest thumbnail image.
        if self._snapshot_time < date:
            self._arlo.debug('updating image for ' + self.name)
            self._snapshot_time = date
            date = date.strftime(self._arlo.cfg.last_format)
            self._save_and_do_callbacks(LAST_IMAGE_SRC_KEY, 'capture/' + date)
            self._save_and_do_callbacks(LAST_CAPTURE_KEY, date)
            self._save_and_do_callbacks(LAST_IMAGE_DATA_KEY, img)
        else:
            self._arlo.debug('ignoring image for ' + self.name)

    # Update the last snapshot
    def _update_snapshot(self):
        # Get image and date, if fails ignore.
        img, date = http_get_img(self._load(SNAPSHOT_KEY, None))
        if img is None:
            self._arlo.debug('failed to load snapshot for ' + self.name)
            return

        # Always make this the latest snapshot image.
        if self._snapshot_time < date:
            self._arlo.debug('updating snapshot for ' + self.name)
            self._snapshot_time = date
            date = date.strftime(self._arlo.cfg.last_format)
            self._save_and_do_callbacks(LAST_IMAGE_SRC_KEY, 'snapshot/' + date)
            self._save_and_do_callbacks(LAST_IMAGE_DATA_KEY, img)
        else:
            self._arlo.debug('ignoring snapshot for ' + self.name)

        # Clean up snapshot handler.
        self._stop_snapshot()

    def _set_recent(self, timeo):
        with self._lock:
            self._recent = True
            self._arlo.bg.cancel(self._recent_job)
            self._recent_job = self._arlo.bg.run_in(self._clear_recent, timeo)
        self._arlo.debug('turning recent ON for ' + self._name)
        self._do_callbacks(RECENT_ACTIVITY_KEY, True)

    def _clear_recent(self):
        with self._lock:
            self._recent = False
            self._recent_job = None
        self._arlo.debug('turning recent OFF for ' + self._name)
        self._do_callbacks(RECENT_ACTIVITY_KEY, False)

    def _stop_snapshot(self):
        # Signal to anybody waiting.
        with self._lock:
            if not self.is_taking_snapshot:
                return
            self._activity_state.remove("snapshot")
            self._dump_activities("_stop_snapshot")
            self._lock.notify_all()

        self._stop_stream(stopping_for="snapshot-stream")
        self._arlo.debug('snapshot finished, re-signal real state')
        self._save_and_do_callbacks(ACTIVITY_STATE_KEY, self._load(ACTIVITY_STATE_KEY, 'unknown'))

    def _stop_activity(self):
        """Request the camera stop whatever it is doing and return to the idle state.
        """
        self._arlo.be.notify(base=self.base_station,
                             body={
                                 'action': 'set',
                                 'properties': {'activityState': 'idle'},
                                 'publishResponse': True,
                                 'resource': self.resource_id,
                             })

    def _start_stream(self, starting_for):
        with self._lock:
            # Already streaming. Update subactivity as needed.
            if self.is_streaming:
                self._activity_state.add(starting_for)
                self._dump_activities("_start_stream")
                return self._stream_url

            # We can't start a stream if we are doing a straight snapshot.
            if self.is_taking_idle_snapshot:
                return None
            self._activity_state.add(starting_for)
            self._dump_activities("_start_stream2")

        body = {
            'action': 'set',
            'from': self.web_id,
            'properties': {'activityState': 'startUserStream', 'cameraId': self.device_id},
            'publishResponse': True,
            'responseUrl': '',
            'resource': self.resource_id,
            'to': self.parent_id,
            'transId': self._arlo.be.gen_trans_id()
        }
        self._stream_url = self._arlo.be.post(STREAM_START_PATH, body, headers={"xcloudId": self.xcloud_id})
        if self._stream_url is not None:
            self._stream_url = self._stream_url['url'].replace("rtsp://", "rtsps://")
            self._arlo.debug('url={}'.format(self._stream_url))
        else:
            with self._lock:
                self._activity_state = set()
        return self._stream_url

    def _stop_stream(self, stopping_for="user-stream"):
        with self._lock:
            if not self.is_streaming:
                return
            self._activity_state.remove(stopping_for)
            self._dump_activities("_stop_stream")
            if self.is_streaming:
                return
        self._stop_activity()

    def _event_handler(self, resource, event):
        self._arlo.debug(self.name + ' CAMERA got one ' + resource)

        # Stream has stopped or recording has stopped so new media is available.
        if resource == MEDIA_UPLOAD_KEY:

            # Look for easy keys.
            for key in MEDIA_UPLOAD_KEYS:
                value = event.get(key, None)
                if value is not None:
                    self._save_and_do_callbacks(key, value)

            # The last image thumnbail has changed. Queue an update.
            if LAST_IMAGE_KEY in event:
                self._arlo.debug("{} -> thumbnail changed".format(self.name))
                self._arlo.bg.run_low(self._update_image)

            # Recording has stopped so a new video is available. Queue and
            # update.
            if event.get(RECORDING_STOPPED_KEY, False):
                self._arlo.debug("{} -> recording stopped".format(self.name))
                self._arlo.ml.queue_update(self._update_media)

            # A snapshot is ready. Queue an update.
            value = event.get(STREAM_SNAPSHOT_KEY, '')
            if '/snapshots/' in value:
                self._arlo.debug("{} -> snapshot ready".format(self.name))
                self._save(SNAPSHOT_KEY, value)
                self._arlo.bg.run_low(self._update_snapshot)

            # Something just happened.
            self._set_recent(self._arlo.cfg.recent_time)

            return

        # Camera Activity State
        activity = event.get('properties', {}).get('activityState', 'unknown')

        # Camera has gone idle.
        if activity == 'idle':
            # Currently recording or streaming and media upload not working?
            # Then send in a request for updated media.
            if self.is_recording or self.is_streaming:
                self._arlo.debug('got a stream/recording stop')
                for retry in self._arlo.cfg.media_retry:
                    self._arlo.debug("queueing update in {}".format(retry))
                    self._arlo.bg.run_in(self._arlo.ml.queue_update, retry, cb=self._update_media)

                # Something just happened.
                self._set_recent(self._arlo.cfg.recent_time)

            # Reset and signal anybody waiting.
            self._arlo.debug("resetting activity state")
            with self._lock:
                self._activity_state = set()
                #  self._clear_activities()
                self._dump_activities("_event::idle")
                self._lock.notify_all()



        # Camera is active. If we don't know about it then update our status.
        if activity == 'fullFrameSnapshot':
            with self._lock:
                if not self.is_taking_snapshot:
                    self._activity_state.add("snapshot")
                self._dump_activities("_event::snap")
        if activity == 'alertStreamActive':
            with self._lock:
                if not self.is_recording:
                    self._activity_state.add("recording")
                if not self.has_activity("alert-stream-active"):
                    self._activity_state.add("alert-stream-active")
                    self._lock.notify_all()
                self._dump_activities("_event::record")
        if activity == 'userStreamActive':
            with self._lock:
                if not self.is_streaming:
                    self._activity_state.add("streaming")
                if not self.has_activity("user-stream-active"):
                    self._activity_state.add("user-stream-active")
                    self._lock.notify_all()
                self._dump_activities("_event::stream")

        # Snapshot is updated. Queue retrieval.
        if event.get('action', '') == 'fullFrameSnapshotAvailable':
            value = event.get('properties', {}).get('presignedFullFrameSnapshotUrl', None)
            if value is not None:
                self._arlo.debug("{} -> snapshot ready".format(self.name))
                self._save(SNAPSHOT_KEY, value)
                self._arlo.bg.run_low(self._update_snapshot)

        # Ambient sensors update, decode and push changes.
        if resource.endswith('/ambientSensors/history'):
            data = self._decode_sensor_data(event.get('properties', {}))
            if data is not None:
                self._save_and_do_callbacks('temperature', data.get('temperature'))
                self._save_and_do_callbacks('humidity', data.get('humidity'))
                self._save_and_do_callbacks('airQuality', data.get('airQuality'))

        # Properties settings.
        properties = event.get("properties", {})

        # Anything to trip recent activity?
        for key in properties:
            if key in RECENT_ACTIVITY_KEYS:
                self._arlo.debug('recent activity key')
                self._set_recent(self._arlo.cfg.recent_time)

        # Night light status.
        nightlight = properties.get(NIGHTLIGHT_KEY, None)
        if nightlight is not None:
            self._arlo.debug("got a night light {}".format(nightlight.get("enabled", False)))
            if nightlight.get("enabled", False) is True:
                self._save_and_do_callbacks(LAMP_STATE_KEY, "on")
            else:
                self._save_and_do_callbacks(LAMP_STATE_KEY, "off")

            brightness = nightlight.get("brightness")
            if brightness is not None:
                self._save_and_do_callbacks(LIGHT_BRIGHTNESS_KEY, brightness)

            mode = nightlight.get("mode")
            if mode is not None:
                rgb = nightlight.get("rgb")
                temperature = nightlight.get("temperature")

                light_mode = {
                    'mode': mode
                }

                if rgb is not None:
                    light_mode['rgb'] = rgb
                if temperature is not None:
                    light_mode['temperature'] = temperature

                self._save_and_do_callbacks(LIGHT_MODE_KEY, light_mode)

        # Spotlight status.
        spotlight = properties.get(SPOTLIGHT_KEY, None)
        if spotlight is not None:
            self._arlo.debug("got a spotlight {}".format(spotlight.get("enabled", False)))
            if spotlight.get("enabled", False) is True:
                self._save_and_do_callbacks(SPOTLIGHT_KEY, "on")
            else:
                self._save_and_do_callbacks(SPOTLIGHT_KEY, "off")

            brightness = spotlight.get("intensity")
            if brightness is not None:
                self._save_and_do_callbacks(SPOTLIGHT_BRIGHTNESS_KEY, brightness)

        # Floodlight status.
        floodlight = properties.get(FLOODLIGHT_KEY, None)
        if floodlight is not None:
            self._arlo.debug("got a flood light {}".format(floodlight.get("on", False)))
            self._save_and_do_callbacks(FLOODLIGHT_KEY, floodlight)

        # Audio analytics.
        audioanalytics = properties.get(AUDIO_ANALYTICS_KEY, None)
        if audioanalytics is not None:
            triggered = audioanalytics.get(CRY_DETECTION_KEY, {}).get("triggered", False)
            self._save_and_do_callbacks(CRY_DETECTION_KEY, triggered)

        # Pass event to lower level.
        super()._event_handler(resource, event)

    @property
    def resource_type(self):
        return "cameras"

    @property
    def last_thumbnail(self):
        """Returns the URL of the last image as reported by Arlo.
        """
        return self._load(LAST_IMAGE_KEY, None)

    @property
    def last_snapshot(self):
        """Returns the URL of the last snapshot as reported by Arlo.
        """
        return self._load(SNAPSHOT_KEY, None)

    @property
    def last_image(self):
        """Returns the URL of the last snapshot or image taken.

        Will pick snapshot or image based on most recently updated.
        """
        image = None
        if self.last_image_source.startswith('snapshot/'):
            image = self.last_snapshot
        if image is None:
            image = self.last_thumbnail
        return image

    @property
    def last_image_from_cache(self):
        """Returns the last image or snapshot in binary format.

        :return: Binary reprsensation of the last image.
        :rtype: bytearray
        """
        return self._load(LAST_IMAGE_DATA_KEY, self._arlo.blank_image)

    @property
    def last_image_source(self):
        """Returns a string describing what triggered the last image capture.

        Currently either `capture/${date}` or `snapshot/${date}`.
        """
        return self._load(LAST_IMAGE_SRC_KEY, '')

    @property
    def last_video(self):
        """Returns a video object describing the last captured video.

        :return: Video object or `None` if no videos present.
        :rtype: ArloVideo
        """
        with self._lock:
            if self._cached_videos:
                return self._cached_videos[0]
        return None

    def last_n_videos(self, count):
        """Returns the last count video objects describing the last captured videos.

        :return: `count` video objects or `None` if no videos present.
        :rtype: list(ArloVideo)
        """
        with self._lock:
            if self._cached_videos:
                return self._cached_videos[:count]
        return []

    @property
    def last_capture(self):
        """Returns a date string showing when the last video was captured.

        It uses the format returned by `last_capture_date_format`.
        """
        return self._load(LAST_CAPTURE_KEY, None)

    @property
    def last_capture_date_format(self):
        """Returns a date format string used by the last_capture function.

        You can set this value in the parameters passed to PyArlo.
        """
        return self._arlo.cfg.last_format

    @property
    def brightness(self):
        """Returns the camera brightness setting.
        """
        return self._load(BRIGHTNESS_KEY, None)

    @property
    def flip_state(self):
        """Returns `True` if the camera is flipped, `False` otherwise.
        """
        return self._load(FLIP_KEY, None)

    @property
    def mirror_state(self):
        """Returns `True` if the camera is mirrored, `False` otherwise.
        """
        return self._load(MIRROR_KEY, None)

    @property
    def motion_detection_sensitivity(self):
        """Returns the camera motion sensitivity setting.
        """
        return self._load(MOTION_SENS_KEY, None)

    @property
    def powersave_mode(self):
        """Returns `True` if the camera is on power save mode, `False` otherwise.
        """
        return self._load(POWER_SAVE_KEY, None)

    @property
    def unseen_videos(self):
        """Returns the camera unseen video count. """
        return self._load(MEDIA_COUNT_KEY, 0)

    @property
    def captured_today(self):
        """Returns the number of videos captured today. """
        return self._load(CAPTURED_TODAY_KEY, 0)

    @property
    def min_days_vdo_cache(self):
        return self._min_days_vdo_cache

    @min_days_vdo_cache.setter
    def min_days_vdo_cache(self, value):
        self._min_days_vdo_cache = value

    def update_media(self, wait=None):
        """Requests latest list of recordings from the backend server.

        :param wait if True then wait for completion, if False then don't wait,
        if None then use synchronous_mode setting.

        Reloads the videos library from Arlo. 
        """
        if wait is None:
            wait = self._cfg.synchronous_mode
        if wait:
            self._arlo.debug('doing media update')
            self._update_media()
        else:
            self._arlo.debug('queueing media update')
            self._arlo.bg.run_low(self._update_media)

    def update_last_image(self, wait=None):
        """Requests last thumbnail from the backend server. 

        :param wait if True then wait for completion, if False then don't wait,
        if None then use synchronous_mode setting.

        Updates the last image.
        """
        if wait is None:
            wait = self._cfg.synchronous_mode
        if wait:
            self._arlo.debug('doing image update')
            self._update_image()
        else:
            self._arlo.debug('queueing image update')
            self._arlo.bg.run_low(self._update_image)

    def update_ambient_sensors(self):
        """Requests the latest temperature, humidity and air quality settings.

        Queues a job that requests the info from Arlo.
        """
        if self.model_id == 'ABC1000':
            self._arlo.be.notify(base=self.base_station,
                                 body={"action": "get",
                                       "resource": 'cameras/{}/ambientSensors/history'.format(self.device_id),
                                       "publishResponse": False})

    def _take_streaming_snapshot(self):
        body = {
            'xcloudId': self.xcloud_id,
            'parentId': self.parent_id,
            'deviceId': self.device_id,
            'olsonTimeZone': self.timezone,
        }
        self._save_and_do_callbacks(ACTIVITY_STATE_KEY, 'fullFrameSnapshot')
        self._arlo.bg.run(self._arlo.be.post, path=STREAM_SNAPSHOT_PATH, params=body,
                          headers={"xcloudId": self.xcloud_id})

    def _take_idle_snapshot(self):
        body = {
            'action': 'set',
            'from': self.web_id,
            'properties': {'activityState': 'fullFrameSnapshot'},
            'publishResponse': True,
            'resource': self.resource_id,
            'to': self.parent_id,
            'transId': self._arlo.be.gen_trans_id()
        }
        self._arlo.bg.run(self._arlo.be.post, path=IDLE_SNAPSHOT_PATH, params=body,
                          headers={"xcloudId": self.xcloud_id})

    def request_snapshot(self):
        with self._lock:
            if self.is_taking_snapshot:
                return
            stream_snapshot = self.is_streaming
            self._activity_state.add("snapshot")
            self._dump_activities("request_snapshot")

        if stream_snapshot:
            self._arlo.debug("streaming/recording snapshot")
            self._take_streaming_snapshot()
        else:
            self._arlo.debug("idle snapshot")
            self._take_idle_snapshot()

        for check in self._arlo.cfg.snapshot_checks:
            self._arlo.debug("queueing snapshot check in {}".format(check))
            self._arlo.bg.run_in(self._arlo.ml.queue_update, check, cb=self._update_media)
        self._arlo.debug("handle dodgy cameras")
        self._arlo.bg.run_in(self._stop_snapshot, self._arlo.cfg.snapshot_timeout)

    def get_snapshot(self, timeout=30):
        """Gets a snapshot from the camera and returns it.

        :param timeout: how long to wait, in seconds, before stopping the snapshot attempt
        :return: a binary represention of the image, or the last image if snapshot timed out
        :rtype: bytearray
        """
        self.request_snapshot()

        mnow = time.monotonic()
        mend = mnow + timeout
        with self._lock:
            while mnow < mend and self.is_taking_snapshot:
                self._lock.wait(mend - mnow)
                mnow = time.monotonic()
        return self.last_image_from_cache

    @property
    def is_taking_snapshot(self):
        """Returns `True` if camera is taking a snapshot, `False` otherwise.
        """
        return "snapshot" in self._activity_state

    @property
    def is_taking_idle_snapshot(self):
        """Returns `True` if camera is taking a non-streaming snapshot, `False`
        otherwise.
        """
        return "snapshot" in self._activity_state and len(self._activity_state) == 1

    @property
    def is_recording(self):
        """Returns `True` if camera is recording a video, `False` otherwise.
        """
        return "recording" in self._activity_state

    @property
    def is_streaming(self):
        """Returns `True` if camera is streaming a video, `False` otherwise.
        """
        return "streaming" in self._activity_state or \
               "user-stream" in self._activity_state or \
               "recording-stream" in self._activity_state or \
               "snapshot-stream" in self._activity_state

    def has_activity(self, activity):
        """ Returns `True` is camera is performing a particular activity,
        `False` otherwise.
        """
        return activity in self._activity_state

    @property
    def was_recently_active(self):
        """Returns `True` if camera was recently active, `False` otherwise.
        """
        return self._recent

    @property
    def state(self):
        """Returns the camera's current state.
        """
        if not self.is_on:
            return 'off'
        if self.is_taking_snapshot or self.has_activity("snapshot-stream"):
            if self.is_recording or self.has_activity("recording-stream"):
                return 'recording + snapshot'
            if self.has_activity("streaming") or self.has_activity("user-stream"):
                return 'streaming + snapshot'
            return 'taking snapshot'
        if self.is_recording or self.has_activity("recording-stream"):
            return 'recording'
        if self.is_streaming:
            return 'streaming'
        if self.was_recently_active:
            return 'recently active'
        return super().state

    def get_stream(self):
        """Start a stream and return the URL for it.

        Code does nothing with the url, it's up to you to pass the url to something.

        The stream will stop if nothing connects to it within 30 seconds.
        """
        return self._start_stream("user-stream")

    def start_stream(self):
        """Start a stream and return the URL for it.

        Code does nothing with the url, it's up to you to pass the url to something.

        The stream will stop if nothing connects to it within 30 seconds.
        """
        return self._start_stream("user-stream")

    def start_snapshot_stream(self):
        return self._start_stream("snapshot-stream")

    def start_recording_stream(self):
        return self._start_stream("recording-stream")

    def stop_stream(self):
        self._stop_stream("user-stream")

    def stop_snapshot_stream(self):
        self._stop_stream("snapshot-stream")

    def stop_recording_stream(self):
        self._stop_stream("recording-stream")

    def wait_for_user_stream(self, timeout=15):
        self._arlo.debug('waiting for stream')
        mnow = time.monotonic()
        mend = mnow + timeout
        with self._lock:
            while mnow < mend and not self.has_activity("user-stream-active"):
                self._lock.wait(mend - mnow)
                mnow = time.monotonic()
            self._arlo.debug("got {}".format(self.has_activity("user-stream-active")))
            active = self.has_activity("user-stream-active")

        # Is active, give a small delay to get going.
        if active:
            self._event.wait(self._arlo.cfg.user_stream_delay)
        return active

    def get_video(self):
        """Download and return the last recorded video.

        **Note:** Prefer getting the url and downloading it yourself.
        """
        video = self.last_video
        if video is not None:
            return http_get(video.video_url)
        return None

    def stop_activity(self):
        """Request the camera stop whatever it is doing and return to the idle state.
        """
        # has_any_activity
        self._stop_activity()
        return True

    def start_recording(self, duration=None):
        """Request the camera start recording.

        :param duration: seconds for recording to run, `None` means no stopping.

        **Note:** Arlo will stop the recording after 30 seconds if nothing
        connects to the stream.
        **Note:** Arlo will stop the recording after 30 minutes anyway.
        """
        with self._lock:
            if not self.is_streaming:
                return None
            if self.is_recording:
                return self._stream_url
            self._activity_state.add("recording")
            self._dump_activities("start_recording")

        body = {
            'parentId': self.parent_id,
            'deviceId': self.device_id,
            'olsonTimeZone': self.timezone,
        }
        self._arlo.debug('starting recording')
        self._save_and_do_callbacks(ACTIVITY_STATE_KEY, 'alertStreamActive')
        self._arlo.bg.run(self._arlo.be.post, path=RECORD_START_PATH, params=body,
                          headers={"xcloudId": self.xcloud_id})

        # Queue up stop.
        if duration is not None:
            self._arlo.debug('queueing stop')
            self._arlo.bg.run_in(self.stop_recording, duration)

        return self._stream_url

    def stop_recording(self):
        """Request the camera stop recording.
        """
        with self._lock:
            if not self.is_recording:
                return
            self._activity_state.remove("recording")
            self._dump_activities("stop_recording")

        body = {
            'parentId': self.parent_id,
            'deviceId': self.device_id,
        }
        self._arlo.debug('stopping recording')
        self._arlo.bg.run(self._arlo.be.post, path=RECORD_STOP_PATH, params=body,
                          headers={"xcloudId": self.xcloud_id})

        # stop stream
        self._arlo.bg.run_in(self.stop_recording_stream, 1)

    @property
    def _siren_resource_id(self):
        return "siren/{}".format(self.device_id)

    @property
    def siren_state(self):
        return self._load(SIREN_STATE_KEY, "off")

    def siren_on(self, duration=300, volume=8):
        """Turn camera siren on.

        Does nothing if camera doesn't support sirens.

        :param duration: how long, in seconds, to sound for
        :param volume: how long, from 1 to 8, to sound
        """
        body = {
            'action': 'set',
            'resource': self._siren_resource_id,
            'publishResponse': True,
            'properties': {'sirenState': 'on', 'duration': int(duration), 'volume': int(volume), 'pattern': 'alarm'}
        }
        self._arlo.be.notify(base=self, body=body)

    def siren_off(self):
        """Turn camera siren off.

        Does nothing if camera doesn't support sirens.
        """
        body = {
            'action': 'set',
            'resource': self._siren_resource_id,
            'publishResponse': True,
            'properties': {'sirenState': 'off'}
        }
        self._arlo.be.notify(base=self, body=body)

    @property
    def is_on(self):
        """Returns `True` if the camera turned on.
        """
        return not self._load(PRIVACY_KEY, False)

    def turn_on(self):
        """Turn the camera on.
        """
        body = {
            'action': 'set',
            'resource': self.resource_id,
            'publishResponse': True,
            'properties': {'privacyActive': False}
        }
        self._arlo.be.notify(base=self.base_station, body=body)

    def turn_off(self):
        """Turn the camera off.
        """
        body = {
            'action': 'set',
            'resource': self.resource_id,
            'publishResponse': True,
            'properties': {'privacyActive': True}
        }
        self._arlo.be.notify(base=self.base_station, body=body)

    def get_audio_playback_status(self):
        """Gets the current playback status and available track list
        """
        body = {
            'action': 'get',
            'publishResponse': True,
            'resource': 'audioPlayback'
        }
        self._arlo.be.notify(base=self, body=body)

    def play_track(self, track_id=None, position=0):
        """Play the track. A track ID of None will resume playing the current
        track.

        :param track_id: track id
        :param position: position in the track
        """
        body = {
            'publishResponse': True,
            'resource': MEDIA_PLAYER_RESOURCE_ID,
        }

        if track_id is not None:
            body.update({
                'action': 'playTrack',
                'properties': {
                    AUDIO_TRACK_KEY: track_id,
                    AUDIO_POSITION_KEY: position
                }
            })
        else:
            body.update({
                'action': 'play',
            })
        self._arlo.be.notify(base=self, body=body)

    def pause_track(self):
        """Pause the playing track.
        """
        body = {
            'action': 'pause',
            'publishResponse': True,
            'resource': MEDIA_PLAYER_RESOURCE_ID,
        }
        self._arlo.be.notify(base=self, body=body)

    def previous_track(self):
        """Skips to the previous track in the playlist.
        """
        body = {
            'action': 'prevTrack',
            'publishResponse': True,
            'resource': MEDIA_PLAYER_RESOURCE_ID,
        }
        self._arlo.be.notify(base=self, body=body)

    def next_track(self):
        """Skips to the next track in the playlist.
        """
        body = {
            'action': 'nextTrack',
            'publishResponse': True,
            'resource': MEDIA_PLAYER_RESOURCE_ID,
        }
        self._arlo.be.notify(base=self, body=body)

    def set_music_loop_mode_continuous(self):
        """Sets the music loop mode to repeat the entire playlist.
        """
        body = {
            'action': 'set',
            'publishResponse': True,
            'resource': 'audioPlayback/config',
            'properties': {
                'config': {
                    'loopbackMode': 'continuous'
                }
            }
        }
        self._arlo.be.notify(base=self, body=body)

    def set_music_loop_mode_single(self):
        """Sets the music loop mode to repeat the current track.
        """
        body = {
            'action': 'set',
            'publishResponse': True,
            'resource': 'audioPlayback/config',
            'properties': {
                'config': {
                    'loopbackMode': 'singleTrack'
                }
            }
        }
        self._arlo.be.notify(base=self, body=body)

    def set_shuffle(self, shuffle=True):
        """Sets playback to shuffle.

        :param shuffle: `True` to turn on shuffle.
        """
        body = {
            'action': 'set',
            'publishResponse': True,
            'resource': 'audioPlayback/config',
            'properties': {
                'config': {
                    'shuffleActive': shuffle
                }
            }
        }
        self._arlo.be.notify(base=self, body=body)

    def set_volume(self, mute=False, volume=50):
        """Sets the music volume.

        :param mute: `True` to mute the volume.
        :param volume: set volume (0-100)
        """
        body = {
            'action': 'set',
            'publishResponse': True,
            'resource': self.resource_id,
            'properties': {
                'speaker': {
                    'mute': mute,
                    'volume': volume
                }
            }
        }
        self._arlo.be.notify(base=self, body=body)

    def _set_nightlight_properties(self, properties):
        self._arlo.debug('{}: setting nightlight properties: {}'.format(self._name, properties))
        self._arlo.be.notify(base=self.base_station,
                             body={
                                 'action': 'set',
                                 'properties': {
                                     'nightLight': properties
                                 },
                                 'publishResponse': True,
                                 'resource': self.resource_id,
                             })
        return True

    def nightlight_on(self):
        """Turns the nightlight on.
        """
        return self._set_nightlight_properties({
            'enabled': True
        })

    def nightlight_off(self):
        """Turns the nightlight off.
        """
        return self._set_nightlight_properties({
            'enabled': False
        })

    def set_nightlight_brightness(self, brightness):
        """Sets the nightlight brightness.

        :param brightness: brightness (0-255)
        """
        return self._set_nightlight_properties({
            'brightness': brightness
        })

    def set_nightlight_rgb(self, red=255, green=255, blue=255):
        """Turns the nightlight color to the specified RGB value.

        :param red: red value
        :param green: green value
        :param blue: blue value
        """
        return self._set_nightlight_properties({
            'mode': 'rgb',
            'rgb': {'red': red, 'green': green, 'blue': blue}
        })

    def set_nightlight_color_temperature(self, temperature):
        """Turns the nightlight to the specified Kelvin color temperature.

        :param temperature: temperature, in Kelvin
        """
        return self._set_nightlight_properties({
            'mode': 'temperature',
            'temperature': str(temperature)
        })

    def set_nightlight_mode(self, mode):
        """Turns the nightlight to a particular mode.

        :param mode: either `rgb`, `temperature` or `rainbow`
        :return:
        """
        return self._set_nightlight_properties({
            'mode': mode
        })

    def _set_spotlight_properties(self, properties):
        self._arlo.debug('{}: setting spotlight properties: {}'.format(self._name, properties))
        self._arlo.be.notify(base=self.base_station,
                             body={
                                 'action': 'set',
                                 'properties': {
                                     'spotlight': properties
                                 },
                                 'publishResponse': True,
                                 'resource': self.resource_id,
                             })
        return True

    def set_spotlight_on(self):
        """Turns the spotlight on
        """
        return self._set_spotlight_properties({
            'enabled': True
        })

    def set_spotlight_off(self):
        """Turns the spotlight off
        """
        return self._set_spotlight_properties({
            'enabled': False
        })

    def set_spotlight_brightness(self, brightness):
        """Sets the nightlight brightness.

        :param brightness: brightness (0-255)
        """
        # Note: Intensity is 0-100 scale, which we map from 0-255 to
        #       provide an API consistent with nightlight brightness
        return self._set_spotlight_properties({
            'intensity': (brightness / 255 * 100)
        })

    def _set_floodlight_properties(self, properties):
        self._arlo.debug(
            "{}: setting floodlight properties: {}".format(self._name, properties)
        )
        self._arlo.be.notify(
            base=self.base_station,
            body={
                "action": "set",
                "properties": {"floodlight": properties},
                "publishResponse": True,
                "resource": self.resource_id,
            },
        )
        return True

    def floodlight_on(self):
        """Turns the floodlight on."""
        return self._set_floodlight_properties({"on": True})

    def floodlight_off(self):
        """Turns the floodlight off."""
        return self._set_floodlight_properties({"on": False})

    def set_floodlight_brightness(self, brightness):
        """Turns the floodlight brightness value (0-255)."""
        percentage = int(brightness / 255 * 100)
        return self._set_floodlight_properties(
            {
                FLOODLIGHT_BRIGHTNESS1_KEY: percentage,
                FLOODLIGHT_BRIGHTNESS2_KEY: percentage,
            }
        )

    def has_capability(self, cap):
        if cap in (MOTION_DETECTED_KEY, BATTERY_KEY, SIGNAL_STR_KEY):
            return True
        if cap in (LAST_CAPTURE_KEY, CAPTURED_TODAY_KEY, RECENT_ACTIVITY_KEY):
            return True
        if cap in (AUDIO_DETECTED_KEY,):
            if self.model_id.startswith(
                ('VMC4030', 'VMC4040', 'VMC5040', 'ABC1000', 'FB1001')):
                return True
            if self.device_type.startswith('arloq'):
                return True
        if cap in (SIREN_STATE_KEY,):
            if self.model_id.startswith(('VMC4040', 'VMC5040', 'FB1001')):
                return True
        if cap in (SPOTLIGHT_KEY,):
            if self.model_id.startswith(('VMC4040', 'VMC5040')):
                return True
        if cap in (TEMPERATURE_KEY, HUMIDITY_KEY, AIR_QUALITY_KEY):
            if self.model_id.startswith('ABC1000'):
                return True
        if cap in (MEDIA_PLAYER_KEY, NIGHTLIGHT_KEY, CRY_DETECTION_KEY):
            if self.model_id.startswith('ABC1000'):
                return True
        if cap in (FLOODLIGHT_KEY,):
            if self.model_id.startswith('FB1001'):
                return True
        if cap in (CONNECTION_KEY,):
            # These devices are their own base stations so don't re-add connection key.
            if self.model_id.startswith(('ABC1000', 'FB1001A')):
                return False;
            if self.device_type in ('arloq', 'arloqs'):
                return False
        return super().has_capability(cap)
