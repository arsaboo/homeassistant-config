import time

from .constant import (AUTOMATION_PATH, DEFAULT_MODES, DEFINITIONS_PATH, CONNECTION_KEY,
                       MODE_ID_TO_NAME_KEY, MODE_KEY,
                       MODE_NAME_TO_ID_KEY, MODE_IS_SCHEDULE_KEY,
                       SCHEDULE_KEY, SIREN_STATE_KEY, TEMPERATURE_KEY, HUMIDITY_KEY, AIR_QUALITY_KEY)
from .device import ArloDevice
from .util import time_to_arlotime

day_of_week = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su', 'Mo']


class ArloBase(ArloDevice):

    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)
        self._refresh_rate = 15
        self._schedules = None

    def _id_to_name(self, mode_id):
        return self._load([MODE_ID_TO_NAME_KEY, mode_id], None)

    def _id_is_schedule(self, mode_id):
        return self._load([MODE_IS_SCHEDULE_KEY, mode_id], False)

    def _name_to_id(self, mode_name):
        return self._load([MODE_NAME_TO_ID_KEY, mode_name.lower()], None)

    def _parse_modes(self, modes):
        for mode in modes:
            mode_id = mode.get('id', None)
            mode_name = mode.get('name', '')
            if mode_name == '':
                mode_name = mode.get('type', '')
                if mode_name == '':
                    mode_name = mode_id
            if mode_id and mode_name != '':
                self._arlo.debug(mode_id + '<=M=>' + mode_name)
                self._save([MODE_ID_TO_NAME_KEY, mode_id], mode_name)
                self._save([MODE_NAME_TO_ID_KEY, mode_name.lower()], mode_id)
                self._save([MODE_IS_SCHEDULE_KEY, mode_name.lower()], False)

    def schedule_to_modes(self):
        if self._schedules is None:
            return []
        now = time.localtime()
        day = day_of_week[now.tm_wday]
        minute = (now.tm_hour * 60) + now.tm_min
        for schedule in self._schedules:
            if not schedule.get('enabled', False):
                continue
            for action in schedule.get('schedule', []):
                if day in action.get('days', []):
                    start = action.get('startTime', 65535)
                    duration = action.get('duration', 65536)
                    if start <= minute < (start + duration):
                        modes = action.get('startActions', {}).get('enableModes', None)
                        if modes:
                            self._arlo.debug("schdule={}".format(modes[0]))
                            return modes
        return []

    def _parse_schedules(self, schedules):
        self._schedules = schedules
        for schedule in schedules:
            schedule_id = schedule.get('id', None)
            schedule_name = schedule.get('name', '')
            if schedule_name == '':
                schedule_name = schedule_id
            if schedule_id and schedule_name != '':
                self._arlo.debug(schedule_id + '<=S=>' + schedule_name)
                self._save([MODE_ID_TO_NAME_KEY, schedule_id], schedule_name)
                self._save([MODE_NAME_TO_ID_KEY, schedule_name.lower()], schedule_id)
                self._save([MODE_IS_SCHEDULE_KEY, schedule_name.lower()], True)

    def _set_mode_or_schedule(self, event):
        # schedule on or off?
        schedule_ids = event.get('activeSchedules', [])
        if schedule_ids:
            self._arlo.debug(self.name + ' schedule change ' + schedule_ids[0])
            schedule_name = self._id_to_name(schedule_ids[0])
            self._save_and_do_callbacks(SCHEDULE_KEY, schedule_name)
        else:
            self._arlo.debug(self.name + ' schedule cleared ')
            self._save_and_do_callbacks(SCHEDULE_KEY, None)

        # mode present? we just set to that one... If no mode but schedule then
        # try to parse that out
        mode_ids = event.get('activeModes', [])
        if not mode_ids and schedule_ids:
            mode_ids = self.schedule_to_modes()
        if mode_ids:
            self._arlo.debug(self.name + ' mode change ' + mode_ids[0])
            mode_name = self._id_to_name(mode_ids[0])
            self._save_and_do_callbacks(MODE_KEY, mode_name)

    def _event_handler(self, resource, event):
        self._arlo.debug(self.name + ' BASE got ' + resource)

        # modes on base station
        if resource == 'modes':
            props = event.get('properties', {})

            # list of modes - recheck?
            self._parse_modes(props.get('modes', []))

            # mode change?
            if 'activeMode' in props:
                self._save_and_do_callbacks(MODE_KEY, self._id_to_name(props['activeMode']))
            elif 'active' in props:
                self._save_and_do_callbacks(MODE_KEY, self._id_to_name(props['active']))

        # mode change?
        elif resource == 'activeAutomations':
            self._set_mode_or_schedule(event)

        # schedule has changed, so reload
        elif resource == 'automationRevisionUpdate':
            self.update_modes()

        # pass on to lower layer
        else:
            super()._event_handler(resource, event)

    @property
    def _v1_modes(self):
        if self._arlo.cfg.mode_api.lower() == 'v1':
            self._arlo.vdebug('forced v1 api')
            return True
        if self._arlo.cfg.mode_api.lower() == 'v2':
            self._arlo.vdebug('forced v2 api')
            return False
        if self.model_id == 'ABC1000' or self.device_type == 'arloq' or self.device_type == 'arloqs':
            self._arlo.vdebug('deduced v1 api')
            return True
        else:
            self._arlo.vdebug('deduced v2 api')
            return False

    @property
    def available_modes(self):
        return list(self.available_modes_with_ids.keys())

    @property
    def available_modes_with_ids(self):
        modes = {}
        for key, mode_id in self._load_matching([MODE_NAME_TO_ID_KEY, '*']):
            modes[key.split('/')[-1]] = mode_id
        if not modes:
            modes = DEFAULT_MODES
        return modes

    @property
    def mode(self):
        return self._load(MODE_KEY, 'unknown')

    @mode.setter
    def mode(self, mode_name):
        mode_id = self._name_to_id(mode_name)
        if mode_id:

            # Schedule or mode? Manually set schedule key.
            if self._id_is_schedule(mode_id):
                active = 'activeSchedules'
                inactive = 'activeModes'
                self._save_and_do_callbacks(SCHEDULE_KEY, mode_name)
            else:
                active = 'activeModes'
                inactive = 'activeSchedules'
                self._save_and_do_callbacks(SCHEDULE_KEY, None)

            # Post change.
            self._arlo.debug(self.name + ':new-mode=' + mode_name + ',id=' + mode_id)
            if self._v1_modes:
                self._arlo.bg.run(self._arlo.be.notify, base=self,
                                  body={"action": "set",
                                        "resource": "modes",
                                        "publishResponse": True,
                                        "properties": {"active": mode_id}})
            else:
                def _set_mode_v2_cb():
                    params = {'activeAutomations':
                                  [{'deviceId': self.device_id,
                                    'timestamp': time_to_arlotime(),
                                    active: [mode_id],
                                    inactive: []}]}
                    for i in range(1, 3):
                        body = self._arlo.be.post(AUTOMATION_PATH, params=params, raw=True)
                        if body['success']:
                            return
                        self._arlo.warning('attempt {0}: error in response when setting mode={1}'.format(i, str(body)))
                        self._arlo.debug('Fetching device list (hoping this will fix arming/disarming)')
                        self._arlo.be.devices()
                    self._arlo.error('Failed to set mode.')
                    self._arlo.debug('Giving up on setting mode! Session headers=' + self._arlo.be.session.headers)
                    self._arlo.debug('Giving up on setting mode! Session cookies=' + self._arlo.be.session.cookies)

                self._arlo.bg.run(_set_mode_v2_cb)
        else:
            self._arlo.warning('{0}: mode {1} is unrecognised'.format(self.name, mode_name))

    def update_mode(self):
        data = self._arlo.be.get(AUTOMATION_PATH)
        for mode in data:
            if mode.get('uniqueId', '') == self.unique_id:
                self._set_mode_or_schedule(mode)

    def update_modes(self):
        if self._v1_modes:
            resp = self._arlo.be.notify_and_get_response(base=self, body={"action": "get", "resource": "modes",
                                                                          "publishResponse": False})
            props = resp.get('properties', {})
            self._parse_modes(props.get('modes', []))
        else:
            modes = self._arlo.be.get(DEFINITIONS_PATH + "?uniqueIds={}".format(self.unique_id))
            modes = modes.get(self.unique_id, {})
            self._parse_modes(modes.get('modes', []))
            self._parse_schedules(modes.get('schedules', []))

    @property
    def schedule(self):
        return self._load(SCHEDULE_KEY, None)

    @property
    def on_schedule(self):
        return self.schedule is not None

    @property
    def refresh_rate(self):
        return self._refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, value):
        if isinstance(value, (int, float)):
            self._refresh_rate = value

    @property
    def siren_state(self):
        return self._load(SIREN_STATE_KEY, "off")

    def siren_on(self, duration=300, volume=8):
        body = {
            'action': 'set',
            'resource': 'siren',
            'publishResponse': True,
            'properties': {'sirenState': 'on', 'duration': int(duration), 'volume': int(volume), 'pattern': 'alarm'}
        }
        self._arlo.debug(str(body))
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def siren_off(self):
        body = {
            'action': 'set',
            'resource': 'siren',
            'publishResponse': True,
            'properties': {'sirenState': 'off'}
        }
        self._arlo.debug(str(body))
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def _ping_and_check_reply(self):
        body = {
            'action': 'set',
            'resource': self._arlo.be.sub_id,
            'publishResponse': False,
            'properties': {'devices': [self.device_id]}
        }
        self._arlo.debug(str(body))
        if self._arlo.be.notify(base=self, body=body) is None:
            self._save_and_do_callbacks(CONNECTION_KEY, 'unavailable')
        else:
            self._save_and_do_callbacks(CONNECTION_KEY, 'available')

    def ping(self):
        self._arlo.bg.run(self._ping_and_check_reply)

    @property
    def state(self):
        if self.is_unavailable:
            return 'unavailable'
        return 'available'

    def has_capability(self, cap):
        if cap in (TEMPERATURE_KEY, HUMIDITY_KEY, AIR_QUALITY_KEY):
            if self.model_id.startswith('ABC1000'):
                return True
        if cap in (SIREN_STATE_KEY,):
            if self.model_id.startswith(('VMB400', 'VMB450')):
                return True
        return super().has_capability(cap)
