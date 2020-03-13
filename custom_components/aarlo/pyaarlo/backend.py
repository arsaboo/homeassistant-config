import json
import pprint
import re
import requests
import requests.adapters
import threading
import time
import uuid

from .constant import (DEFAULT_RESOURCES, LOGIN_PATH, LOGOUT_PATH,
                       NOTIFY_PATH, SUBSCRIBE_PATH, TRANSID_PREFIX, DEVICES_PATH)
from .sseclient import SSEClient
from .util import time_to_arlotime, now_strftime


# include token and session details
class ArloBackEnd(object):

    def __init__(self, arlo):

        self._arlo = arlo
        self._lock = threading.Condition()
        self._req_lock = threading.Lock()

        self._dump_file = self._arlo.cfg.storage_dir + '/' + 'packets.dump'

        self._requests = {}
        self._callbacks = {}
        self._resource_types = DEFAULT_RESOURCES

        self._token = None
        self._user_id = None
        self._web_id = None
        self._sub_id = None

        self._ev_stream = None

        # login
        self._session = None
        self._logged_in = self._login()
        if not self._logged_in:
            self._arlo.warning('failed to log in')
            return

        # event loop thread - started as needed
        self._ev_start()

        # start logout daemon
        if self._arlo.cfg.reconnect_every != 0:
            self._arlo.debug('automatically reconnecting')
            self._arlo.bg.run_every(self.logout, self._arlo.cfg.reconnect_every)

    def _request(self, path, method='GET', params=None, headers=None, stream=False, raw=False, timeout=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if timeout is None:
            timeout = self._arlo.cfg.request_timeout
        try:
            with self._req_lock:
                url = self._arlo.cfg.host + path
                #self._arlo.vdebug('starting request=' + str(url))
                #self._arlo.vdebug('starting request=' + str(params))
                #self._arlo.vdebug('starting request=' + str(headers))
                if method == 'GET':
                    r = self._session.get(url, params=params, headers=headers, stream=stream, timeout=timeout)
                    if stream is True:
                        return r
                elif method == 'PUT':
                    r = self._session.put(url, json=params, headers=headers, timeout=timeout)
                elif method == 'POST':
                    r = self._session.post(url, json=params, headers=headers, timeout=timeout)
        except Exception as e:
            self._arlo.warning('request-error={}'.format(type(e).__name__))
            return None

        # self._arlo.debug('finish request=' + str(r.status_code))
        if r.status_code != 200:
            return None

        body = r.json()
        # self._arlo.debug(pprint.pformat(body, indent=2))

        if raw:
            return body
        if body['success']:
            if 'data' in body:
                return body['data']
        else:
            self._arlo.warning('error in response=' + str(body))
        return None

    def gen_trans_id(self, trans_type=TRANSID_PREFIX):
        return trans_type + '!' + str(uuid.uuid4())

    def _ev_reconnected(self):
        self._arlo.debug('Fetching device list after ev-reconnect')
        self.devices()

    def _ev_dispatcher(self, response):

        # get message type(s) and id(s)
        responses = []
        resource = response.get('resource', '')

        err = response.get('error', None)
        if err is not None:
            self._arlo.info('error: code=' + str(err.get('code', 'xxx')) + ',message=' + str(err.get('message', 'XXX')))

        #
        # I'm trying to keep this as generic as possible... but it needs some
        # smarts to figure out where to send responses - the packets from Arlo
        # are anything but consistent...
        # See docs/packets for and idea of what we're parsing.
        #

        # Answer for async ping. Note and finish.
        # Packet number #1.
        if resource.startswith('subscriptions/'):
            self._arlo.vdebug('async ping response ' + resource)
            return

        # These is a base station mode response. Find base station ID and
        # forward response.
        # Packet number #4.
        if resource == 'activeAutomations':
            for device_id in response:
                if device_id != 'resource':
                    responses.append((device_id, resource, response[device_id]))

        # These are individual device responses. Find device ID and forward
        # response.
        # Packet number #?.
        elif [x for x in self._resource_types if resource.startswith(x + '/')]:
            device_id = resource.split('/')[1]
            responses.append((device_id, resource, response))

        # These are base station responses. Which can be about the base station
        # or devices on it... Check if property is list.
        # Packet number #3/#2
        elif resource in self._resource_types:
            prop_or_props = response.get('properties', [])
            if isinstance(prop_or_props, list):
                for prop in prop_or_props:
                    device_id = prop.get('serialNumber')
                    responses.append((device_id, resource, prop))
            else:
                device_id = response.get('from', None)
                responses.append((device_id, resource, response))

        elif resource.startswith('audioPlayback'):
            device_id = response.get('from')
            properties = response.get('properties')
            if resource == 'audioPlayback/status':
                # Wrap the status event to match the 'audioPlayback' event
                properties = {'status': response.get('properties')}

            self._arlo.info('audio playback response {} - {}'.format(resource, response))
            if device_id is not None and properties is not None:
                responses.append((device_id, resource, properties))

        # This a list ditch effort to funnel the answer the correct place...
        #  Check for device_id
        #  Check for unique_id
        # If none of those then is unhandled
        # Packet number #?.
        else:
            device_id = response.get('deviceId', None)
            if device_id is not None:
                responses.append((device_id, resource, response))
            else:
                device_id = response.get('uniqueId', None)
                if device_id is not None:
                    responses.append((device_id, resource, response))
                else:
                    self._arlo.debug('unhandled response {} - {}'.format(resource, response))

        # Now find something waiting for this/these.
        for device_id, resource, response in responses:
            cbs = []
            self._arlo.debug('sending ' + resource + ' to ' + device_id)
            with self._lock:
                if device_id and device_id in self._callbacks:
                    cbs.extend(self._callbacks[device_id])
                if 'all' in self._callbacks:
                    cbs.extend(self._callbacks['all'])
            for cb in cbs:
                cb(resource, response)

    def _ev_loop(self, stream):
        # for event in stream.events():
        for event in stream:

            # stopped?
            if event is None:
                with self._lock:
                    self._ev_connected_ = False
                    self._lock.notify_all()
                break

            response = json.loads(event.data)
            if self._arlo.cfg.dump:
                with open(self._dump_file, 'a') as dump:
                    time_stamp = now_strftime("%Y-%m-%d %H:%M:%S.%f")
                    dump.write("{}: {}\n".format(time_stamp,pprint.pformat(response, indent=2)))

            # logged out? signal exited
            if response.get('action') == 'logout':
                with self._lock:
                    self._ev_connected_ = False
                    self._requests = {}
                    self._lock.notify_all()
                self._arlo.warning('logged out? did you log in from elsewhere?')
                break

            # connected - yay!
            if response.get('status') == 'connected':
                with self._lock:
                    self._ev_connected_ = True
                    self._lock.notify_all()
                continue

            # is this from a notify? then signal to waiting entity, also
            # pass into dispatcher
            tid = response.get('transId')
            with self._lock:
                if tid and tid in self._requests:
                    self._requests[tid] = response
                    self._lock.notify_all()
                    continue

            self._ev_dispatcher(response)

    def _ev_thread(self):

        self._arlo.debug('starting event loop')
        while True:

            # login again if not first iteration, this will also create a new session
            while not self._logged_in:
                with self._lock:
                    self._lock.wait(5)
                self._arlo.debug('re-logging in')
                self._logged_in = self._login()

            # get stream, restart after requested seconds of inactivity or forced close
            try:
                if self._arlo.cfg.stream_timeout == 0:
                    self._arlo.debug('starting stream with no timeout')
                    # self._ev_stream = SSEClient( self.get( SUBSCRIBE_PATH + self._token,stream=True,raw=True ) )
                    self._ev_stream = SSEClient(self._arlo, self._arlo.cfg.host + SUBSCRIBE_PATH + self._token,
                                                session=self._session,
                                                reconnect_cb=self._ev_reconnected)
                else:
                    self._arlo.debug('starting stream with {} timeout'.format(self._arlo.cfg.stream_timeout))
                    # self._ev_stream = SSEClient(
                    #     self.get(SUBSCRIBE_PATH + self._token, stream=True, raw=True,
                    #              timeout=self._arlo.cfg.stream_timeout))
                    self._ev_stream = SSEClient(self._arlo, self._arlo.cfg.host + SUBSCRIBE_PATH + self._token,
                                                session=self._session,
                                                reconnect_cb=self._ev_reconnected,
                                                timeout=self._arlo.cfg.stream_timeout)
                self._ev_loop(self._ev_stream)
            except requests.exceptions.ConnectionError:
                self._arlo.warning('event loop timeout')
            except AttributeError as e:
                self._arlo.warning('forced close ' + str(e))
            except Exception as e:
                self._arlo.warning('general exception ' + str(e))

            # restart login...
            self._ev_stream = None
            self._logged_in = False

    def _ev_start(self):
        self._ev_stream = None
        self._ev_connected_ = False
        self._ev_thread = threading.Thread(name="ArloEventStream", target=self._ev_thread, args=())
        self._ev_thread.setDaemon(True)
        self._ev_thread.start()

        # give time to start
        with self._lock:
            self._lock.wait(30)
        if not self._ev_connected_:
            self._arlo.warning('event loop failed to start')
            self._ev_thread = None
            return False
        return True

    def notify(self, base, body, trans_id=None):
        if trans_id is None:
            trans_id = self.gen_trans_id()

        body['to'] = base.device_id
        body['from'] = self._web_id
        body['transId'] = trans_id
        self.post(NOTIFY_PATH + base.device_id, body, headers={"xcloudId": base.xcloud_id})
        return trans_id

    def notify_and_get_response(self, base, body, timeout=None):
        if timeout is None:
            timeout = self._arlo.cfg.request_timeout

        with self._lock:
            tid = self.gen_trans_id()
            self._requests[tid] = None

        self.notify(base, body, trans_id=tid)
        mnow = time.monotonic()
        mend = mnow + timeout

        with self._lock:
            while not self._requests[tid]:
                self._lock.wait(mend - mnow)
                if self._requests[tid]:
                    return self._requests.pop(tid)
                mnow = time.monotonic()
                if mnow >= mend:
                    return self._requests.pop(tid)

    def ping(self, base):
        return self.notify_and_get_response(base, {"action": "set", "resource": self._sub_id,
                                                   "publishResponse": False,
                                                   "properties": {"devices": [base.device_id]}})

    def async_ping(self, base):
        return self.notify(base, {"action": "set", "resource": self._sub_id,
                                  "publishResponse": False, "properties": {"devices": [base.device_id]}})

    def async_on_off(self, base, device, privacy_on):
        return self.notify(base, {"action": "set", "resource": device.resource_id,
                                  "publishResponse": True,
                                  "properties": {"privacyActive": privacy_on}})

    # login and set up session
    def _login(self):

        # attempt login
        self._session = requests.Session()
        if self._arlo.cfg.http_connections != 0 and self._arlo.cfg.http_max_size != 0:
            self._arlo.debug(
                'custom connections {}:{}'.format(self._arlo.cfg.http_connections, self._arlo.cfg.http_max_size))
            self._session.mount('https://',
                                requests.adapters.HTTPAdapter(
                                    pool_connections=self._arlo.cfg.http_connections,
                                    pool_maxsize=self._arlo.cfg.http_max_size))
        body = self.post(LOGIN_PATH, {'email': self._arlo.cfg.username, 'password': self._arlo.cfg.password})
        if body is None:
            self._arlo.debug('login failed')
            return False

        # save new login information
        self._token = body['token']
        self._user_id = body['userId']
        self._web_id = self._user_id + '_web'
        self._sub_id = 'subscriptions/' + self._web_id

        # update sessions headers
        # XXX allow different user agent
        headers = {
            # 'DNT': '1',
            'Accept': 'application/json, text/plain, */*',
            'schemaVersion': '1',
            'Host': re.sub('https?://', '', self._arlo.cfg.host),
            'Content-Type': 'application/json; charset=utf-8;',
            'Referer': self._arlo.cfg.host,
            'Authorization': self._token
        }
        if self._arlo.cfg.user_agent == 'apple':
            headers['User-Agent'] = ('Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_2 like Mac OS X) '
                                     'AppleWebKit/604.3.5 (KHTML, like Gecko) Mobile/15B202 NETGEAR/v1 '
                                     '(iOS Vuezone)')
        else:
            headers['User-Agent'] = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/72.0.3626.81 Safari/537.36')

        self._session.headers.update(headers)
        return True

    def is_connected(self):
        return self._logged_in

    def logout(self):
        self._arlo.debug('trying to logout')
        if self._ev_stream is not None:
            self._ev_stream.stop()
        self.put(LOGOUT_PATH)

    def get(self, path, params=None, headers=None, stream=False, raw=False, timeout=None):
        return self._request(path, 'GET', params, headers, stream, raw, timeout)

    def put(self, path, params=None, headers=None, raw=False, timeout=None):
        return self._request(path, 'PUT', params, headers, False, raw, timeout)

    def post(self, path, params=None, headers=None, raw=False, timeout=None):
        return self._request(path, 'POST', params, headers, False, raw, timeout)

    @property
    def session(self):
        return self._session

    def add_listener(self, device, callback):
        with self._lock:
            if device.device_id not in self._callbacks:
                self._callbacks[device.device_id] = []
            self._callbacks[device.device_id].append(callback)
            if device.unique_id not in self._callbacks:
                self._callbacks[device.unique_id] = []
            self._callbacks[device.unique_id].append(callback)

    def add_any_listener(self, callback):
        with self._lock:
            if 'all' not in self._callbacks:
                self._callbacks['all'] = []
            self._callbacks['all'].append(callback)

    def del_listener(self, device, callback):
        pass

    def devices(self):
        return self.get(DEVICES_PATH + "?t={}".format(time_to_arlotime()))
