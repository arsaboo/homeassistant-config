import json
import pprint
import re
import threading
import time
import uuid

import requests
import requests.adapters

from .constant import (AUTH_HOST, AUTH_PATH, AUTH_VALIDATE_PATH, AUTH_GET_FACTORS, AUTH_START_PATH, AUTH_FINISH_PATH,
                       DEFAULT_RESOURCES, LOGOUT_PATH, SESSION_PATH,
                       NOTIFY_PATH, SUBSCRIBE_PATH, TRANSID_PREFIX, DEVICES_PATH)
from .sseclient import SSEClient
from .tfa import Arlo2FA
from .util import time_to_arlotime, now_strftime, to_b64


# include token and session details
class ArloBackEnd(object):

    def __init__(self, arlo):

        self._arlo = arlo
        self._lock = threading.Condition()
        self._req_lock = threading.Lock()

        self._dump_file = self._arlo.cfg.dump_file

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

    def _request(self, path, method='GET', params=None, headers=None, stream=False, raw=False, timeout=None, host=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if timeout is None:
            timeout = self._arlo.cfg.request_timeout
        try:
            with self._req_lock:
                if host is None:
                    host = self._arlo.cfg.host
                url = host + path
                self._arlo.vdebug('starting request=' + str(url))
                self._arlo.vdebug('starting request=' + str(params))
                self._arlo.vdebug('starting request=' + str(headers))
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

        self._arlo.vdebug('finish request=' + str(r.status_code))
        if r.status_code != 200:
            return None

        body = r.json()
        self._arlo.vdebug(pprint.pformat(body, indent=2))

        if raw:
            return body

        # New auth style and TFA helper
        if 'meta' in body:
            if body['meta']['code'] == 200:
                return body['data']
            else:
                self._arlo.warning('error in new response=' + str(body))

        # Original response type
        elif 'success' in body:
            if body['success']:
                if 'data' in body:
                    return body['data']
                # success, but no data so fake empty data
                return {}
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
                    device_id = prop.get('serialNumber',None)
                    if device_id is None:
                        device_id = response.get('from', None)
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
            self._arlo.debug("sending {} to {}".format(resource, device_id))
            with self._lock:
                if device_id and device_id in self._callbacks:
                    cbs.extend(self._callbacks[device_id])
                if 'all' in self._callbacks:
                    cbs.extend(self._callbacks['all'])
            for cb in cbs:
                cb(resource, response)

    def _ev_loop(self, stream):

        # say we're starting
        if self._dump_file is not None:
            with open(self._dump_file, 'a') as dump:
                time_stamp = now_strftime("%Y-%m-%d %H:%M:%S.%f")
                dump.write("{}: {}\n".format(time_stamp, "ev_loop start"))

        # for event in stream.events():
        for event in stream:

            # stopped?
            if event is None:
                with self._lock:
                    self._ev_connected_ = False
                    self._lock.notify_all()
                break

            response = json.loads(event.data)
            if self._dump_file is not None:
                with open(self._dump_file, 'a') as dump:
                    time_stamp = now_strftime("%Y-%m-%d %H:%M:%S.%f")
                    dump.write("{}: {}\n".format(time_stamp, pprint.pformat(response, indent=2)))
            self._arlo.vdebug("packet in={}".format(pprint.pformat(response, indent=2)))


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
                    self._ev_stream = SSEClient(self._arlo, self._arlo.cfg.host + SUBSCRIBE_PATH,
                                                session=self._session,
                                                reconnect_cb=self._ev_reconnected)
                else:
                    self._arlo.debug('starting stream with {} timeout'.format(self._arlo.cfg.stream_timeout))
                    # self._ev_stream = SSEClient(
                    #     self.get(SUBSCRIBE_PATH + self._token, stream=True, raw=True,
                    #              timeout=self._arlo.cfg.stream_timeout))
                    self._ev_stream = SSEClient(self._arlo, self._arlo.cfg.host + SUBSCRIBE_PATH,
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

        with self._lock:
            self._ev_thread.start()
            if not self._ev_connected_:
                self._arlo.debug('waiting for stream up')
                self._lock.wait(30)

        self._arlo.debug('stream up')
        return True

    def notify(self, base, body, trans_id=None):
        if trans_id is None:
            trans_id = self.gen_trans_id()

        body['to'] = base.device_id
        body['from'] = self._web_id
        body['transId'] = trans_id
        if self.post(NOTIFY_PATH + base.device_id, body, headers={"xcloudId": base.xcloud_id}) is None:
            return None
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

    def _update_auth_info(self, body):
        self._token = body['token']
        self._token64 = to_b64(self._token)
        self._user_id = body['userId']
        self._web_id = self._user_id + '_web'
        self._sub_id = 'subscriptions/' + self._web_id

    def _auth(self):
        headers = {'Auth-Version': '2',
                   'Accept': 'application/json, text/plain, */*',
                   'Referer': 'https://my.arlo.com',
                   'User-Agent': self._user_agent,
                   'Source': 'arloCamWeb'}

        # Initial attempt
        self._arlo.debug('login attempt #1')
        body = self.auth_post(AUTH_PATH, {'email': self._arlo.cfg.username,
                                          'password': to_b64(self._arlo.cfg.password),
                                          'language': "en",
                                          'EnvSource': 'prod'}, headers)
        if body is None:
            return False

        # save new login information
        self._update_auth_info(body)

        # Looks like we need 2FA. So, request a code be sent to our email address.
        if not body['authCompleted']:

            # update headers and create 2fa instance
            self._arlo.debug('need 2FA...')
            headers['Authorization'] = self._token64
            tfa = Arlo2FA(self._arlo)

            # get available 2fa choices,
            self._arlo.debug('getting tfa choices')
            factors = self.auth_get(AUTH_GET_FACTORS + "?data = {}".format(int(time.time())), {}, headers)
            if factors is None:
                self._arlo.debug('couldnt find tfa choices')
                return False

            # look for code source choice
            self._arlo.debug('looking for {}'.format(self._arlo.cfg.tfa_type))
            factor_id = None
            for factor in factors['items']:
                if factor['factorType'].lower() == self._arlo.cfg.tfa_type:
                    factor_id = factor['factorId']
            if factor_id is None:
                self._arlo.debug('couldnt find tfa choice')
                return False

            # snapshot 2fa before sending in request
            if not tfa.start():
                self._arlo.debug('tfa start failed')
                return False

            # start authentication with email
            self._arlo.debug('starting auth with {}'.format(self._arlo.cfg.tfa_type))
            body = self.auth_post(AUTH_START_PATH, {'factorId': factor_id}, headers)
            if body is None:
                self._arlo.debug('startAuth failed')
                return False
            factor_auth_code = body['factorAuthCode']

            # get code from TFA source
            code = tfa.get()
            if code is None:
                self._arlo.debug('tfa get failed')
                return False

            # tidy 2fa
            tfa.stop()

            # finish authentication
            self._arlo.debug('finishing auth')
            body = self.auth_post(AUTH_FINISH_PATH, {'factorAuthCode': factor_auth_code,
                                                     'otp': code}, headers)
            if body is None:
                self._arlo.debug('finishAuth failed')
                return False

            # save new login information
            self._update_auth_info(body)

        return True

    def _validate(self):
        headers = {'Auth-Version': '2',
                   'Accept': 'application/json, text/plain, */*',
                   'Authorization': self._token64,
                   'Referer': 'https://my.arlo.com',
                   'User-Agent': self._user_agent,
                   'Source': 'arloCamWeb'}

        # Validate it!
        validated = self.auth_get(AUTH_VALIDATE_PATH + "?data = {}".format(int(time.time())), {},
                                  headers)
        return validated is not None

    def _v2_session(self):
        v2_session = self.get(SESSION_PATH)
        return v2_session is not None

    def _login(self):

        # set agent before starting
        if self._arlo.cfg.user_agent == 'apple':
            self._user_agent = ('Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_2 like Mac OS X) '
                                'AppleWebKit/604.3.5 (KHTML, like Gecko) Mobile/15B202 NETGEAR/v1 '
                                '(iOS Vuezone)')
        else:
            self._user_agent = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/72.0.3626.81 Safari/537.36')

        # set up session
        self._session = requests.Session()
        if self._arlo.cfg.http_connections != 0 and self._arlo.cfg.http_max_size != 0:
            self._arlo.debug(
                'custom connections {}:{}'.format(self._arlo.cfg.http_connections, self._arlo.cfg.http_max_size))
            self._session.mount('https://',
                                requests.adapters.HTTPAdapter(
                                    pool_connections=self._arlo.cfg.http_connections,
                                    pool_maxsize=self._arlo.cfg.http_max_size))

        if not self._auth():
            self._arlo.debug('login failed')
            return False

        if not self._validate():
            self._arlo.debug('validation failed')
            return False

        # update sessions headers
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Auth-Version': '2',
            'schemaVersion': '1',
            'Host': re.sub('https?://', '', self._arlo.cfg.host),
            'Content-Type': 'application/json; charset=utf-8;',
            'Referer': self._arlo.cfg.host,
            'User-Agent': self._user_agent,
            'Authorization': self._token
        }
        self._session.headers.update(headers)

        if not self._v2_session():
            self._arlo.debug('v2 session failed')
            return False

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

    def auth_post(self, path, params=None, headers=None, raw=False, timeout=None):
        return self._request(path, 'POST', params, headers, False, raw, timeout, AUTH_HOST)

    def auth_get(self, path, params=None, headers=None, stream=False, raw=False, timeout=None):
        return self._request(path, 'GET', params, headers, stream, raw, timeout, AUTH_HOST)

    @property
    def session(self):
        return self._session

    @property
    def sub_id(self):
        return self._sub_id

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
