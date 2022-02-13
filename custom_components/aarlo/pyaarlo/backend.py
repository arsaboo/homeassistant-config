import json
import pickle
import pprint
import random
import re
import ssl
import threading
import time
import traceback
import uuid

import cloudscraper
import paho.mqtt.client as mqtt
import requests
import requests.adapters

from .constant import (
    AUTH_FINISH_PATH,
    AUTH_GET_FACTORS,
    AUTH_PATH,
    AUTH_START_PATH,
    AUTH_VALIDATE_PATH,
    DEFAULT_RESOURCES,
    DEVICES_PATH,
    LOGOUT_PATH,
    MQTT_HOST,
    MQTT_PATH,
    NOTIFY_PATH,
    ORIGIN_HOST,
    REFERER_HOST,
    SESSION_PATH,
    SUBSCRIBE_PATH,
    TFA_CONSOLE_SOURCE,
    TFA_IMAP_SOURCE,
    TFA_PUSH_SOURCE,
    TFA_REST_API_SOURCE,
    TRANSID_PREFIX,
)
from .sseclient import SSEClient
from .tfa import Arlo2FAConsole, Arlo2FAImap, Arlo2FARestAPI
from .util import days_until, now_strftime, time_to_arlotime, to_b64


# include token and session details
class ArloBackEnd(object):
    def __init__(self, arlo):

        self._arlo = arlo
        self._lock = threading.Condition()
        self._req_lock = threading.Lock()

        self._dump_file = self._arlo.cfg.dump_file
        self._use_mqtt = self._arlo.cfg.use_mqtt

        self._requests = {}
        self._callbacks = {}
        self._resource_types = DEFAULT_RESOURCES

        self._load_session()

        # event thread stuff
        self._event_thread = None
        self._event_client = None
        self._event_connected = False
        self._stop_thread = False

        # login
        self._session = None
        self._logged_in = self._login()
        if not self._logged_in:
            self._arlo.debug("failed to log in")
            return

    def _load_session(self):
        self._user_id = None
        self._web_id = None
        self._sub_id = None
        self._token = None
        self._expires_in = 0
        if not self._arlo.cfg.save_session:
            return
        try:
            with open(self._arlo.cfg.session_file, "rb") as dump:
                session_info = pickle.load(dump)
                self._user_id = session_info["user_id"]
                self._web_id = session_info["web_id"]
                self._sub_id = session_info["sub_id"]
                self._token = session_info["token"]
                self._expires_in = session_info["expires_in"]
                self._arlo.debug(f"load:session_info={session_info}")
        except Exception:
            self._arlo.debug("session file not read")

    def _save_session(self):
        if not self._arlo.cfg.save_session:
            return
        try:
            with open(self._arlo.cfg.session_file, "wb") as dump:
                session_info = {
                    "user_id": self._user_id,
                    "web_id": self._web_id,
                    "sub_id": self._sub_id,
                    "token": self._token,
                    "expires_in": self._expires_in,
                }
                pickle.dump(session_info, dump)
                self._arlo.debug(f"save:session_info={session_info}")
        except Exception as e:
            self._arlo.warning("session file not written" + str(e))

    def _request(
        self,
        path,
        method="GET",
        params=None,
        headers=None,
        stream=False,
        raw=False,
        timeout=None,
        host=None,
    ):
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
                self._arlo.vdebug("request-url={}".format(url))
                self._arlo.vdebug("request-params=\n{}".format(pprint.pformat(params)))
                self._arlo.vdebug(
                    "request-headers=\n{}".format(pprint.pformat(headers))
                )
                if method == "GET":
                    r = self._session.get(
                        url,
                        params=params,
                        headers=headers,
                        stream=stream,
                        timeout=timeout,
                    )
                    if stream is True:
                        return r
                elif method == "PUT":
                    r = self._session.put(
                        url, json=params, headers=headers, timeout=timeout
                    )
                elif method == "POST":
                    r = self._session.post(
                        url, json=params, headers=headers, timeout=timeout
                    )
        except Exception as e:
            self._arlo.warning("request-error={}".format(type(e).__name__))
            return None

        try:
            body = r.json()
            self._arlo.vdebug("request-body=\n{}".format(pprint.pformat(body)))
        except Exception as e:
            self._arlo.warning("body-error={}".format(type(e).__name__))
            return None

        self._arlo.vdebug("request-end={}".format(r.status_code))
        if r.status_code != 200:
            return None

        if raw:
            return body

        # New auth style and TFA helper
        if "meta" in body:
            if body["meta"]["code"] == 200:
                return body["data"]
            else:
                self._arlo.warning("error in new response=" + str(body))

        # Original response type
        elif "success" in body:
            if body["success"]:
                if "data" in body:
                    return body["data"]
                # success, but no data so fake empty data
                return {}
            else:
                self._arlo.warning("error in response=" + str(body))

        return None

    def gen_trans_id(self, trans_type=TRANSID_PREFIX):
        return trans_type + "!" + str(uuid.uuid4())

    def _event_dispatcher(self, response):

        # get message type(s) and id(s)
        responses = []
        resource = response.get("resource", "")

        err = response.get("error", None)
        if err is not None:
            self._arlo.info(
                "error: code="
                + str(err.get("code", "xxx"))
                + ",message="
                + str(err.get("message", "XXX"))
            )

        #
        # I'm trying to keep this as generic as possible... but it needs some
        # smarts to figure out where to send responses - the packets from Arlo
        # are anything but consistent...
        # See docs/packets for and idea of what we're parsing.
        #

        # Answer for async ping. Note and finish.
        # Packet number #1.
        if resource.startswith("subscriptions/"):
            self._arlo.vdebug("async ping response " + resource)
            return

        # These is a base station mode response. Find base station ID and
        # forward response.
        # Packet number #4.
        if resource == "activeAutomations":
            for device_id in response:
                if device_id != "resource":
                    responses.append((device_id, resource, response[device_id]))

        # Mode update response
        elif "states" in response:
            device_id = response.get("from", None)
            if device_id is not None:
                responses.append((device_id, "states", response["states"]))

        # These are individual device responses. Find device ID and forward
        # response.
        # Packet number #?.
        elif [x for x in self._resource_types if resource.startswith(x + "/")]:
            device_id = resource.split("/")[1]
            responses.append((device_id, resource, response))

        # These are base station responses. Which can be about the base station
        # or devices on it... Check if property is list.
        # Packet number #3/#2
        elif resource in self._resource_types:
            prop_or_props = response.get("properties", [])
            if isinstance(prop_or_props, list):
                for prop in prop_or_props:
                    device_id = prop.get("serialNumber", None)
                    if device_id is None:
                        device_id = response.get("from", None)
                    responses.append((device_id, resource, prop))
            else:
                device_id = response.get("from", None)
                responses.append((device_id, resource, response))

        elif resource.startswith("audioPlayback"):
            device_id = response.get("from")
            properties = response.get("properties")
            if resource == "audioPlayback/status":
                # Wrap the status event to match the 'audioPlayback' event
                properties = {"status": response.get("properties")}

            self._arlo.info(
                "audio playback response {} - {}".format(resource, response)
            )
            if device_id is not None and properties is not None:
                responses.append((device_id, resource, properties))

        # This a list ditch effort to funnel the answer the correct place...
        #  Check for device_id
        #  Check for unique_id
        # If none of those then is unhandled
        # Packet number #?.
        else:
            device_id = response.get("deviceId", None)
            if device_id is not None:
                responses.append((device_id, resource, response))
            else:
                device_id = response.get("uniqueId", None)
                if device_id is not None:
                    responses.append((device_id, resource, response))
                else:
                    self._arlo.debug(
                        "unhandled response {} - {}".format(resource, response)
                    )

        # Now find something waiting for this/these.
        for device_id, resource, response in responses:
            cbs = []
            self._arlo.debug("sending {} to {}".format(resource, device_id))
            with self._lock:
                if device_id and device_id in self._callbacks:
                    cbs.extend(self._callbacks[device_id])
                if "all" in self._callbacks:
                    cbs.extend(self._callbacks["all"])
            for cb in cbs:
                self._arlo.bg.run(cb, resource=resource, event=response)

    def _event_handle_response(self, response):

        # Debugging.
        if self._dump_file is not None:
            with open(self._dump_file, "a") as dump:
                time_stamp = now_strftime("%Y-%m-%d %H:%M:%S.%f")
                dump.write(
                    "{}: {}\n".format(time_stamp, pprint.pformat(response, indent=2))
                )
        self._arlo.vdebug("packet-in=\n{}".format(pprint.pformat(response, indent=2)))

        # Run the dispatcher to set internal state and run callbacks.
        self._event_dispatcher(response)

        # is there a notify/post waiting for this response? If so, signal to waiting entity.
        tid = response.get("transId", None)
        resource = response.get("resource", None)
        device_id = response.get("from", None)
        with self._lock:
            # Transaction ID
            # Simple. We have a transaction ID, look for that. These are
            # usually returned by notify requests.
            if tid and tid in self._requests:
                self._requests[tid] = response
                self._lock.notify_all()

            # Resource
            # These are usually returned after POST requests. We trap these
            # to make async calls sync.
            if resource:
                # Historical. We are looking for a straight matching resource.
                if resource in self._requests:
                    self._arlo.vdebug("{} found by text!".format(resource))
                    self._requests[resource] = response
                    self._lock.notify_all()
                else:
                    # Complex. We are looking for a resource and-or
                    # deviceid matching a regex.
                    if device_id:
                        resource = "{}:{}".format(resource, device_id)
                        self._arlo.vdebug("{} bounded device!".format(resource))
                    for request in self._requests:
                        if re.match(request, resource):
                            self._arlo.vdebug(
                                "{} found by regex {}!".format(resource, request)
                            )
                            self._requests[request] = response
                            self._lock.notify_all()

    def _event_stop_loop(self):
        self._stop_thread = True

    def _event_main(self):
        self._arlo.debug("re-logging in")

        while not self._stop_thread:

            # say we're starting
            if self._dump_file is not None:
                with open(self._dump_file, "a") as dump:
                    time_stamp = now_strftime("%Y-%m-%d %H:%M:%S.%f")
                    dump.write("{}: {}\n".format(time_stamp, "event_thread start"))

            # login again if not first iteration, this will also create a new session
            while not self._logged_in:
                with self._lock:
                    self._lock.wait(5)
                self._arlo.debug("re-logging in")
                self._logged_in = self._login()

            if self._use_mqtt:
                self._mqtt_main()
            else:
                self._sse_main()

            # clear down and signal out
            with self._lock:
                self._client_connected = False
                self._requests = {}
                self._lock.notify_all()

            # restart login...
            self._event_client = None
            self._logged_in = False

    def _mqtt_subscribe(self):
        # Make sure we are listening to library events and individual base
        # station events. This seems sufficient for now.
        self._event_client.subscribe(
            [
                (f"u/{self._user_id}/in/userSession/connect", 0),
                (f"u/{self._user_id}/in/userSession/disconnect", 0),
                (f"u/{self._user_id}/in/library/add", 0),
                (f"u/{self._user_id}/in/library/update", 0),
                (f"u/{self._user_id}/in/library/remove", 0),
            ]
        )

        topics = []
        for device in self._arlo.devices:
            for topic in device.get("allowedMqttTopics", []):
                topics.append((topic, 0))
        self._arlo.debug("topcs=\n{}".format(pprint.pformat(topics)))
        self._event_client.subscribe(topics)

    def _mqtt_on_connect(self, _client, _userdata, _flags, rc):
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self._arlo.debug(f"mqtt: connected={str(rc)}")
        self._mqtt_subscribe()
        with self._lock:
            self._event_connected = True
            self._lock.notify_all()

    def _mqtt_on_log(self, _client, _userdata, _level, msg):
        self._arlo.vdebug(f"mqtt: log={str(msg)}")

    def _mqtt_on_message(self, _client, _userdata, msg):
        self._arlo.debug(f"mqtt: topic={msg.topic}")

        try:
            response = json.loads(msg.payload.decode("utf-8"))

            # deal with mqtt specific pieces
            if response.get("action", "") == "logout":
                # Logged out? MQTT will log back in until stopped.
                self._arlo.warning("logged out? did you log in from elsewhere?")
                return

            # pass on to general handler
            self._event_handle_response(response)

        except json.decoder.JSONDecodeError as e:
            self._arlo.debug("reopening: json error " + str(e))

    def _mqtt_main(self):

        try:
            self._arlo.debug("(re)starting mqtt event loop")
            headers = {
                "Host": MQTT_HOST,
                "Origin": ORIGIN_HOST,
            }

            # Build a new client_id per login. The last 10 numbers seem to need to be random.
            self._event_client_id = f"user_{self._user_id}_" + "".join(
                str(random.randint(0, 9)) for _ in range(10)
            )
            self._arlo.debug(f"mqtt: client_id={self._event_client_id}")

            # Create and set up the MQTT client.
            self._event_client = mqtt.Client(
                client_id=self._event_client_id, transport="websockets"
            )
            self._event_client.on_log = self._mqtt_on_log
            self._event_client.on_connect = self._mqtt_on_connect
            self._event_client.on_message = self._mqtt_on_message
            self._event_client.tls_set_context(ssl.create_default_context())
            self._event_client.username_pw_set(f"{self._user_id}", self._token)
            self._event_client.ws_set_options(path=MQTT_PATH, headers=headers)

            # Connect.
            self._event_client.connect(MQTT_HOST, port=443, keepalive=60)
            self._event_client.loop_forever()

        except Exception as e:
            # self._arlo.warning('general exception ' + str(e))
            self._arlo.error(
                "general-error={}\n{}".format(type(e).__name__, traceback.format_exc())
            )

    def _sse_reconnected(self):
        self._arlo.debug("fetching device list after ev-reconnect")
        self.devices()

    def _sse_reconnect(self):
        self._arlo.debug("trying to reconnect")
        if self._event_client is not None:
            self._event_client.stop()

    def _sse_main(self):

        # get stream, restart after requested seconds of inactivity or forced close
        try:
            if self._arlo.cfg.stream_timeout == 0:
                self._arlo.debug("starting stream with no timeout")
                self._event_client = SSEClient(
                    self._arlo,
                    self._arlo.cfg.host + SUBSCRIBE_PATH,
                    session=self._session,
                    reconnect_cb=self._sse_reconnected,
                )
            else:
                self._arlo.debug(
                    "starting stream with {} timeout".format(
                        self._arlo.cfg.stream_timeout
                    )
                )
                self._event_client = SSEClient(
                    self._arlo,
                    self._arlo.cfg.host + SUBSCRIBE_PATH,
                    session=self._session,
                    reconnect_cb=self._sse_reconnected,
                    timeout=self._arlo.cfg.stream_timeout,
                )

            for event in self._event_client:

                # stopped?
                if event is None:
                    self._arlo.debug("reopening: no event")
                    break

                # dig out response
                try:
                    response = json.loads(event.data)
                except json.decoder.JSONDecodeError as e:
                    self._arlo.debug("reopening: json error " + str(e))
                    break

                # deal with SSE specific pieces
                # logged out? signal exited
                if response.get("action", "") == "logout":
                    self._arlo.warning("logged out? did you log in from elsewhere?")
                    break

                # connected - yay!
                if response.get("status", "") == "connected":
                    with self._lock:
                        self._event_connected = True
                        self._lock.notify_all()
                    continue

                # pass on to general handler
                self._event_handle_response(response)

        except requests.exceptions.ConnectionError:
            self._arlo.warning("event loop timeout")
        except AttributeError as e:
            self._arlo.warning("forced close " + str(e))
        except Exception as e:
            # self._arlo.warning('general exception ' + str(e))
            self._arlo.error(
                "general-error={}\n{}".format(type(e).__name__, traceback.format_exc())
            )

    def start_monitoring(self):
        self._event_client = None
        self._event_connected = False
        self._event_thread = threading.Thread(
            name="ArloEventStream", target=self._event_main, args=()
        )
        self._event_thread.setDaemon(True)

        with self._lock:
            self._event_thread.start()
            count = 0
            while not self._event_connected and count < 30:
                self._arlo.debug("waiting for stream up")
                self._lock.wait(1)
                count += 1

        # start logout daemon for sse clients
        if not self._use_mqtt:
            if self._arlo.cfg.reconnect_every != 0:
                self._arlo.debug("automatically reconnecting")
                self._arlo.bg.run_every(self._sse_reconnect, self._arlo.cfg.reconnect_every)
        self._arlo.debug("stream up")
        return True

    def _get_tfa(self):
        """Return the 2FA type we're using."""
        tfa_type = self._arlo.cfg.tfa_source
        if tfa_type == TFA_CONSOLE_SOURCE:
            return Arlo2FAConsole(self._arlo)
        elif tfa_type == TFA_IMAP_SOURCE:
            return Arlo2FAImap(self._arlo)
        elif tfa_type == TFA_REST_API_SOURCE:
            return Arlo2FARestAPI(self._arlo)
        else:
            return tfa_type

    def _update_auth_info(self, body):
        self._token = body["token"]
        self._token64 = to_b64(self._token)
        self._user_id = body["userId"]
        self._web_id = self._user_id + "_web"
        self._sub_id = "subscriptions/" + self._web_id
        self._expires_in = body["expiresIn"]

    def _auth(self):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": ORIGIN_HOST,
            "Referer": REFERER_HOST,
            "Source": "arloCamWeb",
            "User-Agent": self._user_agent,
        }

        # Handle 1015 error
        attempt = 0
        body = None
        while attempt < 3:
            attempt += 1
            self._arlo.debug("login attempt #{}".format(attempt))
            body = self.auth_post(
                AUTH_PATH,
                {
                    "email": self._arlo.cfg.username,
                    "password": to_b64(self._arlo.cfg.password),
                    "language": "en",
                    "EnvSource": "prod",
                },
                headers,
            )
            if body is not None:
                break
            time.sleep(1)
        if body is None:
            self._arlo.error("authentication failed")
            return False

        # save new login information
        self._update_auth_info(body)

        # Looks like we need 2FA. So, request a code be sent to our email address.
        if not body["authCompleted"]:
            self._arlo.debug("need 2FA...")

            # update headers and create 2fa instance
            headers["Authorization"] = self._token64
            tfa = self._get_tfa()

            # get available 2fa choices,
            self._arlo.debug("getting tfa choices")
            factors = self.auth_get(
                AUTH_GET_FACTORS + "?data = {}".format(int(time.time())), {}, headers
            )
            if factors is None:
                self._arlo.error("2fa: no secondary choices available")
                return False

            # look for code source choice
            self._arlo.debug("looking for {}".format(self._arlo.cfg.tfa_type))
            factor_id = None
            for factor in factors["items"]:
                if factor["factorType"].lower() == self._arlo.cfg.tfa_type:
                    factor_id = factor["factorId"]
            if factor_id is None:
                self._arlo.error("2fa no suitable secondary choice available")
                return False

            if tfa != TFA_PUSH_SOURCE:
                # snapshot 2fa before sending in request
                if not tfa.start():
                    self._arlo.error("2fa startup failed")
                    return False

                # start authentication with email
                self._arlo.debug(
                    "starting auth with {}".format(self._arlo.cfg.tfa_type)
                )
                body = self.auth_post(AUTH_START_PATH, {"factorId": factor_id}, headers)
                if body is None:
                    self._arlo.error("2fa startAuth failed")
                    return False
                factor_auth_code = body["factorAuthCode"]

                # get code from TFA source
                code = tfa.get()
                if code is None:
                    self._arlo.error("2fa core retrieval failed")
                    return False

                # tidy 2fa
                tfa.stop()

                # finish authentication
                self._arlo.debug("finishing auth")
                body = self.auth_post(
                    AUTH_FINISH_PATH,
                    {"factorAuthCode": factor_auth_code, "otp": code},
                    headers,
                )
                if body is None:
                    self._arlo.error("2fa finishAuth failed")
                    return False
            else:
                # start authentication
                self._arlo.debug(
                    "starting auth with {}".format(self._arlo.cfg.tfa_type)
                )
                body = self.auth_post(AUTH_START_PATH, {"factorId": factor_id}, headers)
                if body is None:
                    self._arlo.error("2fa startAuth failed")
                    return False
                factor_auth_code = body["factorAuthCode"]
                tries = 1
                while True:
                    # finish authentication
                    self._arlo.debug("finishing auth")
                    body = self.auth_post(
                        AUTH_FINISH_PATH,
                        {"factorAuthCode": factor_auth_code},
                        headers,
                    )
                    if body is None:
                        self._arlo.warning("2fa finishAuth - tries {}".format(tries))
                        if tries < self._arlo.cfg.tfa_retries:
                            time.sleep(self._arlo.cfg.tfa_delay)
                            tries += 1
                        else:
                            self._arlo.error("2fa finishAuth failed")
                            return False
                    else:
                        break

            # save new login information
            self._update_auth_info(body)

        return True

    def _validate(self):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self._token64,
            "Origin": ORIGIN_HOST,
            "Referer": REFERER_HOST,
            "User-Agent": self._user_agent,
            "Source": "arloCamWeb",
        }

        # Validate it!
        validated = self.auth_get(
            AUTH_VALIDATE_PATH + "?data = {}".format(int(time.time())), {}, headers
        )
        if validated is None:
            self._arlo.error("token validation failed")
            return False
        return True

    def _v2_session(self):
        v2_session = self.get(SESSION_PATH)
        if v2_session is None:
            self._arlo.error("session start failed")
            return False
        return True

    def _login(self):

        # pickup user configured user agent
        self._user_agent = self.user_agent(self._arlo.cfg.user_agent)

        # If token looks invalid we'll try the whole process.
        get_new_session = days_until(self._expires_in) < 2
        if get_new_session:
            self._session = cloudscraper.create_scraper()
            self._arlo.debug("oldish session, getting a new one")
            if not self._auth():
                return False
            if not self._validate():
                return False
            self._save_session()

        else:
            self._session = requests.session()
            self._arlo.debug("newish sessions, re-using")

        # update sessions headers
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Auth-Version": "2",
            "Authorization": self._token,
            "Content-Type": "application/json; charset=utf-8;",
            "Origin": ORIGIN_HOST,
            "Pragma": "no-cache",
            "Referer": REFERER_HOST,
            "SchemaVersion": "1",
            "User-Agent": self._user_agent,
        }
        self._session.headers.update(headers)

        # Grab a session. Needed for new session and used to check existing
        # session. (May not really be needed for existing but will fail faster.)
        if not self._v2_session():
            if not get_new_session:
                self._expires_in = 0
                self._token = None
                return self._login()
            return False
        return True

    def _notify(self, base, body, trans_id=None):
        if trans_id is None:
            trans_id = self.gen_trans_id()

        body["to"] = base.device_id
        body["from"] = self._web_id
        body["transId"] = trans_id

        if (
            self.post(
                NOTIFY_PATH + base.device_id, body, headers={"xcloudId": base.xcloud_id}
            )
            is None
        ):
            return None
        return trans_id

    def _start_transaction(self, tid=None):
        if tid is None:
            tid = self.gen_trans_id()
        self._arlo.vdebug("starting transaction-->{}".format(tid))
        with self._lock:
            self._requests[tid] = None
        return tid

    def _wait_for_transaction(self, tid, timeout):
        if timeout is None:
            timeout = self._arlo.cfg.request_timeout
        mnow = time.monotonic()
        mend = mnow + timeout

        self._arlo.vdebug("finishing transaction-->{}".format(tid))
        with self._lock:
            try:
                while mnow < mend and self._requests[tid] is None:
                    self._lock.wait(mend - mnow)
                    mnow = time.monotonic()
                response = self._requests.pop(tid)
            except KeyError as _e:
                self._arlo.debug("got a key error")
                response = None
        self._arlo.vdebug("finished transaction-->{}".format(tid))
        return response

    @property
    def is_connected(self):
        return self._logged_in

    def logout(self):
        self._arlo.debug("trying to logout")
        self._event_stop_loop()
        if self._event_client is not None:
            if self._use_mqtt:
                self._event_client.disconnect()
            else:
                self._event_client.stop()
        self.put(LOGOUT_PATH)

    def notify(self, base, body, timeout=None, wait_for=None):
        """Send in a notification.

        Notifications are Arlo's way of getting stuff done - turn on a light, change base station mode,
        start recording. Pyaarlo will post a notification and Arlo will post a reply on the event
        stream indicating if it worked or not or of a state change.

        How Pyaarlo treats notifications depends on the mode it's being run in. For asynchronous mode - the
        default - it sends the notification and returns immediately. For synchronous mode it sends the
        notification and waits for the event related to the notification to come back. To use the default
        settings leave `wait_for` as `None`, to force asynchronous set `wait_for` to `nothing` and to force
        synchronous set `wait_for` to `event`.

        There is a third way to send a notification where the code waits for the initial response to come back
        but that must be specified by setting `wait_for` to `response`.

        :param base: base station to use
        :param body: notification message
        :param timeout: how long to wait for response before failing, only applied if `wait_for` is `event`.
        :param wait_for: what to wait for, either `None`, `event`, `response` or `nothing`.
        :return: either a response packet or an event packet
        """
        if wait_for is None:
            wait_for = "event" if self._arlo.cfg.synchronous_mode else "nothing"

        if wait_for == "event":
            self._arlo.vdebug("notify+event running")
            tid = self._start_transaction()
            self._notify(base, body=body, trans_id=tid)
            return self._wait_for_transaction(tid, timeout)
            # return self._notify_and_get_event(base, body, timeout=timeout)
        elif wait_for == "response":
            self._arlo.vdebug("notify+response running")
            return self._notify(base, body=body)
        else:
            self._arlo.vdebug("notify+ sent")
            self._arlo.bg.run(self._notify, base=base, body=body)

    def get(
        self,
        path,
        params=None,
        headers=None,
        stream=False,
        raw=False,
        timeout=None,
        host=None,
        wait_for="response",
    ):
        if wait_for == "response":
            self._arlo.vdebug("get+response running")
            return self._request(
                path, "GET", params, headers, stream, raw, timeout, host
            )
        else:
            self._arlo.vdebug("get sent")
            self._arlo.bg.run(
                self._request, path, "GET", params, headers, stream, raw, timeout, host
            )

    def put(
        self,
        path,
        params=None,
        headers=None,
        raw=False,
        timeout=None,
        wait_for="response",
    ):
        if wait_for == "response":
            self._arlo.vdebug("put+response running")
            return self._request(path, "PUT", params, headers, False, raw, timeout)
        else:
            self._arlo.vdebug("put sent")
            self._arlo.bg.run(
                self._request, path, "PUT", params, headers, False, raw, timeout
            )

    def post(
        self,
        path,
        params=None,
        headers=None,
        raw=False,
        timeout=None,
        tid=None,
        wait_for="response",
    ):
        """Post a request to the Arlo servers.

        Posts are used to retrieve data from the Arlo servers. Mostly. They are also used to change
        base station modes.

        The default mode of operation is to wait for a response from the http request. The `wait_for`
        variable can change the operation. Setting it to `response` waits for a http response.
        Setting it to `resource` waits for the resource in the `params` parameter to appear in the event
        stream. Setting it to `nothing` causing the post to run in the background. Setting it to `None`
        uses `resource` in synchronous mode and `response` in asynchronous mode.
        """
        if wait_for is None:
            wait_for = "resource" if self._arlo.cfg.synchronous_mode else "response"

        if wait_for == "resource":
            self._arlo.vdebug("notify+resource running")
            if tid is None:
                tid = list(params.keys())[0]
            tid = self._start_transaction(tid)
            self._request(path, "POST", params, headers, False, raw, timeout)
            return self._wait_for_transaction(tid, timeout)
        if wait_for == "response":
            self._arlo.vdebug("post+response running")
            return self._request(path, "POST", params, headers, False, raw, timeout)
        else:
            self._arlo.vdebug("post sent")
            self._arlo.bg.run(
                self._request, path, "POST", params, headers, False, raw, timeout
            )

    def auth_post(self, path, params=None, headers=None, raw=False, timeout=None):
        return self._request(
            path, "POST", params, headers, False, raw, timeout, self._arlo.cfg.auth_host
        )

    def auth_get(
        self, path, params=None, headers=None, stream=False, raw=False, timeout=None
    ):
        return self._request(
            path, "GET", params, headers, stream, raw, timeout, self._arlo.cfg.auth_host
        )

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
            if "all" not in self._callbacks:
                self._callbacks["all"] = []
            self._callbacks["all"].append(callback)

    def del_listener(self, device, callback):
        pass

    def devices(self):
        return self.get(DEVICES_PATH + "?t={}".format(time_to_arlotime()))

    def user_agent(self, agent):
        """Map `agent` to a real user agent.

        User provides a default user agent they want for most interactions but it can be overridden
        for stream operations.
        """
        self._arlo.debug(f"looking for user_agent {agent}")
        if agent.lower() == "arlo":
            return (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_2 like Mac OS X) "
                "AppleWebKit/604.3.5 (KHTML, like Gecko) Mobile/15B202 NETGEAR/v1 "
                "(iOS Vuezone)"
            )
        elif agent.lower() == "iphone":
            return (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1_3 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Mobile/15E148 Safari/604.1"
            )
        elif agent.lower() == "ipad":
            return (
                "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1"
            )
        elif agent.lower() == "mac":
            return (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15"
            )
        elif agent.lower() == "firefox":
            return (
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) "
                "Gecko/20100101 Firefox/85.0"
            )
        else:
            return (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
            )

    def ev_inject(self, response):
        self._event_dispatcher(response)
