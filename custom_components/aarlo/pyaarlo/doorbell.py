from .constant import (
    BATTERY_KEY,
    BUTTON_PRESSED_KEY,
    CHIMES_KEY,
    CONNECTION_KEY,
    MODEL_WIRED_VIDEO_DOORBELL,
    MODEL_WIREFREE_VIDEO_DOORBELL,
    MOTION_DETECTED_KEY,
    SIGNAL_STR_KEY,
    SILENT_MODE_ACTIVE_KEY,
    SILENT_MODE_CALL_KEY,
    SILENT_MODE_KEY,
    SIREN_STATE_KEY,
)
from .device import ArloChildDevice


class ArloDoorBell(ArloChildDevice):
    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)
        self._motion_time_job = None
        self._ding_time_job = None
        self._has_motion_detect = False
        self._chimes = {}

    def _motion_stopped(self):
        self._save_and_do_callbacks(MOTION_DETECTED_KEY, False)
        with self._lock:
            self._motion_time_job = None

    def _button_unpressed(self):
        self._save_and_do_callbacks(BUTTON_PRESSED_KEY, False)
        with self._lock:
            self._ding_time_job = None

    def _event_handler(self, resource, event):
        self._arlo.debug(self.name + " DOORBELL got one " + resource)

        # create fake motion/button press event...
        if resource == self.resource_id:
            props = event.get("properties", {})

            # Newer doorbells send a motionDetected True followed by False. If we
            # see this then turn off connectionState checking.
            if MOTION_DETECTED_KEY in props:
                self._arlo.debug(self.name + " has motion detection support")
                self._has_motion_detect = True

            # Older doorbells signal a connectionState as available when motion
            # is detected. We check the properties length to not confuse it
            # with a device update. There is no motion stopped event so set a
            # timer to turn off the motion detect.
            if len(props) == 1 and not self._has_motion_detect:
                if props.get(CONNECTION_KEY, "") == "available":
                    self._save_and_do_callbacks(MOTION_DETECTED_KEY, True)
                    with self._lock:
                        self._arlo.bg.cancel(self._motion_time_job)
                        self._motion_time_job = self._arlo.bg.run_in(
                            self._motion_stopped, self._arlo.cfg.db_motion_time
                        )

            # For button presses we only get a buttonPressed notification, not
            # a "no longer pressed" notification - set a timer to turn off the
            # press.
            if BUTTON_PRESSED_KEY in props:
                self._save_and_do_callbacks(BUTTON_PRESSED_KEY, True)
                with self._lock:
                    self._arlo.bg.cancel(self._ding_time_job)
                    self._ding_time_job = self._arlo.bg.run_in(
                        self._button_unpressed, self._arlo.cfg.db_ding_time
                    )

            # Save out chimes
            if CHIMES_KEY in props:
                self._chimes = props[CHIMES_KEY]

            # Pass silent mode notifications so we can track them in the "ding"
            # entity.
            silent_mode = props.get(SILENT_MODE_KEY, {})
            if silent_mode:
                self._save_and_do_callbacks(SILENT_MODE_KEY, silent_mode)

        # pass on to lower layer
        super()._event_handler(resource, event)

    @property
    def resource_type(self):
        return "doorbells"

    @property
    def is_video_doorbell(self):
        return self.model_id.startswith(
            MODEL_WIRED_VIDEO_DOORBELL
        ) or self.model_id.startswith(MODEL_WIREFREE_VIDEO_DOORBELL)

    def has_capability(self, cap):
        if cap in (BUTTON_PRESSED_KEY, SILENT_MODE_KEY):
            return True
        if cap in (MOTION_DETECTED_KEY, BATTERY_KEY, SIGNAL_STR_KEY):
            # video doorbell provides these as a camera type
            if not self.is_video_doorbell:
                return True
        if cap in (CONNECTION_KEY,):
            # If video door bell is its own base station then don't provide connectivity here.
            if self.is_video_doorbell and self.parent_id == self.device_id:
                return False
        if cap in (SIREN_STATE_KEY,):
            if self.is_video_doorbell:
                return True
        return super().has_capability(cap)

    def update_silent_mode(self):
        """Requests the latest silent mode settings.

        Queues a job that requests the info from Arlo.
        """
        self._arlo.be.notify(
            base=self.base_station,
            body={
                "action": "get",
                "resource": self.resource_id,
                "publishResponse": False,
            },
        )

    def _build_chimes(self, on_or_off):
        chimes = {"traditional": on_or_off}
        for chime in self._chimes:
            chimes[chime] = on_or_off
        return chimes

    def _silence(self, active, calls, chimes):

        # Build settings
        silence_settings = {
            SILENT_MODE_ACTIVE_KEY: active,
            SILENT_MODE_CALL_KEY: calls,
        }
        if chimes:
            silence_settings[CHIMES_KEY] = chimes

        # Build request
        properties = {SILENT_MODE_KEY: silence_settings}
        self._arlo.debug(self.name + " silence is " + str(properties))

        # Send out request.
        response = self._arlo.be.notify(
            base=self.base_station,
            body={
                "action": "set",
                "properties": properties,
                "publishResponse": True,
                "resource": self.resource_id,
            },
            wait_for="response",
        )

        # Not none means a 200 so we assume it works until told otherwise.
        if response is not None:
            self._arlo.bg.run(
                self._save_and_do_callbacks,
                attr=SILENT_MODE_KEY,
                value=silence_settings,
            )

    def silence_off(self):
        self._silence(False, False, {})

    def silence_on(self):
        self._silence(True, True, self._build_chimes(True))

    def silence_chimes(self):
        self._silence(True, False, self._build_chimes(True))

    def silence_calls(self):
        self._silence(True, True, self._build_chimes(False))

    @property
    def is_silenced(self):
        return self._load(SILENT_MODE_KEY, {}).get(SILENT_MODE_ACTIVE_KEY, False)

    @property
    def calls_are_silenced(self):
        return self._load(SILENT_MODE_KEY, {}).get(SILENT_MODE_CALL_KEY, False)

    @property
    def chimes_are_silenced(self):
        for on_or_off in self._load(SILENT_MODE_KEY, {}).get(CHIMES_KEY, {}).values():
            if on_or_off is True:
                return True
        return False

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
            "action": "set",
            "resource": self._siren_resource_id,
            "publishResponse": True,
            "properties": {
                "sirenState": "on",
                "duration": int(duration),
                "volume": int(volume),
                "pattern": "alarm",
            },
        }
        self._arlo.be.notify(base=self, body=body)

    def siren_off(self):
        """Turn camera siren off.

        Does nothing if camera doesn't support sirens.
        """
        body = {
            "action": "set",
            "resource": self._siren_resource_id,
            "publishResponse": True,
            "properties": {"sirenState": "off"},
        }
        self._arlo.be.notify(base=self, body=body)
